# AI Agent API Server

Flask API server untuk mengintegrasikan AI Agent system dengan Line Bot.

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

### 2. Setup Environment Variables

Buat file `.env` di direktori `AI Agent` dengan konfigurasi yang diperlukan:

```env
# Google AI API Key
GOOGLE_API_KEY=your_google_api_key_here

# Database configuration (jika menggunakan Supabase)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Port untuk API server (opsional, default: 5000)
PORT=5000
```

### 3. Jalankan API Server

#### Cara 1: Menggunakan startup script
```bash
python start_api.py
```

#### Cara 2: Langsung menjalankan
```bash
python api_server.py
```

Server akan berjalan di `http://localhost:5000`

## 📡 API Endpoints

### 1. Health Check
```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "service": "AI Agent API",
  "chat_system_ready": true
}
```

### 2. Chat Endpoint (Main)
```
POST /api/chat
```

Request Body:
```json
{
  "message": "Pertanyaan atau pesan user",
  "session_id": "optional_session_id"
}
```

Response:
```json
{
  "status": "success",
  "message": "Response dari AI Agent",
  "timestamp": "2024-01-01T12:00:00",
  "session_id": "session_id"
}
```

### 3. Systems Info
```
GET /api/systems
```

Response:
```json
{
  "available_systems": [
    "Rules UAP",
    "Assistant Search",
    "Rules Mengajar",
    "Correction",
    "Job Query",
    "Material Criteria",
    "Find Room"
  ],
  "description": "Unified Academic Assistant with 7 specialized AI systems",
  "timestamp": "2024-01-01T12:00:00"
}
```

### 4. Status
```
GET /api/status
```

Response:
```json
{
  "chat_system_ready": true,
  "service": "AI Agent API",
  "version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00",
  "session_info": {
    "start_time": "2024-01-01T12:00:00",
    "queries_processed": 10,
    "systems_used": ["Rules UAP", "Material Criteria"],
    "errors_encountered": 0
  }
}
```

## 🔧 Integration dengan Line Bot

Line Bot sudah dikonfigurasi untuk memanggil endpoint `/api/chat` di `http://localhost:5000/api/chat`.

### Testing API

#### Menggunakan curl:
```bash
# Test health check
curl http://localhost:5000/health

# Test chat endpoint
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Apa itu UAP?", "session_id": "test123"}'
```

#### Menggunakan Python requests:
```python
import requests

# Test chat
response = requests.post(
    "http://localhost:5000/api/chat",
    json={
        "message": "Apa itu UAP?",
        "session_id": "test123"
    }
)

print(response.json())
```

## 🛠️ Troubleshooting

### 1. Port sudah digunakan
Jika port 5000 sudah digunakan, ubah di file `.env`:
```env
PORT=5001
```

### 2. Virtual environment tidak ditemukan
```bash
# Buat virtual environment baru
python -m venv venv

# Aktifkan
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install requirements
pip install -r requirements.txt
```

### 3. Google API Key error
Pastikan `GOOGLE_API_KEY` sudah diset di file `.env` dan valid.

### 4. Import error
Pastikan semua dependencies sudah terinstall:
```bash
pip install -r requirements.txt
```

## 📝 Logs

API server akan menampilkan logs yang informatif:
- 📨 Pesan masuk dari Line Bot
- 📤 Response yang dikirim
- ❌ Error yang terjadi
- 🚀 Status startup

## 🔄 Restart Server

Untuk restart server:
1. Tekan `Ctrl+C` untuk stop
2. Jalankan kembali: `python api_server.py`

## 📊 Monitoring

Gunakan endpoint `/api/status` untuk monitoring:
- Status chat system
- Jumlah query yang diproses
- Sistem yang digunakan
- Error yang terjadi 