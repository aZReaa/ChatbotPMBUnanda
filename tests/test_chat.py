import os
from fastapi.testclient import TestClient

os.environ['TESTING'] = '1'

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json() == {'status': 'ok'}


def test_faq():
    r = client.get('/faq')
    assert r.status_code == 200
    assert 'university' in r.json()


def test_search():
    r = client.get('/search', params={'q': 'pendaftaran'})
    assert r.status_code == 200
    assert 'results' in r.json()


def test_chat():
    r = client.post('/chat', json={'message': 'Halo'})
    assert r.status_code == 200
    assert 'answer' in r.json()
