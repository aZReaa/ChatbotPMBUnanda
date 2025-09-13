from pathlib import Path
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / 'data' / 'pmb' / 'pmb_unanda.json'


def load_documents() -> List[Document]:
    text = DATA_FILE.read_text(encoding="utf-8")
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=80)
    docs: List[Document] = []
    for i, chunk in enumerate(splitter.split_text(text)):
        docs.append(
            Document(
                page_content=chunk,
                metadata={"source": "pmb_unanda.json", "doc_id": f"pmb:{i}"},
            )
        )
    return docs


def build_vectorstore(embeddings):
    docs = load_documents()
    return FAISS.from_documents(docs, embeddings)


def search_docs(vs, query: str, k: int = 5, min_score: float = 0.35) -> List[Dict[str, Any]]:
    hits = vs.similarity_search_with_relevance_scores(query, k=k)
    results: List[Dict[str, Any]] = []
    for doc, score in hits:
        if score >= min_score:
            results.append({"doc_id": doc.metadata.get("doc_id"), "text": doc.page_content, "score": score})
    return results
