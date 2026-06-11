import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

def get_groq_api_key():
    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key or api_key == "XXXXXXXX":
        raise ValueError("Environment variable GROQ_API_KEY is not set.")
    return api_key

def get_azure_openai_llm():
    api_key = get_groq_api_key()
    llm = ChatGroq(
        temperature=0.3,
        groq_api_key=api_key,
        model_name="llama-3.3-70b-versatile"
    )
    return llm

def get_azure_openai_embeddings():
    # Free local embeddings - no API key needed
    embedding_model = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    return embedding_model

