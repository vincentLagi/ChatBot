# RIG Chat System

Sistem chat terintegrasi yang menggabungkan Line Bot dengan AI Agent untuk membantu mahasiswa dengan pertanyaan akademik.

## 🎯 Overview

Sistem ini terdiri dari:
- **Line Bot** (Port 3030) - Interface untuk user melalui LINE
- **AI Agent API** (Port 5000) - Backend AI dengan 7 sistem khusus
- **Unified Router** - Mengarahkan pertanyaan ke sistem yang tepat

### 7 Sistem AI yang Tersedia:
1. **Rules UAP** - Peraturan dan prosedur UAP
2. **Assistant Search** - Pencarian asisten
3. **Rules Mengajar** - Peraturan mengajar
4. **Correction** - Sistem koreksi dan case making
5. **Job Query** - Pencarian lowongan kerja
6. **Material Criteria** - Materi kuliah dan kriteria
7. **Find Room** - Pencarian ruangan

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Masuk ke direktori AI Agent
cd "AI Agent"

# Buat virtual environment (jika belum ada)
python -m venv venv

# Aktifkan virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Konfigurasi Environment Variables

Buat file `.env` di direktori `AI Agent`:

```env
# Google AI API Key (Required)
GOOGLE_API_KEY=your_google_api_key_here

# Database configuration (Optional)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Port configuration (Optional)
PORT=5000
```

### 3. Jalankan Sistem

#### Cara 1: Menggunakan script otomatis (Recommended)
```bash
# Dari direktori AI Agent
python start_servers.py
```

#### Cara 2: Manual
```bash
# Terminal 1 - AI Agent API
cd "AI Agent"
venv\Scripts\activate  # Windows
python api_server.py

# Terminal 2 - Line Bot
cd "Line Bot"
python app.py
```

## 📡 API Endpoints

### AI Agent API (http://localhost:5000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/chat` | POST | Main chat endpoint |
| `/api/systems` | GET | Info sistem yang tersedia |
| `/api/status` | GET | Status detail sistem |

### Line Bot (http://localhost:3030)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/callback` | POST | LINE webhook endpoint |

## 🧪 Testing

### Test AI Agent API
```bash
cd "AI Agent"
python test_api.py
```

### Test Query Spesifik
```bash
cd "AI Agent"
python test_api.py "Apa itu UAP?"
```

### Test dengan curl
```bash
# Health check
curl http://localhost:5000/health

# Chat endpoint
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Apa itu UAP?", "session_id": "test123"}'
```

## 🔧 Konfigurasi Line Bot

Line Bot sudah dikonfigurasi untuk memanggil AI Agent API di `http://localhost:5000/api/chat`.

### Webhook URL untuk LINE Developer Console:
```
http://your-domain:3030/callback
```

## 📁 Struktur File

```
RIG/
├── AI Agent/
│   ├── api_server.py              # Flask API server
│   ├── start_api.py               # Startup script untuk API saja
│   ├── start_servers.py           # Startup script untuk kedua server
│   ├── test_api.py                # Test script
│   ├── requirements.txt           # Dependencies
│   ├── config_example.txt         # Environment variables example
│   ├── API_README.md              # API documentation
│   ├── RIG_CHAT_SYSTEM_README.md  # This file
│   └── unified_system/            # AI systems
└── Line Bot/
    └── app.py                     # Line Bot server
```

## 🛠️ Troubleshooting

### 1. Port sudah digunakan
```bash
# Cek port yang digunakan
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Linux/Mac

# Ubah port di .env file
PORT=5001
```

### 2. Virtual environment error
```bash
# Hapus dan buat ulang virtual environment
rm -rf venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Google API Key error
- Pastikan `GOOGLE_API_KEY` valid
- Cek quota dan billing di Google Cloud Console

### 4. Import error
```bash
# Install ulang dependencies
pip install -r requirements.txt --force-reinstall
```

### 5. Line Bot tidak merespon
- Cek apakah AI Agent API berjalan di port 5000
- Cek webhook URL di LINE Developer Console
- Cek logs di terminal

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:5000/health
```

### Status Detail
```bash
curl http://localhost:5000/api/status
```

### Logs
- AI Agent API: Lihat output di terminal
- Line Bot: Lihat output di terminal
- Keduanya akan menampilkan logs yang informatif

## 🔄 Restart System

### Restart Otomatis
```bash
# Stop dengan Ctrl+C, lalu jalankan ulang
python start_servers.py
```

### Restart Manual
```bash
# Stop semua proses
# Jalankan ulang sesuai langkah di atas
```

## 📝 Development

### Menambah Sistem AI Baru
1. Buat folder baru di `AI Agent/systems/`
2. Implementasi `agents.py`, `tasks.py`, `tools.py`
3. Update router di `unified_system/router/`
4. Test dengan `test_api.py`

### Modifikasi API
1. Edit `AI Agent/api_server.py`
2. Tambah endpoint baru
3. Test dengan `test_api.py`

## 🚨 Security Notes

- Jangan commit file `.env` ke repository
- Gunakan HTTPS untuk production
- Validasi input di semua endpoint
- Monitor API usage dan rate limiting

## 📞 Support

Jika ada masalah:
1. Cek logs di terminal
2. Test dengan `test_api.py`
3. Cek health check endpoint
4. Restart sistem

## 🎉 Selamat Menggunakan!

Sistem RIG Chat siap membantu mahasiswa dengan pertanyaan akademik melalui LINE Bot yang terintegrasi dengan AI Agent canggih! 