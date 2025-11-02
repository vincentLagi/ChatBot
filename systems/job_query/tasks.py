from crewai import Task
from datetime import datetime
from unified_system.config.settings import get_fallback, get_answering_style
import pytz

def create_job_search_task(agent, user_query: str, context: list = None) -> Task:
    """Create task for Query Processing Agent"""

    tz = pytz.timezone("Asia/Jakarta")
    today_dt = datetime.now(tz)
    today_str = today_dt.strftime("%m/%d/%Y")
    fallback_message = get_fallback(user_query)
    description = f"""Analisis dan proses pertanyaan user berikut untuk mendapatkan informasi pekerjaan asisten SLC.

    USER QUERY: "{user_query}"

    Tanggal hari ini: {today_str} (timezone Asia/Jakarta)

    TUGAS ANDA:
    1. 🧠 Analisis Intent:
    - Apakah user ingin:
        - 🔹 Mencari jadwal pekerjaan (harian/mingguan) => gunakan `fetch_job_data`
        - 🔹 Melihat kelas/pelajaran apa saja yang diajar pada semester ini => gunakan `fetch_teaching_data`

    2. 🧩 Ekstrak Informasi Utama:
    - 👤 Username: format seperti KA24-1, IR23-1, ZN22-2
         2 huruf pertama merupakan sebuah inisial atau panggal dari sebuah assistant dan angka berikutnya merupakan generasi dari seorang assistant
    - 🗓️ Tanggal: hanya untuk permintaan jadwal (bukan teaching list). Bisa dalam format alami seperti:
        - "besok", "hari ini", "Senin depan", "minggu ini", "minggu depan", "bulan ini", "bulan kemarin"
        - atau tanggal spesifik seperti "10 Juli"
    - 📂 Jenis Job: (optional) user bisa menyebutkan jenis job seperti "case making", "marking", "teaching"

    3. 🔄 Normalisasi:
    - Username: ubah ke UPPERCASE
    - Tanggal: konversi ke ISO (YYYY-MM-DD) berdasarkan timezone Asia/Jakarta
    - Jenis Job: kapitalisasi awal setiap kata (contoh: "Case Making")

    4. ✅ Validasi:
    - Username harus cocok dengan regex `[A-Z]{{2}}\d{{2}}-\d`
    - Tanggal harus valid jika disebutkan

    5. 📋 Output:
    - Untuk job harian: hasil berupa list pekerjaan sesuai filter
    - Untuk teaching semesteran: hasil berupa daftar kelas yang diampu semester ini

    6. 📅 Asumsi jika tidak ada tanggal:
    - Jika tidak ada tanggal dan intent adalah job, tampilkan semua pekerjaan `Not Done` dengan `StartDate ≥ hari ini`
    - Jika intent adalah teaching semesteran, langsung tampilkan hasil dari `fetch_teaching_data`

    7. ❗ Penanganan khusus natural date:
    - Jika tanggal seperti "hari ini", "minggu ini", digunakan, pastikan hanya pekerjaan yang waktunya (`StartDate` s/d `EndDate`) mencakup tanggal tersebut

    Jika pertanyaan user ambigu atau tidak jelas dan melanggar validasi pada point ke 4, awali jawaban dengan fallback berikut:
    {fallback_message} (note: penanyaan job harus menggunakan initial+gen, ex: KA24-1), kemudian jelaskan lagi error sesuai dengan context.

    """

    expected_output = """Contoh output jika hasil berupa pekerjaan harian (fetch_job_data):
    [
        {
            "Description": "CPEN6098010-Computer Networks Quiz 2",
            "StartDate": "2025-07-17T07:00:00",
            "EndDate": "2025-08-12T20:00:00",
            "Status": "Not Done",
            "JobType": "Case Making",
            "ClassTransactionDetailId": ""
        },
        {
            "Description": "COMP6584001-Network and System Programming BB01  723 1",
            "StartDate": "2025-07-18T15:20:00",
            "EndDate": "2025-07-18T17:00:00",
            "Status": "Not Done",
            "JobType": "Teaching",
            "ClassTransactionDetailId": "f42db2aa-1fe0-ef11-a1ca-9440c921bcaf"
        }
    ]

    Contoh output jika hasil berupa kelas semesteran (fetch_teaching_data):
    [
        {
            "CourseName": "Data Structures",
            "ClassCode": "BE01",
            "Day": "Senin",
            "Time": "13:20 - 15:00",
            "Realization": "0/13"
        },
        {
            "CourseName": "Data Structures",
            "ClassCode": "LE01",
            "Day": "Kamis",
            "Time": "11:20 - 13:00",
            "Realization": "0/5"
        }
    ]

    Jika mendapatkan JSON seperti ini:
    {
        "details": "json: cannot unmarshal object into Go value of type []model.Job",
        "error": "Username Tidak di temukan"
    }
    awali jawaban dengan fallback, kemudian tambahkan penjelasan sesuai dengan error pada JSON-nya.
    """

    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        context=context or []
    )

