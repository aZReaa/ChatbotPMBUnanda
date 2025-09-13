from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
import requests
import os
import json
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document

USE_OLLAMA = os.getenv("USE_OLLAMA", "0") == "1"
if USE_OLLAMA:
    from langchain_community.llms import Ollama
    llm = Ollama(model="llama3.1:8b")
else:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o-mini")

app = FastAPI()

# Load PMB dataset for RAG
DATA_FILE = Path(__file__).parent / "pmb_unanda.json"
with open(DATA_FILE, "r", encoding="utf-8") as f:
    DATASET = json.load(f)

split = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)
docs: List[Document] = []

def add_docs(item, tag):
    text = json.dumps(item, ensure_ascii=False)
    for ch in split.split_text(text):
        docs.append(Document(page_content=ch, metadata={"tag": tag}))

add_docs(DATASET.get("university", {}), "university")
add_docs(DATASET.get("admission_tracks", []), "admission_tracks")
add_docs(DATASET.get("programs", []), "programs")
add_docs(DATASET.get("application_guide", {}), "application_guide")
add_docs(DATASET.get("tuition_and_fees", {}), "tuition")

emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vs = FAISS.from_documents(docs, emb)

class ChatIn(BaseModel):
    message: str


def route_intent(q: str) -> str:
    q = q.lower()
    if any(w in q for w in ["jadwal", "kelas", "dosen", "ruang"]):
        return "jadwal"
    if any(w in q for w in ["libur", "krs", "uts", "uas", "kalender"]):
        return "kalender"
    if any(w in q for w in ["kontak", "email", "telp", "unit"]):
        return "kontak"
    if any(w in q for w in ["pmb", "pendaftaran", "biaya", "syarat"]):
        return "pmb"
    return "faq"


def call_tool(intent: str, q: str) -> Optional[dict]:
    try:
        if intent == "jadwal":
            # TODO: parse entity from q -> params
            return requests.get(
                "http://localhost:8001/api/jadwal",
                params={"prodi": "TI", "kelas": "A", "hari": "Senin"},
                timeout=5,
            ).json()
        if intent == "kalender":
            return requests.get(
                "http://localhost:8001/api/kalender", timeout=5
            ).json()
        if intent == "kontak":
            return requests.get(
                "http://localhost:8001/api/kontak",
                params={"unit": "BAAK"},
                timeout=5,
            ).json()
    except Exception:
        return None
    return None


@app.post("/chat")
def chat(inp: ChatIn):
    intent = route_intent(inp.message)
    data = call_tool(intent, inp.message)
    if data and data.get("items"):
        context = str(data["items"])
        source = data.get("source", f"endpoint:{intent}")
    else:
        sims = vs.similarity_search(inp.message, k=4)
        context = "\n".join(d.page_content for d in sims)
        source = ", ".join(sorted(set(d.metadata.get("tag", "doc") for d in sims)))

    prompt = f"""
Peran: Asisten LLM terverifikasi. Konteks terpercaya: {context if context else '(kosong)'}
Pertanyaan: {inp.message}
Instruksi:
- Jawab singkat dalam bullet.
- Nyatakan tanggal/angka jelas.
- Baris terakhir: 'Sumber: {source}'
"""
    answer = llm.invoke(prompt)
    return {"intent": intent, "answer": answer, "source": source}


@app.get("/", response_class=HTMLResponse)
def home():
    html_path = Path(__file__).parent / "index.html"
    return html_path.read_text(encoding="utf-8")
