import csv
import hashlib
import hmac
import io
import json
import os
import secrets
import time
from pathlib import Path
from typing import Literal
from uuid import UUID, uuid4

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pydantic import BaseModel, ConfigDict, Field, StrictInt

from app.business_central import BusinessCentral, ConnectionError
from app.domain import RuleError, Store, now


class Input(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class Login(Input):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=False)
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=256)


class Line(Input):
    product_id: str = Field(min_length=1, max_length=80)
    quantity: StrictInt = Field(ge=1, le=500)


class Order(Input):
    customer_id: str = 'walk-in'
    kind: Literal['counter', 'quote'] = 'counter'
    payment: Literal['cash', 'card'] = 'card'
    lines: list[Line] = Field(min_length=1, max_length=100)


class Action(Input):
    restock: bool = False


class Purchase(Input):
    vendor_id: str
    ingredient_id: str
    quantity: StrictInt = Field(ge=1, le=100000)


class Waste(Input):
    ingredient_id: str
    quantity: StrictInt = Field(gt=0, le=100000)
    reason: str = Field(min_length=3, max_length=200)


class Customer(Input):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(default='', max_length=150)


class Case(Input):
    customer_id: str = 'walk-in'
    subject: str = Field(min_length=3, max_length=180)
    priority: Literal['normal', 'high'] = 'normal'


class Resolution(Input):
    resolution: str = Field(min_length=3, max_length=500)


class Close(Input):
    counted: StrictInt = Field(ge=0, le=10000000)


class Draft(Input):
    customer_id: UUID
    item_id: UUID
    quantity: StrictInt = Field(ge=1, le=500)


