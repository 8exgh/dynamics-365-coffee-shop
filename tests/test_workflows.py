import json
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.domain import RuleError, Store, cents
from app.main import create_app


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path / 'coffee.db')


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('COFFEE_CASHIER_PASSWORD', 'cashier-test-password')
    app = create_app(tmp_path / 'coffee.db', 'manager-test-password', 'test-session-secret-that-is-at-least-32-characters')
    with TestClient(app) as client:
        result = client.post('/api/login', json={'username': 'manager', 'password': 'manager-test-password'})
        client.headers['X-CSRF-Token'] = result.json()['csrf']
        client.headers['Idempotency-Key'] = str(uuid4())
        yield client


def sale(product='flat-white', quantity=1, customer='maya', payment='card', kind='counter'):
    return {'customer_id': customer, 'payment': payment, 'kind': kind, 'lines': [{'product_id': product, 'quantity': quantity}]}


def post(client, path, body=None):
    return client.post(path, json=body or {}, headers={'Idempotency-Key': str(uuid4())})


def invariant(store):
    snap = store.snapshot()
    assert snap['metrics']['journal_balance'] == 0
    assert all(i['stock'] >= 0 for i in snap['ingredients'])
    assert snap['metrics']['inventory_value'] == sum(i['stock'] * i['cost'] for i in snap['ingredients'])
    with store.connect() as db:
        assert not db.execute('SELECT journal_id FROM ledger GROUP BY journal_id HAVING SUM(debit)<>SUM(credit)').fetchall()


def test_counter_sale_updates_recipe_loyalty_and_ledger(store):
    before = store.snapshot()
    with store.transaction() as db:
        result = store.create_order(db, sale(quantity=2), 'test')
    after = store.snapshot()
    assert result['subtotal'] == 1050
    assert result['tax'] == 53
    assert result['total'] == 1103
    assert next(i for i in before['ingredients'] if i['id'] == 'beans')['stock'] - next(i for i in after['ingredients'] if i['id'] == 'beans')['stock'] == 36
    assert next(c for c in after['customers'] if c['id'] == 'maya')['points'] - next(c for c in before['customers'] if c['id'] == 'maya')['points'] == 10
    invariant(store)


def test_stock_failure_rolls_back_everything(store):
    before = store.snapshot()
    with pytest.raises(RuleError, match='Not enough'):
        with store.transaction() as db:
            store.create_order(db, sale('latte', 500), 'test')
    assert store.snapshot() == before


def test_concurrent_sales_cannot_oversell(store):
    with store.transaction() as db:
        available = store.get(db, 'ingredients', 'retail')['stock']
    def attempt(_):
        try:
            with store.transaction() as db:
                store.create_order(db, sale('house-blend', available), 'test')
            return True
        except RuleError:
            return False
    with ThreadPoolExecutor(2) as executor:
        assert sorted(executor.map(attempt, [1,2])) == [False, True]
    invariant(store)


def test_refund_never_recreates_prepared_drinks(store):
    with store.transaction() as db:
        order = store.create_order(db, sale(), 'test')
    before = store.snapshot()
    with pytest.raises(RuleError, match='Only unopened'):
        with store.transaction() as db:
            store.order_action(db, order['id'], 'refund', {'restock': True}, 'test')
    with store.transaction() as db:
        store.order_action(db, order['id'], 'refund', {}, 'test')
    after = store.snapshot()
    assert before['ingredients'] == after['ingredients']
    assert next(c for c in before['customers'] if c['id'] == 'maya')['points'] - next(c for c in after['customers'] if c['id'] == 'maya')['points'] == 5
    with pytest.raises(RuleError):
        with store.transaction() as db:
            store.order_action(db, order['id'], 'refund', {}, 'test')
    invariant(store)


def test_retail_refund_returns_stock(store):
    before = store.snapshot()
    with store.transaction() as db:
        order = store.create_order(db, sale('house-blend'), 'test')
        store.order_action(db, order['id'], 'refund', {'restock': True}, 'test')
    assert before['ingredients'] == store.snapshot()['ingredients']
    invariant(store)