def create_job_answer_task(agent, user_query: str, context: list = None) -> Task:
    """Create task for answering assistant's job schedule and teaching assignments"""

    description = f"""Berdasarkan hasil pencarian dari Query Processing Agent, bantu user mendapatkan jawaban tentang jadwal pekerjaan asisten (seperti Teaching, Case Making) atau kelas yang mereka pegang selama 1 semester.

    USER QUERY: "{user_query}"

    DATA DARI API:
    Bisa terdiri dari:
    - Job Data:
        - Description: Nama kegiatan atau kelas
        - StartDate & EndDate: Waktu mulai dan selesai
        - Status: Approved / Done / Not Done
        - JobType: Teaching, Case Making, Marking, dll
        - ClassTransactionDetailId: ID sesi kelas (jika relevan)

    - Teaching Class Assignment:
        - ClassCode: Misalnya LC01, BE02
        - CourseName: Nama mata kuliah
        - DayName: Hari (Senin, Selasa, dst.)
        - StartTime & EndTime: Jam
        - Room: Ruangan
        - SessionType: BB, LC, Exam, dll

    TUGAS ANDA:
    1. 🔎 Analisis data yang tersedia:
        - Jika data berisi StartDate/EndDate → itu data **Job**
        - Jika data berisi ClassCode/CourseName → itu data **Teaching Assignment Semester**

    2. 🧠 Tentukan konteks pertanyaan:
        - Jika user bertanya tentang: "minggu ini", "hari ini", "ada jadwal mengajar?" → cari di JOB data
        - Jika user bertanya: "mengajar apa semester ini?", "kelas apa yang saya pegang?" → pakai Teaching Assignment


    4. 📅 Jika pertanyaan tentang waktu (misal: "hari ini", "besok", "minggu depan"):
        - Untuk Teaching: hanya jika StartDate jatuh tepat pada hari tersebut
        - Untuk Case Making / Marking: jika tanggal pertanyaan berada dalam rentang StartDate dan EndDate
        - Gunakan timezone Asia/Jakarta

    5. 🔍 Gunakan tool `detect_ambiguity` untuk memastikan hasil tidak membingungkan

    6. 💬 Jawaban harus ramah, informatif, dan ditulis dalam bahasa Indonesia

    FORMAT JIKA LANGSUNG BISA JAWAB:

    **Jika data job (pekerjaan):**
    "Berikut pekerjaan asisten yang saya temukan:

    1. **Computer Networks Quiz 2**
        - 📌 Tipe: Case Making
        - 📆 7 Mei – 27 Mei 2025
        - ✅ Status: Approved

    2. **Data Structures LC09**
        - 📌 Tipe: Teaching
        - 🕒 7 Mei 2025 pukul 15.20 – 17.00
        - ✅ Status: Done"

    **Jika data teaching assignment:**
    "Berikut kelas yang Anda ampu semester ini:

    1. **Network and System Programming** (BB01)
        - 🏫 Ruang: 723
        - 📅 Kamis, 15:20 – 17:00

    2. **Distributed Systems** (LC03)
        - 🏫 Ruang: 718
        - 📅 Rabu, 13:00 – 14:40

    ❗ Jangan tampilkan JSON mentah
    ❗ Jika data ambigu (bentrok waktu, terlalu banyak, atau mirip), minta klarifikasi dulu

    Gaya Jawaban:
    {get_answering_style()}

    """

    expected_output = f"""Jawaban natural dan komunikatif tentang pekerjaan asisten, bisa berupa:
    - Jadwal kegiatan harian/mingguan seperti teaching, marking, case making
    - Daftar kelas yang diampu semester ini
    - Klarifikasi jika data ambigu
    - Ditulis dengan gaya ramah dan mudah dimengerti"""

    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        context=context or []
    )

def create_job_workflow_tasks(query_agent, answer_agent, user_query: str, context: list = None):
    """Create connected workflow tasks for both agents"""
    
    search_task = create_job_search_task(query_agent, user_query, context)
    answer_task = create_job_answer_task(answer_agent, user_query, context=[search_task])
    
    return [search_task, answer_task]