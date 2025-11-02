"""
Response Formatter for Unified Academic Assistant
Provides consistent formatting for responses across all systems

Features:
- Unified response styling
- System-specific formatting
- Error message formatting
- Help and guidance formatting
"""

from typing import Dict, Optional
from datetime import datetime

class ResponseFormatter:
    """
    📝 Formats responses consistently across all systems
    """
    
    def __init__(self):
        """Initialize response formatter with styling configurations"""
        
        # System styling configuration
        self.system_styles = {
            'rules_uap': {
                'emoji': '📝',
                'color': 'blue',
                'name': 'Rules UAP',
                'icon': '⚖️'
            },
            'assistant_search': {
                'emoji': '👥',
                'color': 'green', 
                'name': 'Assistant Search',
                'icon': '🔍'
            },
            'rules_mengajar': {
                'emoji': '🖥️',
                'color': 'purple',
                'name': 'Rules Mengajar',
                'icon': '🏫'
            },
            'correction_casemaking': {
                'emoji': '📋',
                'color': 'orange',
                'name': 'Correction & Case Making',
                'icon': '📊'
            }
        }
        
        # Response templates
        self.templates = {
            'success': "✅ **{system_name}** - Query berhasil diproses",
            'error': "❌ **{system_name}** - Terjadi error",
            'warning': "⚠️ **{system_name}** - Peringatan",
            'info': "ℹ️ **{system_name}** - Informasi"
        }
        
        print("📝 Response Formatter initialized successfully!")
    
    def format_system_response(self, response: str, system_type: str, 
                              classification_result: Dict, 
                              add_metadata: bool = True) -> str:
        """
        🎨 Format response with system branding and metadata
        
        Args:
            response: Raw response from system
            system_type: System that generated the response
            classification_result: Classification metadata
            add_metadata: Whether to add classification metadata
            
        Returns:
            Formatted response string
        """
        
        # Get system styling
        style = self.system_styles.get(system_type, {})
        emoji = style.get('emoji', '🔍')
        name = style.get('name', system_type.title())
        
        # Get classification info
        confidence = classification_result.get('confidence', 0.0)
        classification_type = classification_result.get('classification_type', 'unknown')
        
        # Build header
        header = f"{emoji} **{name}**"
        
        # Add confidence indicator for non-high confidence
        if add_metadata and confidence < 0.8:
            confidence_emoji = self._get_confidence_emoji(confidence)
            header += f" {confidence_emoji} (confidence: {confidence:.1%})"
        
        # Build formatted response
        formatted_response = f"{header}\n\n{response}"
        
        # Add footer metadata if requested
        if add_metadata and classification_type != 'high_confidence':
            footer = self._generate_footer(classification_result, system_type)
            formatted_response += f"\n\n{footer}"
        
        return formatted_response
    
    def format_error_response(self, error_message: str, system_type: str, 
                             query: str, include_suggestions: bool = True) -> str:
        """
        🚨 Format error responses consistently
        """
        
        style = self.system_styles.get(system_type, {})
        emoji = style.get('emoji', '🔍')
        name = style.get('name', system_type.title())
        
        formatted = f"""🚨 **Error - {name}**

❌ **Problem:** Terjadi error saat memproses query kamu
📝 **Query:** "{query}"
💬 **Error:** {error_message}
"""
        
        if include_suggestions:
            formatted += """
💡 **Solusi yang bisa dicoba:**
• Coba query yang lebih sederhana
• Gunakan kata kunci yang lebih spesifik
• Periksa ejaan dan tata bahasa
• Atau coba sistem lain yang mungkin relevan

🔄 **Bantuan:** Ketik 'help' untuk melihat panduan lengkap
"""
        
        return formatted
    
    def format_ambiguous_response(self, ambiguity_message: str, 
                                 suggestions: list, query: str) -> str:
        """
        🤔 Format responses for ambiguous queries
        """
        
        formatted = f"""🤔 **Perlu Klarifikasi**

✨ **Query Kamu:** "{query}"

{ambiguity_message}

💡 **Saran sistem:**
"""
        
        for i, suggestion in enumerate(suggestions[:3], 1):
            style = self.system_styles.get(suggestion, {})
            emoji = style.get('emoji', '🔍')
            name = style.get('name', suggestion.title())
            formatted += f"\n{i}. {emoji} **{name}**"
        
        formatted += """

🎯 **Cara mudah:**
• Ketik nomor (1, 2, 3) untuk pilih sistem
• Atau jelaskan lebih spesifik apa yang kamu cari
"""
        
        return formatted
    
    def format_help_response(self, help_type: str = 'general') -> str:
        """
        💡 Format help and guidance responses
        """
        
        if help_type == 'general':
            return self._generate_general_help()
        elif help_type == 'systems':
            return self._generate_systems_help()
        elif help_type == 'tips':
            return self._generate_tips_help()
        else:
            return self._generate_general_help()
    
    def _get_confidence_emoji(self, confidence: float) -> str:
        """Get emoji based on confidence level"""
        
        if confidence >= 0.8:
            return "🎯"  # High confidence
        elif confidence >= 0.6:
            return "🎪"  # Medium confidence  
        elif confidence >= 0.4:
            return "🤔"  # Low confidence
        else:
            return "❓"  # Very low confidence
    
    def _generate_footer(self, classification_result: Dict, system_type: str) -> str:
        """Generate metadata footer"""
        
        confidence = classification_result.get('confidence', 0.0)
        classification_type = classification_result.get('classification_type', 'unknown')
        
        footer = f"📊 **Metadata:** Confidence {confidence:.1%} • Type: {classification_type}"
        
        # Add tips for improvement
        if confidence < 0.6:
            footer += "\n💡 **Tip:** Gunakan kata kunci yang lebih spesifik untuk hasil yang lebih akurat"
        
        return footer
    
    def _generate_general_help(self) -> str:
        """Generate general help message"""
        
        return """🎯 **UNIFIED ACADEMIC ASSISTANT - BANTUAN**

🤖 **Selamat datang!** Aku bisa bantu kamu dengan 4 sistem spesialis:

📝 **Rules UAP** - Aturan ujian, sanksi, dan pelanggaran akademik
👥 **Assistant Search** - Data asisten, dosen, dan lokasi ruangan  
🖥️ **Practicum Rules** - Prosedur praktikum dan setup lab komputer
📋 **Correction & Case Making** - Koreksian dan pembuatan soal ujian

🚀 **Cara pakai:**
• Langsung tanya apa aja - aku akan otomatis route ke sistem yang tepat
• Kalau bingung, ketik nomor sistem (1, 2, 3, 4)
• Atau gunakan kata kunci spesifik untuk hasil yang lebih akurat

💡 **Tips:** Semakin spesifik query kamu, semakin akurat jawabannya!

📞 **Bantuan lain:**
• Ketik 'systems' untuk detail semua sistem
• Ketik 'tips' untuk tips penggunaan
• Ketik 'help' kapan aja untuk bantuan
"""
    
    def _generate_systems_help(self) -> str:
        """Generate detailed systems help"""
        
        help_text = """🎯 **DETAIL SISTEM YANG TERSEDIA**

"""
        
        system_details = {
            'rules_uap': {
                'description': 'Aturan ujian, sanksi, dan pelanggaran akademik',
                'examples': [
                    'Aturan menyontek di ujian',
                    'Sanksi plagiarisme', 
                    'Pelanggaran akademik'
                ]
            },
            'assistant_search': {
                'description': 'Data asisten, dosen, dan lokasi ruangan',
                'examples': [
                    'Siapa asisten di kampus Syahdan?',
                    'Kontak dosen matematika',
                    'Ruangan lab komputer'
                ]
            },
            'rules_mengajar': {
                'description': 'Prosedur praktikum dan setup lab komputer',
                'examples': [
                    'Cara setup lab komputer',
                    'Prosedur mengajar praktikum',
                    'Persiapan ruang lab'
                ]
            },
            'correction_casemaking': {
                'description': 'Koreksian dan pembuatan soal ujian',
                'examples': [
                    'Cara melakukan koreksian',
                    'Template case making',
                    'Submit ke Messier'
                ]
            }
        }
        
        for i, (system, style) in enumerate(self.system_styles.items(), 1):
            emoji = style['emoji']
            name = style['name']
            details = system_details.get(system, {})
            description = details.get('description', '')
            examples = details.get('examples', [])
            
            help_text += f"""{i}. {emoji} **{name}**
   📝 {description}
   
   💡 Contoh query:
"""
            for example in examples:
                help_text += f"   • \"{example}\"\n"
            
            help_text += "\n"
        
        return help_text
    
    def _generate_tips_help(self) -> str:
        """Generate usage tips"""
        
        return """💡 **TIPS PENGGUNAAN UNIFIED ASSISTANT**

🎯 **Untuk Query Yang Akurat:**
• Gunakan kata kunci yang spesifik
• Sebutkan konteks yang jelas (kampus, mata kuliah, dll)
• Kalau bisa, gunakan istilah akademik yang tepat

🔍 **Contoh Query Yang Baik:**
✅ "Aturan menyontek di ujian UAP" (spesifik)
❌ "aturan" (terlalu umum)

✅ "Asisten praktikum komputer di Syahdan" (konteks jelas)
❌ "asisten" (terlalu umum)

🎪 **Kalau Hasil Tidak Sesuai:**
• Coba kata kunci yang berbeda
• Tambahkan konteks lebih detail
• Atau pilih sistem manual dengan mengetik nomor (1-4)

🚀 **Fitur Pintar:**
• Aku bisa pahami bahasa natural Indonesia
• Aku akan otomatis route ke sistem yang tepat
• Kalau ragu, aku akan tanya klarifikasi

💬 **Butuh bantuan?** Ketik 'help' kapan aja!
"""
    
    def format_welcome_message(self) -> str:
        """Format welcome message for new users"""
        
        return """🎉 **SELAMAT DATANG DI UNIFIED ACADEMIC ASSISTANT!**

🤖 **Halo!** Aku adalah assistant yang bisa bantu kamu dengan berbagai kebutuhan akademik.

🎯 **Aku bisa bantu dengan:**
📝 Aturan ujian & sanksi akademik
👥 Info asisten & dosen
🖥️ Prosedur praktikum
📋 Koreksian & case making

💬 **Langsung aja tanya apa yang kamu butuhkan!**

💡 **Contoh:**
• "Bagaimana aturan ujian UAP?"
• "Siapa asisten di kampus Kemanggisan?"
• "Cara setup lab komputer"
• "Template koreksian"

📞 **Bantuan:** Ketik 'help' untuk panduan lengkap
"""

if __name__ == "__main__":
    # Test the response formatter
    print("🧪 Testing Response Formatter")
    print("=" * 50)
    
    formatter = ResponseFormatter()
    
    # Test system response formatting
    print("1. Testing system response formatting:")
    test_response = "Berikut adalah informasi yang kamu cari..."
    test_classification = {
        'system': 'rules_uap',
        'confidence': 0.85,
        'classification_type': 'high_confidence'
    }
    
    formatted = formatter.format_system_response(
        test_response, 'rules_uap', test_classification
    )
    print(formatted[:100] + "...")
    
    # Test error formatting
    print("\n2. Testing error formatting:")
    error_formatted = formatter.format_error_response(
        "Database connection failed", 'assistant_search', "siapa asisten"
    )
    print(error_formatted[:150] + "...")
    
    # Test help formatting
    print("\n3. Testing help formatting:")
    help_formatted = formatter.format_help_response('general')
    print(help_formatted[:200] + "...") 