from crewai import Task

from datetime import datetime, timedelta
from unified_system.config.settings import get_fallback, get_answering_style
import pytz
def create_room_search_task(agent, user_query: str, context: list = None) -> Task:
    """Create task for Query Processing Agent"""

    tz = pytz.timezone("Asia/Jakarta")
    today_dt = datetime.now(tz)
    tomorrow_dt = today_dt + timedelta(days=1)
    today_str = today_dt.strftime("%m/%d/%Y")
    tomorrow_str = tomorrow_dt.strftime("%m/%d/%Y")
    fallback_message = get_fallback(user_query)

    description = f"""‼️PERHATIAN: Semua tanggal harus dalam format MM/DD/YYYY. Jangan gunakan format lain.

    USER QUERY: "{user_query}"

    TANGGAL HARI INI (format MM/DD/YYYY): {today_str}
    TANGGAL BESOK (format MM/DD/YYYY): {tomorrow_str}

    🎯 TUGAS ANDA:
    1. 🧠 Analisis Intent:
       - Apakah user ingin mencari ruangan kosong seluruh shift?
       - Apakah user ingin mencari ruangan kosong pada shift tertentu?
       - Apakah user ingin tahu siapa yang meminjam ruangan tertentu?
       - Apakah user ingin tahu alasan kenapa ruangan tidak kosong?

    2. 🧩 Ekstrak Informasi Utama:
       - Nomor ruangan (misal: 601)
       - Tanggal ("hari ini", "besok", atau tanggal spesifik)
       - Shift (jika disebutkan, misalnya "shift 3")

    3. 🔄 Normalisasi:
       - Ruangan → ekstrak angkanya saja (contoh: "601")
       - Tanggal:
         - "hari ini" → {today_str}
         - "besok" → {tomorrow_str}
         - Tanggal lainnya harus dalam format MM/DD/YYYY
       - Shift → ekstrak angka dari "shift X"

    4. ✅ Validasi:
       - Ruangan harus 329, 601-610, 621-631, 613-614, 706, 708, 710, 711A, 721-724, 724 Meeting Room, 725, 727-731, Jika nomor ruangan tidak berada diantara nomor itu, kembalikan fallback dengan penjelasan tidak ada ruangan dengn nomor itu. 
       - Shift harus antara 1–7
       - Tanggal harus valid dan dalam satu hari

    5. 📊 Format Output JSON:
       - Jika mencari ruangan kosong (semua shift): kembalikan ruangan yang `StatusDetails` seluruh elemennya `null`
       - Jika mencari ruangan kosong pada shift tertentu: kembalikan ruangan yang `StatusDetails[shift-1] == null`
       - Jika mencari siapa yang meminjam: kembalikan `StatusDetails` yang berisi data
       - Jika ingin tahu alasan ruangan tidak kosong: kembalikan `StatusDetails[x]` beserta `Description`
       - Jika input tidak valid: kembalikan JSON dengan `error` dan `message`

    OUTPUT:
    - JSON list dengan jadwal ruangan peminjaman.
    - Atau: JSON error dengan pesan kesalahan
    - Atau: empty list [] jika tidak ditemukan hasil

    Jika pertanyaan user ambigu atau tidak jelas, awali jawaban dengan fallback berikut:
    {fallback_message}, kemudian jelaskan lagi error sesuai dengan context,
    """

    expected_output = """

    Contoh jika list berisi jadwal ruangan peminjaman:
    [
      {
         "Campus": "ANGGREK",
         "RoomName": "329",
         "StatusDetails": [
               null,
               null,
               null,
               null,
               null,
               null,
               null
         ]
      },
      {
         "Campus": "ANGGREK",
         "RoomName": "601",
         "StatusDetails": [
               null,
               null,
               null,
               null,
               null,
               [
                  {
                     "Assistant": "CF24-1",
                     "ClassName": "00001",
                     "Description": "CALIB-Calibration - 00001 - 601",
                     "Division": null,
                     "Email": null,
                     "InsertedDate": "6/26/2025 1:26:40 PM",
                     "Name": null,
                     "NeedInternet": false,
                     "Softwares": null,
                     "Status": "C",
                     "StudentOnsiteStatus": "n",
                     "Subject": null,
                     "TransactionDetailId": "c385fd81-5652-f011-a1d1-9440c921bcaf",
                     "TransactionId": "8deda078-1cfa-4d4e-8cd8-c2181989d54a",
                     "Type": null
                  }
               ],
               null
         ]
      },
      {
         "Campus": "ANGGREK",
         "RoomName": "603",
         "StatusDetails": [
               null,
               null,
               null,
               null,
               null,
               null,
               null
         ]
      },
      {
         "Campus": "ANGGREK",
         "RoomName": "604",
         "StatusDetails": [
               null,
               [
                  {
                     "Assistant": null,
                     "ClassName": null,
                     "Description": "Upgrade PC (Cici Suryani - SLC) [Verified]",
                     "Division": "SLC",
                     "Email": "extadminslc@binus.edu",
                     "InsertedDate": null,
                     "Name": "Cici Suryani",
                     "NeedInternet": false,
                     "Softwares": [],
                     "Status": "B",
                     "StudentOnsiteStatus": "n",
                     "Subject": null,
                     "TransactionDetailId": null,
                     "TransactionId": "2f8e290f-ce22-4281-b13c-dfa2c79bfaa3",
                     "Type": null
                  }
               ],
               [
                  {
                     "Assistant": null,
                     "ClassName": null,
                     "Description": "Upgrade PC (Cici Suryani - SLC) [Verified]",
                     "Division": "SLC",
                     "Email": "extadminslc@binus.edu",
                     "InsertedDate": null,
                     "Name": "Cici Suryani",
                     "NeedInternet": false,
                     "Softwares": [],
                     "Status": "B",
                     "StudentOnsiteStatus": "n",
                     "Subject": null,
                     "TransactionDetailId": null,
                     "TransactionId": "2f8e290f-ce22-4281-b13c-dfa2c79bfaa3",
                     "Type": null
                  }
               ],
               [
                  {
                     "Assistant": null,
                     "ClassName": null,
                     "Description": "Upgrade PC (Cici Suryani - SLC) [Verified]",
                     "Division": "SLC",
                     "Email": "extadminslc@binus.edu",
                     "InsertedDate": null,
                     "Name": "Cici Suryani",
                     "NeedInternet": false,
                     "Softwares": [],
                     "Status": "B",
                     "StudentOnsiteStatus": "n",
                     "Subject": null,
                     "TransactionDetailId": null,
                     "TransactionId": "2f8e290f-ce22-4281-b13c-dfa2c79bfaa3",
                     "Type": null
                  }
               ],
               [
                  {
                     "Assistant": null,
                     "ClassName": null,
                     "Description": "Upgrade PC (Cici Suryani - SLC) [Verified]",
                     "Division": "SLC",
                     "Email": "extadminslc@binus.edu",
                     "InsertedDate": null,
                     "Name": "Cici Suryani",
                     "NeedInternet": false,
                     "Softwares": [],
                     "Status": "B",
                     "StudentOnsiteStatus": "n",
                     "Subject": null,
                     "TransactionDetailId": null,
                     "TransactionId": "2f8e290f-ce22-4281-b13c-dfa2c79bfaa3",
                     "Type": null
                  }
               ],
               null,
               null
         ]
      },
      {
         "Campus": "ANGGREK",
         "RoomName": "605",
         "StatusDetails": [
               [
                  {
                     "Assistant": "VS22-2",
                     "ClassName": "00005",
                     "Description": "CALIB-Calibration - 00005 - 605",
                     "Division": null,
                     "Email": null,
                     "InsertedDate": "6/26/2025 1:26:40 PM",
                     "Name": null,
                     "NeedInternet": false,
                     "Softwares": null,
                     "Status": "C",
                     "StudentOnsiteStatus": "n",
                     "Subject": null,
                     "TransactionDetailId": "3385fd81-5652-f011-a1d1-9440c921bcaf",
                     "TransactionId": "d8b80b24-b3c1-42b0-8754-73a61fbc4efc",
                     "Type": null
                  }
               ],
               null,
               null,
               null,
               null,
               null,
               null
         ]
      }
   ]
    """

    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        context=context or []
    )

