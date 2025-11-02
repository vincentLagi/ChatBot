#!/usr/bin/env python3
"""
Script untuk import data dari output.csv ke Supabase
"""

import os
import csv
import sys
from typing import List, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

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

def create_table_if_not_exists():
    """Create table if it doesn't exist"""
    try:
        # SQL untuk membuat table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS assistant_csv (
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
        """
        
        # Execute SQL
        result = supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
        logger.info("✅ Table assistant_csv created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating table: {str(e)}")
        return False

def read_csv_data(csv_file_path: str) -> List[Dict[str, Any]]:
    """Read CSV file and return list of dictionaries"""
    try:
        data = []
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                # Clean data - remove extra whitespace
                cleaned_row = {}
                for key, value in row.items():
                    if value is not None:
                        cleaned_row[key] = value.strip()
                    else:
                        cleaned_row[key] = value
                
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
            
            # Insert batch
            result = supabase.table('assistant_csv').insert(batch).execute()
            
            logger.info(f"✅ Inserted batch {i//batch_size + 1}: {len(batch)} rows")
            
            # Show progress
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
            # Show sample data
            sample = result.data[0]
            logger.info(f"📋 Sample data: {sample.get('initial')} - {sample.get('name')}")
        
        return count > 0
        
    except Exception as e:
        logger.error(f"❌ Error verifying data: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 Starting CSV import to Supabase...")
    print("=" * 50)
    
    # Path to CSV file
    csv_file_path = os.path.join(os.path.dirname(__file__), 'data', 'csv', 'output.csv')
    
    if not os.path.exists(csv_file_path):
        logger.error(f"❌ CSV file not found: {csv_file_path}")
        return False
    
    try:
        # Step 1: Create table if not exists
        logger.info("📋 Step 1: Creating table...")
        if not create_table_if_not_exists():
            return False
        
        # Step 2: Read CSV data
        logger.info("📖 Step 2: Reading CSV data...")
        data = read_csv_data(csv_file_path)
        if not data:
            return False
        
        # Step 3: Ask user if want to clear existing data
        print(f"\n📊 Found {len(data)} rows in CSV")
        clear_choice = input("🗑️ Clear existing data from table? (y/N): ").strip().lower()
        
        if clear_choice == 'y':
            logger.info("🗑️ Clearing existing data...")
            if not clear_existing_data():
                return False
        
        # Step 4: Insert data
        logger.info("📤 Step 3: Inserting data to Supabase...")
        if not insert_data_to_supabase(data):
            return False
        
        # Step 5: Verify import
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