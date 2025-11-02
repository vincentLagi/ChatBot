#!/usr/bin/env python3
"""
Rules UAP Embedding Script
Handles embedding for University Academic Procedures rules and regulations
"""

import os
import sys
from pathlib import Path



project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from base_embedder import BaseEmbedder

class RulesUAPEmbedder(BaseEmbedder):
    """Embedder for Rules UAP system"""
    
    def __init__(self):
        super().__init__(
            system_name="Rules UAP",
            table_name="rules_procedure_uap",
            csv_file="Rules&ProcedureUAP.csv"
        )
    
    def get_required_columns(self):
        """Rules UAP CSV requires Embed and Content columns"""
        return ['Embed', 'Content']
    
    def get_sample_description(self, row):
        """Custom sample data display for Rules UAP"""
        return f"Embed: '{row['Embed'][:30]}...' | Content: {row['Content'][:50]}..."
    
    def get_embedding_text(self, row):
        """Extract text for embedding from CSV row"""
        # Rules UAP specific text extraction for Embed,Content format
        
        if 'Embed' in row:
            # Use the Embed column (keyword) for embedding - keyword_only strategy
            return row['Embed']
        
        return ""
    
    def process_single_row(self, row, index, total):
        """Rules UAP specific processing"""
        
        keyword = row['Embed']
        content = row['Content']
        
        print(f"\n📝 Processing rule {index+1}/{total}")
        print(f"🔑 Keyword: '{keyword[:50]}...'")
        print(f"📄 Content: {content[:80]}...")
        
        # Generate embedding for keyword only (Rules UAP strategy)
        print("🧠 Generating embedding...")
        embedding = self.generate_embedding(keyword)
        if embedding is None:
            print(f"❌ Failed to generate embedding for: {keyword}")
            return False
        
        print(f"✅ Generated embedding: {len(embedding)} dimensions")
        
        # Insert with Rules UAP specific metadata
        print("💾 Inserting to database...")
        success = self.insert_document(
            id=str(__import__('uuid').uuid4()),
            keyword=keyword,
            content=content,
            embedding=embedding,
            metadata={
                "keyword_length": len(keyword),
                "content_length": len(content),
                "source": "Rules&ProcedureUAP.csv",
                "category": "UAP_Rules",
                "embedding_strategy": "keyword_only",
                "full_content": content
            }
        )
        
        if success:
            print(f"✅ Successfully inserted: {keyword[:30]}...")
        else:
            print(f"❌ Failed to insert: {keyword}")
        
        return success

def main():
    """Main execution function"""
    print("Starting Rules UAP embedding process...")
    
    try:
        embedder = RulesUAPEmbedder()
        success = embedder.process_embeddings()
        
        if success:
            print("✅ Rules UAP embedding completed successfully!")
            # embedder.print_performance_stats() # if available
        else:
            print("❌ Rules UAP embedding failed!")
            return 1
            
    except Exception as e:
        print(f"❌ Error during Rules UAP embedding: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 