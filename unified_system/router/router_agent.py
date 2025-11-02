
from typing import Dict, List, Optional
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_google_genai import GoogleGenerativeAI

from ..config.settings import get_router_model_config, get_additional_information, get_general_info_position

load_dotenv()



class IntelligentRouter:

    def __init__(self):

        self.router_agent = Agent(
            role="Router Agent Specialist",
            goal="Memahami pertanyaan user secara natural dan menentukan sistem yang tepat untuk menjawabnya",
            backstory=f"""
            Saya adalah AI specialist yang ahli dalam memahami konteks pertanyaan akademik di Software Laboratory Center (SLC)dan memutuskan sistem mana yang paling tepat untuk menjawabnya.
            
            🎯 SISTEM YANG TERSEDIA:
            
            0. **general_response** - RESPONS UMUM (greetings, general info, simple questions)
               📋 Konten: Sapa user, jelaskan tentang SLC, academic system, umum tentang lab
               🔍 Keywords: halo, hai, hello, selamat, apa itu, penjelasan umum, terima kasih, thanks
               ✅ Langsung jawab: greeting, penjelasan SLC/academic, pertanyaan sederhana
               ❌ Bukan: pertanyaan spesifik yang butuh data dari sistem lain
            
            1. **rules_uap** - Aturan UJIAN (exam rules, violations, supervision, assignment)
               📋 Konten: Prosedur ujian, pengawasan ujian, sanksi menyontek, kelengkapan ujian, TheoryExam system
               🔍 Keywords: ujian, exam, mengawas ujian, menyontek, keterlambatan ujian, eligible, theoryexam.slc.net, finalize theoryexam, submit backup FTP, exam eligibility, binusian card, Assignment
               ❌ Bukan: mengajar, praktikum, lab setup, messier attendance, ruman
            Note: Assignemnt disini konteksnya bukan tugas namun seperti quiz atau ujian.
               

            2. **assistant_search** - Database ASISTEN (names, contacts, locations, majors)
               📋 Konten: Data asisten (nama, email, major, lokasi kampus, shift, leader)
               🔍 Keywords: asisten, nama, kontak, email, ALS/KMG/SMG, leader, major TI/SI/MTI
               ❌ Bukan: jadwal kerja, schedule, job availability
            
            3. **rules_mengajar** - Prosedur MENGAJAR/PRAKTIKUM (lab procedures, room setup)
               📋 Konten: Persiapan mengajar, setup ruangan/komputer, attendance log, Ruman automation, Messier attendance
               🔍 Keywords: mengajar, praktikum, lab, setup, ruman, clear drive D, clear FTP, messier attendance, login messier, scan barcode, kunci ruangan, slc.net, poster NAR
               ❌ Bukan: ujian, exam violations, menyontek, messier marking/queue
            
            4. **correction_casemaking** - Proses KOREKSI (marking, grading, queue)
               📋 Konten: Workflow koreksi, template, deadline, SubCo coordination, Messier marking system
               🔍 Keywords: cara koreksi, langkah koreksian, template, queue, SubCo briefing, SubCo template, deadline koreksian, score, workflow, messier marking, download dari messier, academic.slc.net, My Queue
               ❌ Bukan: jadwal/availability koreksian, ada koreksian hari ini, messier attendance, ruman setup
            
            5. **job_query** - JADWAL KERJA asisten (schedules, availability, shifts)
               📋 Konten: Jadwal mengajar, job availability, work schedules, koreksian availability
               🔍 Keywords: jadwal, schedule, job, shift, availability, hari ini, minggu ini, ada [job] tidak, [kode asisten] hari ini
               ❌ Bukan: data personal asisten, kontak, cara/template/prosedur
            
            6. **material_criteria** - MATERIAL KULIAH (course materials, download links)
               📋 Konten: Course codes, material downloads, SharePoint links, TM1/UAP/PRY materials
               🔍 Keywords: download, material, COMP6xxx, SharePoint, TM1, UAP, PRY, criteria
               ❌ Bukan: proses koreksi, marking
            
            7. **find_room** - RUANGAN (room availability, schedules, locations)
               📋 Konten: Room schedules, availability, locations
               🔍 Keywords: ruangan, room, availability, schedule ruangan, lantai, gedung
               ❌ Bukan: data asisten, campus location dalam konteks asisten

            🧠 KEAHLIAN SAYA:
            - Memahami konteks dan intent dari pertanyaan user
            - Menganalisis kata kunci dan makna semantik
            - Mempertimbangkan ambiguitas dan multiple possibilities
            - Memberikan confidence score yang akurat
            - Handling edge cases dan pertanyaan kompleks

            📋 DECISION PROCESS:
            1. Analyze pertanyaan user dengan teliti
            2. Cek apakah pertanyaan bisa dijawab langsung (general_response)
            3. Identifikasi kata kunci dan konteks utama untuk sistem spesifik
            4. Pertimbangkan kemungkinan sistem yang relevan
            5. Evaluasi confidence level (high/medium/low/ambiguous)
            6. Return structured decision dengan reasoning

            ✅ PRINSIP ROUTING:
            - Jika greeting/general question → return "general_response" dengan high confidence
            - Jika jelas mengarah ke 1 sistem → return sistem tersebut dengan high confidence
            - Jika ada 2-3 kemungkinan tapi 1 dominan → return yang dominan dengan medium confidence
            - Jika benar-benar ambigu → return "ambiguous" dengan saran sistem
            - Selalu berikan reasoning yang jelas untuk decision

            🎯 GENERAL RESPONSE GUIDELINES:
            - Sapa user dengan ramah dan profesional
            - Jelaskan tentang Software Laboratory Center (SLC) jika ditanya
            - Berikan overview sistem academic yang tersedia
            - Jawab pertanyaan umum tentang fungsi lab dan praktikum
            - Arahkan user untuk pertanyaan lebih spesifik jika perlu
            
            🎯 KONTEKS KHUSUS & AMBIGUITY HANDLING:
            
            📝 EXAM vs TEACHING Context:
            - "mengawas ujian" / "pengawasan ujian" / "saat ujian" → rules_uap
            - "mengawas praktikum" / "mengawas lab" / "mengawas kelas" → rules_mengajar
            - "mengawas" ambiguous → tanya konteks atau default ke rules_uap
            
            ⏰ TIMING Context:
            - "sebelum ujian" / "selama ujian" / "sesudah ujian" → rules_uap
            - "sebelum mengajar" / "sesudah mengajar" → rules_mengajar
            - "persiapan mengawas" (without context) → rules_uap (exam supervision)
            
            🔍 ASISTEN vs JOB Context:
            - "siapa asisten X" / "kontak asisten" / "asisten di KMG" → assistant_search
            - "jadwal asisten X" / "shift hari ini" / "job availability" → job_query
            - "[kode asisten] ada [aktivitas] hari ini?" → job_query (availability)
            - "[kode asisten] hari ini ada [job]?" → job_query (schedule check)
            
            📚 MATERIAL vs CORRECTION Context:
            - "download COMP6xxx" / "material TM1" / "SharePoint link" → material_criteria
            - "cara koreksi" / "template koreksian" / "deadline koreksi" → correction_casemaking
            
            📅 JOB SCHEDULE vs CORRECTION PROCEDURE:
            - "ada koreksian hari ini?" / "[asisten] hari ini ada koreksian?" → job_query (availability)
            - "cara koreksian" / "langkah koreksian" / "template koreksian" → correction_casemaking (procedure)
            
            🎯 VIOLATION Context:
            - "menyontek" / "terlambat ujian" / "tidak eligible" → rules_uap
            - "telat mengajar" / "berhalangan mengajar" → rules_mengajar
            
            💻 TECHNICAL Context & Platform-Specific:
            - "theoryexam" / "finalize" / "submit FTP ujian" → rules_uap
            - "messier attendance" / "session log" / "ruman setup" → rules_mengajar
            
            🖥️ PLATFORM & TOOL Context:
            - "messier marking" / "messier queue" / "download dari messier" → correction_casemaking
            - "messier attendance" / "login messier" / "scan barcode messier" → rules_mengajar  
            - "ruman setup" / "ruman clear" / "drive D" / "clear FTP" → rules_mengajar
            - "SubCo briefing" / "template dari SubCo" / "kumpul ke SubCo" → correction_casemaking
            - "academic.slc.net queue" / "My Queue" → correction_casemaking
            - "theoryexam.slc.net" / "finalize theoryexam" → rules_uap


            """,
            allow_delegation=False,
            verbose=True,
            tools=[],
            llm=GoogleGenerativeAI(**get_router_model_config())
        )
        
        print("🧠 Intelligent Router Agent initialized successfully!")
        
        self.general_agent = Agent(
            role="General Response Assistant",
            goal="Memberikan respons umum dan ramah untuk pertanyaan dasar tentang SLC dan academic system",
            backstory=f"""
            Saya adalah asisten AI yang ramah dan informatif untuk Software Laboratory Center (SLC).
            {get_general_info_position()}
            {get_additional_information()}
            
            🎯 TUGAS SAYA:
            - Menyapa user dengan ramah dan profesional
            - Memberikan informasi umum tentang SLC dan sistem academic
            - Menjelaskan fungsi dasar laboratorium dan praktikum
            - Memberikan overview sistem yang tersedia
            - Membantu user mengarahkan pertanyaan mereka dengan lebih spesifik
            
            💬 GAYA KOMUNIKASI:
            - Ramah, informatif, dan profesional
            - Menggunakan bahasa Indonesia yang natural
            - Memberikan konteks yang berguna
            - Tidak terlalu teknis untuk penjelasan umum
            - Siap membantu user dengan pertanyaan lanjutan
            """,
            allow_delegation=False,
            verbose=False,
            tools=[],
            llm=GoogleGenerativeAI(**get_router_model_config())
        )
    
    def classify_intent(self, query: str) -> Dict:
        """
        🎯 Main classification method using AI reasoning
        
        Args:
            query: User query string
            
        Returns:
            Dict with classification result including system, confidence, and reasoning
        """
        
        print(f"🔍 Analyzing intent with AI: '{query}'")
        
        routing_task = Task(
            description=f"""
            🎯 TUGAS ROUTING INTELLIGENCE:
            
            Analisis pertanyaan user dan tentukan cara terbaik untuk memberikan respons:

            USER QUERY: "{query}"

            📋 OPSI ROUTING:
            
            **OPTION 1: GENERAL_RESPONSE** 
            Gunakan jika pertanyaan adalah:
            - Greeting (halo, hai, selamat pagi, dll)
            - Pertanyaan umum tentang SLC/academic system
            - Terima kasih atau ucapan courtesy
            - Pertanyaan sederhana yang bisa dijawab tanpa data spesifik
            
            **OPTION 2: SPECIFIC SYSTEM**
            Gunakan jika pertanyaan membutuhkan:
            - Data spesifik dari database (asisten, jadwal, ruangan)
            - Prosedur/aturan detail (ujian, mengajar, koreksi)
            - Material/dokumen tertentu
            - Informasi yang perlu pencarian di sistem khusus

            🔍 **ANALISIS YANG DIPERLUKAN:**
            1. **Intent Detection**: Apakah ini greeting, general info, atau specific query?
            2. **Keyword Analysis**: Kata kunci apa yang terdeteksi?
            3. **Context Understanding**: Konteks apa yang dibutuhkan untuk menjawab?
            4. **System Selection**: Sistem mana yang paling tepat (termasuk general_response)?
            5. **Confidence Assessment**: Seberapa yakin dengan pilihan ini?

            📤 **OUTPUT FORMAT:**
            Berikan JSON dengan format:
            {{
                "system": "general_response/rules_uap/assistant_search/rules_mengajar/correction_casemaking/job_query/material_criteria/find_room/ambiguous",
                "confidence": "high/medium/low/ambiguous",
                "reasoning": "Penjelasan singkat mengapa memilih routing ini",
                "alternative_systems": ["sistem_alternatif_jika_ada"],
                "keywords_detected": ["kata_kunci_utama"],
                "intent_type": "greeting/general_info/specific_query/unclear"
            }}

            🎯 **CONTOH ROUTING:**
            - "Halo" → general_response (greeting)
            - "Apa itu SLC?" → general_response (general_info)  
            - "Siapa DJ24-1?" → assistant_search (specific_query)
            - "Cara mengawas ujian?" → rules_uap (specific_query)
            """,
            expected_output="JSON dengan sistem routing, confidence, reasoning, alternatives, keywords, dan intent type",
            agent=self.router_agent
        )
        
        crew = Crew(
            agents=[self.router_agent],
            tasks=[routing_task],
            process='sequential',
            verbose=False
        )
        
        try:
            result = crew.kickoff()
            
            import json
            import re
            
            result_str = str(result)
            json_match = re.search(r'\{.*\}', result_str, re.DOTALL)
            
            if json_match:
                json_str = json_match.group()
                try:
                    parsed_result = json.loads(json_str)
                    
                    classification_result = {
                        'system': parsed_result.get('system', 'ambiguous'),
                        'confidence': self._map_confidence(parsed_result.get('confidence', 'low')),
                        'classification_type': parsed_result.get('confidence', 'low'),
                        'reasoning': parsed_result.get('reasoning', 'AI analysis completed'),
                        'alternative_systems': parsed_result.get('alternative_systems', []),
                        'keywords_detected': parsed_result.get('keywords_detected', []),
                        'intent_type': parsed_result.get('intent_type', 'unclear'),
                        'query': query,
                        'used_agent': True
                    }
                    
                    print(f"✅ AI Classification: {classification_result['system']} ({classification_result['confidence']:.3f})")
                    print(f"💭 Reasoning: {classification_result['reasoning']}")
                    
                    return classification_result
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing error: {e}")
                    return self._fallback_classification(query)
            else:
                print("❌ No JSON found in agent response")
                return self._fallback_classification(query)
                
        except Exception as e:
            print(f"❌ Router agent error: {e}")
            return self._fallback_classification(query)
    
    def generate_general_response(self, query: str) -> str:
        """
        🎯 Generate general response for common queries like greetings or basic info
        
        Args:
            query: User query string
            
        Returns:
            String with appropriate general response
        """
        
        print(f"💬 Generating general response for: '{query}'")
        
        general_task = Task(
            description=f"""
            User bertanya: "{query}"
            
            🎯 TUGAS ANDA:
            Berikan respons yang ramah dan informatif sesuai dengan pertanyaan user.
            
            📋 JENIS RESPONS:
            1. **Greeting**: Jika user menyapa (halo, hai, hello, selamat pagi/siang/malam)
               → Sapa balik dengan ramah dan perkenalkan diri sebagai AI assistant SLC
            
            2. **Penjelasan SLC/Academic**: Jika user bertanya tentang apa itu SLC, academic system, dll
               → Jelaskan Software Laboratory Center, fungsi lab, sistem academic yang tersedia
            
            3. **Terima kasih**: Jika user berterima kasih
               → Respons dengan senang hati membantu dan siap untuk pertanyaan lanjutan
            
            4. **Pertanyaan umum lainnya**: 
               → Jawab sebaik mungkin dengan informasi yang tersedia, arahkan ke sistem spesifik jika perlu
            
            💬 GAYA RESPONS:
            - Ramah dan profesional
            - Bahasa Indonesia yang natural
            - Informatif tapi tidak bertele-tele
            - Berikan konteks yang berguna
            - Tawarkan bantuan lebih lanjut jika perlu
            
            ⚠️ HINDARI:
            - Informasi teknis yang terlalu detail
            - Data spesifik yang perlu sistem lain
            - Respons yang terlalu panjang
            
            Berikan respons langsung dalam bahasa Indonesia tanpa format JSON atau markup.
            """,
            expected_output="Respons natural dalam bahasa Indonesia yang sesuai dengan pertanyaan user",
            agent=self.general_agent
        )
        
        crew = Crew(
            agents=[self.general_agent],
            tasks=[general_task],
            process='sequential',
            verbose=False
        )
        
        try:
            result = crew.kickoff()
            response = str(result).strip()
            
            print(f"✅ General response generated successfully")
            return response
            
        except Exception as e:
            print(f"❌ General response error: {e}")
            return self._fallback_general_response(query)
    
    def _fallback_general_response(self, query: str) -> str:
        """Fallback general response if agent fails"""
        
        query_lower = query.lower()
        
        if any(greeting in query_lower for greeting in ['halo', 'hai', 'hello', 'selamat']):
            return """Halo! 👋 
            
Saya adalah AI Assistant untuk Software Laboratory Center (SLC). Saya siap membantu Anda dengan berbagai informasi tentang:

🔹 Data asisten laboratorium
🔹 Jadwal dan ketersediaan ruangan  
🔹 Aturan ujian dan praktikum
🔹 Material kuliah dan kriteria
🔹 Proses koreksi dan grading
🔹 Dan informasi akademik lainnya

Silakan tanyakan apa yang Anda butuhkan! 😊"""

        elif any(word in query_lower for word in ['apa itu', 'tentang', 'slc', 'academic']):
            return """Software Laboratory Center (SLC) adalah pusat laboratorium komputer yang menyediakan fasilitas praktikum untuk mahasiswa.

🏢 **Fungsi SLC:**
- Mengelola laboratorium komputer di berbagai kampus
- Menyediakan asisten untuk praktikum dan ujian
- Mengatur jadwal dan ketersediaan ruangan
- Mengelola sistem academic dan grading

📍 **Lokasi SLC:**
- KMG (Kemanggisan)
- ALS (Alam Sutera) 
- BKS (Bekasi)
- SMG (Semarang)
- BDG (Bandung)

Apakah ada yang ingin Anda ketahui lebih lanjut tentang SLC?"""

        elif any(word in query_lower for word in ['terima kasih', 'thanks', 'thank you']):
            return """Sama-sama! 😊 Senang bisa membantu Anda.

Jika ada pertanyaan lain tentang SLC, asisten, jadwal, atau informasi akademik lainnya, jangan ragu untuk bertanya ya! 

Saya siap membantu kapan saja. 🤝"""

        else:
            return """Maaf, saya belum bisa memberikan jawaban yang tepat untuk pertanyaan tersebut.

Saya dapat membantu Anda dengan:
🔹 Informasi asisten laboratorium
🔹 Jadwal kerja dan ketersediaan  
🔹 Aturan ujian dan praktikum
🔹 Material kuliah
🔹 Proses koreksi

Bisa coba tanyakan dengan lebih spesifik? Saya akan dengan senang hati membantu! 😊"""
    
    def _map_confidence(self, confidence_str: str) -> float:
        """Map confidence string to float value"""
        
        confidence_mapping = {
            'high': 0.9,
            'medium': 0.65,
            'low': 0.4,
            'ambiguous': 0.2
        }
        
        return confidence_mapping.get(confidence_str.lower(), 0.3)
    
    def _fallback_classification(self, query: str) -> Dict:
        """Fallback classification if agent fails"""
        
        print("⚠️ Using fallback classification")
        
        query_lower = query.lower()
        
        # Check for general responses first
        if any(word in query_lower for word in ['halo', 'hai', 'hello', 'selamat', 'terima kasih', 'thanks']):
            return {
                'system': 'general_response',
                'confidence': 0.9,
                'classification_type': 'high',
                'reasoning': 'Fallback: detected greeting or courtesy expression',
                'intent_type': 'greeting',
                'query': query,
                'used_agent': False
            }
        elif any(word in query_lower for word in ['apa itu', 'tentang', 'slc', 'academic', 'penjelasan']):
            return {
                'system': 'general_response',
                'confidence': 0.8,
                'classification_type': 'high',
                'reasoning': 'Fallback: detected general information request',
                'intent_type': 'general_info',
                'query': query,
                'used_agent': False
            }
        elif any(word in query_lower for word in ['ruangan', 'room', 'kosong', 'shift', 'empty']):
            return {
                'system': 'find_room',
                'confidence': 0.6,
                'classification_type': 'medium',
                'reasoning': 'Fallback: detected room-related keywords',
                'intent_type': 'specific_query',
                'query': query,
                'used_agent': False
            }
        elif any(word in query_lower for word in ['job', 'jadwal', 'schedule', 'kerja', 'teaching']):
            return {
                'system': 'job_query', 
                'confidence': 0.6,
                'classification_type': 'medium',
                'reasoning': 'Fallback: detected job-related keywords',
                'intent_type': 'specific_query',
                'query': query,
                'used_agent': False
            }
        elif any(word in query_lower for word in ['material', 'criteria', 'download', 'link']):
            return {
                'system': 'material_criteria',
                'confidence': 0.6,
                'classification_type': 'medium', 
                'reasoning': 'Fallback: detected material-related keywords',
                'intent_type': 'specific_query',
                'query': query,
                'used_agent': False
            }
        else:
            return {
                'system': 'ambiguous',
                'confidence': 0.2,
                'classification_type': 'ambiguous',
                'reasoning': 'Fallback: unable to determine intent',
                'intent_type': 'unclear',
                'query': query,
                'used_agent': False
            }

if __name__ == "__main__":
    print("🧪 Testing Intelligent Router Agent with General Response")
    print("=" * 60)
    
    router = IntelligentRouter()
    
    test_queries = [
        # General responses
        "Halo",
        "Apa itu SLC?", 
        "Terima kasih",
        "Selamat pagi",
        
        # Specific system queries
        "Ruangan 601 kosong shift 1?",
        "KA24-1 ada job apa hari ini?",
        "Download material COMP6048",
        "Aturan menyontek di ujian",
        "Siapa asisten di Syahdan?",
        "Cara setup computer lab"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: '{query}'")
        result = router.classify_intent(query)
        print(f"📊 System: {result['system']}")
        print(f"📈 Confidence: {result['confidence']:.3f}")
        print(f"🎯 Intent Type: {result.get('intent_type', 'N/A')}")
        print(f"💭 Reasoning: {result['reasoning']}")
        
        # Test general response if routed to general_response
        if result['system'] == 'general_response':
            print(f"💬 General Response:")
            response = router.generate_general_response(query)
            print(f"   {response[:100]}..." if len(response) > 100 else f"   {response}")
        
        print("-" * 50) 