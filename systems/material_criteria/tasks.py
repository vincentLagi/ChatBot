#!/usr/bin/env python3
"""
Material and Criteria Search Tasks
CrewAI tasks for material and criteria search workflow
"""

from crewai import Task
from unified_system.config.settings import get_fallback, get_answering_style


def create_material_search_task(agent, user_query: str) -> Task:
    """Create a task for searching course materials and criteria."""
    fallback_message = get_fallback(user_query)

    return Task(
        description=f"""
        Analisis pertanyaan pengguna berikut: "{user_query}"
        
        Tugas Anda:
        1. Pahami apa yang dicari oleh pengguna (materi mata kuliah, kriteria penilaian, atau tautan unduhan)
        2. Identifikasi kode mata kuliah, nama mata kuliah, atau jenis penilaian yang disebutkan
        3. Tentukan apakah pengguna ingin:
           - Jenis materi tertentu (TM1, TM2, PRY, UAP)
           - Seluruh materi untuk satu mata kuliah
           - Materi yang sesuai dengan kata kunci pencarian
        4. Gunakan tools yang tersedia untuk mencari materi yang sesuai
        5. Jika jenis materi tidak disebutkan secara spesifik, berikan semua materi yang tersedia untuk mata kuliah tersebut
        
        Gunakan tools pencarian yang sesuai berdasarkan query:
        - Gunakan `search_course_materials` untuk pencarian umum
        - Gunakan `get_all_course_materials` jika pengguna ingin semua materi dari satu mata kuliah
        - Gunakan `search_by_type` jika pengguna menyebutkan jenis penilaian tertentu
        
        Berikan hasil pencarian yang lengkap dengan semua materi relevan dan tautan unduhannya.
        
        Jika pertanyaan user ambigu atau tidak jelas, awali jawaban dengan fallback berikut:
        {fallback_message}, kemudian jelaskan lagi error sesuai dengan context.
        """,
        agent=agent,
        expected_output="Raw search results (course code, name, material type, and download URLs) with no formatting"

    )

def create_material_answer_task(agent, user_query: str, context: list = None) -> Task:
    """Create a task for providing information about course materials."""
    return Task(
        description=f"""
        Berdasarkan hasil pencarian dari task sebelumnya, berikan respons yang jelas dan bermanfaat mengenai materi mata kuliah yang disebutkan
        pada {user_query}.

        TAMBAHAN CONTEXT: contoh mata kuliah MATH6183 - Scientific Computing
        MATH itu kode group mata kuliah, 6183 itu kode mata kuliah, Scientific Computing itu nama mata kuliah.

        Kadang aja juga yang menanyakan 6183 diikuti dengan angka lainnya misal 6183001. Angka belakang itu adalah
        generasi dari kode mata kuliah tersebut, jadi hiraukan saja.


        
        Tugas Anda:
        1. Tinjau hasil pencarian (Abaikan nilai similarity atau simalirty score, fokus pada konten jadi ambil kode matkuliah atau nama mata kuliah yang sama persis
        soalnya hasil dari search_course_materials itu sudah diurutkan berdasarkan similarity score sehingga ada
        matkul yang tidak relevan tapi ada di hasil pencarian tapi scorenya juga tinggi)
        2. Format informasi agar mudah dipahami oleh pengguna 
         - untuk link download, gunakan format:(URL)
        3. Jelaskan fungsi dari masing-masing jenis materi (jika relevan):
           - TM1/TM2: Materi kuis dan kriteria penilaian
           - PRY: Tugas proyek dan panduan pengerjaan
           - UAP: Materi ujian akhir praktikum
        4. Berikan tautan unduhan dengan jelas
        5. Tambahkan konteks atau saran tambahan jika diperlukan
        6. Gunakan Bahasa Indonesia jika sesuai
        
        Pastikan untuk:
        - Menyajikan informasi dengan jelas dan terstruktur
        - Menyertakan semua tautan unduhan yang relevan
        - Menjelaskan konteks dari setiap jenis penilaian
        - Memberikan informasi tambahan yang berguna jika tersedia
        
        Jika tidak ditemukan materi, berikan saran cara pencarian lain atau referensi ke mata kuliah alternatif.

        Gaya Jawaban: 
        {get_answering_style()}
        """,
        agent=agent,
        expected_output="Clear, organized response with material information and download links, formatted for easy understanding",
        context=context or []
    )

def create_material_criteria_workflow_tasks(query_agent, answer_agent, user_query: str):
    """Create and connect the workflow tasks for material and criteria search."""
    search_task = create_material_search_task(query_agent, user_query)
    answer_task = create_material_answer_task(answer_agent, user_query, context=[search_task])
    
    return [search_task, answer_task]