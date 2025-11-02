#!/usr/bin/env python3
"""
Embed Material and Criteria Script
Process MaterialAndCriteriaDataset.csv and store in Supabase with embeddings

Strategy: Course code + course name + type embedding
- Embed comprehensive text for semantic search
- Store in Supabase database for fast retrieval
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
from typing import List, Dict, Any

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

def load_material_criteria_csv():
    """Load the Material and Criteria CSV file"""
    
    csv_path = "MaterialAndCriteriaDataset.csv"

    print("Exists?", os.path.exists(csv_path))
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return None
    
    try:
        # Try reading with different encodings
        try:
            df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(csv_path, sep=';', encoding='latin-1')
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Clean data
        df = df.dropna()
        
        # Clean whitespace from all string columns
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].str.strip()
        
        print(f"✅ Loaded {len(df)} records from MaterialAndCriteriaDataset.csv")
        return df
    
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return None

def create_embedding_text(row: pd.Series) -> str:
    """Create embedding text from course info"""
    course_code = row['Course Code']
    course_name = row['Course name']
    type_code = row['Type']
    
    # Map type codes to descriptions
    type_descriptions = {
        'TM1': 'Quiz 1 Mid Term 1',
        'TM2': 'Quiz 2 Mid Term 2', 
        'PRY': 'Project Assignment',
        'UAP': 'Final Exam Lab Assessment'
    }
    
    type_desc = type_descriptions.get(type_code, type_code)
    
    # Create comprehensive embedding text
    embedding_text = f"{course_code} {course_name} {type_code} {type_desc}"
    
    return embedding_text

def generate_embedding(text: str) -> List[float]:
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
    """Clear existing material criteria data"""
    
    try:
        # Use a valid UUID format for the condition, or better yet, just delete all
        result = supabase.table('material_criteria_documents').delete().gte('created_at', '1900-01-01').execute()
        print(f"✅ Cleared existing data")
        return True
    
    except Exception as e:
        error_str = str(e)
        print(f"❌ Error clearing data: {error_str}")
        if "row-level security policy" in error_str.lower():
            print("💡 RLS ISSUE: Need service role key or disable RLS policy")
        return False

def determine_material_category(course_code: str, course_name: str) -> str:
    """Determine material category based on course code"""
    
    course_code_upper = course_code.upper()
    
    if course_code_upper.startswith('COMP'):
        return 'Computer Science'
    elif course_code_upper.startswith('ISYS'):
        return 'Information Systems'
    elif course_code_upper.startswith('MOBI'):
        return 'Mobile Development'
    elif course_code_upper.startswith('MATH'):
        return 'Mathematics'
    elif course_code_upper.startswith('SCIE'):
        return 'Science'
    elif course_code_upper.startswith('CPEN'):
        return 'Computer Engineering'
    else:
        return 'General'

def insert_material_criteria(course_code: str, course_name: str, type_code: str, 
                           link_download: str, embedding_text: str, embedding: List[float]) -> bool:
    """Insert a single material criteria record with embedding"""
    
    try:
        # Determine category
        category = determine_material_category(course_code, course_name)
        
        # Prepare metadata
        metadata = {
            "course_code": course_code,
            "course_name": course_name,
            "type": type_code,
            "category": category,
            "embedding_text_length": len(embedding_text),
            "source": "MaterialAndCriteriaDataset.csv",
            "embedding_strategy": "course_code_name_type",
            "type_description": {
                'TM1': 'Quiz 1 Mid Term 1',
                'TM2': 'Quiz 2 Mid Term 2',
                'PRY': 'Project Assignment',
                'UAP': 'Final Exam Lab Assessment'
            }.get(type_code, type_code)
        }
        
        # Generate UUID
        material_id = str(uuid.uuid4())
        
        # Insert to database
        result = supabase.table('material_criteria_documents').insert({
            "id": material_id,
            "course_code": course_code,
            "course_name": course_name,
            "type": type_code,
            "link_download": link_download,
            "embedding_text": embedding_text,
            "embedding": embedding,
            "metadata": metadata
        }).execute()
        
        return True
        
    except Exception as e:
        error_str = str(e)
        print(f"❌ Error inserting material '{course_code} {type_code}': {error_str}")
        if "row-level security policy" in error_str.lower():
            print("💡 RLS ISSUE: Need service role key or disable RLS policy")
        return False

def process_material_criteria():
    """Main processing function"""
    
    print("🚀 Starting Material and Criteria Embedding Process")
    print("=" * 60)
    
    # Load CSV data
    df = load_material_criteria_csv()
    if df is None:
        return False
    
    # Clear existing data
    print("\n🗑️  Clearing existing data...")
    if not clear_existing_data():
        return False
    
    # Process each material
    print(f"\n🔄 Processing {len(df)} material criteria records...")
    
    success_count = 0
    error_count = 0
    
    for index, row in df.iterrows():
        course_code = row['Course Code']
        course_name = row['Course name']
        type_code = row['Type']
        link_download = row['Link Download']
        
        print(f"\n📝 Processing material {index + 1}/{len(df)}")
        print(f"🔑 Course: {course_code} - {course_name}")
        print(f"📋 Type: {type_code}")
        
        # Create embedding text
        embedding_text = create_embedding_text(row)
        print(f"📄 Embedding text: {embedding_text}")
        
        # Generate embedding
        print("🧠 Generating embedding...")
        embedding = generate_embedding(embedding_text)
        
        if embedding is None:
            print(f"❌ Failed to generate embedding for: {embedding_text}")
            error_count += 1
            continue
        
        print(f"✅ Generated embedding: {len(embedding)} dimensions")
        
        # Insert to database
        print("💾 Inserting to database...")
        if insert_material_criteria(course_code, course_name, type_code, link_download, embedding_text, embedding):
            print(f"✅ Successfully inserted: {course_code} {type_code}")
            success_count += 1
        else:
            print(f"❌ Failed to insert: {course_code} {type_code}")
            error_count += 1
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 MATERIAL & CRITERIA EMBEDDING SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully processed: {success_count} materials")
    print(f"❌ Errors: {error_count} materials")
    print(f"📈 Success rate: {(success_count/(success_count+error_count)*100):.1f}%")
    
    if success_count > 0:
        print(f"\n🎉 Material & criteria embedding completed successfully!")
        print(f"📚 Database ready for semantic search on {success_count} materials")
        return True
    else:
        print(f"\n💥 No materials were successfully processed!")
        return False

def verify_database():
    """Verify the data was inserted correctly"""
    
    try:
        print("\n🔍 Verifying database...")
        
        # Count total materials
        result = supabase.rpc('count_material_criteria').execute()
        total_count = result.data
        
        print(f"📊 Total materials in database: {total_count}")
        
        # Get statistics
        result = supabase.rpc('get_material_criteria_stats').execute()
        if result.data and len(result.data) > 0:
            stats = result.data[0]
            print(f"📋 TM1 materials: {stats['tm1_count']}")
            print(f"📋 TM2 materials: {stats['tm2_count']}")
            print(f"📋 PRY materials: {stats['pry_count']}")
            print(f"📋 UAP materials: {stats['uap_count']}")
            print(f"📚 Unique courses: {stats['unique_courses']}")
        
        # Get sample data
        result = supabase.table('material_criteria_documents').select('*').limit(3).execute()
        sample_data = result.data
        
        print(f"\n📋 Sample data:")
        for i, material in enumerate(sample_data, 1):
            print(f"{i}. Course: {material['course_code']} - {material['course_name']}")
            print(f"   Type: {material['type']}")
            print(f"   Link: {material['link_download'][:50]}...")
            print(f"   Embedding: {len(material['embedding'])} dimensions")
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
        test_keywords = ["data structures", "COMP6048", "quiz", "project"]
        
        for keyword in test_keywords:
            print(f"\n🔍 Testing search: '{keyword}'")
            
            result = supabase.rpc('search_material_criteria_keyword', {
                'search_keyword': keyword,
                'match_count': 3
            }).execute()
            
            if result.data:
                print(f"✅ Found {len(result.data)} matches")
                for match in result.data[:2]:  # Show top 2
                    print(f"   - {match['course_code']} {match['type']}: {match['course_name']}")
            else:
                print(f"❌ No matches found")
        
        return True
        
    except Exception as e:
        print(f"❌ Search test error: {str(e)}")
        return False

if __name__ == "__main__":
    print("📚 MATERIAL & CRITERIA EMBEDDING SYSTEM")
    print("=" * 55)
    
    # Process the materials
    success = process_material_criteria()
    
    if success:
        # Verify database
        verify_database()
        
        # Test search
        test_search()
        
        print("\n🎯 READY FOR USE!")
        print("You can now test the unified system with material criteria queries!")
    else:
        print("\n💥 EMBEDDING FAILED!")
        sys.exit(1) 