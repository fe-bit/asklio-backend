import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
import os
from fastapi import UploadFile
from src.models import ProcurementRequest
from fastapi import HTTPException


async def extract_procurement_request_from_pdf(file: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    # Load PDF text using LangChain
    loader = PyPDFLoader(tmp_path)
    pages = loader.load()
    text = "\n".join([page.page_content for page in pages])

    # Define output parser for ProcurementRequest
    parser = PydanticOutputParser(pydantic_object=ProcurementRequest)

    # Prompt for extraction
    prompt = f"""
    Extract the procurement request information from the following text. Return only valid JSON for the ProcurementRequest model:
    ---
    {text}
    ---
    """

    # Use OpenAI LLM via LangChain
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not set")
    llm = ChatOpenAI(openai_api_key=openai_api_key, temperature=0)
    response = llm.invoke(prompt)

    # Parse output to ProcurementRequest
    try:
        result = parser.parse(response.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")
    finally:
        os.remove(tmp_path)

    return result
