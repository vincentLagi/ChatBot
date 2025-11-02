from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from .tools import (
    search_rules_uap_semantic,
)

# Import global model configurations
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from unified_system.config.settings import get_search_model_config, get_answer_model_config

# Search agent LLM (temperature: 0.1)
llm = ChatGoogleGenerativeAI(**get_search_model_config())

# def create_rules_query_agent():
#     """
#     Membuat agen yang bertanggung jawab untuk memproses pertanyaan terkait
#     Aturan & Prosedur UAP dengan menggunakan kata kunci yang tersedia.
#     """
#     return Agent(
#         role="Spesialis Pemrosesan Kuery Aturan & Prosedur UAP",
#         goal="Menganalisis kueri pengguna dan menemukan informasi yang paling relevan menggunakan pencarian dengan kata kunci dari database.",
#         backstory="""Anda adalah agen yang bertugas memproses kueri untuk Aturan & Prosedur UAP. Anda menggunakan keyword yang telah diembed untuk membantu menemukan informasi secara cepat dan efisien.""",
#         tools=[search_rules_uap_semantic],
#         llm=llm,
#         verbose=True,
#         allow_delegation=False,
#         max_iter=3,
#         memory=True
#     )

def create_rules_answer_agent():
    # Answer agent LLM (temperature: 0.7)
    answer_llm = ChatGoogleGenerativeAI(**get_answer_model_config())
    
    return Agent(
        role="Asisten Bot Aturan & Prosedur UAP / Assignment",
        goal="Menghasilkan jawaban natural dan percakapan tentang Aturan & Prosedur UAP berdasarkan jawaban dari agent Rules & Procedure UAP Query Processing Specialist",
        backstory="""Anda adalah bot asisten yang ramah untuk Aturan & Prosedur UAP (Ujian Akhir Praktikum) / Assignment. Yang akan menanyakan anda adalah assisten yang ingin mengetahui aturan dan prosedur UAP / Assignment.

        TM = Assignment
        
        Keahlian Anda meliputi:
        - Mengubah hasil pencarian database menjadi jawaban natural dan percakapan dalam bahasa Indonesia
        - Menjawab pertanyaan seperti asisten bot yang membantu, bukan dokumen formal
        - Menyediakan informasi praktis berdasarkan aturan yang ditemukan di database
        - Berbicara dengan bahasa alami dan santai sambil tetap informatif

        Gaya komunikasi Anda:
        - Informasi praktis dan dapat ditindaklanjuti
        - Nada yang santai namun profesional
        - Tidak menggunakan template formal atau format terstruktur
        """,
        tools=[],
        llm=answer_llm,
        verbose=True,
        allow_delegation=False,
        max_iter=2,
        memory=True
    )

def create_rules_uap_agents():
    # query_agent = create_rules_query_agent()
    answer_agent = create_rules_answer_agent()
    return answer_agent

# def get_rules_uap_query_agent():
#     """Backward compatibility function"""
#     return create_rules_query_agent()

def get_rules_uap_answer_agent():
    return create_rules_answer_agent()