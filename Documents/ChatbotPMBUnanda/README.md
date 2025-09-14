# Chatbot PMB Unanda

## Tujuan
Chatbot ini memberikan informasi seputar Pendaftaran Mahasiswa Baru (PMB) Universitas Andi Djemma.

## Arsitektur singkat
- **FastAPI** sebagai server API.
- **Knowledge base** berupa berkas JSON `data/pmb/pmb_unanda.json`.
- **Retriever** fuzzy dengan ambang skor untuk memastikan jawaban berdasar konteks.
- **Endpoint** utama: `/health` dan `/chat`.

## Cara menjalankan
1. Salin `.env.example` menjadi `.env` bila ingin menyimpan konfigurasi lokal.
2. Install dependensi: `pip install -r requirements.txt`.
3. Jalankan server: `uvicorn app.main:app --reload`.

## Contoh curl
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Syarat pendaftaran?"}'
```
