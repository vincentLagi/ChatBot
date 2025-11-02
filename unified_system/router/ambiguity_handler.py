"""
Ambiguity Handler for Unified Academic Assistant
Handles unclear, mixed, or low-confidence query classifications

Features:
- Generate clarification questions
- Handle multi-system queries
- Provide intelligent fallbacks
- User-friendly suggestion system
"""

from typing import Dict, List, Optional
import random

class AmbiguityHandler:
    """
    ❓ Handles ambiguous queries and provides intelligent fallbacks
    """
    
    def __init__(self):
        """Initialize ambiguity handler with system information"""
        
        # System descriptions for user guidance
        self.system_info = {
            'rules_uap': {
                'name': 'Rules UAP',
                'emoji': '📝',
                'description': 'Aturan ujian, sanksi, dan pelanggaran akademik',
                'examples': [
                    'Aturan menyontek di ujian',
                    'Sanksi plagiarisme',
                    'Pelanggaran akademik'
                ],
                'keywords': ['rules', 'uap', 'ujian', 'sanksi']
            },
            'assistant_search': {
                'name': 'Assistant Search',
                'emoji': '👥',
                'description': 'Data asisten, dosen, dan lokasi ruangan',
                'examples': [
                    'Siapa asisten di kampus Syahdan?',
                    'Kontak dosen matematika',
                    'Ruangan lab komputer'
                ],
                'keywords': ['assistant', 'search', 'asisten', 'dosen']
            },
            'rules_mengajar': {
                'name': 'Rules Mengajar',
                'emoji': '🖥️',
                'description': 'Prosedur praktikum dan setup lab komputer',
                'examples': [
                    'Cara setup lab komputer',
                    'Prosedur mengajar praktikum',
                    'Persiapan ruang lab'
                ],
                'keywords': ['practicum', 'praktikum', 'lab', 'computer', 'mengajar', 'teaching']
            },
            'correction_casemaking': {
                'name': 'Correction & Case Making',
                'emoji': '📋',
                'description': 'Koreksian dan pembuatan soal ujian',
                'examples': [
                    'Cara melakukan koreksian',
                    'Template case making',
                    'Submit ke Messier'
                ],
                'keywords': ['correction', 'koreksian', 'case', 'template']
            },
            'material_criteria': {
                'name': 'Material & Criteria Search',
                'emoji': '📚',
                'description': 'Course materials, criteria, and download links',
                'examples': [
                    'Download link untuk COMP6048',
                    'Kriteria mata kuliah Data Structures',
                    'Material quiz TM1'
                ],
                'keywords': ['material', 'criteria', 'materi', 'kriteria']
            },
            'find_room': {
                'name': 'Find Room',
                'emoji': '🏢',
                'description': 'Room availability, schedule, and booking information',
                'examples': [
                    'Ruangan mana yang kosong hari ini?',
                    'Apakah ruangan 601 kosong shift 1?',
                    'Cek jadwal ruangan besok'
                ],
                'keywords': ['ruangan', 'room', 'kosong', 'shift', 'jadwal']
            }
        }
        
        # Clarification templates
        self.clarification_templates = [
            "Hmm, pertanyaan kamu bisa berkaitan dengan beberapa sistem. Bisa diperjelas?",
            "Sepertinya query kamu bisa masuk ke beberapa kategori. Mau pilih yang mana?",
            "Aku butuh sedikit klarifikasi untuk memberikan jawaban yang tepat.",
            "Pertanyaan kamu cukup general. Bisa lebih spesifik tentang apa yang kamu cari?"
        ]
        
        print("❓ Ambiguity Handler initialized successfully!")
    
    def handle_ambiguous_query(self, classification_result: Dict, query: str) -> str:
        """
        🎯 Main method to handle ambiguous queries
        
        Args:
            classification_result: Result from intent classifier
            query: Original user query
            
        Returns:
            Helpful response for user clarification
        """
        
        classification_type = classification_result.get('classification_type', 'unknown')
        
        if classification_type == 'ambiguous':
            return self._handle_completely_ambiguous(classification_result, query)
        elif classification_type == 'low_confidence':
            return self._handle_low_confidence(classification_result, query)
        else:
            # This shouldn't happen, but provide fallback
            return self._generate_general_help(query)
    
    def _handle_completely_ambiguous(self, result: Dict, query: str) -> str:
        """Handle queries with no clear classification"""
        
        # Get system suggestions
        suggestions = self._get_smart_suggestions(result, query)
        
        # Generate clarification question
        clarification = random.choice(self.clarification_templates)
        
        response = f"""🤔 {clarification}

✨ **Query Kamu:** "{query}"

Sepertinya ini bisa berkaitan dengan:
"""
        
        # Add system options
        for i, system in enumerate(suggestions[:3], 1):
            info = self.system_info.get(system, {})
            emoji = info.get('emoji', '🔍')
            name = info.get('name', system)
            desc = info.get('description', 'Sistem pencarian')
            
            response += f"\n{i}. {emoji} **{name}** - {desc}"
        
        response += f"""

💡 **Cara mudah:**
• Ketik nomor (1, 2, 3) untuk pilih sistem
• Atau jelaskan lebih spesifik pertanyaanmu
• Ketik 'help' untuk melihat semua sistem yang tersedia

Contoh: "1" atau "Aku mau tanya tentang aturan ujian"
"""
        
        return response
    
    def _handle_low_confidence(self, result: Dict, query: str) -> str:
        """Handle queries with low confidence classification"""
        
        best_system = result.get('system', 'unknown')
        confidence = result.get('confidence', 0.0)
        all_scores = result.get('all_scores', {})
        
        # Get top 2 systems
        top_systems = list(all_scores.keys())[:2]
        
        response = f"""🎯 Sepertinya kamu bertanya tentang **{self.system_info.get(best_system, {}).get('name', best_system)}**, tapi aku tidak 100% yakin.

✨ **Query Kamu:** "{query}"
📊 **Confidence:** {confidence:.1%}

🤖 **Aku akan coba jawab dengan sistem {self.system_info.get(best_system, {}).get('emoji', '🔍')} {self.system_info.get(best_system, {}).get('name', best_system)}**

Tapi kalau jawaban tidak sesuai, mungkin kamu maksud:
"""
        
        # Add alternative systems
        for system in top_systems[1:2]:  # Only show top alternative
            info = self.system_info.get(system, {})
            emoji = info.get('emoji', '🔍')
            name = info.get('name', system)
            response += f"• {emoji} **{name}** - {info.get('description', '')}\n"
        
        response += f"""
💡 **Tips:** Coba gunakan kata kunci yang lebih spesifik untuk hasil yang lebih akurat!
"""
        
        return response
    
    def _get_smart_suggestions(self, result: Dict, query: str) -> List[str]:
        """Get intelligent system suggestions based on query content"""
        
        # Get scores from classification result
        all_scores = result.get('all_scores', {})
        keyword_scores = result.get('keyword_scores', {})
        
        # Combine and sort suggestions
        suggestions = []
        
        # Add systems with any score > 0
        for system, score in all_scores.items():
            if score > 0.05:  # Very low threshold for suggestions
                suggestions.append((system, score))
        
        # If no good suggestions, provide most relevant based on keywords
        if not suggestions:
            query_lower = query.lower()
            for system, info in self.system_info.items():
                keywords = info.get('keywords', [])
                if any(kw in query_lower for kw in keywords):
                    suggestions.append((system, 0.1))  # Low score but relevant
        
        # If still no suggestions, show all systems
        if not suggestions:
            suggestions = [(system, 0.1) for system in self.system_info.keys()]
        
        # Sort by score and return system names
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [system for system, score in suggestions]
    
    def generate_system_overview(self) -> str:
        """Generate overview of all available systems"""
        
        response = """🎯 **UNIFIED ACADEMIC ASSISTANT - SISTEM YANG TERSEDIA**

Aku bisa bantu kamu dengan 4 sistem spesialis:

"""
        
        for i, (system, info) in enumerate(self.system_info.items(), 1):
            emoji = info.get('emoji', '🔍')
            name = info.get('name', system)
            desc = info.get('description', '')
            examples = info.get('examples', [])
            
            response += f"""{i}. {emoji} **{name}**
   📝 {desc}
   
   💡 Contoh query:
"""
            for example in examples[:2]:  # Show top 2 examples
                response += f"   • \"{example}\"\n"
            
            response += "\n"
        
        response += """🚀 **Cara pakai:**
• Langsung tanya apa aja - aku akan otomatis route ke sistem yang tepat
• Kalau bingung, ketik nomor sistem (1, 2, 3, 4)
• Atau gunakan kata kunci spesifik untuk hasil yang lebih akurat

💬 **Tips:** Semakin spesifik query kamu, semakin akurat jawabannya!
"""
        
        return response
    
    def _generate_general_help(self, query: str) -> str:
        """Generate general help message"""
        
        return f"""🤖 **BUTUH BANTUAN?**

Query kamu: "{query}"

Sepertinya aku perlu info lebih untuk memberikan jawaban yang tepat. 

💡 **Coba:**
• Gunakan kata kunci yang lebih spesifik
• Ketik 'help' untuk melihat semua sistem
• Atau pilih langsung sistem yang kamu butuhkan:

📝 **1** - Rules UAP (aturan ujian)
👥 **2** - Assistant Search (data asisten/dosen)  
🖥️ **3** - Practicum Rules (prosedur praktikum)
📋 **4** - Correction & Case Making (koreksian/soal)

Ketik nomor atau tanya langsung!
"""
    
    def parse_user_selection(self, user_input: str) -> Optional[str]:
        """
        Parse user's system selection from clarification response
        
        Args:
            user_input: User's response to clarification
            
        Returns:
            System name if valid selection, None otherwise
        """
        
        user_input = user_input.strip().lower()
        
        # Direct number selection
        number_map = {
            '1': 'rules_uap',
            '2': 'assistant_search', 
            '3': 'rules_mengajar',
            '4': 'correction_casemaking',
            '5': 'job_query',
            '6': 'material_criteria',
            '7': 'find_room'
        }
        
        if user_input in number_map:
            return number_map[user_input]
        
        # Keyword-based selection
        keyword_map = {
            'rules': 'rules_uap',
            'uap': 'rules_uap',
            'ujian': 'rules_uap',
            'sanksi': 'rules_uap',
            
            'assistant': 'assistant_search',
            'search': 'assistant_search',
            'asisten': 'assistant_search',
            'dosen': 'assistant_search',
            
            'practicum': 'rules_mengajar',
            'praktikum': 'rules_mengajar',
            'lab': 'rules_mengajar',
            'computer': 'rules_mengajar',
            'mengajar': 'rules_mengajar',
            'teaching': 'rules_mengajar',
            
            'correction': 'correction_casemaking',
            'koreksian': 'correction_casemaking',
            'case': 'correction_casemaking',
            'template': 'correction_casemaking',
            
            'job': 'job_query',
            'jobs': 'job_query',
            'jadwal': 'job_query',
            'schedule': 'job_query',
            'pekerjaan': 'job_query',
            
            'material': 'material_criteria',
            'criteria': 'material_criteria',
            'materi': 'material_criteria',
            'kriteria': 'material_criteria',
            'download': 'material_criteria',
            
            'room': 'find_room',
            'ruangan': 'find_room',
            'kosong': 'find_room',
            'shift': 'find_room',
            'empty': 'find_room'
        }
        
        for keyword, system in keyword_map.items():
            if keyword in user_input:
                return system
        
        return None

