import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain.output_parsers import PydanticOutputParser, RetryOutputParser
import os
from fastapi import UploadFile, HTTPException
from src.models.dto import ProcurementRequestCreateDTO
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
    parser = PydanticOutputParser(pydantic_object=ProcurementRequestCreateDTO)
    prompt_template = """
        Extract the procurement request information from the following text.
        
        {format_instructions}
        
        Text:
        ---
        {pdf_text}
        ---
        """
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["pdf_text"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    llm = get_llm()
    retry_parser = RetryOutputParser.from_llm(
        parser=parser,
        llm=llm,
        max_retries=3,
    )

    prompt_value = prompt.format_prompt(pdf_text=text)
    try:
        llm_output = await llm.ainvoke(prompt_value)
        return await retry_parser.aparse_with_prompt(llm_output.content, prompt_value)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        os.remove(tmp_path)
