import os
from dotenv import load_dotenv
from supabase import create_client, Client
from google.generativeai import embed_content
import google.generativeai as genai
from crewai_tools import tool

# Load environment variables
load_dotenv()

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Changed from SUPABASE_SERVICE_ROLE_KEY

# Initialize clients
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_query_embedding(query_text: str) -> list:
    """Generate embedding for search query"""
    try:
        result = embed_content(
            model="models/embedding-001",
            content=query_text,
            task_type="retrieval_query"
        )
        return result['embedding']
    except Exception as e:
        print(f"❌ Embedding error for query '{query_text}': {str(e)}")
        return None

@tool("search_practicum_rules_semantic")
def search_practicum_rules_semantic(query: str, match_threshold: float = 0.5, match_count: int = 5) -> str:
    """
    Search practicum rules using semantic similarity.
    
    Parameters:
    - query: Natural language search query about practicum rules/procedures
    - match_threshold: Minimum similarity score (0.0-1.0), default 0.5
    - match_count: Maximum number of results to return, default 5
    
    Example queries:
    - "cara mengambil kunci ruangan"
    - "prosedur sebelum mengajar"
    - "aturan tentang Ruman"
    - "apa yang harus dilakukan sesudah mengajar"
    """
    
    try:
        print(f"🔍 Semantic search for practicum rules: '{query}'")
        
        # Generate embedding for the query
        query_embedding = generate_query_embedding(query)
        if query_embedding is None:
            return "❌ Error: Could not generate embedding for the search query."
        
        # Execute similarity search using database function
        result = supabase.rpc('match_practicum_rules', {
            'query_embedding': query_embedding,
            'match_threshold': match_threshold,
            'match_count': match_count
        }).execute()
        
        if not result.data:
            return f"❌ No practicum rules found matching '{query}' with threshold {match_threshold}. Try lowering the threshold or use different keywords."
        
        # Format results
        response = f"📚 Found {len(result.data)} practicum rules matching '{query}':\n\n"
        
        for i, rule in enumerate(result.data, 1):
            keyword = rule['keyword']
            content = rule['content']
            similarity = rule['similarity']
            
            response += f"{i}. **{keyword}** (similarity: {similarity:.3f})\n"
            response += f"   📝 {content}\n\n"
        
        return response
        
    except Exception as e:
        error_msg = f"❌ Semantic search error: {str(e)}"
        print(error_msg)
        return error_msg

@tool("search_practicum_rules_keyword")
def search_practicum_rules_keyword(keyword: str, match_count: int = 5) -> str:
    """
    Search practicum rules using keyword/text matching.
    
    Parameters:
    - keyword: Specific keyword or phrase to search for
    - match_count: Maximum number of results to return, default 5
    
    Example keywords:
    - "mengajar"
    - "ruangan"
    - "kunci"
    - "ruman"
    - "telat"
    """
    
    try:
        print(f"🔎 Keyword search for practicum rules: '{keyword}'")
        
        # Execute keyword search using database function
        result = supabase.rpc('search_practicum_rules_keyword', {
            'search_keyword': keyword,
            'match_count': match_count
        }).execute()
        
        if not result.data:
            return f"❌ No practicum rules found containing keyword '{keyword}'. Try different keywords or use semantic search."
        
        # Format results
        response = f"🔑 Found {len(result.data)} practicum rules containing '{keyword}':\n\n"
        
        for i, rule in enumerate(result.data, 1):
            rule_keyword = rule['keyword']
            content = rule['content']
            
            response += f"{i}. **{rule_keyword}**\n"
            response += f"   📝 {content}\n\n"
        
        return response
        
    except Exception as e:
        error_msg = f"❌ Keyword search error: {str(e)}"
        print(error_msg)
        return error_msg

@tool("browse_all_practicum_rules")
def browse_all_practicum_rules() -> str:
    """
    Retrieve all practicum rules for browsing.
    
    Use this when user wants to see all available practicum rules or when 
    search queries return no results and you want to show what's available.
    """
    
    try:
        print("📋 Browsing all practicum rules...")
        
        # Get all rules using database function
        result = supabase.rpc('get_all_practicum_rules').execute()
        
        if not result.data:
            return "❌ No practicum rules found in database."
        
        # Format results
        response = f"📚 All Practicum Rules ({len(result.data)} total):\n\n"
        
        for i, rule in enumerate(result.data, 1):
            keyword = rule['keyword']
            content = rule['content']
            
            response += f"{i}. **{keyword}**\n"
            response += f"   📝 {content}\n\n"
        
        return response
        
    except Exception as e:
        error_msg = f"❌ Browse error: {str(e)}"
        print(error_msg)
        return error_msg

@tool("get_practicum_rules_stats")
def get_practicum_rules_stats() -> str:
    """
    Get statistics about the practicum rules database.
    
    Useful for understanding the scope and coverage of available rules.
    """
    
    try:
        print("📊 Getting practicum rules statistics...")
        
        # Get stats using database function
        result = supabase.rpc('get_practicum_rules_stats').execute()
        
        if not result.data:
            return "❌ Could not retrieve statistics."
        
        stats = result.data[0]
        
        response = "📊 **Practicum Rules Database Statistics:**\n\n"
        response += f"📚 Total rules: {stats['total_rules']}\n"
        response += f"📏 Average keyword length: {stats['avg_keyword_length']:.1f} characters\n"
        response += f"📄 Average content length: {stats['avg_content_length']:.1f} characters\n"
        
        if stats['categories']:
            response += f"🏷️  Categories: {', '.join(stats['categories'])}\n"
        
        response += "\n💡 Available search methods:\n"
        response += "- Semantic search: search_practicum_rules_semantic\n"
        response += "- Keyword search: search_practicum_rules_keyword\n"
        response += "- Browse all: browse_all_practicum_rules\n"
        
        return response
        
    except Exception as e:
        error_msg = f"❌ Stats error: {str(e)}"
        print(error_msg)
        return error_msg

# Export tools for easy import
practicum_search_tools = [
    search_practicum_rules_semantic,
    search_practicum_rules_keyword,
    browse_all_practicum_rules,
    get_practicum_rules_stats
]

if __name__ == "__main__":
    # Test the tools
    print("🧪 Testing Practicum Search Tools")
    print("=" * 40)
    
    # Test semantic search
    print("\n1. Testing semantic search...")
    result = search_practicum_rules_semantic("cara mengambil kunci ruangan")
    print(result[:200] + "..." if len(result) > 200 else result)
    
    # Test keyword search
    print("\n2. Testing keyword search...")
    result = search_practicum_rules_keyword("mengajar")
    print(result[:200] + "..." if len(result) > 200 else result)
    
    # Test browse all
    print("\n3. Testing browse all...")
    result = browse_all_practicum_rules()
    print(result[:200] + "..." if len(result) > 200 else result)
    
    # Test stats
    print("\n4. Testing stats...")
    result = get_practicum_rules_stats()
    print(result) 