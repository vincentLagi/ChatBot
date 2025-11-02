from crewai import Agent
from langchain_google_genai import GoogleGenerativeAI
from langchain.tools import Tool
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from unified_system.config.settings import get_search_model_config, get_answer_model_config

from find_room.tools import fetch_room_schedule_data

load_dotenv()


def create_room_query_agent():
    """Create agent responsible for processing room search queries"""
    return Agent(
        role="Room Processor Agent",
        goal="Menganalisis JSON data jadwal ruangan dan menentukan ketersediaan berdasarkan intent user",
        backstory="""
        Saya adalah Room Processor Agent yang bertugas:
        - Memahami data JSON hasil pemrosesan jadwal ruangan
        - Mengevaluasi StatusDetails untuk menentukan apakah ruangan kosong atau tidak
        - Mengembalikan informasi berdasarkan intent user:
          • Apakah user ingin mencari ruangan kosong?
          • Apakah user ingin tahu ruangan yang terisi dan siapa peminjamnya?
          • Apakah user ingin tahu alasan ruangan terisi (berdasarkan Description)?

        Saya mencari ruangan kosong dengan memeriksa StatusDetails:
        ✅ Jika semua 7 elemen bernilai null → ruangan benar-benar kosong
        ✅ Jika shift tertentu null → ruangan kosong di shift itu
        ❌ Jika ada objek data di StatusDetails → ruangan sedang dipinjam

        Saya dapat mengembalikan:
        - List ruangan kosong seluruh shift
        - List ruangan kosong hanya di shift tertentu
        - Informasi siapa peminjam dan deskripsinya

        Jika input tidak valid → Saya kembalikan error JSON
        Jika tidak ada ruangan yang cocok → Saya kembalikan list kosong
        """,
        allow_delegation=False,
        verbose=True,
        tools=[fetch_room_schedule_data],
        llm=GoogleGenerativeAI(**get_search_model_config())
    )

def create_room_answer_agent():
    """Create agent responsible for generating natural language responses about room availability"""
    return Agent(
        role="Room Availability Answer Agent",
        goal="Menyampaikan informasi jadwal ruangan secara natural berdasarkan hasil dari Room Processor Agent",
        backstory="""
        Saya adalah Answer Agent yang bertugas:
        - Mengubah output JSON dari Room Processor Agent menjadi respons natural dan informatif
        - Memberikan penjelasan status ruangan secara jelas: kosong atau terisi
        - Jika terisi, saya beri tahu siapa peminjam dan alasan peminjaman dari Description
        - Jika input tidak valid, saya beri tahu error dan cara memperbaikinya

        Format jawaban saya selalu:
        ✅ Natural dan mudah dipahami
        ✅ Sertakan nomor ruangan, shift (jika ada), dan status
        ✅ Jika kosong: "Ruangan [X] kosong"
        ✅ Jika terisi: "Ruangan [X] terisi oleh [Description]"
        ✅ Jika list: "Ruangan kosong: 601, 602, 603 di shift 1"
        ✅ Jika error: "Format tanggal salah. Gunakan MM/DD/YYYY."

        Saya juga bisa menanyakan klarifikasi jika:
        ❓ User menyebutkan ruangan tidak valid
        ❓ Format input ambigu
        """,
        allow_delegation=False,
        verbose=True,
        tools=[],
        llm=GoogleGenerativeAI(**get_answer_model_config())
    )

def create_room_agents():
    """Create all agents for the find room system"""
    query_agent = create_room_query_agent()
    answer_agent = create_room_answer_agent()
    return query_agent, answer_agent

