from fastapi import HTTPException
from typing import List, Dict, Any

ALLOWED_TOPICS = [
    "jalur",
    "biaya",
    "periode",
    "syarat",
    "prodi",
    "kontak",
    "dokumen",
]


def validate_message(msg: str) -> str:
    if not msg.strip():
        raise HTTPException(status_code=400, detail="empty message")
    if len(msg) > 1000:
        raise HTTPException(status_code=400, detail="message too long")
    return msg


def is_out_of_scope(q: str) -> bool:
    ql = q.lower()
    return not any(t in ql for t in ALLOWED_TOPICS)


def validate_citations(answer: Dict[str, Any], ctx: List[Dict[str, Any]]) -> bool:
    ctx_ids = {c["doc_id"] for c in ctx}
    citations = answer.get("citations")
    if not citations:
        return False
    return all(c.get("doc_id") in ctx_ids for c in citations)
