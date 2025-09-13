# Chatbot PMB Unanda

## Tujuan
Chatbot ini memberikan informasi Pendaftaran Mahasiswa Baru (PMB) Universitas Andi Djemma.

## Arsitektur singkat
- **FastAPI** sebagai API server.
- **RAG** dengan FAISS untuk mengambil konteks dari `pmb_unanda.json`.
- **Endpoint**: `/health`, `/chat`, `/search`, `/faq`.
- **Guard** sederhana memvalidasi input pengguna.

## Cara menjalankan
1. Salin `.env.example` menjadi `.env` dan isi API key LLM bila perlu.
2. Install dependensi: `pip install -r requirements.txt`.
3. Jalankan server: `uvicorn app.main:app --reload`.

## Contoh curl
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Syarat pendaftaran?"}'
```
