import sqlite3
import json
from .models import ProcurementRequest, OrderLine


# Database setup

conn = sqlite3.connect('procurement.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS procurement_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requestor_name TEXT,
    title TEXT,
    vendor_name TEXT,
    vat_id TEXT,
    commodity_group TEXT,
    total_cost REAL,
    department TEXT,
    status TEXT,
    order_lines TEXT
)''')

# Commodity groups table
c.execute('''CREATE TABLE IF NOT EXISTS commodity_groups (
    id TEXT PRIMARY KEY,
    category TEXT,
    group_name TEXT
)''')
conn.commit()



def get_db_connection():
    return conn

def serialize_order_lines(order_lines):
    return json.dumps([ol.dict() for ol in order_lines])
def deserialize_order_lines(order_lines_str):
    return [OrderLine(**ol) for ol in json.loads(order_lines_str)]

# Commodity group CRUD
def add_commodity_group(id: str, category: str, group: str):
    c.execute('''INSERT OR IGNORE INTO commodity_groups (id, category, group_name) VALUES (?, ?, ?)''', (id, category, group))
    conn.commit()

def get_commodity_group(id: str):
    c.execute('SELECT id, category, group_name FROM commodity_groups WHERE id=?', (id,))
    row = c.fetchone()
    if row:
        from .models import CommodityGroup
        return CommodityGroup(id=row[0], category=row[1], group=row[2])
    return None

def get_all_commodity_groups():
    c.execute('SELECT id, category, group_name FROM commodity_groups')
    rows = c.fetchall()
    from .models import CommodityGroup
    return [CommodityGroup(id=row[0], category=row[1], group=row[2]) for row in rows]
