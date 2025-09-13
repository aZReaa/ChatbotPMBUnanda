import os
from pathlib import Path
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from .deps import get_llm, get_embeddings
from .rag import build_vectorstore, search_docs
from .guards import validate_message, is_out_of_scope, validate_citations

BASE_DIR = Path(__file__).resolve().parents[1]

llm = get_llm()
vectorstore = build_vectorstore(get_embeddings())

app = FastAPI()


@app.get('/health')
def health():
    return {"status": "ok"}


@app.get('/')
def root() -> HTMLResponse:
    html = (BASE_DIR / 'public' / 'index.html').read_text(encoding='utf-8')
    return HTMLResponse(html)


@app.get('/faq')
def faq():
    data = json.loads((BASE_DIR / 'data' / 'pmb' / 'pmb_unanda.json').read_text(encoding='utf-8'))
    return JSONResponse(content=data)


@app.get('/search')
def search(q: str, k: int = 4):
    docs = vectorstore.similarity_search(q, k=k)
    return {
        "results": [
            {"content": d.page_content, "source": d.metadata.get('source')}
            for d in docs
        ]
    }


class ChatInput(BaseModel):
    message: str
    top_k: int = 5


@app.post('/chat')
def chat(inp: ChatInput):
    msg = validate_message(inp.message)
    if is_out_of_scope(msg):
        return {
            "status": "out_of_scope",
            "answer": "Pertanyaan di luar cakupan PMB Unanda. Silakan hubungi panitia PMB di 082159054365 atau email pmb@unanda.ac.id.",
            "citations": [],
        }

    docs = search_docs(vectorstore, msg, k=inp.top_k, min_score=0.35)
    if not docs:
        return {
            "status": "not_found",
            "answer": "Maaf, belum ada data yang mendukung pertanyaan tersebut di basis data PMB kami.",
            "citations": [],
        }

    if os.getenv("TESTING"):
        answer = {
            "status": "ok",
            "answer": "dummy",
            "citations": [{"doc_id": docs[0]["doc_id"], "spans": []}],
        }
    else:
        system_prompt = (BASE_DIR / 'prompts' / 'system.md').read_text(encoding='utf-8')
        context = "\n".join(f"{d['doc_id']}: {d['text']}" for d in docs)
        schema = '{"status": "ok | not_found | out_of_scope", "answer": "string", "citations": [{"doc_id": "string", "spans": ["string"]}]}'
        prompt = f"{system_prompt}\nSkema JSON jawaban: {schema}\n\n[Context]\n{context}\n\n[User Question]\n{msg}"
        raw = llm.invoke(prompt, temperature=0.2, top_p=0.1, response_format={"type": "json_object"})
        answer = json.loads(raw)

    if not validate_citations(answer, docs) or answer.get("status") != "ok":
        return {
            "status": "not_found",
            "answer": "Maaf, belum ada data yang mendukung pertanyaan tersebut di basis data PMB kami.",
            "citations": [],
        }

    return answer
