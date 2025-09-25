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
    You are an expert procurement analyst. Your task is to select the **single most appropriate commodity group** for a given procurement request.  

Before making your selection, carefully consider:
1. The title, vendor, department, and all order line descriptions.
2. How each commodity group aligns with the procurement details.
3. Potential ambiguities and why one group is a better match than the others.

After reasoning, provide only the **ID of the best matching commodity group**.  

Procurement Request:
Title: {request.title}
Vendor Name: {request.vendor_name}
Department: {request.department}
Order Lines: {[ol.position_description for ol in request.order_lines]}

Commodity Groups:
{group_text}

Step-by-step reasoning (brief, 2-3 sentences), then return only the ID:

ID:
    """
    llm = get_llm()
    response = llm.invoke(prompt)
    prompt = f"""Given the following response, please extract the commodity group ID mentioned. Do not include any other text.
    Response: {response.content}
    ID: 
    """
    id_response = await llm.ainvoke(prompt)
    # Extract the ID from the response
    best_id = id_response.content.strip().replace(":", "").split()[0]
    # Fallback: ensure the ID exists in DB
    for cg in commodity_groups:
        if cg.id == best_id:
            return cg
    raise HTTPException(status_code=400, detail="No matching commodity group found")
