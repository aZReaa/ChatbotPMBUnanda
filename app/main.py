from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---- Konfigurasi ----
ALLOWED_TOPICS = ["jalur","biaya","periode","syarat","prodi","kontak","dokumen"]
MIN_SCORE = 0.40  # naikkan bila masih "ngarang"
TOP_K = 5

app = FastAPI(title="Chatbot PMB Unanda")

class Citation(BaseModel):
    doc_id: str

class ChatReq(BaseModel):
    message: str
    top_k: int | None = None

class ChatResp(BaseModel):
    status: str
    answer: str
    citations: List[Citation]

# ---- Load data PMB ----
def load_kb() -> list[dict]:
    # dukung path lama (root) & yang disarankan (data/pmb/)
    candidates = [
        Path("data/pmb/pmb_unanda.json"),
        Path("pmb_unanda.json"),
    ]
    for p in candidates:
        if p.exists():
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "items" in data:
                return data["items"]
            return data if isinstance(data, list) else []
    return []

KB = load_kb()

# ---- Util sederhana: OOS & fuzzy skor ringan ----
def is_out_of_scope(q: str) -> bool:
    ql = q.lower()
    return not any(t in ql for t in ALLOWED_TOPICS)

def score_item(q: str, it: dict) -> float:
    blob = json.dumps(it, ensure_ascii=False).lower()
    toks = [t for t in q.lower().split() if len(t) >= 3]
    hits = sum(1 for t in toks if t in blob)
    return hits / max(1, len(toks))

def retrieve(q: str, k: int) -> List[Dict[str, Any]]:
    scored = [{
        "id": it.get("id") or it.get("title") or f"doc_{i}",
        "text": it,
        "score": score_item(q, it)
    } for i, it in enumerate(KB)]
    scored = [s for s in scored if s["score"] >= MIN_SCORE]
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:k]

@app.get("/health")
def health():
    return {"ok": True, "items": len(KB)}

@app.post("/chat", response_model=ChatResp)
def chat(req: ChatReq):
    top_k = req.top_k or TOP_K

    if is_out_of_scope(req.message):
        return ChatResp(
            status="out_of_scope",
            answer="Pertanyaan di luar cakupan PMB Unanda. Silakan hubungi panitia PMB.",
            citations=[],
        )

    ctx = retrieve(req.message, k=top_k)
    if not ctx:
        return ChatResp(
            status="not_found",
            answer="Maaf, belum ada data yang mendukung pertanyaan tersebut di basis data PMB kami.",
            citations=[],
        )

    best = ctx[0]
    doc_id = str(best["id"])
    ringkas = best["text"]
    return ChatResp(
        status="ok",
        answer=f"Berikut info terkait: {ringkas}",
        citations=[Citation(doc_id=doc_id)],
    )
