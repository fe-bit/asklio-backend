from pydantic import BaseModel, Field, validator
from typing import List
from .db import Status


class OrderLine(BaseModel):
    position_description: str = Field(..., min_length=1)
    unit_price: float = Field(..., gt=0)
    amount: int = Field(..., gt=0)
    unit: str = Field(..., min_length=1)
    total_price: float = Field(..., gt=0)

    @validator("total_price")
    def check_total_price(cls, v, values):
        if "unit_price" in values and "amount" in values:
            expected = values["unit_price"] * values["amount"]
            if abs(v - expected) > 0.01:
                raise ValueError("total_price must be unit_price * amount")
        return v


class ProcurementRequestCreateDTO(BaseModel):
    requestor_name: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    vendor_name: str = Field(..., min_length=1)
    vat_id: str = Field(..., min_length=1)
    order_lines: List[OrderLine]
    total_cost: float = Field(..., gt=0)
    department: str = Field(..., min_length=1)


class ProcurementRequestUpdateDTO(BaseModel):
    id: int
    requestor_name: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    vendor_name: str = Field(..., min_length=1)
    vat_id: str = Field(..., min_length=1)
    order_lines: List[OrderLine]
    total_cost: float = Field(..., gt=0)
    department: str = Field(..., min_length=1)
    status: Status = Status.open
