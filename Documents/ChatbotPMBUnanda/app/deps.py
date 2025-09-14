import os
from dotenv import load_dotenv

load_dotenv()


class DummyLLM:
    def invoke(self, prompt: str) -> str:
        return "LLM tidak tersedia"


class DummyEmbeddings:
    def embed_documents(self, texts):
        return [[0.0] * 384 for _ in texts]

    def embed_query(self, text):
        return [0.0] * 384


def get_llm():
    if os.getenv("TESTING"):
        return DummyLLM()
    if os.getenv("USE_OLLAMA") == "1":
        from langchain_community.llms import Ollama
        model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        return Ollama(model=model)
    from langchain_openai import ChatOpenAI
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    api_key = os.getenv("OPENAI_API_KEY")
    return ChatOpenAI(model=model, api_key=api_key)


def get_embeddings():
    if os.getenv("TESTING"):
        return DummyEmbeddings()
    from langchain_community.embeddings import HuggingFaceEmbeddings
    model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    return HuggingFaceEmbeddings(model_name=model_name)
