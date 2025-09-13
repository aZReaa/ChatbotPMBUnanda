from pathlib import Path
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from .deps import get_llm, get_embeddings
from .rag import build_vectorstore
from .guards import validate_message

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


@app.post('/chat')
def chat(inp: ChatInput):
    validate_message(inp.message)
    docs = vectorstore.similarity_search(inp.message, k=4)
    context = "\n".join(d.page_content for d in docs)
    system_prompt = (BASE_DIR / 'prompts' / 'system.md').read_text(encoding='utf-8')
    answer_prompt = (BASE_DIR / 'prompts' / 'answer_faq.md').read_text(encoding='utf-8')
    prompt = f"{system_prompt}\n{answer_prompt}\nKonteks:\n{context}\nPertanyaan: {inp.message}"
    response = llm.invoke(prompt)
    return {"answer": response, "source": 'pmb_unanda.json'}
