import os
import json
import sys
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from crewai_tools import tool
from dotenv import load_dotenv
import logging

# Import global model configurations
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from unified_system.config.settings import get_embedding_model_config

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, GOOGLE_API_KEY]):
    raise ValueError("Missing required environment variables")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client initialized successfully")
except TypeError as e:
    if "proxy" in str(e):
        print("⚠️ Proxy argument error detected, trying alternative initialization...")
        try:
            import supabase as supabase_lib
            supabase: Client = supabase_lib.Client(SUPABASE_URL, SUPABASE_KEY)
            print("✅ Supabase client initialized with alternative method")
        except Exception as alt_e:
            print(f"❌ Alternative Supabase initialization failed: {alt_e}")
            supabase = None
    else:
        print(f"❌ Supabase initialization failed: {e}")
        supabase = None
except Exception as e:
    print(f"❌ Supabase initialization failed: {e}")
    supabase = None

try:
    embeddings = GoogleGenerativeAIEmbeddings(**get_embedding_model_config())
    print("✅ Google embeddings initialized successfully")
except Exception as e:
    print(f"❌ Google embeddings initialization failed: {e}")
    embeddings = None

@tool("search_rules_uap_semantic")
def search_rules_uap_semantic(
    query: str, 
    limit: int = 5,
    filter_keyword: Optional[str] = None,
    filter_category: Optional[str] = None
) -> str:
    """
    Search Rules & Procedure UAP using semantic similarity on KEYWORDS ONLY
    
    Strategy:
    1. Generate embedding for user query
    2. Find similar keywords via vector similarity 
    3. Extract content from metadata for response
    
    Args:
        query: Question or keyword about UAP rules (e.g., "aturan tentang ujian")
        limit: Maximum number of results to return
        filter_keyword: Optional filter for specific keywords
        filter_category: Optional filter for specific category
        
    Returns:
        JSON string with search results containing content from metadata
    """
    try:
        print(f"🔍 Semantic search for UAP rules: '{query}'")
        print(f"📊 Strategy: Search keyword similarity, extract content from metadata")
        print(f"📊 Parameters: limit={limit}, filter_keyword={filter_keyword}, filter_category={filter_category}")
        
        if supabase is None:
            return json.dumps({
                'error': 'Database connection not available',
                'query': query,
                'status': 'error'
            }, ensure_ascii=False, indent=2)
        
        if embeddings is None:
            return json.dumps({
                'error': 'Embeddings service not available',
                'query': query,
                'status': 'error'
            }, ensure_ascii=False, indent=2)
        
        query_embedding = embeddings.embed_query(query)
        print(f"✅ Generated query embedding: {len(query_embedding)} dimensions")
        
        search_result = supabase.rpc('match_rules_procedure_uap', {
            'query_embedding': query_embedding,
            'match_threshold': 0.7,  
            'match_count': limit,
            'filter_keyword': filter_keyword if filter_keyword else None,
            'filter_category': filter_category if filter_category else None
        }).execute()
        
        print(f"📊 Database returned {len(search_result.data) if search_result.data else 0} results")
        
        if search_result.data and len(search_result.data) > 0:
            rules_found = []
            for rule in search_result.data:
                metadata = rule.get('metadata', {})
                full_content = metadata.get('full_content', rule.get('content', ''))
                
                rule_info = {
                    'id': rule['id'],
                    'keyword': rule['keyword'],                     
                    'content': full_content,                         
                    'similarity': round(rule['similarity'], 3),     
                    'metadata': {
                        'content_length': len(full_content),
                        'keyword_length': len(rule['keyword']),
                        'source': metadata.get('source'),
                        'category': metadata.get('category'),
                        'embedding_strategy': metadata.get('embedding_strategy')
                    },
                    'created_at': rule.get('created_at')
                }
                rules_found.append(rule_info)
            
            response = {
                'query': query,
                'results_count': len(rules_found),
                'search_strategy': 'keyword_embedding_similarity',
                'content_source': 'metadata.full_content',
                'search_params': {
                    'limit': limit,
                    'filter_keyword': filter_keyword,
                    'filter_category': filter_category
                },
                'rules': rules_found,
                'status': 'success'
            }
            
            print(f"✅ Found {len(rules_found)} matching rules via keyword similarity")
            return json.dumps(response, ensure_ascii=False, indent=2)
        else:
            return json.dumps({
                'query': query,
                'results_count': 0,
                'rules': [],
                'message': 'No rules found matching your query',
                'search_strategy': 'keyword_embedding_similarity',
                'status': 'success'
            }, ensure_ascii=False, indent=2)
            
    except Exception as e:
        error_response = {
            'error': f"Search error: {str(e)}",
            'query': query,
            'search_strategy': 'keyword_embedding_similarity',
            'status': 'error'
        }
        print(f"❌ Semantic search error: {str(e)}")
        return json.dumps(error_response, ensure_ascii=False, indent=2)
