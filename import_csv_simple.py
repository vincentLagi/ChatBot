#!/usr/bin/env python3
"""
Script sederhana untuk import data dari output.csv ke Supabase
"""

import os
import csv
import sys
from typing import List, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Mapping CSV header to DB column
CSV_TO_DB = {
    "Initial": "initial",
    "Gen": "gen",
    "Initial + Gen": "initial_gen",
    "Name": "name",
    "Binusian ID": "binusian_id",
    "NIM": "nim",
    "Email (edu)": "email_edu",
    "Email (ac.id)": "email_ac_id",
    "Leader": "leader",
    "Major (Long)": "major_long",
    "Major": "major",
    "Streaming": "streaming",
    "Semester": "semester",
    "Global": "global",
    "Location": "location",
    "Position": "position",
    "Shift": "shift"
}

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY]):
    raise ValueError("Missing required environment variables: SUPABASE_URL, SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def read_csv_data(csv_file_path: str) -> List[Dict[str, Any]]:
    """Read CSV file and return list of dictionaries with DB keys"""
    try:
        data = []
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                cleaned_row = {}
                for csv_key, db_key in CSV_TO_DB.items():
                    value = row.get(csv_key, "")
                    cleaned_row[db_key] = value.strip() if value else None
                data.append(cleaned_row)
        
        logger.info(f"✅ Read {len(data)} rows from CSV file")
        return data
        
    except Exception as e:
        logger.error(f"❌ Error reading CSV file: {str(e)}")
        return []

def insert_data_to_supabase(data: List[Dict[str, Any]], batch_size: int = 50):
    """Insert data to Supabase in batches"""
    try:
        total_rows = len(data)
        logger.info(f"📊 Starting to insert {total_rows} rows to Supabase...")
        
        # Insert in batches
        for i in range(0, total_rows, batch_size):
            batch = data[i:i + batch_size]
            result = supabase.table('assistant_csv').insert(batch).execute()
            logger.info(f"✅ Inserted batch {i//batch_size + 1}: {len(batch)} rows")
            progress = min((i + batch_size) / total_rows * 100, 100)
            logger.info(f"📈 Progress: {progress:.1f}%")
        logger.info(f"🎉 Successfully inserted all {total_rows} rows!")
        return True
    except Exception as e:
        logger.error(f"❌ Error inserting data: {str(e)}")
        return False

def clear_existing_data():
    """Clear existing data from table"""
    try:
        result = supabase.table('assistant_csv').delete().neq('id', 0).execute()
        logger.info("🗑️ Cleared existing data from assistant_csv table")
        return True
    except Exception as e:
        logger.error(f"❌ Error clearing data: {str(e)}")
        return False

def verify_data_import():
    """Verify that data was imported correctly"""
    try:
        result = supabase.table('assistant_csv').select('*').execute()
        count = len(result.data)
        logger.info(f"✅ Verification: {count} rows found in database")
        if count > 0:
            sample = result.data[0]
            logger.info(f"📋 Sample data: {sample.get('initial')} - {sample.get('name')}")
        return count > 0
    except Exception as e:
        logger.error(f"❌ Error verifying data: {str(e)}")
        return False

def check_table_exists():
    """Check if table exists by trying to select from it"""
    try:
        result = supabase.table('assistant_csv').select('id').limit(1).execute()
        logger.info("✅ Table assistant_csv exists")
        return True
    except Exception as e:
        logger.error(f"❌ Table assistant_csv does not exist: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 Starting CSV import to Supabase...")
    print("=" * 50)
    csv_file_path = os.path.join(os.path.dirname(__file__), 'data', 'csv', 'output.csv')
    if not os.path.exists(csv_file_path):
        logger.error(f"❌ CSV file not found: {csv_file_path}")
        return False
    try:
        logger.info("📋 Step 1: Checking if table exists...")
        if not check_table_exists():
            print("\n❌ Table 'assistant_csv' does not exist!")
            print("💡 Please create the table first using this SQL:")
            print("""
CREATE TABLE assistant_csv (
    id SERIAL PRIMARY KEY,
    initial TEXT,
    gen TEXT,
    initial_gen TEXT,
    name TEXT,
    binusian_id TEXT,
    nim TEXT,
    email_edu TEXT,
    email_ac_id TEXT,
    leader TEXT,
    major_long TEXT,
    major TEXT,
    streaming TEXT,
    semester TEXT,
    global TEXT,
    location TEXT,
    position TEXT,
    shift TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
            """)
            return False
        logger.info("📖 Step 2: Reading CSV data...")
        data = read_csv_data(csv_file_path)
        if not data:
            return False
        print(f"\n📊 Found {len(data)} rows in CSV")
        clear_choice = input("🗑️ Clear existing data from table? (y/N): ").strip().lower()
        if clear_choice == 'y':
            logger.info("🗑️ Clearing existing data...")
            if not clear_existing_data():
                return False
        logger.info("📤 Step 3: Inserting data to Supabase...")
        if not insert_data_to_supabase(data):
            return False
        logger.info("🔍 Step 4: Verifying data import...")
        if not verify_data_import():
            return False
        print("\n" + "=" * 50)
        print("🎉 CSV import completed successfully!")
        print(f"📊 Total rows imported: {len(data)}")
        print("✅ Data is now available in assistant_csv table")
        return True
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 