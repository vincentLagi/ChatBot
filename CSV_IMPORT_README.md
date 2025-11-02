# CSV Import ke Supabase

Panduan untuk mengimport data dari `output.csv` ke database Supabase.

## 📋 Langkah-langkah Import

### 1. Buat Table di Supabase

#### Cara 1: Menggunakan SQL Editor
1. Buka Supabase Dashboard
2. Masuk ke **SQL Editor**
3. Copy dan paste SQL dari file `create_assistant_csv_table.sql`
4. Jalankan SQL

#### Cara 2: Menggunakan Table Editor
1. Buka Supabase Dashboard
2. Masuk ke **Table Editor**
3. Klik **Create a new table**
4. Isi dengan detail berikut:
   - **Name**: `assistant_csv`
   - **Columns**:
     ```
     id (int8, primary key, auto increment)
     initial (text)
     gen (text)
     initial_gen (text)
     name (text)
     binusian_id (text)
     nim (text)
     email_edu (text)
     email_ac_id (text)
     leader (text)
     major_long (text)
     major (text)
     streaming (text)
     semester (text)
     global (text)
     location (text)
     position (text)
     shift (text)
     created_at (timestamptz, default: now())
     ```

### 2. Setup Environment Variables

Pastikan file `.env` di direktori `AI Agent` sudah berisi:

```env
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
```

### 3. Jalankan Script Import

#### Cara 1: Menggunakan script sederhana (Recommended)
```bash
cd "AI Agent"
python import_csv_simple.py
```

#### Cara 2: Menggunakan script lengkap
```bash
cd "AI Agent"
python import_csv_to_supabase.py
```

### 4. Verifikasi Import

Setelah script selesai, cek di Supabase:
1. Buka **Table Editor**
2. Pilih table `assistant_csv`
3. Pastikan ada 189 rows (sesuai jumlah data di CSV)

## 📊 Struktur Data

Data yang akan diimport:

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| initial | text | Inisial asisten (AA, AC, AI, dll) |
| gen | text | Generasi (24-2, 25-1, dll) |
| initial_gen | text | Kombinasi initial + gen |
| name | text | Nama lengkap asisten |
| binusian_id | text | ID Binusian |
| nim | text | NIM |
| email_edu | text | Email @binus.edu |
| email_ac_id | text | Email @binus.ac.id |
| leader | text | Leader (EA, TR, JB, dll) |
| major_long | text | Jurusan lengkap |
| major | text | Kode jurusan (TI, SI, dll) |
| streaming | text | Streaming/Spesialisasi |
| semester | text | Semester |
| global | text | Global class (Yes/No) |
| location | text | Lokasi (KMG, ALS, BKS, SMG) |
| position | text | Posisi/jabatan |
| shift | text | Shift (M, P, N) |

## 🛠️ Troubleshooting

### Error: Table tidak ditemukan
```
❌ Table 'assistant_csv' does not exist
```
**Solusi**: Jalankan SQL dari `create_assistant_csv_table.sql` di Supabase SQL Editor

### Error: Environment variables tidak ditemukan
```
❌ Missing required environment variables
```
**Solusi**: Pastikan file `.env` berisi `SUPABASE_URL` dan `SUPABASE_KEY`

### Error: Permission denied
```
❌ Error inserting data: permission denied
```
**Solusi**: 
1. Cek Row Level Security (RLS) di table
2. Pastikan API key memiliki permission yang cukup
3. Disable RLS sementara: `ALTER TABLE assistant_csv DISABLE ROW LEVEL SECURITY;`

### Error: CSV file tidak ditemukan
```
❌ CSV file not found
```
**Solusi**: Pastikan file `output.csv` ada di `AI Agent/data/csv/`

## 📈 Monitoring Import

Script akan menampilkan progress:
```
📊 Starting to insert 189 rows to Supabase...
✅ Inserted batch 1: 50 rows
📈 Progress: 26.5%
✅ Inserted batch 2: 50 rows
📈 Progress: 52.9%
...
🎉 Successfully inserted all 189 rows!
```

## 🔍 Verifikasi Data

Setelah import selesai, cek data dengan query:

```sql
-- Cek jumlah total
SELECT COUNT(*) FROM assistant_csv;

-- Cek sample data
SELECT initial, name, location, position 
FROM assistant_csv 
LIMIT 5;

-- Cek distribusi lokasi
SELECT location, COUNT(*) 
FROM assistant_csv 
GROUP BY location;
```

## 🎯 Penggunaan Data

Setelah data terimport, Anda bisa:
1. Menggunakan data untuk search assistant
2. Filter berdasarkan location, major, position
3. Integrasi dengan AI Agent system

## 📞 Support

Jika ada masalah:
1. Cek logs di terminal
2. Verifikasi environment variables
3. Cek permission di Supabase
4. Restart script import 