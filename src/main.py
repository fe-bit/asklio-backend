from typing import List
from fastapi import FastAPI, HTTPException
from .models.db import ProcurementRequest
from .models.dto import ProcurementRequestCreateDTO, ProcurementRequestUpdateDTO
from .db import (
    get_db_connection,
    serialize_order_lines,
    deserialize_order_lines,
    get_commodity_group,
    get_procurement_request,
)
from .utils.commodity_group_ai import find_best_commodity_group
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
async def create_request(req: ProcurementRequestCreateDTO):
    # Use AI to find the right commodity group
    commodity_group = await find_best_commodity_group(req)
    proc_request = ProcurementRequest(
        **req.dict(), commodity_group=commodity_group, id=None
    )
    c.execute(
        """INSERT INTO procurement_requests (
        requestor_name, title, vendor_name, vat_id, commodity_group, total_cost, department, status, order_lines
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            proc_request.requestor_name,
            proc_request.title,
            proc_request.vendor_name,
            proc_request.vat_id,
            commodity_group.id,
            proc_request.total_cost,
            proc_request.department,
            proc_request.status,
            serialize_order_lines(proc_request.order_lines),
        ),
    )
    conn.commit()
    new_id = c.lastrowid
    return ProcurementRequest(
        id=new_id,
        **{
            **proc_request.dict(exclude={"id", "commodity_group"}),
            "commodity_group": commodity_group,
        },
    )


@app.get("/requests", response_model=List[ProcurementRequest])
async def list_requests():
    c.execute("SELECT * FROM procurement_requests")
    rows = c.fetchall()
    result = []
    for row in rows:
        cg = get_commodity_group(row[5])
        result.append(
            ProcurementRequest(
                id=row[0],
                requestor_name=row[1],
                title=row[2],
                vendor_name=row[3],
                vat_id=row[4],
                commodity_group=cg,
                total_cost=row[6],
                department=row[7],
                status=row[8],
                order_lines=deserialize_order_lines(row[9]),
            )
        )
    return result


@app.get("/requests/{request_id}", response_model=ProcurementRequest)
async def get_request(request_id: int):
    c.execute("SELECT * FROM procurement_requests WHERE id=?", (request_id,))
    row = c.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Request not found")
    cg = get_commodity_group(row[5])
    return ProcurementRequest(
        id=row[0],
        requestor_name=row[1],
        title=row[2],
        vendor_name=row[3],
        vat_id=row[4],
        commodity_group=cg,
        total_cost=row[6],
        department=row[7],
        status=row[8],
        order_lines=deserialize_order_lines(row[9]),
    )


@app.put("/requests/{request_id}", response_model=ProcurementRequest)
async def update_request(request_id: int, req: ProcurementRequestUpdateDTO):
    c.execute("SELECT * FROM procurement_requests WHERE id=?", (request_id,))
    if not c.fetchone():
        raise HTTPException(status_code=404, detail="Request not found")
    c.execute(
        """UPDATE procurement_requests SET
        requestor_name=?, title=?, vendor_name=?, vat_id=?, total_cost=?, department=?, status=?, order_lines=?
        WHERE id=?""",
        (
            req.requestor_name,
            req.title,
            req.vendor_name,
            req.vat_id,
            req.total_cost,
            req.department,
            req.status,
            serialize_order_lines(req.order_lines),
            request_id,
        ),
    )
    conn.commit()
    proc_req = get_procurement_request(request_id=req.id)
    if proc_req is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return proc_req


@app.post("/extract-pdf", response_model=ProcurementRequest)
async def extract_pdf(file: UploadFile = File(...)):
    return await extract_procurement_request_from_pdf(file)


@app.delete("/requests/{request_id}")
async def delete_request(request_id: int):
    c.execute("SELECT * FROM procurement_requests WHERE id=?", (request_id,))
    if not c.fetchone():
        raise HTTPException(status_code=404, detail="Request not found")
    c.execute("DELETE FROM procurement_requests WHERE id=?", (request_id,))
    conn.commit()
    return {"detail": "Deleted"}