if __name__ == "__main__":
    # Test the ambiguity handler
    print("🧪 Testing Ambiguity Handler")
    print("=" * 40)
    
    handler = AmbiguityHandler()
    
    # Test completely ambiguous
    ambiguous_result = {
        'system': 'ambiguous',
        'classification_type': 'ambiguous',
        'confidence': 0.0,
        'all_scores': {'rules_uap': 0.1, 'assistant_search': 0.1},
        'keyword_scores': {'rules_uap': 0.1, 'assistant_search': 0.1}
    }
    
    print("1. Testing completely ambiguous query:")
    response = handler.handle_ambiguous_query(ambiguous_result, "template")
    print(response[:200] + "...")
    
    # Test low confidence
    low_conf_result = {
        'system': 'correction_casemaking',
        'classification_type': 'low_confidence',
        'confidence': 0.3,
        'all_scores': {'correction_casemaking': 0.4, 'practicum_rules': 0.3},
        'keyword_scores': {'correction_casemaking': 0.2, 'practicum_rules': 0.1}
    }
    
    print("\n2. Testing low confidence query:")
    response = handler.handle_ambiguous_query(low_conf_result, "setup template")
    print(response[:200] + "...")
    
    # Test system overview
    print("\n3. Testing system overview:")
    overview = handler.generate_system_overview()
    print(overview[:300] + "...")
    
    # Test user selection parsing
    print("\n4. Testing user selection parsing:")
    test_inputs = ["1", "assistant", "praktikum", "invalid"]
    for inp in test_inputs:
        result = handler.parse_user_selection(inp)
        print(f"Input: '{inp}' -> System: {result}") 