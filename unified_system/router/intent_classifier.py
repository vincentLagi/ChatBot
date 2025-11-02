"""
Smart Intent Classifier for Unified Academic Assistant
Intelligently routes user queries to appropriate specialized systems

Features:
- Multi-stage classification (keyword + semantic)
- Confidence scoring
- Ambiguity detection
- Performance optimized
"""

import os
import re
from typing import Dict, List, Tuple
from dotenv import load_dotenv
from google.generativeai import embed_content
import google.generativeai as genai

# Load environment variables
load_dotenv()

class SmartIntentRouter:
    """
    🧠 Intelligent query classifier for routing to specialized systems
    
    Classification Strategy:
    1. Fast keyword matching (μs speed)
    2. Semantic analysis (only if needed)
    3. Confidence scoring & decision making
    """
    
    def __init__(self):
        """Initialize the intent classifier with keyword patterns and system descriptions"""
        
        # Initialize Google AI for embeddings
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        if GOOGLE_API_KEY:
            genai.configure(api_key=GOOGLE_API_KEY)
        
        # System keyword patterns for fast classification
        self.system_patterns = {
            'rules_uap': {
                'keywords': [
                    # Indonesian terms
                    'ujian', 'menyontek', 'sanksi', 'pelanggaran', 'aturan ujian',
                    'exam', 'cheat', 'punishment', 'violation', 'exam rules',
                    'akademik', 'integrity', 'cheating', 'academic misconduct',
                    'plagiarisme', 'fraud', 'disciplinary', 'tindakan', 'larangan',
                    # UAP specific
                    'uap', 'final exam', 'ujian akhir'
                ],
                'weight': 1.0
            },
            'assistant_search': {
                'keywords': [
                    # Indonesian terms
                    'asisten', 'dosen', 'ruangan', 'lokasi', 'contact', 'staff',
                    'assistant', 'lecturer', 'room', 'location', 'teacher',
                    'pengajar', 'instruktur', 'fakultas', 'kontak', 'telepon',
                    'email', 'alamat', 'lab assistant', 'teaching assistant',
                    # Location specific
                    'syahdan', 'kemanggisan', 'alam sutera', 'senayan', 'campus'
                ],
                'weight': 1.0
            },
            'rules_mengajar': {
                'keywords': [
                    # Indonesian terms
                    'praktikum', 'lab', 'computer', 'teaching', 'setup', 'kunci',
                    'practicum', 'laboratory', 'computer lab', 'room key',
                    'laboratorium', 'ruang komputer', 'persiapan', 'mengajar',
                    'prosedur', 'preparation', 'classroom', 'equipment',
                    # Specific terms
                    'ruman', '724', 'komputer', 'projector', 'setup ruangan'
                ],
                'weight': 1.0
            },
            'correction_casemaking': {
                'keywords': [
                    # Indonesian terms
                    'koreksian', 'case making', 'template', 'messier', 'deadline',
                    'marking', 'grading', 'soal ujian', 'exam questions',
                    'pembuatan soal', 'koreksi', 'penilaian', 'template soal',
                    'submit queue', 'academic.slc.net', 'subco', 'approval',
                    # System specific
                    'binusmaya', 'academic', 'queue', 'submission', 'briefing'
                ],
                'weight': 1.0
            },
            'job_query': {
                'keywords': [
                    # Indonesian terms
                    'job', 'jobs', 'pekerjaan', 'kerja', 'tugas', 'jadwal',
                    'schedule', 'teaching', 'case making', 'praktikum', 'lab',
                    'mengajar', 'assistant', 'today', 'tomorrow', 'hari ini',
                    'besok', 'have work', 'ada kerja', 'ada job', 'work schedule',
                    'jadwal kerja', 'jadwal assistant', 'working', 'availability',
                    # Assistant codes
                    'ka24', 'ir23', 'lo24', 'zn22', 'ru24', 'assistant code',
                    # Time related
                    'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                    'senin', 'selasa', 'rabu', 'kamis', 'jumat', 'weekend'
                ],
                'weight': 1.0
            },
            'material_criteria': {
                'keywords': [
                    # Indonesian terms
                    'material', 'criteria', 'materi', 'kriteria', 'download',
                    'link', 'course', 'mata kuliah', 'matkul', 'course material',
                    'course criteria', 'assignment', 'tugas', 'project', 'quiz',
                    'ujian', 'exam', 'tm1', 'tm2', 'pry', 'uap',
                    # Assessment types
                    'mid term', 'final exam', 'praktikum', 'lab assessment',
                    'tugas besar', 'project assignment', 'quiz 1', 'quiz 2',
                    'ujian akhir', 'final', 'assessment', 'evaluation',
                    # Course codes
                    'comp', 'isys', 'mobi', 'math', 'scie', 'cpen',
                    'comp6048', 'comp6051', 'comp6064', 'comp6114', 'comp6115',
                    # Common requests
                    'sharepoint', 'binus', 'binusianorg', 'file', 'pdf',
                    'download link', 'link download', 'material download'
                ],
                'weight': 1.0
            },
            'find_room': {
                'keywords': [
                    # Indonesian terms
                    'ruangan', 'room', 'kosong', 'empty', 'tersedia', 'available',
                    'jadwal ruangan', 'room schedule', 'peminjaman ruangan', 'room booking',
                    'shift', 'cari ruangan', 'find room', 'ruang kosong', 'empty room',
                    'ketersediaan ruangan', 'room availability', 'status ruangan', 'room status',
                    # Room numbers
                    '601', '602', '603', '604', '605', '606', '607', '608', '609', '610',
                    '621', '622', '623', '624', '625', '626', '627', '628', '629',
                    '706', '707', '708', '709', '710', '721', '722', '723', '724', '725',
                    '727', '728', '729', '730', '731', 'ruangan 6', 'ruangan 7',
                    # Schedule related
                    'hari ini', 'besok', 'today', 'tomorrow', 'shift 1', 'shift 2', 'shift 3',
                    'shift 4', 'shift 5', 'shift 6', 'shift 7', 'ada jadwal', 'tidak ada jadwal',
                    'terisi', 'occupied', 'tidak terisi', 'not occupied', 'bebas',
                    # Common queries
                    'ruangan mana yang kosong', 'which room is empty', 'ada ruangan kosong',
                    'cek ruangan', 'check room', 'lihat jadwal ruangan', 'see room schedule'
                ],
                'weight': 1.0
            }
        }
        
        # System descriptions for semantic analysis
        self.system_descriptions = {
            'rules_uap': "exam rules violations sanctions academic integrity cheating plagiarism disciplinary actions final exam UAP",
            'assistant_search': "teaching assistants lecturers staff contact information location room faculty instructor email phone campus",
            'rules_mengajar': "computer lab practicum procedures setup teaching laboratory preparation classroom equipment room key mengajar",
            'correction_casemaking': "grading marking case making exam creation deadlines template submission queue messier academic platform subco approval",
            'job_query': "assistant job schedule work availability teaching case making practicum lab today tomorrow date specific assistant username",
            'material_criteria': "course materials criteria download links assignments quizzes projects final exams TM1 TM2 PRY UAP assessment evaluation SharePoint course codes",
            'find_room': "room availability schedule empty rooms booking shift time room numbers 601-731 check availability today tomorrow occupied free"
        }
        
        # Confidence thresholds
        self.high_confidence_threshold = 0.7
        self.medium_confidence_threshold = 0.4
        self.ambiguous_threshold = 0.3
        
        print("🧠 Smart Intent Router initialized successfully!")
    
    def classify_intent(self, query: str) -> Dict:
        """
        🎯 Main classification method
        
        Args:
            query: User query string
            
        Returns:
            Dict with classification result including system, confidence, and metadata
        """
        
        print(f"🔍 Classifying intent for: '{query}'")
        
        # Stage 1: Fast keyword classification
        keyword_scores = self._keyword_classification(query)
        best_keyword_score = max(keyword_scores.values()) if keyword_scores else 0.0
        
        print(f"📊 Keyword scores: {keyword_scores}")
        
        # Stage 2: Semantic classification (if needed)
        final_scores = keyword_scores
        used_semantic = False
        
        if best_keyword_score < self.high_confidence_threshold:
            print("🧠 Running semantic analysis for better accuracy...")
            semantic_scores = self._semantic_classification(query)
            final_scores = self._combine_scores(keyword_scores, semantic_scores)
            used_semantic = True
            print(f"🔬 Semantic scores: {semantic_scores}")
            print(f"⚖️ Combined scores: {final_scores}")
        
        # Stage 3: Decision making
        decision = self._make_decision(final_scores, query)
        decision['used_semantic'] = used_semantic
        decision['keyword_scores'] = keyword_scores
        
        print(f"✅ Classification result: {decision['system']} (confidence: {decision['confidence']:.3f})")
        
        return decision
    
    def _keyword_classification(self, query: str) -> Dict[str, float]:
        """
        🔍 Fast keyword-based classification
        """
        
        query_lower = query.lower()
        # Remove punctuation and normalize
        query_clean = re.sub(r'[^\w\s]', ' ', query_lower)
        query_words = set(query_clean.split())
        
        scores = {}
        
        for system, config in self.system_patterns.items():
            keywords = config['keywords']
            weight = config['weight']
            
            # Count exact matches
            exact_matches = sum(1 for kw in keywords if kw in query_lower)
            
            # Count word matches  
            word_matches = sum(1 for kw in keywords if kw in query_words)
            
            # Calculate score with bonus for exact matches
            total_keywords = len(keywords)
            exact_score = exact_matches / total_keywords if total_keywords > 0 else 0
            word_score = word_matches / total_keywords if total_keywords > 0 else 0
            
            # Combined score with preference for exact matches
            combined_score = (exact_score * 1.5 + word_score) / 2.5
            scores[system] = combined_score * weight
        
        return scores
    
    def _semantic_classification(self, query: str) -> Dict[str, float]:
        """
        🧠 Semantic similarity classification using embeddings
        """
        
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            if query_embedding is None:
                print("❌ Failed to generate query embedding, falling back to keyword scores")
                return {}
            
            scores = {}
            
            for system, description in self.system_descriptions.items():
                # Generate description embedding
                desc_embedding = self._generate_embedding(description)
                if desc_embedding is None:
                    continue
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, desc_embedding)
                scores[system] = max(0.0, similarity)  # Ensure non-negative
            
            return scores
            
        except Exception as e:
            print(f"❌ Semantic classification error: {e}")
            return {}
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using Google Generative AI"""
        
        try:
            result = embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_query"
            )
            return result['embedding']
            
        except Exception as e:
            print(f"❌ Embedding generation error for '{text[:50]}...': {e}")
            return None
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        
        try:
            # Dot product
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            
            # Magnitudes
            magnitude1 = sum(a * a for a in vec1) ** 0.5
            magnitude2 = sum(b * b for b in vec2) ** 0.5
            
            # Cosine similarity
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            return dot_product / (magnitude1 * magnitude2)
            
        except Exception as e:
            print(f"❌ Cosine similarity calculation error: {e}")
            return 0.0
    
    def _combine_scores(self, keyword_scores: Dict[str, float], semantic_scores: Dict[str, float]) -> Dict[str, float]:
        """
        ⚖️ Combine keyword and semantic scores with weighted average
        """
        
        combined = {}
        all_systems = set(keyword_scores.keys()) | set(semantic_scores.keys())
        
        # Weights: keyword gets more weight for exact matches, semantic for understanding
        keyword_weight = 0.6
        semantic_weight = 0.4
        
        for system in all_systems:
            kw_score = keyword_scores.get(system, 0.0)
            sem_score = semantic_scores.get(system, 0.0)
            
            combined[system] = (kw_score * keyword_weight) + (sem_score * semantic_weight)
        
        return combined
    
    def _make_decision(self, scores: Dict[str, float], query: str) -> Dict:
        """
        🎯 Final decision making with confidence calculation
        """
        
        if not scores:
            return {
                'system': 'ambiguous',
                'confidence': 0.0,
                'query': query,
                'reason': 'No classification scores available'
            }
        
        # Sort scores
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_system, best_score = sorted_scores[0]
        second_best_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0.0
        
        # Calculate confidence based on score and gap
        score_gap = best_score - second_best_score
        confidence = min(1.0, (best_score + score_gap) / 2)
        
        # Determine classification quality
        if best_score < self.ambiguous_threshold:
            classification_type = 'ambiguous'
            system = 'ambiguous'
        elif confidence < self.medium_confidence_threshold:
            classification_type = 'low_confidence'
            system = best_system
        elif confidence < self.high_confidence_threshold:
            classification_type = 'medium_confidence'
            system = best_system
        else:
            classification_type = 'high_confidence'
            system = best_system
        
        return {
            'system': system,
            'confidence': confidence,
            'classification_type': classification_type,
            'score': best_score,
            'score_gap': score_gap,
            'all_scores': dict(sorted_scores),
            'query': query,
            'reason': f"Best score: {best_score:.3f}, Gap: {score_gap:.3f}"
        }
    
    def get_system_suggestions(self, query: str) -> List[str]:
        """
        💡 Get system suggestions for ambiguous queries
        """
        
        scores = self._keyword_classification(query)
        # Return systems with scores above minimum threshold
        suggestions = [
            system for system, score in scores.items() 
            if score > 0.1  # Minimum threshold for suggestions
        ]
        
        # Sort by score
        suggestions.sort(key=lambda x: scores[x], reverse=True)
        
        return suggestions[:3]  # Top 3 suggestions

if __name__ == "__main__":
    # Test the intent classifier
    print("🧪 Testing Smart Intent Router")
    print("=" * 50)
    
    router = SmartIntentRouter()
    
    test_queries = [
        "Bagaimana cara melakukan koreksian?",
        "Siapa asisten yang mengajar di kampus Syahdan?",
        "Aturan menyontek di ujian",
        "Setup computer lab untuk praktikum",
        "deadline template",  # Ambiguous
        "ruangan"  # Ambiguous
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        result = router.classify_intent(query)
        print(f"Result: {result['system']} (confidence: {result['confidence']:.3f})")
        print(f"Type: {result['classification_type']}")
        print("-" * 40) 