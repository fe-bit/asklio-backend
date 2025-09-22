import os
from fastapi import HTTPException
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm():
    return get_gemini_llm()

def get_chatgpt_llm():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not set")
    return ChatOpenAI(openai_api_key=openai_api_key, temperature=0)

def get_gemini_llm():
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise HTTPException(status_code=500, detail="Google API key not set")
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=google_api_key,  # <-- Pass the key here!
        temperature=0
    )
