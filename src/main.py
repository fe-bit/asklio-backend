
from typing import List
from fastapi import FastAPI, HTTPException
from .models import ProcurementRequest, OrderLine, Status
from .db import get_db_connection, serialize_order_lines, deserialize_order_lines
from .mock_data import add_mock_data
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File
from .utils.extract_pdf import extract_procurement_request_from_pdf
from dotenv import load_dotenv
from .setup import setup

load_dotenv(override=True)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conn = get_db_connection()
c = conn.cursor()
setup()
add_mock_data()

@app.post("/requests", response_model=ProcurementRequest)
def create_request(req: ProcurementRequest):
    c.execute('''INSERT INTO procurement_requests (
        requestor_name, title, vendor_name, vat_id, commodity_group, total_cost, department, status, order_lines
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
        req.requestor_name, req.title, req.vendor_name, req.vat_id, req.commodity_group,
        req.total_cost, req.department, req.status, serialize_order_lines(req.order_lines)
    ))
    conn.commit()
    new_id = c.lastrowid
    return ProcurementRequest(id=new_id, **req.dict(exclude={'id'}))

@app.get("/requests", response_model=List[ProcurementRequest])
def list_requests():
    c.execute('SELECT * FROM procurement_requests')
    rows = c.fetchall()
    result = []
    for row in rows:
        result.append(ProcurementRequest(
            id=row[0],
            requestor_name=row[1], title=row[2], vendor_name=row[3], vat_id=row[4],
            commodity_group=row[5], total_cost=row[6], department=row[7], status=row[8],
            order_lines=deserialize_order_lines(row[9])
        ))
    return result

@app.get("/requests/{request_id}", response_model=ProcurementRequest)
def get_request(request_id: int):
    c.execute('SELECT * FROM procurement_requests WHERE id=?', (request_id,))
    row = c.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Request not found")
    return ProcurementRequest(
        id=row[0],
        requestor_name=row[1], title=row[2], vendor_name=row[3], vat_id=row[4],
        commodity_group=row[5], total_cost=row[6], department=row[7], status=row[8],
        order_lines=deserialize_order_lines(row[9])
    )

@app.put("/requests/{request_id}", response_model=ProcurementRequest)
def update_request(request_id: int, req: ProcurementRequest):
    c.execute('SELECT * FROM procurement_requests WHERE id=?', (request_id,))
    if not c.fetchone():
        raise HTTPException(status_code=404, detail="Request not found")
    c.execute('''UPDATE procurement_requests SET
        requestor_name=?, title=?, vendor_name=?, vat_id=?, commodity_group=?, total_cost=?, department=?, status=?, order_lines=?
        WHERE id=?''', (
        req.requestor_name, req.title, req.vendor_name, req.vat_id, req.commodity_group,
        req.total_cost, req.department, req.status, serialize_order_lines(req.order_lines), request_id
    ))
    conn.commit()
    return ProcurementRequest(id=request_id, **req.dict(exclude={'id'}))


@app.post("/extract-pdf", response_model=ProcurementRequest)
async def extract_pdf(file: UploadFile = File(...)):
    return extract_procurement_request_from_pdf(file)

@app.delete("/requests/{request_id}")
def delete_request(request_id: int):
    c.execute('SELECT * FROM procurement_requests WHERE id=?', (request_id,))
    if not c.fetchone():
        raise HTTPException(status_code=404, detail="Request not found")
    c.execute('DELETE FROM procurement_requests WHERE id=?', (request_id,))
    conn.commit()
    return {"detail": "Deleted"}
