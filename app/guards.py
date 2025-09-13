from fastapi import HTTPException


def validate_message(msg: str) -> str:
    if not msg.strip():
        raise HTTPException(status_code=400, detail="empty message")
    if len(msg) > 1000:
        raise HTTPException(status_code=400, detail="message too long")
    return msg
