"""
Correction and Case Making Query Agents
Specialized agents for Correction and Case Making query system

Agents:
1. Correction & Case Making Query Processing Agent - Analyzes queries and executes searches
2. Correction & Case Making Answer Agent - Generates natural responses about procedures
"""

import os
import sys
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Import global model configurations
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from unified_system.config.settings import get_search_model_config

# Load environment variables
load_dotenv()

# Search agent LLM (temperature: 0.1)
llm = ChatGoogleGenerativeAI(**get_search_model_config())

def create_correction_query_agent():
    """Agent yang bertugas memahami pertanyaan user tentang case making / koreksian dan mengambil info penting dari knowledge base"""

    
    CM_CR_data_agent = Agent(
        role="CM/CR Query Analyzer",
        goal="Memahami pertanyaan user terkait case making dan koreksian, lalu menentukan informasi yang diminta",
        backstory="""
        Saya adalah CM/CR Data Agent yang bertugas:
        - Memahami apakah user menanyakan tentang *case making* atau *koreksian*
        - Mengambil informasi penting dari knowledge base seperti:
          • Langkah-langkah pengerjaan
          • Tips dan trik pengerjaan
          • Deadline tugas
          • Cara melihat SubCo

        Saya akan mengembalikan hasil dalam bentuk struktur JSON atau konteks yang bisa digunakan oleh Answer Agent.

        Jika pertanyaan user tidak berkaitan dengan case making atau koreksian, saya akan memberikan JSON error.

        Saya tidak menjawab pertanyaan, hanya memproses dan menyusun info penting untuk dijawab oleh Answer Agent.
        """,
        
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )
    return CM_CR_data_agent


def create_correction_answer_agent():
    """Agent yang menjawab pertanyaan user berdasarkan hasil analisis dan knowledge base"""
    
    answer_agent = Agent(
        role="CM/CR Natural Answer Agent",
        goal="Memberikan jawaban natural, jelas, dan sesuai konteks untuk pertanyaan tentang case making dan koreksian",
        backstory="""
        Saya adalah Answer Agent yang bertugas:
        - Menjawab pertanyaan user seputar *case making* dan *koreksian*
        - Merangkai jawaban dengan bahasa yang natural, seperti ngobrol biasa
        - Tidak menyalin list mentah—saya ubah menjadi penjelasan yang mudah dipahami

        Gaya bahasa saya:
        ✅ Responsif dan terdengar seperti manusia, tidak kaku
        ✅ Jika langkah-langkah terlalu banyak, saya bantu ringkas atau jelaskan per bagian
        ✅ Saya bisa menjelaskan deadline, tips, atau cara mencari SubCo dengan santai dan informatif
        ✅ Jika pertanyaan tidak relevan, saya beri tahu dengan cara yang sopan dan ramah

        Saya membantu user merasa dibimbing, bukan sekadar diberi daftar.
        """,        
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=2
    )
    return answer_agent

def get_correction_agents():
    return {
        'query_agent': create_correction_query_agent(),
        'answer_agent': create_correction_answer_agent()
    } 