import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain.output_parsers import PydanticOutputParser
import os
from fastapi import UploadFile
from src.models.db import ProcurementRequest
from fastapi import HTTPException
from .llm import get_llm
from langchain.prompts import PromptTemplate


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
    format_instructions = parser.get_format_instructions()
    prompt_template = PromptTemplate(
        template="""
        Extract the procurement request information from the following text.
        
        {format_instructions}
        
        Text:
        ---
        {text}
        ---
        """,
        input_variables=["text"],
        partial_variables={"format_instructions": format_instructions},
    )
    prompt = prompt_template.format_prompt(text=text)
    llm = get_llm()
    response = llm.invoke(prompt.to_string())
    # Parse output to ProcurementRequest
    try:
        text = response.content.replace("```json", "").replace("```", "").strip()
        result = parser.parse(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")
    finally:
        os.remove(tmp_path)

    return result
