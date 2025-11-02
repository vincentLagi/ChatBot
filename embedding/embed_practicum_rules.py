#!/usr/bin/env python3
"""
Embed Practicum Rules Script
Process Rules&ProceduresPracticum.csv and store in Supabase with embeddings

Strategy: Keyword-only embedding (same as UAP rules)
- Embed only the keyword/phrase (Embed column)
- Store full content in metadata for retrieval
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

def load_practicum_csv():
    """Load and validate the practicum CSV file"""
    
    csv_file = "Rules&ProceduresPracticum.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return None
    
    try:
        # Read CSV with semicolon delimiter and handle multi-line content
        df = pd.read_csv(csv_file, delimiter=';', quotechar='"', skipinitialspace=True)
        print(f"📁 Loaded CSV: {csv_file}")
        print(f"📊 Shape: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Validate required columns
        required_columns = ['Embed', 'Content']
        if not all(col in df.columns for col in required_columns):
            print(f"❌ Missing required columns: {required_columns}")
            print(f"Available columns: {list(df.columns)}")
            return None
        
        # Clean and validate data
        df = df.dropna(subset=['Embed', 'Content'])
        df['Embed'] = df['Embed'].str.strip()
        df['Content'] = df['Content'].str.strip()
        
        # Replace newlines in content with spaces for better processing
        df['Content'] = df['Content'].str.replace('\n', ' ').str.replace('\r', ' ')
        
        print(f"✅ Cleaned data: {len(df)} valid rows")
        
        # Show sample data for verification
        print(f"\n📋 Sample data:")
        for i, row in df.head(2).iterrows():
            print(f"{i+1}. Embed: '{row['Embed']}'")
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
    """Clear existing practicum rules data"""
    
    try:
        result = supabase.table('practicum_rules_documents').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print(f"🗑️  Cleared existing practicum rules data")
        return True
        
    except Exception as e:
        error_str = str(e)
        print(f"❌ Error clearing data: {error_str}")
        if "row-level security policy" in error_str.lower():
            print("💡 TIP: This might be a permissions issue. You may need:")
            print("   - SUPABASE_SERVICE_KEY instead of SUPABASE_KEY")
            print("   - Or disable RLS on the practicum_rules_documents table")
        return False

def insert_practicum_rule(keyword: str, content: str, embedding: list) -> bool:
    """Insert a single practicum rule with embedding"""
    
    try:
        # Prepare metadata
        metadata = {
            "keyword_length": len(keyword),
            "content_length": len(content),
            "source": "Rules&ProceduresPracticum.csv",
            "category": "Practicum_Rules",
            "embedding_strategy": "keyword_only",
            "full_content": content  # Store full content in metadata
        }
        
        # Generate UUID
        rule_id = str(uuid.uuid4())
        
        # Insert to database
        result = supabase.table('practicum_rules_documents').insert({
            "id": rule_id,
            "keyword": keyword,
            "content": content,
            "embedding": embedding,
            "metadata": metadata
        }).execute()
        
        return True
        
    except Exception as e:
        error_str = str(e)
        print(f"❌ Error inserting rule '{keyword}': {error_str}")
        if "row-level security policy" in error_str.lower():
            print("💡 RLS ISSUE: Need service role key or disable RLS policy")
        return False

def process_practicum_rules():
    """Main processing function"""
    
    print("🚀 Starting Practicum Rules Embedding Process")
    print("=" * 55)
    
    # Load CSV data
    df = load_practicum_csv()
    if df is None:
        return False
    
    # Clear existing data
    print("\n🗑️  Clearing existing data...")
    if not clear_existing_data():
        return False
    
    # Process each rule
    print(f"\n🔄 Processing {len(df)} practicum rules...")
    
    success_count = 0
    error_count = 0
    
    for index, row in df.iterrows():
        keyword = row['Embed']
        content = row['Content']
        
        print(f"\n📝 Processing rule {index + 1}/{len(df)}")
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
        if insert_practicum_rule(keyword, content, embedding):
            print(f"✅ Successfully inserted: {keyword}")
            success_count += 1
        else:
            print(f"❌ Failed to insert: {keyword}")
            error_count += 1
    
    # Final summary
    print("\n" + "=" * 55)
    print("📊 PRACTICUM RULES EMBEDDING SUMMARY")
    print("=" * 55)
    print(f"✅ Successfully processed: {success_count} rules")
    print(f"❌ Errors: {error_count} rules")
    print(f"📈 Success rate: {(success_count/(success_count+error_count)*100):.1f}%")
    
    if success_count > 0:
        print(f"\n🎉 Practicum rules embedding completed successfully!")
        print(f"📚 Database ready for semantic search on {success_count} rules")
        return True
    else:
        print(f"\n💥 No rules were successfully processed!")
        return False

def verify_database():
    """Verify the data was inserted correctly"""
    
    try:
        print("\n🔍 Verifying database...")
        
        # Count total rules
        result = supabase.rpc('count_practicum_rules').execute()
        total_count = result.data
        
        print(f"📊 Total rules in database: {total_count}")
        
        # Get sample data
        result = supabase.table('practicum_rules_documents').select('*').limit(3).execute()
        sample_data = result.data
        
        print(f"\n📋 Sample data:")
        for i, rule in enumerate(sample_data, 1):
            print(f"{i}. Keyword: '{rule['keyword']}'")
            print(f"   Content: {rule['content'][:80]}...")
            print(f"   Embedding: {len(rule['embedding'])} dimensions")
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
        test_keywords = ["mengajar", "ruangan", "ruman"]
        
        for keyword in test_keywords:
            print(f"\n🔍 Testing search: '{keyword}'")
            
            result = supabase.rpc('search_practicum_rules_keyword', {
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
    print("📚 PRACTICUM RULES EMBEDDING SYSTEM")
    print("=" * 50)
    
    # Process the rules
    success = process_practicum_rules()
    
    if success:
        # Verify database
        verify_database()
        
        # Test search
        test_search()
        
        print("\n🎯 READY FOR USE!")
        print("You can now run: python run_practicum_query.py")
    else:
        print("\n💥 EMBEDDING FAILED!")
        sys.exit(1) 