def test_catering_quote_to_invoice_to_payment(store):
    before = store.snapshot()
    with store.transaction() as db:
        order = store.create_order(db, sale(quantity=3, kind='quote', customer='studio'), 'test')
    assert before['ingredients'] == store.snapshot()['ingredients']
    with pytest.raises(RuleError):
        with store.transaction() as db:
            store.order_action(db, order['id'], 'collect', {}, 'test')
    with store.transaction() as db:
        store.order_action(db, order['id'], 'accept', {}, 'test')
        store.order_action(db, order['id'], 'invoice', {}, 'test')
    assert store.snapshot()['metrics']['receivable'] == order['total']
    with store.transaction() as db:
        store.order_action(db, order['id'], 'collect', {}, 'test')
    assert store.snapshot()['metrics']['receivable'] == 0
    invariant(store)


def test_purchase_approval_receipt_payment(store):
    with store.transaction() as db:
        po = store.purchase(db, {'vendor_id': 'roaster', 'ingredient_id': 'beans', 'quantity': 20000}, 'test')
    assert po['status'] == 'pending'
    with pytest.raises(RuleError):
        with store.transaction() as db:
            store.purchase_action(db, po['id'], 'receive', 'test')
    with store.transaction() as db:
        store.purchase_action(db, po['id'], 'approve', 'test')
        store.purchase_action(db, po['id'], 'receive', 'test')
    assert store.snapshot()['metrics']['payable'] == 60000
    with store.transaction() as db:
        store.purchase_action(db, po['id'], 'pay', 'test')
    assert store.snapshot()['metrics']['payable'] == 0
    invariant(store)


def test_waste_and_close_reconciliation(store):
    with store.transaction() as db:
        store.waste(db, {'ingredient_id': 'milk', 'quantity': 500, 'reason': 'Spoiled milk'}, 'test')
    expected = store.snapshot()['metrics']['cash']
    with store.transaction() as db:
        result = store.close_day(db, expected - 50, 'test')
    assert result['variance'] == -50
    with pytest.raises(RuleError, match='closed'):
        with store.transaction() as db:
            store.create_order(db, sale(), 'test')
    with pytest.raises(RuleError, match='closed'):
        with store.transaction() as db:
            store.close_day(db, expected, 'test')
    invariant(store)


def test_restarts_preserve_business_data(store):
    before = store.snapshot()
    restarted = Store(store.path)
    assert restarted.snapshot() == before


def test_idempotency_and_payload_conflict(client):
    key = str(uuid4())
    first = client.post('/api/orders', json=sale(), headers={'Idempotency-Key': key})
    second = client.post('/api/orders', json=sale(), headers={'Idempotency-Key': key})
    assert first.status_code == 200
    assert second.json() == first.json()
    changed = client.post('/api/orders', json=sale(quantity=2), headers={'Idempotency-Key': key})
    assert changed.status_code == 409
    assert len(client.get('/api/workspace').json()['orders']) == 5


def test_auth_csrf_roles_validation_and_live_status(client):
    client.headers.pop('X-CSRF-Token')
    assert post(client, '/api/orders', sale()).status_code == 403
    login = client.post('/api/login', json={'username': 'cashier', 'password': 'cashier-test-password'})
    client.headers['X-CSRF-Token'] = login.json()['csrf']
    assert post(client, '/api/orders', sale()).status_code == 200
    assert post(client, '/api/close', {'counted': 0}).status_code == 403
    assert post(client, '/api/purchases', {'vendor_id': 'roaster', 'ingredient_id': 'beans', 'quantity': 2}).status_code == 403
    assert client.get('/api/dynamics/customers').status_code == 403
    assert post(client, '/api/orders', sale(quantity=1.5)).status_code == 422
    assert post(client, '/api/orders', sale(quantity=-1)).status_code == 422
    assert post(client, '/api/orders', {**sale(), 'total': 1}).status_code == 422
    assert client.get('/api/workspace').json()['connection']['configured'] is False
    client.cookies.clear()
    assert client.get('/api/workspace').status_code == 401
    assert client.get('/api/health').status_code == 200


