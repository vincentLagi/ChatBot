from crewai import Task
from unified_system.config.settings import get_fallback, get_answering_style

def create_assistant_search_task(agent, user_query: str, context: list = None) -> Task:
    """
    Create task for Assistant Search Query Processing
    """

    fallback_message = get_fallback(user_query)
    description = f"""Analisis dan proses pertanyaan pengguna berikut untuk mencari data asisten:

    USER QUERY: "{user_query}"
    
    TUGAS ANDA:
    1. 🧠 Analisa Intent: Pahami maksud pengguna terkait pencarian data asisten, dan segala sesuatu tentang leader
    2. 🔍 Identifikasi Kriteria: Tentukan kolom dan nilai yang ingin dicari
    3. ✅ Validasi: Pastikan kriteria pencarian sesuai dengan kolom yang tersedia
    4. 🔍 Strategi Pencarian: Pilih tool yang tepat (single atau multi-column search)
    5. 📊 Lakukan Pencarian: Jalankan pencarian dengan parameter optimal
    6. 📋 Kembalikan Hasil: Berikan hasil lengkap dengan metadata untuk agen jawaban
    
    Gunakan tools yang tersedia:
    - search_assistant_by_column: untuk pencarian sederhana 1-2 kriteria
    - search_assistant_multi_column: untuk pencarian kompleks dengan banyak kriteria
    
    OUTPUT: Hasil pencarian dalam format JSON dengan informasi asisten yang ditemukan.
    
    Leader itu juga merupakan inisial dari seorang asisten, Jadi jika ada pencarian data yang ada inisial + gen cukup gunakan inisialnya saja. Contoh Siapa anak dari leader DE23-2, jadi pencarian datanya cukup menggunakan DE saja.

    Jika pertanyaan user ambigu atau tidak jelas, awali jawaban dengan fallback berikut:
    {fallback_message}, kemudian jelaskan lagi error sesuai dengan context.
    """
    
    expected_output = """Hasil pencarian data asisten dalam format JSON yang mencakup:
    - Status pencarian (success/no_results/error)
    - Jumlah hasil yang ditemukan
    - Data asisten lengkap (nama, kontak, posisi, lokasi, dll)
    - Metadata pencarian untuk referensi"""
    
    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        context=context or []
    )

def create_assistant_answer_task(agent, user_query: str, context: list = None) -> Task:
    """
    Create task for Assistant Search Answer Generation
    """
    description = f"""PENTING: Anda adalah agen KEDUA dalam workflow. Agen pertama sudah melakukan pencarian dan memberikan hasil JSON.

    SUMBER DATA: Ambil hasil pencarian JSON dari output agen sebelumnya (Agen Pencarian Data Asisten)
    KUERI AWAL PENGGUNA: "{user_query}"
    
    INSTRUKSI DETAIL:
    1. 📊 WAJIB: Baca output dari agen sebelumnya yang berisi hasil pencarian JSON
    2. 🔍 Cek field "status" - jika "success" maka ada data ditemukan
    3. 📋 Ekstrak data dari field "results" yang berisi array informasi asisten
    4. 💬 Jawab pertanyaan pengguna dengan data yang sudah ditemukan
    5. 🎯 Fokus pada informasi asisten: nama, kode, posisi, kontak, lokasi
    
    YANG HARUS DILAKUKAN:
    ✅ BACA hasil JSON dari task sebelumnya
    ✅ Jika status="success" dan ada "results", gunakan data tersebut
    ✅ Presentasikan informasi dengan bahasa natural Indonesia
    ✅ Sebutkan nama lengkap, kode (initial_gen), posisi, dan kontak
    ✅ Jelaskan posisi dan lokasi dengan detail yang mudah dipahami
    
    YANG TIDAK BOLEH:
    ❌ Mengabaikan hasil JSON yang sudah ada
    ❌ Bilang "tidak ditemukan" jika data sebenarnya ada
    ❌ Menggunakan format JSON mentah dalam jawaban
    ❌ Menambah informasi yang tidak ada di data
    
    PENTING: 
    - Anda akan menerima hasil pencarian dalam format JSON dari task sebelumnya
    - Baca dengan teliti data "results" dalam JSON tersebut
    - Jika status "success" dan ada results, tampilkan informasi asisten
    - Jika tidak ada results atau status error, beritahu user dengan ramah
    - Jika terdapat 5 json assistant atua lebih, sebutkan nama dan generasi saja
    
    GAYA JAWABAN:
    {get_answering_style()}
    
    CONTOH PROSES:
    
    Jika hasil pencarian JSON berisi:
    {{
      "status": "success",
      "results": [
        {{
          "name": "Michael Stefano Irawadi",
          "initial_gen": "SF24-1",
          "position": "Ast - KMG (S)",
          "email_edu": "michael.irawadi@binus.edu"
        }}
      ]
    }}
    
    
    HARUS:
    ✅ Jawab natural berdasarkan data dari hasil pencarian JSON
    ✅ Sebutkan detail spesifik tentang asisten (nama, posisi, kontak)
    ✅ Gunakan bahasa percakapan Indonesia yang ramah
    ✅ Berikan informasi praktis yang bermanfaat
    
    """
    
    expected_output = """Jawaban dalam bahasa Indonesia yang WAJIB:

    1. BACA hasil JSON dari task sebelumnya
    2. GUNAKAN data yang ditemukan untuk menjawab
    3. FORMAT jawaban natural seperti percakapan
    4. SEBUTKAN nama lengkap, kode asisten, posisi, dan kontak
    5. JELASKAN lokasi dan detail posisi dengan jelas
    
    JANGAN PERNAH jawab "tidak ditemukan" jika JSON menunjukkan status="success" dengan data results!
    """
    
    return Task(
        description=description,
        verbose=True,
        expected_output=expected_output,
        agent=agent,
        context=context or []
    )

def create_assistant_search_workflow_tasks(query_agent, answer_agent, user_query: str, context: list = None):
    """
    Create complete workflow tasks for assistant search with proper task dependencies
    """
    search_task = create_assistant_search_task(query_agent, user_query, context)
    answer_task = create_assistant_answer_task(answer_agent, user_query, context)
    
    answer_task.context = [search_task]
    
    return [search_task, answer_task]