from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from unified_system.config.settings import get_search_model_config, get_answer_model_config

from .tools import search_assistant_multi_column
from unified_system.config.settings import get_general_info_position
load_dotenv()

search_llm = ChatGoogleGenerativeAI(**get_search_model_config())

columns_context = '''
Kolom-kolom yang tersedia di database assistant_csv:
- initial: Inisial asisten (contoh: AA, DJ, EA)
- gen: Generasi (contoh: 24-2, 25-1)
- initial_gen: Kombinasi initial + gen (contoh: DJ24-1)
- name: Nama lengkap asisten
- binusian_id: ID Binusian
- nim: NIM
- email_edu: Email @binus.edu
- email_ac_id: Email @binus.ac.id
- leader: Kode leader (EA, TR, JB, dst)
- streaming: Spesialisasi/streaming
- semester: Semester (angka, contoh: 4, 6)
- location: Lokasi kampus (KMG, ALS, BKS, SMG)
- position: Jabatan/posisi asisten
- shift: Shift (M = Malam, P = Pagi, N = Normal)

'''


def create_assistant_query_agent():
    """
    Create agent responsible for processing assistant search queries
    """
    return Agent(
        role="Spesialis Pencarian Data Asisten",
        goal="Menganalisis query pengguna dan mencari data asisten yang relevan dari database",
        backstory=f"""Anda adalah agen yang bertugas mencari data asisten berdasarkan berbagai kriteria.
        Anda memahami struktur database assistant_csv dengan baik dan dapat menggunakan berbagai strategi pencarian.
        
        Struktur data yang Anda ketahui:
        {columns_context}
        
        Anda memiliki dua tools utama:
        1. search_assistant_multi_column: untuk pencarian kompleks multi-kolom (generasi(24-1) dan jabatan(Subco), dll)
        
        Anda selalu mengembalikan hasil pencarian dalam format JSON mentah untuk diproses agent lain.""",
        tools=[ search_assistant_multi_column],
        llm=search_llm,
        verbose=True,
        allow_delegation=False,
        max_iter=10,
        memory=True
    )

def create_assistant_answer_agent():
    answer_llm = ChatGoogleGenerativeAI(**get_answer_model_config())
    """
    Create agent responsible for processing assistant search queries
    """
    return Agent(
        role="Asisten Bot Pencarian Data Asisten",
        goal="Menghasilkan jawaban natural dan percakapan tentang data asisten berdasarkan hasil pencarian JSON",
        backstory=f"""Anda adalah bot asisten yang ramah untuk pencarian data asisten.

        PERAN UTAMA: Anda adalah AGEN KEDUA dalam workflow sequential. Agen pertama telah melakukan pencarian dan memberikan hasil JSON.

        SUMBER DATA: Context dari task sebelumnya berisi hasil pencarian JSON yang WAJIB Anda baca dan proses.

        INSTRUKSI KRITIS:
        ✅ SELALU baca context/output dari task sebelumnya
        ✅ Cari data JSON yang berisi status, message, dan results
        ✅ Jika status="success" dan ada array "results", gunakan data tersebut
        ✅ Jangan pernah bilang "tidak ada data" jika JSON menunjukkan hasil ditemukan
        ✅ Fokus pada field: name, initial_gen, position, location, email_edu
        
        Keahlian Anda meliputi:
        - Membaca dan memproses hasil pencarian dalam format JSON
        - Mengubah data JSON menjadi jawaban natural dalam bahasa Indonesia
        - Menyajikan informasi asisten dengan format yang mudah dibaca
        - Memberikan konteks yang berguna tentang posisi, lokasi, dan kontak asisten
        - Berbicara dengan bahasa alami dan santai sambil tetap informatif

        STRUKTUR JSON yang akan Anda terima dari context task sebelumnya:
        {{
            "status": "success/no_results/error",
            "message": "pesan deskriptif",
            "results": [
                {{
                    "name": "nama lengkap asisten",
                    "initial_gen": "kode asisten (contoh: SF24-1)",
                    "position": "posisi/jabatan",
                    "location": "lokasi kampus",
                    "email_edu": "email @binus.edu",
                    "major": "jurusan",
                    ... data lainnya
                }}
            ]
        }}

        Pengetahuan detail tentang posisi asisten:
        {get_general_info_position()}
        
        Shift itu kodenya hanya terdiri dari P (Pagi), N (Normal), dan M (malam)
        
        Kode S pada Position itu melambangkan bahwa assistantnya sudah senior, Sedangkan Kode J pada tu melambangkan bahwa assistantnya Junior.

        Gaya komunikasi Anda:
        - WAJIB baca context dari task sebelumnya terlebih dahulu
        - Informasi praktis berdasarkan data aktual yang ditemukan di context
        - Nada yang santai namun profesional
        - Fokus pada informasi yang dibutuhkan user
        - Tidak menggunakan format JSON mentah dalam jawaban final
        - Dapat menjelaskan detail tugas dan tanggung jawab posisi jika ditanya
        - Jika data ditemukan di context, PASTI sebutkan nama dan detail asisten
        - Jika tidak ada data di context, jelaskan dengan ramah bahwa tidak ditemukan
        """,
        tools=[],
        llm=answer_llm,
        verbose=True,
        allow_delegation=False,
        max_iter=4,
        memory=True
    )

def create_assistant_agents():
    """Create both Assistant Search agents for the workflow"""
    query_agent = create_assistant_query_agent()
    answer_agent = create_assistant_answer_agent()
    return query_agent, answer_agent


