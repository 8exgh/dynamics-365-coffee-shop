import json
import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from uuid import uuid4
from zoneinfo import ZoneInfo


class RuleError(Exception):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def business_date():
    return datetime.now(ZoneInfo(os.getenv('COFFEE_TIMEZONE', 'America/Edmonton'))).date().isoformat()


def cents(value):
    return int(Decimal(str(value)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


SCHEMA = '''
CREATE TABLE IF NOT EXISTS customers(id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL, points INTEGER NOT NULL DEFAULT 0, visits INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS ingredients(id TEXT PRIMARY KEY, name TEXT NOT NULL, unit TEXT NOT NULL, stock INTEGER NOT NULL CHECK(stock >= 0), reorder INTEGER NOT NULL, cost INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS products(id TEXT PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL, price INTEGER NOT NULL CHECK(price >= 0), color TEXT NOT NULL, recipe TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS vendors(id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL, lead_days INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS orders(id TEXT PRIMARY KEY, number TEXT UNIQUE NOT NULL, customer_id TEXT REFERENCES customers(id), kind TEXT NOT NULL, status TEXT NOT NULL, lines TEXT NOT NULL, subtotal INTEGER NOT NULL, tax INTEGER NOT NULL, total INTEGER NOT NULL, payment TEXT, points INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL, refunded_at TEXT);
CREATE TABLE IF NOT EXISTS purchases(id TEXT PRIMARY KEY, number TEXT UNIQUE NOT NULL, vendor_id TEXT NOT NULL REFERENCES vendors(id), ingredient_id TEXT NOT NULL REFERENCES ingredients(id), quantity INTEGER NOT NULL CHECK(quantity > 0), total INTEGER NOT NULL CHECK(total > 0), status TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS cases(id TEXT PRIMARY KEY, customer_id TEXT REFERENCES customers(id), subject TEXT NOT NULL, priority TEXT NOT NULL, status TEXT NOT NULL, resolution TEXT, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS journals(id TEXT PRIMARY KEY, reference TEXT NOT NULL, description TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS ledger(id INTEGER PRIMARY KEY, journal_id TEXT NOT NULL REFERENCES journals(id), account TEXT NOT NULL, debit INTEGER NOT NULL DEFAULT 0 CHECK(debit >= 0), credit INTEGER NOT NULL DEFAULT 0 CHECK(credit >= 0));
CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY, actor TEXT NOT NULL, action TEXT NOT NULL, reference TEXT NOT NULL, detail TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS idempotency(key TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, result TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS closes(id TEXT PRIMARY KEY, business_date TEXT NOT NULL UNIQUE, expected INTEGER NOT NULL, counted INTEGER NOT NULL, variance INTEGER NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
'''

ACCOUNTS = {
    '1000': 'Cash on hand', '1010': 'Card clearing', '1100': 'Accounts receivable',
    '1200': 'Inventory', '2000': 'Accounts payable', '2100': 'Demo tax payable',
    '3000': 'Opening equity', '4000': 'Coffee shop sales', '5000': 'Cost of goods sold',
    '5100': 'Waste expense', '5200': 'Cash over / short',
}


class Store:
    def __init__(self, path):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript(SCHEMA)
            db.execute('PRAGMA journal_mode=WAL')
        with self.transaction() as db:
            if not db.execute("SELECT 1 FROM metadata WHERE key='seeded'").fetchone():
                self.seed(db)

    def connect(self):
        db = sqlite3.connect(self.path, timeout=20)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        return db

    @contextmanager
    def transaction(self):
        db = self.connect()
        try:
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def seed(self, db):
        db.executemany('INSERT INTO customers VALUES (?,?,?,?,?)', [
            ('walk-in', 'Counter guest', '', 0, 0),
            ('maya', 'Maya Chen', 'maya@example.test', 86, 12),
            ('oliver', 'Oliver Brooks', 'oliver@example.test', 42, 7),
            ('studio', 'North Studio', 'hello@north.example.test', 120, 4),
            ('ava', 'Ava Thompson', 'ava@example.test', 210, 28),
        ])
        db.executemany('INSERT INTO ingredients VALUES (?,?,?,?,?,?)', [
            ('beans', 'House espresso beans', 'g', 6400, 2500, 3),
            ('milk', 'Whole milk', 'ml', 12000, 4000, 1),
            ('oat', 'Oat milk', 'ml', 1800, 2500, 1),
            ('chocolate', 'Dark chocolate', 'g', 1500, 500, 2),
            ('cups', 'Takeaway cups', 'each', 240, 100, 18),
            ('croissant', 'Butter croissants', 'each', 16, 20, 175),
            ('cookie', 'Chocolate cookies', 'each', 36, 15, 110),
            ('retail', 'House blend · 250 g bags', 'each', 24, 10, 750),
        ])
        products = [
            ('espresso', 'Espresso', 'Coffee', 350, 'espresso', {'beans': 18, 'cups': 1}),
            ('flat-white', 'Flat white', 'Coffee', 525, 'flat', {'beans': 18, 'milk': 180, 'cups': 1}),
            ('latte', 'Oat latte', 'Coffee', 625, 'latte', {'beans': 18, 'oat': 220, 'cups': 1}),
            ('mocha', 'Dark mocha', 'Coffee', 650, 'mocha', {'beans': 18, 'milk': 200, 'chocolate': 25, 'cups': 1}),
            ('americano', 'Americano', 'Coffee', 400, 'americano', {'beans': 18, 'cups': 1}),
            ('croissant', 'Butter croissant', 'Bakery', 450, 'pastry', {'croissant': 1}),
            ('cookie', 'Chocolate cookie', 'Bakery', 350, 'cookie', {'cookie': 1}),
            ('house-blend', 'House blend · 250 g', 'Retail', 1800, 'bag', {'retail': 1}),
        ]
        db.executemany('INSERT INTO products VALUES (?,?,?,?,?,?)', [(a,b,c,d,e,json.dumps(f)) for a,b,c,d,e,f in products])
        db.executemany('INSERT INTO vendors VALUES (?,?,?,?)', [
            ('roaster', 'Prairie Roasting Co.', 'orders@prairie.example.test', 3),
            ('dairy', 'Meadow Dairy & Oats', 'orders@meadow.example.test', 1),
            ('bakery', 'Earlybird Bakehouse', 'orders@earlybird.example.test', 1),
        ])
        stock_value = sum(r['stock'] * r['cost'] for r in db.execute('SELECT * FROM ingredients'))
        self.journal(db, 'OPENING', 'Opening inventory and cash float', [('1200', stock_value, 0), ('1000', 20000, 0), ('3000', 0, stock_value + 20000)])
        for customer, lines, payment in [
            ('maya', [{'product_id': 'flat-white', 'quantity': 2}, {'product_id': 'croissant', 'quantity': 1}], 'card'),
            ('oliver', [{'product_id': 'latte', 'quantity': 1}], 'cash'),
            ('ava', [{'product_id': 'house-blend', 'quantity': 1}, {'product_id': 'espresso', 'quantity': 1}], 'card'),
        ]:
            self.create_order(db, {'customer_id': customer, 'lines': lines, 'payment': payment, 'kind': 'counter'}, 'seed')
        self.create_order(db, {'customer_id': 'studio', 'kind': 'quote', 'lines': [{'product_id': 'flat-white', 'quantity': 12}, {'product_id': 'croissant', 'quantity': 12}]}, 'seed')
        db.execute('INSERT INTO cases VALUES (?,?,?,?,?,?,?)', (str(uuid4()), 'maya', 'Oat milk preference on recurring order', 'normal', 'open', None, now()))
        db.execute("INSERT INTO metadata VALUES ('seeded', '1')")

    def journal(self, db, reference, description, lines):
        lines = [line for line in lines if line[1] or line[2]]
        if sum(x[1] for x in lines) != sum(x[2] for x in lines):
            raise RuleError('Journal must balance.')
        jid = str(uuid4())
        db.execute('INSERT INTO journals VALUES (?,?,?,?)', (jid, reference, description, now()))
        db.executemany('INSERT INTO ledger(journal_id,account,debit,credit) VALUES (?,?,?,?)', [(jid, *line) for line in lines])
        return jid

    def log(self, db, actor, action, reference, detail=''):
        db.execute('INSERT INTO audit(actor,action,reference,detail,created_at) VALUES (?,?,?,?,?)', (actor, action, reference, detail, now()))

    def get(self, db, table, key):
        if table not in {'customers', 'products', 'ingredients', 'orders', 'purchases', 'cases', 'vendors'}:
            raise RuleError('Unknown record type.')
        row = db.execute(f'SELECT * FROM {table} WHERE id=?', (key,)).fetchone()
        if not row:
            raise RuleError('Record not found.')
        return dict(row)

    def next_number(self, db, table, prefix):
        if table not in {'orders', 'purchases'}:
            raise RuleError('Unknown document type.')
        return f'{prefix}-{1001 + db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]}'

    def prepare_lines(self, db, lines):
        if not lines or len(lines) > 100:
            raise RuleError('Choose between 1 and 100 order lines.')
        result = []
        for line in lines:
            quantity = line['quantity']
            if type(quantity) is not int or not 1 <= quantity <= 500:
                raise RuleError('Quantity must be a whole number from 1 to 500.')
            product = self.get(db, 'products', line['product_id'])
            recipe = json.loads(product['recipe'])
            cost = sum(self.get(db, 'ingredients', key)['cost'] * value for key, value in recipe.items())
            result.append({'product_id': product['id'], 'name': product['name'], 'quantity': quantity, 'price': product['price'], 'cost': cost, 'recipe': recipe})
        return result

    def inventory(self, db, lines, direction):
        needs = {}
        for line in lines:
            for ingredient, amount in line['recipe'].items():
                needs[ingredient] = needs.get(ingredient, 0) + amount * line['quantity']
        for key, amount in needs.items():
            ingredient = self.get(db, 'ingredients', key)
            if direction < 0 and ingredient['stock'] < amount:
                raise RuleError(f"Not enough {ingredient['name']}: need {amount} {ingredient['unit']}, have {ingredient['stock']}.")
            db.execute('UPDATE ingredients SET stock=stock+? WHERE id=?', (amount * direction, key))

    def ensure_open_day(self, db):
        if db.execute('SELECT 1 FROM closes WHERE business_date=?', (business_date(),)).fetchone():
            raise RuleError('Today is closed. Counter sales and cash movements resume tomorrow.')

    def create_order(self, db, payload, actor):
        kind = payload.get('kind', 'counter')
        if kind not in {'counter', 'quote'}:
            raise RuleError('Choose counter sale or catering quote.')
        customer = self.get(db, 'customers', payload.get('customer_id', 'walk-in'))
        lines = self.prepare_lines(db, payload['lines'])
        subtotal = sum(line['price'] * line['quantity'] for line in lines)
        tax = cents(Decimal(subtotal) * Decimal('0.05'))
        total = subtotal + tax
        oid = str(uuid4())
        number = self.next_number(db, 'orders', 'CS' if kind == 'counter' else 'QT')
        payment = payload.get('payment', 'card') if kind == 'counter' else None
        points = subtotal // 100 if customer['id'] != 'walk-in' and kind == 'counter' else 0
        if kind == 'counter':
            self.ensure_open_day(db)
            if payment not in {'cash', 'card'}:
                raise RuleError('Choose cash or card.')
            self.inventory(db, lines, -1)
            cost = sum(line['cost'] * line['quantity'] for line in lines)
            self.journal(db, number, 'Counter sale', [('1000' if payment == 'cash' else '1010', total, 0), ('4000', 0, subtotal), ('2100', 0, tax), ('5000', cost, 0), ('1200', 0, cost)])
            db.execute('UPDATE customers SET points=points+?, visits=visits+1 WHERE id=?', (points, customer['id']))
        db.execute('INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', (oid, number, customer['id'], kind, 'paid' if kind == 'counter' else 'draft', json.dumps(lines), subtotal, tax, total, payment, points, now(), None))
        self.log(db, actor, 'Sale completed' if kind == 'counter' else 'Quote created', number)
        return self.get(db, 'orders', oid)

    def order_action(self, db, oid, action, payload, actor):
        order = self.get(db, 'orders', oid)
        lines = json.loads(order['lines'])
        cost = sum(line['cost'] * line['quantity'] for line in lines)
        if action == 'accept' and order['kind'] == 'quote' and order['status'] == 'draft':
            db.execute("UPDATE orders SET status='accepted' WHERE id=?", (oid,))
        elif action == 'invoice' and order['kind'] == 'quote' and order['status'] == 'accepted':
            self.inventory(db, lines, -1)
            self.journal(db, order['number'], 'Catering invoice', [('1100', order['total'], 0), ('4000', 0, order['subtotal']), ('2100', 0, order['tax']), ('5000', cost, 0), ('1200', 0, cost)])
            db.execute("UPDATE orders SET status='invoiced' WHERE id=?", (oid,))
        elif action == 'collect' and order['status'] == 'invoiced':
            self.journal(db, order['number'], 'Customer payment', [('1010', order['total'], 0), ('1100', 0, order['total'])])
            points = order['subtotal'] // 100 if order['customer_id'] != 'walk-in' else 0
            db.execute("UPDATE orders SET status='paid',payment='card',points=? WHERE id=?", (points, oid))
            db.execute('UPDATE customers SET points=points+?,visits=visits+1 WHERE id=?', (points, order['customer_id']))
        elif action == 'refund' and order['status'] == 'paid':
            self.ensure_open_day(db)
            if payload.get('restock', False):
                if any(line['product_id'] != 'house-blend' for line in lines):
                    raise RuleError('Only unopened retail bags can be returned to inventory. Prepared food and drinks cannot be restocked.')
                self.inventory(db, lines, 1)
            refund_lines = [('4000', order['subtotal'], 0), ('2100', order['tax'], 0), ('1000' if order['payment'] == 'cash' else '1010', 0, order['total'])]
            if payload.get('restock', False):
                refund_lines.extend([('1200', cost, 0), ('5000', 0, cost)])
            self.journal(db, order['number'], 'Full refund' + (' with retail return' if payload.get('restock') else ''), refund_lines)
            db.execute("UPDATE orders SET status='refunded',refunded_at=? WHERE id=?", (now(), oid))
            db.execute('UPDATE customers SET points=MAX(0,points-?), visits=MAX(0,visits-1) WHERE id=?', (order['points'], order['customer_id']))
        else:
            raise RuleError(f"Cannot {action} an order in {order['status']} status.")
        self.log(db, actor, f'Order {action}', order['number'])
        return self.get(db, 'orders', oid)

    def purchase(self, db, payload, actor):
        self.get(db, 'vendors', payload['vendor_id'])
        ingredient = self.get(db, 'ingredients', payload['ingredient_id'])
        quantity = payload['quantity']
        if type(quantity) is not int or not 1 <= quantity <= 100000:
            raise RuleError('Quantity must be a whole number from 1 to 100,000.')
        total = quantity * ingredient['cost']
        pid = str(uuid4())
        number = self.next_number(db, 'purchases', 'PO')
        db.execute('INSERT INTO purchases VALUES (?,?,?,?,?,?,?,?)', (pid, number, payload['vendor_id'], ingredient['id'], quantity, total, 'pending' if total >= 50000 else 'approved', now()))
        self.log(db, actor, 'Purchase requested', number)
        return self.get(db, 'purchases', pid)

    def purchase_action(self, db, pid, action, actor):
        po = self.get(db, 'purchases', pid)
        if action == 'approve' and po['status'] == 'pending':
            status = 'approved'
        elif action == 'receive' and po['status'] == 'approved':
            db.execute('UPDATE ingredients SET stock=stock+? WHERE id=?', (po['quantity'], po['ingredient_id']))
            self.journal(db, po['number'], 'Purchase receipt and invoice', [('1200', po['total'], 0), ('2000', 0, po['total'])])
            status = 'received'
        elif action == 'pay' and po['status'] == 'received':
            self.journal(db, po['number'], 'Vendor payment from card clearing', [('2000', po['total'], 0), ('1010', 0, po['total'])])
            status = 'paid'
        else:
            raise RuleError(f"Cannot {action} a purchase in {po['status']} status.")
        db.execute('UPDATE purchases SET status=? WHERE id=?', (status, pid))
        self.log(db, actor, f'Purchase {action}', po['number'])
        return self.get(db, 'purchases', pid)

    def waste(self, db, payload, actor):
        ingredient = self.get(db, 'ingredients', payload['ingredient_id'])
        quantity = payload['quantity']
        if type(quantity) is not int or quantity <= 0 or quantity > ingredient['stock']:
            raise RuleError('Waste must be a positive quantity within available stock.')
        value = quantity * ingredient['cost']
        db.execute('UPDATE ingredients SET stock=stock-? WHERE id=?', (quantity, ingredient['id']))
        self.journal(db, ingredient['id'], 'Waste: ' + payload['reason'], [('5100', value, 0), ('1200', 0, value)])
        self.log(db, actor, 'Waste recorded', ingredient['name'], f"{quantity} {ingredient['unit']}: {payload['reason']}")
        return {'quantity': quantity, 'value': value}

    def close_day(self, db, counted, actor):
        self.ensure_open_day(db)
        expected = db.execute("SELECT COALESCE(SUM(debit-credit),0) FROM ledger WHERE account='1000'").fetchone()[0]
        variance = counted - expected
        cid = str(uuid4())
        db.execute('INSERT INTO closes VALUES (?,?,?,?,?,?)', (cid, business_date(), expected, counted, variance, now()))
        if variance:
            self.journal(db, cid, 'Cash count adjustment', [('1000', max(variance, 0), max(-variance, 0)), ('5200', max(-variance, 0), max(variance, 0))])
        self.log(db, actor, 'Day closed', business_date(), f'Variance: {variance} cents')
        return {'id': cid, 'expected': expected, 'counted': counted, 'variance': variance}

    def snapshot(self):
        with self.connect() as db:
            db.execute('BEGIN')
            data = {name: [dict(row) for row in db.execute(f'SELECT * FROM {name}')] for name in ['products', 'customers', 'ingredients', 'vendors', 'orders', 'purchases', 'cases', 'closes']}
            for order in data['orders']:
                order['lines'] = json.loads(order['lines'])
            for product in data['products']:
                product['recipe'] = json.loads(product['recipe'])
            data['audit'] = [dict(r) for r in db.execute('SELECT * FROM audit ORDER BY id DESC LIMIT 40')]
            balances = {r['account']: dict(r) for r in db.execute('SELECT account, SUM(debit) debit, SUM(credit) credit, SUM(debit-credit) balance FROM ledger GROUP BY account')}
            data['accounts'] = [{'account': code, 'name': name, **balances.get(code, {'debit': 0, 'credit': 0, 'balance': 0})} for code, name in ACCOUNTS.items()]
            revenue = -balances.get('4000', {}).get('balance', 0)
            cogs = balances.get('5000', {}).get('balance', 0)
            data['metrics'] = {'revenue': revenue, 'gross_profit': revenue-cogs, 'cash': balances.get('1000', {}).get('balance', 0), 'receivable': balances.get('1100', {}).get('balance', 0), 'payable': -balances.get('2000', {}).get('balance', 0), 'inventory_value': balances.get('1200', {}).get('balance', 0), 'journal_balance': sum(r['balance'] for r in balances.values()), 'orders': sum(o['status'] == 'paid' for o in data['orders']), 'low_stock': sum(i['stock'] <= i['reorder'] for i in data['ingredients']), 'closed': any(c['business_date'] == business_date() for c in data['closes'])}
            data['journals'] = [dict(r) for r in db.execute('SELECT j.*, SUM(l.debit) amount FROM journals j JOIN ledger l ON l.journal_id=j.id GROUP BY j.id ORDER BY j.created_at DESC LIMIT 30')]
            return data
