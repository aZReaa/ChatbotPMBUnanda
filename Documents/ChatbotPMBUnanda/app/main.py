from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any
from dotenv import load_dotenv
from app.rag import get_rag_chain

# Load environment variables
load_dotenv()

app = FastAPI(title="Chatbot PMB Unanda")

class ChatReq(BaseModel):
    message: str

class Citation(BaseModel):
    doc_id: str
    text: str
    score: float

class ChatResp(BaseModel):
    status: str
    answer: str
    citations: List[Citation]

# Dependency to get the RAG chain
async def get_chain():
    if not hasattr(app.state, "chain"):
        app.state.chain = await get_rag_chain()
    return app.state.chain

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/chat", response_model=ChatResp)
async def chat(req: ChatReq, chain = Depends(get_chain)):
    
    result = await chain.ainvoke(req.message)
    
    answer = result["answer"]
    citations = []
    for doc, score in result["docs"]:
        citations.append(
            Citation(
                doc_id=doc.metadata.get("doc_id", ""),
                text=doc.page_content,
                score=score
            )
        )

    return ChatResp(
        status="ok",
        answer=answer,
        citations=citations,
    )

# Mount static files last
app.mount("/", StaticFiles(directory="public", html=True), name="static")