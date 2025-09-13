import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.main import app

client = TestClient(app)

def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    data = r.json()
    assert data['ok'] is True
    assert data['items'] > 0

def test_chat_out_of_scope():
    r = client.post('/chat', json={'message': 'halo apa kabar'})
    assert r.status_code == 200
    assert r.json()['status'] == 'out_of_scope'

def test_chat_not_found():
    r = client.post('/chat', json={'message': 'biaya qwertyui asdfgh'})
    data = r.json()
    assert data['status'] == 'not_found'
    assert data['citations'] == []

def test_chat_ok():
    r = client.post('/chat', json={'message': 'biaya pendaftaran'})
    data = r.json()
    assert data['status'] == 'ok'
    assert data['citations']
    assert isinstance(data['citations'][0]['doc_id'], str)