def test_customer_care_and_report_export(client):
    customer = post(client, '/api/customers', {'name': 'Test Regular', 'email': 'regular@example.test'}).json()
    case = post(client, '/api/cases', {'customer_id': customer['id'], 'subject': 'Missing oat milk', 'priority': 'high'}).json()
    result = post(client, f"/api/cases/{case['id']}/resolve", {'resolution': 'Replaced the drink.'})
    assert result.json()['status'] == 'resolved'
    assert post(client, f"/api/cases/{case['id']}/resolve", {'resolution': 'Repeated action'}).status_code == 409
    response = client.get('/api/reports/trial-balance.csv')
    assert response.status_code == 200
    assert 'Account,Name,Debit CAD' in response.text
    assert 'attachment' in response.headers['content-disposition']


def test_connected_draft_reconciles_repeat_and_hides_credentials(client, monkeypatch):
    bc = client.app.state.bc
    calls = []
    async def draft(customer_id, item_id, quantity, reference):
        calls.append(reference)
        return {'id': str(uuid4()), 'number': 'SO-001'}
    monkeypatch.setattr(bc, 'draft_order', draft)
    body = {'customer_id': str(uuid4()), 'item_id': str(uuid4()), 'quantity': 2}
    key = str(uuid4())
    first = client.post('/api/dynamics/draft-order', json=body, headers={'Idempotency-Key': key})
    second = client.post('/api/dynamics/draft-order', json=body, headers={'Idempotency-Key': key})
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    assert len(calls) == 1
    assert 'secret' not in json.dumps(client.get('/api/workspace').json()['connection'])


def test_microsoft_api_contract_uses_server_token_and_deep_insert(monkeypatch):
    import asyncio
    import httpx
    from app.business_central import BusinessCentral
    tenant, company, appid = [str(uuid4()) for _ in range(3)]
    monkeypatch.setenv('BC_TENANT_ID', tenant)
    monkeypatch.setenv('BC_COMPANY_ID', company)
    monkeypatch.setenv('BC_CLIENT_ID', appid)
    monkeypatch.setenv('BC_CLIENT_SECRET', 'private-test-secret')
    monkeypatch.setenv('BC_ALLOW_WRITES', 'true')
    calls = []
    def handle(request):
        calls.append(request)
        if 'login.microsoftonline.com' in request.url.host:
            assert b'client_credentials' in request.content
            assert b'private-test-secret' in request.content
            return httpx.Response(200, json={'access_token': 'server-only-token', 'expires_in': 3600})
        assert request.headers['Authorization'] == 'Bearer server-only-token'
        assert f'/{tenant}/Sandbox/api/v2.0/companies({company})/' in str(request.url)
        if request.method == 'GET':
            return httpx.Response(200, json={'value': []})
        payload = json.loads(request.content)
        assert payload['salesOrderLines'][0]['lineType'] == 'Item'
        assert payload['salesOrderLines'][0]['quantity'] == 2
        assert len(payload['externalDocumentNumber']) == 32
        return httpx.Response(201, json={'id': str(uuid4()), 'number': 'SO-TEST'})
    original_client = httpx.AsyncClient
    monkeypatch.setattr(httpx, 'AsyncClient', lambda **kwargs: original_client(transport=httpx.MockTransport(handle), **kwargs))
    bc = BusinessCentral()
    async def exercise():
        await bc.list('customers')
        result = await bc.draft_order(str(uuid4()), str(uuid4()), 2, uuid4().hex)
        assert result['number'] == 'SO-TEST'
    asyncio.run(exercise())
    assert sum('login.microsoftonline.com' in request.url.host for request in calls) == 1
    assert [request.method for request in calls] == ['POST', 'GET', 'GET', 'POST']
