import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def get_config_value(name: str):
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st
        return st.secrets.get(name)
    except Exception:
        return None

TAVILY_API_KEY = get_config_value("TAVILY_API_KEY")
AVIATIONSTACK_API_KEY = get_config_value("AVIATIONSTACK_API_KEY")
OPENWEATHER_API_KEY = get_config_value("OPENWEATHER_API_KEY")
DATABASE_URL = get_config_value("DATABASE_URL")

def get_llm():
    return ChatGroq(
        model=get_config_value("GROQ_MODEL") or "openai/gpt-oss-20b",
        temperature=0,
        max_tokens=2000,
    )
