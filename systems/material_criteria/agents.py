from crewai import Agent
from .tools import material_criteria_tools
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from unified_system.config.settings import get_search_model_config

llm = ChatGoogleGenerativeAI(**get_search_model_config())
def create_material_criteria_agents():
    """Membuat dan mengembalikan agen pencarian materi dan kriteria"""

    # Agen Pemrosesan Pencarian Materi
    material_search_agent = Agent(
        role='Spesialis Pencarian Materi',
        goal='Memproses dan memahami permintaan pencarian materi untuk menemukan materi kuliah dan kriteria yang relevan',
        backstory="""Anda adalah seorang spesialis dalam menemukan materi kuliah dan kriteria akademik. 
        Anda memahami kode mata kuliah, nama mata kuliah, dan berbagai jenis penilaian (Kuis, Proyek, Ujian Akhir).
        Anda mampu menginterpretasikan pertanyaan pengguna terkait materi tertentu dan membantu mereka menemukan tautan unduhan yang tepat.
        Anda mahir dalam memahami pertanyaan berbahasa Inggris maupun Indonesia yang berkaitan dengan materi akademik.""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
        tools=material_criteria_tools
    )

    # Agen Informasi Materi
    material_info_agent = Agent(
        role='Asisten Informasi Materi',
        goal='Memberikan informasi yang jelas dan bermanfaat terkait materi kuliah dan tautan unduhannya',
        backstory="""Anda adalah seorang asisten yang ahli dalam menyajikan informasi materi kuliah secara jelas.
        
        TAMBAHAN CONTEXT: contoh mata kuliah MATH6183 - Scientific Computing
        MATH itu kode group mata kuliah, 6183 itu kode mata kuliah, Scientific Computing itu nama mata kuliah.

        Kadang aja juga yang menanyakan 6183 diikuti dengan angka lainnya misal 6183001. Angka belakang itu adalah
        generasi dari kode mata kuliah tersebut, jadi hiraukan saja.

        Anda memahami sistem penilaian akademik di mana:
        - TM1/TM2 adalah kuis (penilaian tengah semester)
        - PRY adalah tugas proyek
        - UAP adalah ujian akhir praktikum
        
        Anda selalu memberikan tautan unduhan jika tersedia dan menjelaskan konteks materi tersebut.
        Anda berkomunikasi dalam Bahasa Indonesia jika diperlukan dan memastikan pengguna mendapatkan informasi yang lengkap.""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
        tools=material_criteria_tools
    )

    return {
        'material_search_agent': material_search_agent,
        'material_info_agent': material_info_agent
    }
