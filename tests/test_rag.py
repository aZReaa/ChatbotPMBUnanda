import os
os.environ['TESTING'] = '1'

from app.deps import get_embeddings
from app.rag import build_vectorstore


def test_rag_search():
    vs = build_vectorstore(get_embeddings())
    docs = vs.similarity_search('pendaftaran', k=1)
    assert len(docs) >= 1
