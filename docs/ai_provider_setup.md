# AI Provider Setup

Panduan ini menjelaskan konfigurasi integrasi AI pada backend ERP MBG untuk dua kebutuhan:

- NL2SQL analitik dengan OpenAI
- analisa foto dan video dengan Google AI

## Konfigurasi `.env`

Tambahkan atau sesuaikan key berikut pada file [`.env`](C:/projek/fastapi-mbg/.env):

```env
OPENAI_ENABLED=false
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_NL2SQL_MODEL=
OPENAI_TIMEOUT_SECONDS=60
OPENAI_NL2SQL_ALLOW_EXECUTION=false
OPENAI_NL2SQL_MAX_ROWS=200
OPENAI_NL2SQL_SYSTEM_PROMPT=You translate analytical business questions into safe PostgreSQL SELECT queries for ERP MBG. Return JSON only with keys: sql, explanation, assumptions, safety_notes.

GOOGLE_AI_ENABLED=false
GOOGLE_AI_API_KEY=
GOOGLE_AI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
GOOGLE_AI_MEDIA_MODEL=
GOOGLE_AI_TIMEOUT_SECONDS=120
GOOGLE_AI_MEDIA_MAX_DOWNLOAD_MB=20
```

Template yang sama juga tersedia di [`.env.example`](C:/projek/fastapi-mbg/.env.example).

## Rekomendasi Pengisian

Untuk OpenAI:

- set `OPENAI_ENABLED=true`
- isi `OPENAI_API_KEY`
- default yang sudah dipasang adalah `gpt-5.6-terra`
- biarkan `OPENAI_NL2SQL_ALLOW_EXECUTION=false` pada tahap awal agar frontend hanya menerima SQL hasil generate tanpa langsung mengeksekusi query

Untuk Google AI:

- set `GOOGLE_AI_ENABLED=true`
- isi `GOOGLE_AI_API_KEY`
- default yang sudah dipasang adalah `gemini-2.5-flash`
- atur `GOOGLE_AI_MEDIA_MAX_DOWNLOAD_MB` sesuai batas file yang aman untuk workload Anda

## Endpoint Yang Tersedia

Setelah konfigurasi aktif, backend menyediakan endpoint berikut:

- `GET /api/v1/ai/providers/status`
- `POST /api/v1/ai/nl2sql/query`
- `POST /api/v1/ai/media/analyze-image`
- `POST /api/v1/ai/media/analyze-video`

## Catatan NL2SQL

Implementasi saat ini:

- mengirim prompt ke OpenAI Responses API
- membangun schema context otomatis dari `information_schema.columns`
- hanya menerima SQL read-only
- menolak query mutasi dan multi-statement
- bisa mengeksekusi query hanya jika `OPENAI_NL2SQL_ALLOW_EXECUTION=true`

Saran implementasi frontend:

- tampilkan SQL dan penjelasannya lebih dulu
- minta konfirmasi user sebelum mode execute diaktifkan
- tampilkan `assumptions` dan `safety_notes` agar hasil analisa lebih mudah diaudit

## Catatan Analisa Foto dan Video

Implementasi Google AI saat ini:

- menerima `source_url` atau `base64_data`
- memanggil endpoint `generateContent`
- cocok untuk foto dan video pendek
- mengembalikan `analysis_text` dan `raw_response`

Catatan rekomendasi API saat ini:

- dokumentasi OpenAI saat ini menempatkan Responses API sebagai interface utama
- dokumentasi Google AI saat ini merekomendasikan Interactions API untuk implementasi baru
- backend ini masih memakai `generateContent` untuk Google AI karena tetap didukung dan cukup sederhana untuk tahap integrasi awal
- bila nanti kita ingin workflow media yang lebih panjang atau observability yang lebih baik, modul Google AI ini sebaiknya dimigrasikan ke Interactions API

Saran operasional:

- gunakan `source_url` untuk file yang bisa diakses backend
- gunakan `base64_data` bila file berasal dari upload frontend dan belum disimpan
- untuk video besar atau workflow arsip media, siapkan tahap berikutnya berupa upload file permanen lebih dulu lalu kirim referensi yang stabil

## CORS

Karena backend multi-tenant dan multi-SPPG, frontend sering mengirim header:

- `X-Tenant-ID`
- `X-SPPG-ID`

Header `X-SPPG-ID` sudah ditambahkan pada konfigurasi `CORS_ALLOWED_HEADERS` di `.env` dan `.env.example` agar request browser tidak gagal pada preflight.