def create_room_answer_task(agent, user_query: str, context: list = None) -> Task:
   """Create task for answering room availability queries based on processed data"""

   description = f"""🧠 TUGAS ANDA: Buat jawaban yang alami, jelas, dan sesuai dengan konteks pertanyaan user berdasarkan hasil pemrosesan data jadwal ruangan.

   USER QUERY: "{user_query}"

   📦 DATA YANG ANDA GUNAKAN:
   - Data dari Room Processor Agent
   - Format data bisa berupa:
   1. List ruangan kosong
   2. Info bahwa tidak ada peminjaman (libur)
   3. Pesan error jika input tidak valid

   🎯 FOKUS:
   - Tunjukkan apakah ruangan kosong atau terisi, dan jika terisi, sebutkan siapa peminjamnya (jika tersedia)
   - Jika user mencari daftar ruangan kosong, tampilkan daftar tersebut dengan cara yang mudah dibaca
   - Jika tidak ada jadwal, beritahu dengan nada informatif
   - Jika ada error, sampaikan dengan bahasa yang ramah dan beri petunjuk perbaikannya

   🗣️ GAYA JAWABAN:
   {get_answering_style()}
   - Ambil detail penting dari pertanyaan user dan hasil data:
   • Tanggal (hari ini/besok/tanggal tertentu)
   • Shift (jika disebut)
   • Nomor ruangan (jika spesifik)

   📌 FORMAT YANG DISARANKAN:
   - Selalu awali jawaban dengan tanggal. Contoh:
      "Hari ini (07/21/2025), ruangan 601 shift 1 kosong."
      atau
      "Besok (07/22/2025), ruangan 605 shift 2 sudah dipinjam oleh Cici Suryani (SLC)."
      
   - Untuk "No Schedule":
   "Pada tanggal tersebut tidak ada peminjaman ruangan. Mungkin karena hari libur."

   - Untuk error:
   "Sepertinya ada yang salah dengan inputnya. Format tanggal yang benar adalah MM/DD/YYYY, contoh: 07/15/2025."

   - Untuk ambiguitas:
   "Apakah maksud Anda ruangan 603 atau 605? Keduanya tersedia di shift yang berbeda."

   🔍 TIPS:
   - Adaptif terhadap konteks dan gaya bertanya user
   - Jangan beri info berlebihan — cukup yang menjawab pertanyaan dengan jelas
   - Jika jawabannya panjang, kelompokkan dan beri spasi agar enak dibaca
   """

   expected_output = """
   Jawaban alami dan responsif tentang jadwal ruangan, meliputi:
   - Konfirmasi status ruangan (kosong/terisi)
   - Daftar ruangan kosong yang terorganisir (jika banyak)
   - Penjelasan jika tidak ada peminjaman (libur)
   - Error yang ramah pengguna
   - Klarifikasi jika perlu
   """

   return Task(
         description=description,
         expected_output=expected_output,
         agent=agent,
         context=context or []
      )

def create_room_workflow_tasks(query_agent, answer_agent, user_query: str, context: list = None):
    """Create connected workflow tasks for both agents"""
    
    search_task = create_room_search_task(query_agent, user_query, context)
    answer_task = create_room_answer_task(answer_agent, user_query, context=[search_task])
    
    return [search_task, answer_task]