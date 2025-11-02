#!/usr/bin/env python3
"""
Embed Correction and Case Making Script
Process CorrectionAndCaseMaking.csv and store in Supabase with embeddings

Strategy: Keyword-only embedding (same as other rules)
- Embed only the keyword/phrase (embed column)
- Store full content in database for retrieval
"""

import pandas as pd
import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
from google.generativeai import embed_content
import google.generativeai as genai
import json
from datetime import datetime
import uuid

# Load environment variables
load_dotenv()

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
# Try service role key first, fallback to regular key
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

if not all([GOOGLE_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
    print("❌ Missing required environment variables!")
    print("Required: GOOGLE_API_KEY, SUPABASE_URL, SUPABASE_KEY (or SUPABASE_SERVICE_KEY)")
    print("💡 Note: For database insertion, service role key is preferred")
    sys.exit(1)

# Initialize clients
genai.configure(api_key=GOOGLE_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def load_correction_casemaking_csv():
    """Load and validate the correction & case making CSV file"""
    
    csv_file = "CorrectionAndCaseMaking.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return None
    
    try:
        # Read CSV with comma delimiter and handle potential trailing commas
        df = pd.read_csv(csv_file, delimiter=',', quotechar='"', skipinitialspace=True)
        print(f"📁 Loaded CSV: {csv_file}")
        print(f"📊 Shape: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Clean column names (remove trailing spaces/commas)
        df.columns = df.columns.str.strip()
        
        # Validate required columns
        required_columns = ['embed', 'Content']
        available_columns = [col for col in df.columns if col in required_columns]
        
        if len(available_columns) != len(required_columns):
            print(f"❌ Missing required columns: {required_columns}")
            print(f"Available columns: {list(df.columns)}")
            return None
        
        # Clean and validate data
        df = df.dropna(subset=['embed', 'Content'])
        df['embed'] = df['embed'].str.strip()
        df['Content'] = df['Content'].str.strip()
        
        # Replace newlines in content with spaces for better processing
        df['Content'] = df['Content'].str.replace('\n', ' ').str.replace('\r', ' ')
        
        # Remove completely empty rows
        df = df[(df['embed'] != '') & (df['Content'] != '')]
        
        print(f"✅ Cleaned data: {len(df)} valid rows")
        
        # Show sample data for verification
        print(f"\n📋 Sample data:")
        for i, row in df.head(3).iterrows():
            print(f"{i+1}. Embed: '{row['embed']}'")
            print(f"   Content: {row['Content'][:80]}...")
            print()
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading CSV: {str(e)}")
        return None

def generate_embedding(text: str) -> list:
    """Generate embedding using Google Generative AI"""
    
    try:
        result = embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    
    except Exception as e:
        print(f"❌ Embedding error for '{text}': {str(e)}")
        return None

def clear_existing_data():
    """Clear existing correction & case making data"""
    
    try:
        result = supabase.table('correction_casemaking_documents').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print(f"🗑️  Cleared existing correction & case making data")
        return True
        
    except Exception as e:
        error_str = str(e)
        print(f"❌ Error clearing data: {error_str}")
        if "row-level security policy" in error_str.lower():
            print("💡 TIP: This might be a permissions issue. You may need:")
            print("   - SUPABASE_SERVICE_KEY instead of SUPABASE_KEY")
            print("   - Or disable RLS on the correction_casemaking_documents table")
        return False

def determine_procedure_type(keyword: str) -> str:
    """Determine if the procedure is for correction or case making"""
    
    keyword_lower = keyword.lower()
    
    if any(term in keyword_lower for term in ['koreks', 'correction', 'marking']):
        return 'correction'
    elif any(term in keyword_lower for term in ['case', 'making', 'soal']):
        return 'case_making'
    else:
        return 'general'

def insert_correction_casemaking_procedure(keyword: str, content: str, embedding: list) -> bool:
    """Insert a single correction & case making procedure with embedding"""
    
    try:
        # Determine procedure type
        procedure_type = determine_procedure_type(keyword)
        
        # Prepare metadata
        metadata = {
            "keyword_length": len(keyword),
            "content_length": len(content),
            "source": "CorrectionAndCaseMaking.csv",
            "category": "Correction_CaseMaking",
            "procedure_type": procedure_type,
            "embedding_strategy": "keyword_only",
            "full_content": content  # Store full content in metadata
        }
        
        # Generate UUID
        procedure_id = str(uuid.uuid4())
        
        # Insert to database
        result = supabase.table('correction_casemaking_documents').insert({
            "id": procedure_id,
            "keyword": keyword,
            "content": content,
            "embedding": embedding,
            "metadata": metadata
        }).execute()
        
        return True
        
    except Exception as e:
        error_str = str(e)
        print(f"❌ Error inserting procedure '{keyword}': {error_str}")
        if "row-level security policy" in error_str.lower():
            print("💡 RLS ISSUE: Need service role key or disable RLS policy")
        return False

def process_correction_casemaking():
    """Main processing function"""
    
    print("🚀 Starting Correction & Case Making Embedding Process")
    print("=" * 60)
    
    # Load CSV data
    df = load_correction_casemaking_csv()
    if df is None:
        return False
    
    # Clear existing data
    print("\n🗑️  Clearing existing data...")
    if not clear_existing_data():
        return False
    
    # Process each procedure
    print(f"\n🔄 Processing {len(df)} correction & case making procedures...")
    
    success_count = 0
    error_count = 0
    
    for index, row in df.iterrows():
        keyword = row['embed']
        content = row['Content']
        
        print(f"\n📝 Processing procedure {index + 1}/{len(df)}")
        print(f"🔑 Keyword: '{keyword}'")
        print(f"📄 Content: {content[:100]}...")
        
        # Generate embedding for keyword only
        print("🧠 Generating embedding...")
        embedding = generate_embedding(keyword)
        
        if embedding is None:
            print(f"❌ Failed to generate embedding for: {keyword}")
            error_count += 1
            continue
        
        print(f"✅ Generated embedding: {len(embedding)} dimensions")
        
        # Insert to database
        print("💾 Inserting to database...")
        if insert_correction_casemaking_procedure(keyword, content, embedding):
            print(f"✅ Successfully inserted: {keyword}")
            success_count += 1
        else:
            print(f"❌ Failed to insert: {keyword}")
            error_count += 1
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 CORRECTION & CASE MAKING EMBEDDING SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully processed: {success_count} procedures")
    print(f"❌ Errors: {error_count} procedures")
    print(f"📈 Success rate: {(success_count/(success_count+error_count)*100):.1f}%")
    
    if success_count > 0:
        print(f"\n🎉 Correction & case making embedding completed successfully!")
        print(f"📚 Database ready for semantic search on {success_count} procedures")
        return True
    else:
        print(f"\n💥 No procedures were successfully processed!")
        return False

def verify_database():
    """Verify the data was inserted correctly"""
    
    try:
        print("\n🔍 Verifying database...")
        
        # Count total procedures
        result = supabase.rpc('count_correction_casemaking').execute()
        total_count = result.data
        
        print(f"📊 Total procedures in database: {total_count}")
        
        # Get statistics
        result = supabase.rpc('get_correction_casemaking_stats').execute()
        if result.data and len(result.data) > 0:
            stats = result.data[0]
            print(f"📋 Correction procedures: {stats['correction_procedures']}")
            print(f"📋 Case making procedures: {stats['casemaking_procedures']}")
        
        # Get sample data
        result = supabase.table('correction_casemaking_documents').select('*').limit(3).execute()
        sample_data = result.data
        
        print(f"\n📋 Sample data:")
        for i, procedure in enumerate(sample_data, 1):
            print(f"{i}. Keyword: '{procedure['keyword']}'")
            print(f"   Content: {procedure['content'][:80]}...")
            print(f"   Type: {procedure['metadata'].get('procedure_type', 'unknown')}")
            print(f"   Embedding: {len(procedure['embedding'])} dimensions")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Verification error: {str(e)}")
        return False

def test_search():
    """Test search functionality"""
    
    try:
        print("🧪 Testing search functionality...")
        
        # Test keyword search
        test_keywords = ["koreksian", "case making", "deadline"]
        
        for keyword in test_keywords:
            print(f"\n🔍 Testing search: '{keyword}'")
            
            result = supabase.rpc('search_correction_casemaking_keyword', {
                'search_keyword': keyword,
                'match_count': 3
            }).execute()
            
            if result.data:
                print(f"✅ Found {len(result.data)} matches")
                for match in result.data[:2]:  # Show top 2
                    print(f"   - {match['keyword']}: {match['content'][:60]}...")
            else:
                print(f"❌ No matches found")
        
        return True
        
    except Exception as e:
        print(f"❌ Search test error: {str(e)}")
        return False

if __name__ == "__main__":
    print("📚 CORRECTION & CASE MAKING EMBEDDING SYSTEM")
    print("=" * 55)
    
    # Process the procedures
    success = process_correction_casemaking()
    
    if success:
        # Verify database
        verify_database()
        
        # Test search
        test_search()
        
        print("\n🎯 READY FOR USE!")
        print("You can now run: python run_correction_query.py")
    else:
        print("\n💥 EMBEDDING FAILED!")
        sys.exit(1) 