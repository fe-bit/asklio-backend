from pydantic import BaseModel, Field, validator, root_validator
from typing import List
from .db import Status


class OrderLine(BaseModel):
    position_description: str = Field(..., min_length=1)
    unit_price: float = Field(
        ..., gt=0, description="Unit price before tax for a single item or service."
    )
    amount: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1)
    total_price: float = Field(
        ...,
        gt=0,
    )


class ProcurementRequestCreateDTO(BaseModel):
    requestor_name: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    vendor_name: str = Field(..., min_length=1)
    vat_id: str = Field(..., min_length=1, description="Vendor VAT ID. In Germany this usually starts with 'DE'.")
    order_lines: List[OrderLine] = Field(
        ...,
        min_items=1,
        description="List of order lines. Do not include alternative offers here.",
    )
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
