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
conn.commit()


def get_db_connection():
    return conn

def serialize_order_lines(order_lines):
    return json.dumps([ol.dict() for ol in order_lines])
def deserialize_order_lines(order_lines_str):
    return [OrderLine(**ol) for ol in json.loads(order_lines_str)]
