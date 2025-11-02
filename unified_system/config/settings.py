import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
import json

@dataclass
class DatabaseConfig:    
    url: str
    key: str
    timeout: int = 30
    max_connections: int = 10
    retry_attempts: int = 3
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Load database config from environment variables"""
        
        return cls(
            url=os.getenv('SUPABASE_URL', ''),
            key=os.getenv('SUPABASE_KEY', ''),
            timeout=int(os.getenv('DB_TIMEOUT', '30')),
            max_connections=int(os.getenv('DB_MAX_CONNECTIONS', '10')),
            retry_attempts=int(os.getenv('DB_RETRY_ATTEMPTS', '3'))
        )

@dataclass
class AIModelConfig:    
    api_key: str
    
    answer_model: str = "gemini-2.0-flash"
    search_model: str = "gemini-2.0-flash"
    embedding_model: str = "models/embedding-001"
    
    answer_temperature: float = 0.7    
    search_temperature: float = 0.1      
    router_temperature: float = 0.3    
    max_tokens: int = 2000
    timeout: int = 30
    
    @classmethod
    def from_env(cls) -> 'AIModelConfig':
        """Load AI model config from environment variables"""
        
        return cls(
            api_key=os.getenv('GOOGLE_API_KEY', ''),
            answer_model=os.getenv('AI_ANSWER_MODEL', 'gemini-2.0-flash'),
            search_model=os.getenv('AI_SEARCH_MODEL', 'gemini-2.0-flash'),
            embedding_model=os.getenv('EMBEDDING_MODEL', 'models/embedding-001'),
            answer_temperature=float(os.getenv('AI_ANSWER_TEMPERATURE', '0.7')),
            search_temperature=float(os.getenv('AI_SEARCH_TEMPERATURE', '0.1')),
            router_temperature=float(os.getenv('AI_ROUTER_TEMPERATURE', '0.3')),
            max_tokens=int(os.getenv('AI_MAX_TOKENS', '2000')),
            timeout=int(os.getenv('AI_TIMEOUT', '30'))
        )

@dataclass
class CacheConfig:    
    enabled: bool = True
    embedding_cache_size: int = 2000
    search_cache_size: int = 1000
    system_cache_size: int = 100
    embedding_ttl: int = 7200 
    search_ttl: int = 1800     
    system_ttl: int = 3600    
    
    @classmethod
    def from_env(cls) -> 'CacheConfig':
        return cls(
            enabled=os.getenv('CACHE_ENABLED', 'true').lower() == 'true',
            embedding_cache_size=int(os.getenv('CACHE_EMBEDDING_SIZE', '2000')),
            search_cache_size=int(os.getenv('CACHE_SEARCH_SIZE', '1000')),
            system_cache_size=int(os.getenv('CACHE_SYSTEM_SIZE', '100')),
            embedding_ttl=int(os.getenv('CACHE_EMBEDDING_TTL', '7200')),
            search_ttl=int(os.getenv('CACHE_SEARCH_TTL', '1800')),
            system_ttl=int(os.getenv('CACHE_SYSTEM_TTL', '3600'))
        )

@dataclass
class SystemConfig:    
    name: str
    enabled: bool = True
    confidence_threshold: float = 0.4
    ambiguous_threshold: float = 0.3
    medium_confidence_threshold: float = 0.6
    high_confidence_threshold: float = 0.8
    

    search_limit: int = 10
    keywords: List[str] = field(default_factory=list)
    weight: float = 1.0

@dataclass
class LoggingConfig:
    """Logging configuration settings"""
    
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10_000_000
    backup_count: int = 5
    performance_tracking: bool = True
    
    @classmethod
    def from_env(cls) -> 'LoggingConfig':
        """Load logging config from environment variables"""
        
        return cls(
            level=os.getenv('LOG_LEVEL', 'INFO'),
            format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            file_path=os.getenv('LOG_FILE_PATH'),
            max_file_size=int(os.getenv('LOG_MAX_FILE_SIZE', '10000000')),
            backup_count=int(os.getenv('LOG_BACKUP_COUNT', '5')),
            performance_tracking=os.getenv('LOG_PERFORMANCE', 'true').lower() == 'true'
        )

@dataclass
class GlobalConfig:
    
    database: DatabaseConfig
    ai_model: AIModelConfig
    cache: CacheConfig
    logging: LoggingConfig
    
    systems: Dict[str, SystemConfig] = field(default_factory=dict)
    debug: bool = False

    
    @classmethod
    def from_env(cls) -> 'GlobalConfig':
        """Load complete configuration from environment variables"""
        
        # Load core configs
        database_config = DatabaseConfig.from_env()
        ai_model_config = AIModelConfig.from_env()
        cache_config = CacheConfig.from_env()
        logging_config = LoggingConfig.from_env()
        
        # Load system configs
        systems_config = cls._load_systems_config()
        
        return cls(
            database=database_config,
            ai_model=ai_model_config,
            cache=cache_config,
            logging=logging_config,
            systems=systems_config,
            debug=os.getenv('DEBUG', 'false').lower() == 'true'
        )
    
    @classmethod
    def _load_systems_config(cls) -> Dict[str, SystemConfig]:
        """Load system-specific configurations"""
        
        systems = {
            'rules_uap': SystemConfig(
                name='Rules UAP',
                keywords=['ujian', 'menyontek', 'sanksi', 'aturan', 'pelanggaran'],
                weight=1.1
            ),
            'assistant_search': SystemConfig(
                name='Assistant Search',
                keywords=['asisten', 'dosen', 'ruangan', 'lokasi', 'kontak'],
                weight=1.25
            ),
            'rules_mengajar': SystemConfig(
                name='Rules Mengajar',
                keywords=['praktikum', 'lab', 'komputer', 'setup', 'prosedur', 'mengajar', 'teaching'],
                weight=1.15
            ),
            'correction_casemaking': SystemConfig(
                name='Correction & Case Making',
                keywords=['koreksian', 'case making', 'template', 'messier'],
                weight=1.2
            )
        }
        
        return systems
    
    def get_system_config(self, system_name: str) -> Optional[SystemConfig]:        
        return self.systems.get(system_name)
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        
        errors = []
        
        if not self.database.url:
            errors.append("SUPABASE_URL environment variable is required")
        
        if not self.database.key:
            errors.append("SUPABASE_KEY environment variable is required")
        
        if not self.ai_model.api_key:
            errors.append("GOOGLE_API_KEY environment variable is required")
        
        for system_name, system_config in self.systems.items():
            if system_config.confidence_threshold > system_config.high_confidence_threshold:
                errors.append(f"Invalid confidence thresholds for {system_name}")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (for serialization)"""
        
        return {
            'database': {
                'url': '***' if self.database.url else '',  
                'key': '***' if self.database.key else '',
                'timeout': self.database.timeout,
                'max_connections': self.database.max_connections,
                'retry_attempts': self.database.retry_attempts
            },
            'ai_model': {
                'api_key': '***' if self.ai_model.api_key else '',
                'model_name': self.ai_model.model_name,
                'embedding_model': self.ai_model.embedding_model,
                'temperature': self.ai_model.temperature,
                'max_tokens': self.ai_model.max_tokens,
                'timeout': self.ai_model.timeout
            },
            'cache': self.cache.__dict__,
            'logging': self.logging.__dict__,
            'systems': {name: config.__dict__ for name, config in self.systems.items()},
            'app_name': self.app_name,
            'version': self.version,
            'debug': self.debug
        }
    
    def save_to_file(self, file_path: str) -> None:
        """Save configuration to JSON file"""
        
        config_dict = self.to_dict()
        
        with open(file_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    @property
    def rules_uap_csv_path(self) -> str:
        """Path to Rules UAP CSV file"""
        return "data/csv/Rules&ProcedureUAP.csv"
    
    @property
    def assistant_csv_path(self) -> str:
        """Path to Assistant Search CSV file"""
        return "data/csv/output.csv"
    
    @property
    def practicum_csv_path(self) -> str:
        """Path to Practicum Rules CSV file"""
        return "data/csv/Rules&ProceduresPracticum.csv"
    
    @property
    def correction_csv_path(self) -> str:
        """Path to Correction & Case Making CSV file"""
        return "data/csv/CorrectionAndCaseMaking.csv"
    
    @property
    def database_url(self) -> str:
        return self.database.url


config = GlobalConfig.from_env()

def get_config() -> GlobalConfig:
    return config

def get_settings() -> GlobalConfig:
    return config

def reload_config() -> GlobalConfig:
    global config
    config = GlobalConfig.from_env()
    return config

def get_ai_config() -> AIModelConfig:
    """Get AI model configuration"""
    return get_settings().ai_model

def get_answer_model_config() -> dict:
    """Get configuration for answer/response agents (temperature: 0.7)"""
    ai_config = get_ai_config()
    return {
        "model": ai_config.answer_model,
        "temperature": ai_config.answer_temperature,
        "google_api_key": ai_config.api_key,
        "max_tokens": ai_config.max_tokens
    }

def get_search_model_config() -> dict:
    """Get configuration for search/classification agents (temperature: 0.1)"""
    ai_config = get_ai_config()
    return {
        "model": ai_config.search_model,
        "temperature": ai_config.search_temperature,
        "google_api_key": ai_config.api_key,
        "max_tokens": ai_config.max_tokens
    }

def get_additional_information() -> str:
    return """

        Berikut adalah jenis-jenis informasi yang dapat saya bantu:
        1. Rule and Procedure SLC
           Saya bisa memberikan informasi mengenai Rule and Procedure ketika mengajar, UAP, dan sebagainya.
        2. Tata Cara Koreksian dan Case Making
           Saya bisa memberikan langkah-langkah untuk melakukan koreksian dan case making sesuai dengan panduan yang diberikan oleh SubCo.
        3. Material Criteria Mata Kuliah
           Saya dapat memberikan link untuk mendownload Material Criteria sebuah mata kuliah. 
        4. Informasi Terkait Job Assistant
           Saya dapat memberikan informasi terkait pekerjaan pekerjaan apa saja yang dimiliki seorang assistant.
        5. Informasi Jadwal Ruangan Khususnya RANG (Ruang Angkatan)
           Saya dapat melakukan pencarian ruangan SLC yang sama sekali tidak memiliki jadwal peminjaman atau spesifik pada shift tertentu.
        6. Informasi Mengenai Assistant
           Saya dapat menyediakan informasi tentang assistant dari nama, inisial, NIM, Email, Posisi SLC, Binusian ID, dan lainnya.

        [Penjelasan Academic]
        Academic adalah sebuah website yang dikembangkan SLC untuk memudahkan assistant dalam melihat jadwal training, qualification, "My Queue" untuk melihat jadwal koreksian dan case making atau segala hal yang berkaitan dengan SubCo.
        Fungsinya meliputi: melihat jadwal training, melihat ide dari sebuah Case Making, melihat menu "My Queue", melihat qualification.
        Academic bisa di akses melalui: https://academic.slc.net untuk local, atau https://academic-slc.apps.binus.ac.id/

        [Penjelasan Ruman]
        Ruman adalah sistem otomasi ruangan yang dikembangkan oleh SLC untuk memudahkan setup komputer sebelum dan sesudah praktikum. 
        Fungsinya meliputi: membersihkan Drive D, membersihkan FTP, membuka browser Chrome, membuka situs slc.net, membuka poster (termasuk poster NAR), dan software lain yang dibutuhkan.
        Ruman bisa di akses lewat link https://ruman.slc.net

        [Penjelasan Lab Facility]
        Lab Facility adalah website resmi yang digunakan untuk melakukan peminjaman ruangan laboratorium di lingkungan BINUS University.
        Pengajar atau asisten yang ingin mengadakan kelas tambahan atau kegiatan di luar jadwal reguler dapat mengajukan permohonan peminjaman ruangan melalui Lab Facility.
        - Akses website: https://labfacility.apps.binus.ac.id/

        [Penjelasan Messier]
        Messier adalah platform utama yang digunakan oleh asisten untuk mengecek jadwal kegiatan asistensi praktikum di BINUS.
        Website dapat diakses melalui: https://messier.apps.binus.ac.id/ untuk local, untuk global bisa melalui: https://socs1.binus.ac.id/messier/

    """

def get_fallback(user_query: str) -> str:
    return f"""Menurut saya berdasarkan pertanyaan {user_query} Anda."""


def get_answering_style() -> str:
    return """
✅ Buat jawaban yang terdengar seperti manusia, alami, dan tidak kaku
   - Gunakan variasi kalimat agar tidak terkesan robotik
   - Tambahkan kalimat pembuka atau sambutan yang kontekstual jika perlu
   - Hindari penggunaan istilah teknis seperti “Langkah-langkah:” secara kaku

✅ Jawab langsung berdasarkan hasil pencarian yang ditemukan
✅ Gunakan bahasa natural dan seperti percakapan sehari-hari
✅ Fokus pada prosedur praktis yang bisa langsung diterapkan
✅ Jelaskan langkah-langkah secara bertahap jika ada prosedur
✅ Berikan konteks kenapa prosedur atau aturan tersebut penting

❌ Jangan tambahkan informasi yang tidak ada dalam hasil pencarian
❌ Jangan menjawab dengan kalimat generik tanpa data yang relevan
❌ Jangan gunakan format atau template yang sama untuk semua jawaban
"""


def get_router_model_config() -> dict:
    """Get configuration for router/routing agents (temperature: 0.3)"""
    ai_config = get_ai_config()
    return {
        "model": ai_config.search_model,
        "temperature": ai_config.router_temperature,
        "google_api_key": ai_config.api_key,
        "max_tokens": ai_config.max_tokens
    }

def get_embedding_model_config() -> dict:
    """Get configuration for embedding models"""
    ai_config = get_ai_config()
    return {
        "model": ai_config.embedding_model,
        "google_api_key": ai_config.api_key
    }

def get_general_info_position() -> str:
    return '''
INFORMASI DETAIL POSISI ASISTEN:

POSISI MANAGEMENT & LEADERSHIP:

1. OP Officer (Operations Management Officer) - dibagi menjadi 3 role:
   a. OP Officer (Qman) - Quality and Career Management:
      • Memimpin dan koordinasi dengan asisten laboratorium di bawah kepemimpinannya
      • Memelihara dokumentasi kualitas sesuai standar ISO
      • Berkolaborasi dengan stakeholder internal dan eksternal unit
      • Koordinasi penegakan regulasi asisten laboratorium
      • Koordinasi dan mengelola implementasi kegiatan praktikum harian
   
   b. OP Officer (Resman) - Resource Management:
      • Mengalokasi, memantau, dan mengelola jadwal kerja teaching assistant
      • Memimpin dan koordinasi dengan asisten laboratorium di bawah kepemimpinannya
      • Koordinasi penegakan regulasi asisten laboratorium
      • Komunikasi dan bekerja dengan stakeholder internal dan eksternal unit
      • Koordinasi dan mengelola implementasi kegiatan praktikum harian
   
   c. OP Officer (Recsel) - Recruitment and Selection:
      • Melakukan perencanaan rekrutmen asisten baru
      • Koordinasi kegiatan promosi SLC untuk menarik calon kandidat
      • Koordinasi dan memantau kegiatan rekrutmen dan pelatihan
      • Koordinasi wawancara rekrutmen
      • Evaluasi performa trainee SLC dalam proses pelatihan
      • Koordinasi proses rekrutmen asisten baru dengan Human Capital

2. NA Officer (Network Administration Officer):
   • Mengatur hal-hal berhubungan dengan jaringan
   • Memantau kinerja NA Staff
   • Tersedia di lokasi: ALS, KMG

3. Head - KMG:
   • Memimpin dan mengelola seluruh operasional SLC di lokasi Kemanggisan dan juga per devisi

POSISI STAFF & SPECIALIST:

4. NA Staff (Network Administration Staff):
   • Mengatur hal-hal berhubungan dengan jaringan
   • Tersedia di lokasi: ALS, KMG

5. DBA Staff (Database Administrator Staff):
   • Mengatur hal-hal berhubungan dengan database SLC lab practicum

6. RnD Staff (Research and Development Staff):
   • Mengembangkan website aplikasi untuk kebutuhan practicum
   • Maintenance aplikasi yang sudah ada

POSISI ASSISTANT (AST):

7. Ast (Assistant) - tersedia di berbagai lokasi dan shift:
   • Ast - ALS (J) = Assistant Alam Sutera, shift Junior
   • Ast - ALS (S) = Assistant Alam Sutera, shift Senior
   • Ast - BDG (S) = Assistant Bandung, shift Senior
   • Ast - BKS (J) = Assistant Bekasi, shift Junior
   • Ast - BKS (S) = Assistant Bekasi, shift Senior
   • Ast - KMG (J) = Assistant Kemanggisan, shift Junior
   • Ast - KMG (S) = Assistant Kemanggisan, shift Senior
   • Ast - SMG (J) = Assistant Semarang, shift Junior
   • Ast - SMG (S) = Assistant Semarang, shift Senior

POSISI DEVELOPMENT:

8. AstDev (Assistant Developer - Officer):
   • Bertugas pada pengembangan assistant (AST) dengan memberikan TPA (Tes potensi asisten) dan pelatihan qualifikasi mengajar

9. SubDev (Subject Developer - Officer):
   • Bertugas pada mengatur subject di lab bisa berupa course outline dan berhubungan dengan pihak kampus mengenai subject yang ada di lab

POSISI KOORDINATOR:

10. Subco (Subject Coordinator - Staff):
    • Subco - ALS = Subject Coordinator Alam Sutera
    • Subco - KMG = Subject Coordinator Kemanggisan
    • Subco bertugas sebagai penghubung antara asisten dan subdev mengenai subject yang dipegang

POSISI PRAKTIKUM (PRT):

11. Prt (Praktikum) - tersedia di berbagai lokasi dan level:
    • Prt - ALS (J) = Praktikum Alam Sutera, level Junior
    • Prt - ALS (S) = Praktikum Alam Sutera, level Senior
    • Prt - BDG (J) = Praktikum Bandung, level Junior
    • Prt - BDG (S) = Praktikum Bandung, level Senior
    • Prt - BKS (J) = Praktikum Bekasi, level Junior
    • Prt - BKS (S) = Praktikum Bekasi, level Senior
    • [Tugas dan tanggung jawab akan ditambahkan]

CATATAN KODE LOKASI:
- ALS = Alam Sutera
- BDG = Bandung
- BKS = Bekasi
- KMG = Kemanggisan
- SMG = Semarang

CATATAN KODE LEVEL:
- (J) = Junior
- (S) = Senior

CATATAN KODE SHIFT:
- P = Pagi
- M = Malam
- N = Normal
'''

if __name__ == "__main__":
    # Test configuration
    print("🧪 Testing Configuration Management")
    print("=" * 45)
    
    # Load and display config
    test_config = GlobalConfig.from_env()
