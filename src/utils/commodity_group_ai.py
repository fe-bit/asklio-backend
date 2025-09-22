from src.db import get_all_commodity_groups
from src.models.dto import ProcurementRequestCreateDTO
from fastapi import HTTPException
from .llm import get_llm


async def find_best_commodity_group(request: ProcurementRequestCreateDTO):
    # Get all commodity groups from DB
    commodity_groups = get_all_commodity_groups()
    group_descriptions = [
        f"{cg.id}: {cg.category} - {cg.group}" for cg in commodity_groups
    ]
    group_text = "\n".join(group_descriptions)

    # Prepare prompt for LLM
    prompt = f"""
    Based on the following procurement request details, select the most appropriate commodity group from the list below.
    Return only the ID of the best matching commodity group.

    Procurement Request:
    Title: {request.title}
    Vendor Name: {request.vendor_name}
    Department: {request.department}
    Order Lines: {[ol.position_description for ol in request.order_lines]}

    Commodity Groups:
    {group_text}
    """

    llm = get_llm()
    response = llm.invoke(prompt)

    # Extract the ID from the response
    best_id = response.content.strip().split()[0]
    # Fallback: ensure the ID exists in DB
    for cg in commodity_groups:
        if cg.id == best_id:
            return cg
    raise HTTPException(status_code=400, detail="No matching commodity group found")
