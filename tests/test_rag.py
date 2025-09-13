import os
import sys
from pathlib import Path

os.environ['TESTING'] = '1'
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.deps import get_embeddings
from app.rag import build_vectorstore, search_docs


def test_rag_search():
    vs = build_vectorstore(get_embeddings())
    docs = search_docs(vs, 'pendaftaran', k=3)
    assert len(docs) >= 1
    assert 'doc_id' in docs[0]
