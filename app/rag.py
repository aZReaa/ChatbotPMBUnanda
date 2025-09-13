from pathlib import Path
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / 'data' / 'pmb' / 'pmb_unanda.json'


def load_documents() -> List[Document]:
    text = DATA_FILE.read_text(encoding='utf-8')
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=80)
    return [
        Document(page_content=chunk, metadata={"source": 'pmb_unanda.json'})
        for chunk in splitter.split_text(text)
    ]


def build_vectorstore(embeddings):
    docs = load_documents()
    return FAISS.from_documents(docs, embeddings)