def create_app(database=None, admin_password=None, session_secret=None):
    password = admin_password or os.getenv('COFFEE_ADMIN_PASSWORD', '')
    secret = session_secret or os.getenv('COFFEE_SESSION_SECRET', '')
    if len(password) < 12 or len(secret) < 32:
        raise RuntimeError('Run python scripts/configure.py first. Admin password needs 12 characters and session secret needs 32.')
    store = Store(database or os.getenv('COFFEE_DATABASE', 'data/coffee.db'))
    signer = URLSafeTimedSerializer(secret, salt='coffee-session-v1')
    bc = BusinessCentral()
    failures = {}
    password_digest = hashlib.scrypt(password.encode(), salt=secret.encode(), n=16384, r=8, p=1)
    cashier_password = os.getenv('COFFEE_CASHIER_PASSWORD', '')
    cashier_digest = hashlib.scrypt(cashier_password.encode(), salt=secret.encode(), n=16384, r=8, p=1) if len(cashier_password) >= 12 else None
    app = FastAPI(title='Eight Examples Coffee Operations', docs_url=None, redoc_url=None, openapi_url=None)
    app.state.store = store
    app.state.bc = bc

    @app.exception_handler(RuleError)
    async def rule_error(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=409, content={'detail': str(exc)})

    @app.exception_handler(ConnectionError)
    async def connection_error(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=502, content={'detail': str(exc)})

    @app.exception_handler(httpx.HTTPError)
    async def upstream_error(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=502, content={'detail': 'Microsoft could not be reached. Retry with the same request to reconcile its status.'})

    @app.middleware('http')
    async def security(request, call_next):
        if int(request.headers.get('content-length', '0') or 0) > 100000:
            return Response(status_code=413)
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'same-origin'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        if request.url.path.startswith('/api'):
            response.headers['Cache-Control'] = 'no-store'
        return response

    def user(request: Request):
        try:
            data = signer.loads(request.cookies.get('coffee_session', ''), max_age=43200)
        except (BadSignature, SignatureExpired):
            raise HTTPException(401, 'Sign in to continue.')
        if request.method not in {'GET', 'HEAD', 'OPTIONS'}:
            if not hmac.compare_digest(request.headers.get('X-CSRF-Token', ''), data['csrf']):
                raise HTTPException(403, 'Invalid session request. Reload and try again.')
        return data

    def manager(data=Depends(user)):
        if data['role'] != 'manager':
            raise HTTPException(403, 'Manager access required.')
        return data

    def mutate(request, actor, payload, operation):
        key = request.headers.get('Idempotency-Key', '')
        try:
            UUID(key)
        except ValueError:
            raise HTTPException(400, 'A UUID Idempotency-Key header is required.')
        fingerprint = hashlib.sha256(json.dumps([request.url.path, actor['username'], payload], sort_keys=True).encode()).hexdigest()
        with store.transaction() as db:
            existing = db.execute('SELECT * FROM idempotency WHERE key=?', (key,)).fetchone()
            if existing:
                if existing['fingerprint'] != fingerprint:
                    raise HTTPException(409, 'Request key was already used with different data.')
                return json.loads(existing['result'])
            result = operation(db)
            db.execute('INSERT INTO idempotency VALUES (?,?,?)', (key, fingerprint, json.dumps(result)))
            return result

    @app.get('/api/health')
    def health():
        with store.connect() as db:
            db.execute('SELECT 1').fetchone()
        return {'status': 'ok', 'service': 'coffee-operations', 'version': os.getenv('GIT_COMMIT', 'local')}

    @app.post('/api/login')
    def login(payload: Login, request: Request, response: Response):
        ip = request.client.host if request.client else 'unknown'
        current = time.monotonic()
        for key in list(failures):
            if current - failures[key][1] > 300:
                del failures[key]
        count, started = failures.get(ip, (0, current))
        if count >= 8:
            raise HTTPException(429, 'Too many attempts. Try again in five minutes.')
        digest = hashlib.scrypt(payload.password.encode(), salt=secret.encode(), n=16384, r=8, p=1)
        role = None
        if hmac.compare_digest(digest, password_digest) and payload.username == os.getenv('COFFEE_ADMIN_USER', 'manager'):
            role = 'manager'
        if cashier_digest and hmac.compare_digest(digest, cashier_digest) and payload.username == 'cashier':
            role = 'cashier'
        if not role:
            if len(failures) > 2048:
                failures.clear()
            failures[ip] = (count + 1, started)
            raise HTTPException(401, 'Username or password is incorrect.')
        failures.pop(ip, None)
        data = {'username': payload.username, 'role': role, 'csrf': secrets.token_urlsafe(24)}
        response.set_cookie('coffee_session', signer.dumps(data), httponly=True, secure=os.getenv('COFFEE_SECURE_COOKIES', 'false').lower() == 'true', samesite='strict', max_age=43200)
        return data

    @app.get('/api/session')
    def session(data=Depends(user)):
        return data

    @app.post('/api/logout')
    def logout(response: Response, data=Depends(user)):
        response.delete_cookie('coffee_session')
        return {'ok': True}

    @app.get('/api/workspace')
    def workspace(data=Depends(user)):
        snapshot = store.snapshot()
        snapshot['connection'] = bc.status()
        return snapshot

    @app.post('/api/orders')
    def order(payload: Order, request: Request, data=Depends(user)):
        body = payload.model_dump()
        return mutate(request, data, body, lambda db: store.create_order(db, body, data['username']))

    @app.post('/api/orders/{oid}/{action}')
    def order_action(oid: UUID, action: Literal['accept', 'invoice', 'collect', 'refund'], payload: Action, request: Request, data=Depends(manager)):
        body = payload.model_dump()
        return mutate(request, data, body, lambda db: store.order_action(db, str(oid), action, body, data['username']))

    @app.post('/api/purchases')
    def purchase(payload: Purchase, request: Request, data=Depends(manager)):
        body = payload.model_dump()
        return mutate(request, data, body, lambda db: store.purchase(db, body, data['username']))

    @app.post('/api/purchases/{pid}/{action}')
    def purchase_action(pid: UUID, action: Literal['approve', 'receive', 'pay'], request: Request, data=Depends(manager)):
        return mutate(request, data, {}, lambda db: store.purchase_action(db, str(pid), action, data['username']))

    @app.post('/api/waste')
    def waste(payload: Waste, request: Request, data=Depends(manager)):
        body = payload.model_dump()
        return mutate(request, data, body, lambda db: store.waste(db, body, data['username']))

    @app.post('/api/customers')
    def customer(payload: Customer, request: Request, data=Depends(user)):
        def operation(db):
            cid = str(uuid4())
            db.execute('INSERT INTO customers VALUES (?,?,?,?,?)', (cid, payload.name.strip(), payload.email.strip(), 0, 0))
            store.log(db, data['username'], 'Customer added', payload.name)
            return store.get(db, 'customers', cid)
        return mutate(request, data, payload.model_dump(), operation)

    @app.post('/api/cases')
    def case(payload: Case, request: Request, data=Depends(user)):
        def operation(db):
            store.get(db, 'customers', payload.customer_id)
            cid = str(uuid4())
            db.execute('INSERT INTO cases VALUES (?,?,?,?,?,?,?)', (cid, payload.customer_id, payload.subject.strip(), payload.priority, 'open', None, now()))
            store.log(db, data['username'], 'Service issue opened', payload.subject)
            return store.get(db, 'cases', cid)
        return mutate(request, data, payload.model_dump(), operation)

    @app.post('/api/cases/{cid}/resolve')
    def resolve(cid: UUID, payload: Resolution, request: Request, data=Depends(user)):
        def operation(db):
            case = store.get(db, 'cases', str(cid))
            if case['status'] != 'open':
                raise RuleError('This issue is already resolved.')
            db.execute("UPDATE cases SET status='resolved',resolution=? WHERE id=?", (payload.resolution, str(cid)))
            store.log(db, data['username'], 'Service issue resolved', case['subject'], payload.resolution)
            return store.get(db, 'cases', str(cid))
        return mutate(request, data, payload.model_dump(), operation)

    @app.post('/api/close')
    def close(payload: Close, request: Request, data=Depends(manager)):
        return mutate(request, data, payload.model_dump(), lambda db: store.close_day(db, payload.counted, data['username']))

    @app.get('/api/reports/trial-balance.csv')
    def export(data=Depends(manager)):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Account', 'Name', 'Debit CAD', 'Credit CAD', 'Balance CAD'])
        for row in store.snapshot()['accounts']:
            writer.writerow([row['account'], row['name'], f"{row['debit']/100:.2f}", f"{row['credit']/100:.2f}", f"{row['balance']/100:.2f}"])
        return StreamingResponse(iter([output.getvalue()]), media_type='text/csv', headers={'Content-Disposition': 'attachment; filename=coffee-trial-balance.csv'})

    @app.get('/api/dynamics/{resource}')
    async def dynamics(resource: str, data=Depends(manager)):
        return await bc.list(resource)

    @app.post('/api/dynamics/draft-order')
    async def draft(payload: Draft, request: Request, data=Depends(manager)):
        try:
            key = UUID(request.headers.get('Idempotency-Key', '')).hex
        except ValueError:
            raise HTTPException(400, 'A UUID Idempotency-Key header is required.')
        fingerprint = hashlib.sha256(payload.model_dump_json().encode()).hexdigest()
        tracking_key = f'bc:{key}'
        with store.transaction() as db:
            row = db.execute('SELECT * FROM metadata WHERE key=?', (tracking_key,)).fetchone()
            if row:
                previous = json.loads(row['value'])
                if previous['fingerprint'] != fingerprint:
                    raise HTTPException(409, 'Request key was already used with different data.')
                if previous.get('result'):
                    return previous['result']
                if time.time() - previous['started'] < 90:
                    raise HTTPException(409, 'This draft request is still being processed. Retry after 90 seconds.')
            db.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)', (tracking_key, json.dumps({'fingerprint': fingerprint, 'started': time.time()})))
        result = await bc.draft_order(str(payload.customer_id), str(payload.item_id), payload.quantity, key)
        with store.transaction() as db:
            db.execute('UPDATE metadata SET value=? WHERE key=?', (json.dumps({'fingerprint': fingerprint, 'result': result}), tracking_key))
            store.log(db, data['username'], 'Business Central draft created', result.get('number', key))
        return result

    static = Path(os.getenv('COFFEE_STATIC', 'web/dist'))
    if static.exists():
        app.mount('/assets', StaticFiles(directory=static / 'assets'), name='assets')

        @app.get('/{path:path}')
        def index(path: str):
            if path.startswith('api/'):
                raise HTTPException(404, 'Unknown endpoint.')
            return FileResponse(static / 'index.html')

    return app
