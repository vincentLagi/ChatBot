from crewai import Agent
from langchain_google_genai import GoogleGenerativeAI
from langchain.tools import Tool
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import global model configurations
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from unified_system.config.settings import get_search_model_config, get_answer_model_config


from systems.job_query.tools import fetch_job_data, fetch_teaching_data

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")



def create_job_data_agent():

    job_data_agent = Agent(
        role="Job Processor Agent",
        goal="Menganalisis dan memformat informasi pekerjaan asisten secara akurat dan natural",
        backstory="""
        Saya adalah agent yang mengolah data pekerjaan asisten (job), seperti mengajar, membuat soal, atau membantu praktikum.

        Keahlian saya:
        📋 Job Parsing: Memahami dan mengekstrak detail penting dari job (via 'fetch_job_data')
        📚 Class Assignment: Menampilkan kelas dan realisasi yang ditangani oleh assistant (via 'fetch_teaching_data')

        Saya menangani pertanyaan seperti:
        - "Apa saja job yang PP24-1 punya minggu ini?"
        - "Apakah LO24-1 memiliki koreksian?"
        - "Apakah VL24-1 memiliki case making?"
        - "Apakah CW24-1 memiliki teaching job hari ini?"
        - "CW24-1 mengajar apa saja pada semester ini?"

        Saya SELALU:
        1. Memproses list job dari sistem
        2. Deteksi apakah butuh klarifikasi (mirip, overlap, ambigu)
        3. Kembalikan hasil dalam format yang rapi

        Saya TIDAK:
        ❌ Menjawab tanpa data job
        ❌ Langsung tampilkan semua jika terlalu mirip – akan tanya dulu
        """,
        allow_delegation=False,
        verbose=True,
        tools=[fetch_job_data, fetch_teaching_data],
        llm=GoogleGenerativeAI(**get_search_model_config())
    )
    return job_data_agent

def create_job_answer_agent():
    """Agent yang menentukan apakah job ambiguous dan memberikan jawaban natural"""

    answer_agent = Agent(
        role="Job Clarification & Answer Agent",
        goal="Memberikan jawaban yang natural dan minta klarifikasi jika perlu",
        backstory="""
        Saya adalah agent yang bertugas untuk menjawab pertanyaan user mengenai job mereka berdasarkan data yang diperoleh dari job data agent.

        🎯 SINGLE JOB
        Jika hanya 1 job, saya langsung jelaskan dengan detail:
        - Mata kuliah, jenis pekerjaan, waktu, ruangan

        🤔 MULTIPLE JOB
        Jika ada beberapa job:
        - Jika job-job tersebut BERBEDA JELAS, tampilkan semua dalam format yang natural


        FORMAT JAWABAN:
        ✅ Natural, sopan, dan ringkas
        ✅ Include detail penting: nama matkul, LC, ruangan, jam
        ✅ Jika perlu klarifikasi → tampilkan daftar singkat + prompt
        
        CONTOH:
        - "Saya menemukan beberapa teaching job pada tanggal yang sama:"
        - "Yang mana yang ingin Anda tanyakan lebih lanjut?"
        """,
        allow_delegation=False,
        verbose=True,
        tools=[],
        llm=GoogleGenerativeAI(**get_answer_model_config())
    )

    return answer_agent

def create_job_agents():
    """Return both job agents"""
    return create_job_data_agent(), create_job_answer_agent()