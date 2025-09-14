from pathlib import Path
import os
from typing import List, Dict, Any
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.schema.output_parser import StrOutputParser
import json

# Load environment variables
from dotenv import load_dotenv
load_dotenv() # This will load OPENAI_API_KEY and OPENAI_API_BASE from .env

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / 'data' / 'pmb' / 'pmb_unanda.json'
FAISS_INDEX_PATH = BASE_DIR / "faiss_index"

def load_documents() -> List[Document]:
    """Loads documents from the JSON file."""
    text = DATA_FILE.read_text(encoding="utf-8")
    data = json.loads(text)
    docs: List[Document] = []
    
    # University Info
    if "university" in data:
        docs.append(Document(
            page_content=f"Informasi umum tentang universitas: {json.dumps(data['university'], ensure_ascii=False)}",
            metadata={"source": "pmb_unanda.json", "doc_id": "university_info"}
        ))

    # Admission Tracks
    for track in data.get("admission_tracks", []):
        docs.append(Document(
            page_content=f"Informasi tentang jalur pendaftaran: {json.dumps(track, ensure_ascii=False)}",
            metadata={"source": "pmb_unanda.json", "doc_id": f"track_{track.get('track_name', '').replace(' ', '_')}"}
        ))

    # Programs
    for program in data.get("programs", []):
        docs.append(Document(
            page_content=f"Informasi tentang program studi: {json.dumps(program, ensure_ascii=False)}",
            metadata={"source": "pmb_unanda.json", "doc_id": f"program_{program.get('program_name', '').replace(' ', '_')}"}
        ))
        
    # Application Guide
    if "application_guide" in data:
        docs.append(Document(
            page_content=f"Panduan pendaftaran: {json.dumps(data['application_guide'], ensure_ascii=False)}",
            metadata={"source": "pmb_unanda.json", "doc_id": "application_guide"}
        ))

    # Tuition and Fees
    if "tuition_and_fees" in data:
        docs.append(Document(
            page_content=f"Informasi biaya kuliah: {json.dumps(data['tuition_and_fees'], ensure_ascii=False)}",
            metadata={"source": "pmb_unanda.json", "doc_id": "tuition_and_fees"}
        ))

    return docs

async def get_rag_chain():
    """Initializes and returns the RAG chain. 
    
    This function will now load the FAISS index from disk if it exists,
    or create it and save it if it doesn't.
    """
    # For OpenRouter, the base_url and api_key are loaded automatically from .env
    embeddings = OpenAIEmbeddings(model="openai/text-embedding-ada-002")
    
    if FAISS_INDEX_PATH.exists():
        print("Loading FAISS index from disk...")
        vs = FAISS.load_local(
            FAISS_INDEX_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
    else:
        print("Building FAISS index from documents...")
        docs = load_documents()
        try:
            vs = FAISS.from_documents(docs, embeddings)
            print("Saving FAISS index to disk...")
            vs.save_local(FAISS_INDEX_PATH)
        except Exception as e:
            print("!!! AN ERROR OCCURRED DURING FAISS INDEX CREATION !!!")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Details: {e}")
            # Re-raise the exception to ensure the app still fails as expected
            # but after we've printed the details.
            raise

    def retriever_with_scores(query):
        return vs.similarity_search_with_relevance_scores(query, k=5)

    def format_docs(docs):
        return "\n\n".join([doc.page_content for doc, score in docs])

    retriever = RunnableLambda(retriever_with_scores)

    template = """
    Anda adalah chatbot PMB Universitas Andi Djemma.
    Jawab pertanyaan berikut berdasarkan konteks yang diberikan.
    Konteks: {context}
    Pertanyaan: {question}
    Jawaban:
    """
    prompt = PromptTemplate.from_template(template)

    # For OpenRouter, the base_url and api_key are loaded automatically from .env
    llm = ChatOpenAI(model="meta-llama/llama-3-8b-instruct", temperature=0)

    chain = (
        {"docs": retriever, "question": RunnablePassthrough()}
        | RunnablePassthrough.assign(context=lambda x: format_docs(x["docs"]))
        | RunnablePassthrough.assign(answer=(prompt | llm | StrOutputParser()))
    )
    
    return chain
