from crewai import Task
from unified_system.config.settings import get_answering_style, get_fallback


def create_correction_search_task(agent, user_query: str) -> Task:
    """Create task for Case Making / Correction Info Agent"""
    fallback_message = get_fallback(user_query)

    description = f"""Analyze the user query about correction or case making procedures and use the available tools to find the most relevant information.

    USER QUERY: "{user_query}"

     ✅ YANG HARUS ANDA LAKUKAN:

    1. 🔍 Identifikasi topik:
       - Apakah user menanyakan tentang *case making*?
       - Apakah user menanyakan tentang *koreksian*?

    2. 📚 Ambil informasi yang relevan dari knowledge base berikut:
       - **Langkah-langkah pengerjaan**
       - **Tips pengerjaan**
       - **Deadline pengerjaan**
       - **Siapa SubCo-nya dan di mana mencarinya**

    3. 💬 Format jawaban:
       - Jika pertanyaan menanyakan langkah-langkah → tampilkan langkah-langkah sebagai list
       - Jika menanyakan tips → tampilkan tips sebagai list
       - Jika menanyakan deadline → berikan kalimat penjelasan singkat
       - Jika menanyakan SubCo → tunjukkan cara melihat SubCo di website

    4. ❗ Jika pertanyaan tidak relevan dengan case making atau koreksian, kembalikan JSON dengan error dan pesan kesalahan yang sesuai.
   
    🔗 Informasi (Knowledge Base):
    {{
        "case_making": {{
            "langkah": [
                "Lihat jadwal case making pada website messier (perhatikan deadline)",
                "Hubungi SubCo untuk briefing cara case making",
                "Konsultasi ide soal dengan SubCo sebelum membuat soal",
                "Minta template soal dari SubCo lalu buat soal sesuai format",
                "Kumpulkan case ke SubCo (bisa melalui Line atau metode lain)",
                "Submit queue di 'My Queue' academic.slc.net atau apps-nya",
                "Ulangi step 5-6 sampai disetujui SubCo",
                "Submit ke messier via menu 'Job' > 'Case Making'",
                "Beritahu SubCo setelah submit untuk pengecekan akhir",
                "Selesai jika disetujui SubCo di messier"
            ],
            "tips": [
                "Lihat referensi soal di academic.slc.net atau apps-nya",
                "Hubungi SubCo jika bingung atau ada hal yang ambigu",
                "Buat reminder agar tidak lupa jadwal (misal sticky note)"
            ],
            "deadline": "Deadline case making setiap mata kuliah berbeda-beda. Lihat di messier pada menu 'Job' > 'Case Making'.",
            "subco": "Lihat SubCo di website academic.slc.net atau apps-nya melalui menu 'My Queue'."
        }},
        "koreksian": {{
            "langkah": [
                "Lihat jadwal koreksian di messier (perhatikan deadline)",
                "Hubungi SubCo untuk briefing dan minta template",
                "Download jawaban mahasiswa di messier > 'Marking' > 'Answer to be Graded'",
                "Mulai koreksi, tanya SubCo jika ada pertanyaan",
                "Kumpulkan ke SubCo (via Line atau lainnya)",
                "Submit queue di 'My Queue' academic.slc.net atau apps-nya",
                "Ulangi step 5-6 sampai disetujui SubCo",
                "Masukkan skor ke messier via template excel di 'Register Student Score'",
                "Beritahu SubCo untuk pengecekan terakhir",
                "Selesai jika disetujui SubCo di messier"
            ],
            "tips": [
                "Beri komentar detail dan jelas di template koreksi",
                "Tanya SubCo jika template ambigu",
                "Buat reminder agar tidak lupa jadwal"
            ],
            "deadline": "Deadline koreksian berbeda tiap mata kuliah. Cek di messier menu 'Marking'.",
            "subco": "Lihat SubCo di website academic.slc.net atau apps-nya melalui menu 'My Queue'."
        }}
    }}

    💡 Pastikan jawaban singkat, to the point, dan akurat. 

    Jika pertanyaan user ambigu atau tidak jelas, awali jawaban dengan fallback berikut:
    {fallback_message}, kemudian jelaskan lagi error sesuai dengan context.
    """

    expected_output = """
    Hasil pemrosesan berupa topik utama (case making / koreksian) dan informasi relevan yang dibutuhkan seperti langkah-langkah, tips, deadline, dan SubCo.
    """

    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
    )

def create_correction_answer_task(agent,search_results_context, user_query: str, context: list = None) -> Task:
    """Create task for answering case making / koreksian queries based on processed knowledge"""

    description = f"""🧠 TUGAS ANDA: Jawab pertanyaan user tentang *case making* atau *koreksian* dengan gaya bahasa alami, tidak seperti template, dan berdasarkan hasil pemrosesan dari agent sebelumnya.

    USER QUERY: "{user_query}"

    ✅ YANG HARUS ANDA LAKUKAN:

    1. 🎯 Identifikasi topik pertanyaan (case making atau koreksian) dan fokus informasi (langkah, tips, deadline, SubCo)
    
    2. 🔍 Gunakan hasil dari agent sebelumnya (berisi informasi relevan) untuk menyusun jawaban alami.
    
    3. 🗣️ GAYA JAWABAN:
       {get_answering_style()}

    4. 📋 FORMAT JAWABAN YANG DISARANKAN:

       a. Jika user bertanya tentang langkah-langkah:
          Contoh:
          "Kalau kamu ingin mulai koreksi, kamu bisa mulai dengan mengecek jadwalnya dulu di messier, lalu hubungi SubCo untuk dapat briefing dan template-nya..."

       b. Jika user menanyakan tips:
          Contoh:
          "Tipsnya sih yang paling penting adalah kasih komentar sejelas mungkin di template-nya, dan jangan ragu nanya SubCo kalau ada yang bingung."

       c. Jika user menanyakan deadline:
          Contoh:
          "Deadline case making beda-beda tiap mata kuliah, jadi paling aman kamu cek langsung di messier bagian Case Making ya."

       d. Jika menanyakan SubCo:
          Contoh:
          "Kamu bisa lihat siapa SubCo kamu di menu 'My Queue' di academic.slc.net atau lewat apps-nya juga bisa."

    5. ✨ Tambahan:
       - Jika ada daftar, tuliskan seperti orang menjelaskan, bukan copy list
       - Hindari gaya terlalu formal

      🔗 Gunakan informasi dari hasil pemrosesan sebelumnya (search_results_context) sebagai referensi utama.
    """

    expected_output = """
    Contoh jawaban:
    "Kalau kamu lagi ngerjain koreksian, pastikan kamu cek dulu jadwalnya di messier. Setelah itu, kamu bisa hubungi SubCo buat briefing dan minta template koreksiannya. Jangan lupa kasih komentar yang jelas di koreksian kamu biar SubCo nggak bingung pas review. Kalau semua udah OK, kamu submit deh ke messier."

    Atau:

    {
      "error": true,
      "message": "Pertanyaan tidak terkait dengan case making atau koreksian"
    }
    """

    return Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        context=context or []
    )

def create_correction_workflow_tasks(query_agent, answer_agent, user_query: str):
    """Create and connect the workflow tasks for correction and casemaking"""
    search_task = create_correction_search_task(query_agent, user_query)
    answer_task = create_correction_answer_task(answer_agent, user_query, context=[search_task])
    
    return [search_task, answer_task]