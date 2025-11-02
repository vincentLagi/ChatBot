#!/usr/bin/env python3
"""
Material and Criteria Search Tools
LangChain tools for searching course materials and criteria from Supabase
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
from google.generativeai import embed_content
import google.generativeai as genai
from langchain.tools import tool
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

# Initialize clients
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None
    logger.warning("Supabase not configured - material criteria search will be limited")

class MaterialCriteriaSearchEngine:
    """Material and Criteria search engine using Supabase"""
    
    def __init__(self):
        self.supabase = supabase
        self.google_api_key = GOOGLE_API_KEY
    
    def generate_query_embedding(self, query: str) -> Optional[List[float]]:
        """Generate embedding for query using Google API"""
        if not self.google_api_key:
            logger.error("Google API key not configured")
            return None
        
        try:
            result = embed_content(
                model="models/embedding-001",
                content=query,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            return None
    
    def search_materials(self, query: str, top_k: int = 5, min_similarity: float = 0.5) -> List[Dict]:
        """Search for materials based on query using semantic similarity"""
        if not self.supabase:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.generate_query_embedding(query)
            if query_embedding is None:
                # Fallback to keyword search
                return self.search_materials_keyword(query, top_k)
            
            # Search using semantic similarity
            result = self.supabase.rpc('match_material_criteria', {
                'query_embedding': query_embedding,
                'match_threshold': min_similarity,
                'match_count': 3
            }).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error searching materials: {e}")
            # Fallback to keyword search
            return self.search_materials_keyword(query, top_k)
    
    def search_materials_keyword(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for materials using keyword search"""
        if not self.supabase:
            return []
        
        try:
            result = self.supabase.rpc('search_material_criteria_keyword', {
                'search_keyword': query,
                'match_count': top_k
            }).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error in keyword search: {e}")
            return []
    
    def get_all_materials_for_course(self, course_identifier: str) -> List[Dict]:
        """Get all materials for a specific course"""
        if not self.supabase:
            return []
        
        try:
            result = self.supabase.rpc('get_all_course_materials', {
                'course_identifier': course_identifier
            }).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error getting course materials: {e}")
            return []
    
    def search_by_type(self, type_code: str, course_filter: str = None) -> List[Dict]:
        """Search materials by type"""
        if not self.supabase:
            return []
        
        try:
            result = self.supabase.rpc('search_material_criteria_by_type', {
                'assessment_type': type_code,
                'course_filter': course_filter,
                'match_count': 10
            }).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error searching by type: {e}")
            return []

# Initialize search engine
search_engine = MaterialCriteriaSearchEngine()

@tool
def search_course_materials(query: str) -> str:
    """
    Search for course materials and criteria based on course code, course name, or type.
    
    Args:
        query: Search query (e.g., "COMP6048 quiz 1", "Data Structures TM1", "Web Programming project")
    
    Returns:
        String containing search results with course information and download links
    """
    try:
        # Search for materials
        results = search_engine.search_materials(query, top_k=10)
        
        if not results:
            return f"Tidak ditemukan material untuk query: '{query}'. Pastikan nama course code atau nama mata kuliah benar."
        
        # Format results
        response = f"✅ Ditemukan {len(results)} material untuk query '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            course_code = result['course_code']
            course_name = result['course_name']
            type_code = result['type']
            link = result['link_download']
            similarity = result.get('similarity', 1.0)
            
            # Map type codes to Indonesian descriptions
            type_descriptions = {
                'TM1': 'Quiz 1 (Mid Term 1)',
                'TM2': 'Quiz 2 (Mid Term 2)',
                'PRY': 'Project (Tugas Besar)',
                'UAP': 'UAP (Ujian Akhir Praktikum)'
            }
            
            type_desc = type_descriptions.get(type_code, type_code)
            
            response += f"{i}. **{course_code} - {course_name}**\n"
            response += f"   📋 Type: {type_desc}\n"
            response += f"   🔗 Link Download: {link}\n"
            response += f"   📊 Similarity: {similarity:.2f}\n\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error in search_course_materials: {e}")
        return f"Terjadi error saat mencari material: {str(e)}"

@tool
def get_all_course_materials(course_identifier: str) -> str:
    """
    Get all available materials for a specific course (all types: TM1, TM2, PRY, UAP).
    
    Args:
        course_identifier: Course code or course name (e.g., "COMP6048", "Data Structures")
    
    Returns:
        String containing all materials for the course
    """
    try:
        # Get all materials for the course
        results = search_engine.get_all_materials_for_course(course_identifier)
        
        if not results:
            return f"Tidak ditemukan material untuk course: '{course_identifier}'. Pastikan course code atau nama mata kuliah benar."
        
        # Group by course
        course_materials = {}
        for result in results:
            course_key = f"{result['course_code']} - {result['course_name']}"
            if course_key not in course_materials:
                course_materials[course_key] = []
            course_materials[course_key].append(result)
        
        # Format response
        response = f"✅ Semua material tersedia untuk '{course_identifier}':\n\n"
        
        for course_key, materials in course_materials.items():
            response += f"**{course_key}**\n"
            
            # Sort by type order (already sorted by database function)
            for material in materials:
                type_code = material['type']
                link = material['link_download']
                
                # Map type codes to Indonesian descriptions
                type_descriptions = {
                    'TM1': 'Quiz 1 (Mid Term 1)',
                    'TM2': 'Quiz 2 (Mid Term 2)',
                    'PRY': 'Project (Tugas Besar)',
                    'UAP': 'UAP (Ujian Akhir Praktikum)'
                }
                
                type_desc = type_descriptions.get(type_code, type_code)
                
                response += f"  📋 {type_desc}\n"
                response += f"  🔗 {link}\n\n"
            
            response += "---\n\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error in get_all_course_materials: {e}")
        return f"Terjadi error saat mengambil material: {str(e)}"

@tool
def search_by_type(type_code: str, course_filter: str = "") -> str:
    """
    Search materials by type (TM1, TM2, PRY, UAP) with optional course filter.
    
    Args:
        type_code: Type code (TM1, TM2, PRY, UAP)
        course_filter: Optional course code or name filter
    
    Returns:
        String containing materials of the specified type
    """
    try:
        # Search by type
        results = search_engine.search_by_type(type_code, course_filter if course_filter else None)
        
        if not results:
            filter_text = f" dengan filter '{course_filter}'" if course_filter else ""
            return f"Tidak ditemukan material dengan type '{type_code}'{filter_text}."
        
        # Map type codes to Indonesian descriptions
        type_descriptions = {
            'TM1': 'Quiz 1 (Mid Term 1)',
            'TM2': 'Quiz 2 (Mid Term 2)',
            'PRY': 'Project (Tugas Besar)',
            'UAP': 'UAP (Ujian Akhir Praktikum)'
        }
        
        type_desc = type_descriptions.get(type_code.upper(), type_code)
        filter_text = f" dengan filter '{course_filter}'" if course_filter else ""
        
        response = f"✅ Ditemukan {len(results)} material {type_desc}{filter_text}:\n\n"
        
        for i, result in enumerate(results, 1):
            course_code = result['course_code']
            course_name = result['course_name']
            link = result['link_download']
            
            response += f"{i}. **{course_code} - {course_name}**\n"
            response += f"   🔗 Link Download: {link}\n\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error in search_by_type: {e}")
        return f"Terjadi error saat mencari material berdasarkan type: {str(e)}"

# List of available tools
material_criteria_tools = [
    search_course_materials,
    # get_all_course_materials,
    # search_by_type
] 