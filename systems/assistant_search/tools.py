import os
import sys
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
from crewai_tools import tool
import json

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY]):
    raise ValueError("Missing required environment variables: SUPABASE_URL, SUPABASE_KEY")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client initialized successfully")
except Exception as e:
    print(f"❌ Supabase initialization failed: {e}")
    supabase = None

ALLOWED_COLUMNS = [
    "initial", "gen", "initial_gen", "name", "binusian_id", "nim", "email_edu", "email_ac_id",
    "leader", "major_long", "major", "streaming", "semester", "global", "location", "position", "shift"
]

@tool("search_assistant_multi_column") 
def search_assistant_multi_column(
    filters: Dict[str, Any], 
    limit: int = 100
) -> str:
    """ tesdaafasf """
    try:
        print(f"🔍 Multi-column search with filters: {filters}")
        
        if supabase is None:
            return json.dumps({
                "status": "error",
                "message": "Database connection not available"
            }, indent=2)
            
        if not filters:
            return json.dumps({
                "status": "error",
                "message": "No filters provided",
                "allowed_columns": ALLOWED_COLUMNS
            }, indent=2)
            
        processed_filters = []
        ALLOWED_OPERATORS = {
            'eq': 'eq', 'gt': 'gt', 'lt': 'lt', 'gte': 'gte', 'lte': 'lte', 'ilike': 'ilike'
        }
        
        for col, filter_val in filters.items():
            if col not in ALLOWED_COLUMNS:
                logger.warning(f"Column '{col}' is not allowed.")
                continue
                
            operator = 'ilike'
            value = filter_val
            
            if isinstance(filter_val, dict):
                op = filter_val.get('operator')
                val = filter_val.get('value')
                if op and val is not None:
                    if op in ALLOWED_OPERATORS:
                        operator = op
                        value = val
                    else:
                        logger.warning(f"Invalid operator '{op}' for column '{col}'.")
                        continue
                else:
                    logger.warning(f"Malformed filter for column '{col}'.")
                    continue
                    
            if value is not None and str(value).strip() != '':
                processed_filters.append({'column': col, 'operator': operator, 'value': value})
                
        if not processed_filters:
            return json.dumps({
                "status": "error",
                "message": "No valid filters provided after processing",
                "allowed_columns": ALLOWED_COLUMNS
            }, indent=2)
            
        query = supabase.table('assistant_csv').select('*')
        
        for f in processed_filters:
            col = f['column']
            op = f['operator']
            val = f['value']
            
            if op == 'ilike':
                query = query.ilike(col, f"%{val}%")
            else:
                query_method = getattr(query, op)
                query = query_method(col, val)
                
        query = query.limit(limit)
        result = query.execute()
        
        if not result.data:
            return json.dumps({
                "status": "no_results",
                "message": f"No assistant found for filters: {processed_filters}",
                "filters": processed_filters,
                "total_results": 0,
                "results": []
            }, indent=2)
            
        print(f"✅ Found {len(result.data)} assistant(s)")
        return json.dumps({
            "status": "success",
            "message": f"Found {len(result.data)} assistant(s) for filters: {processed_filters}",
            "filters": processed_filters,
            "total_results": len(result.data),
            "results": result.data
        }, indent=2)
        
    except Exception as e:
        print(f"❌ Multi-column search error: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Query failed: {str(e)}",
            "filters": filters,
            "total_results": 0,
            "results": []
        }, indent=2)

