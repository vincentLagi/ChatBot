#!/usr/bin/env python3
"""
Assistant Search Embedding Script  
Handles embedding for general academic assistance and search functionality
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.embedding.base_embedder import BaseEmbedder
from unified_system.config.settings import get_settings

class AssistantSearchEmbedder(BaseEmbedder):
    """Embedder for Assistant Search system"""
    
    def __init__(self):
        settings = get_settings()
        super().__init__(
            system_name="assistant_search",
            csv_file_path=settings.assistant_csv_path,
            database_url=settings.database_url,
            table_name="assistant_search_embeddings"
        )
    
    def get_embedding_text(self, row):
        """Extract text for embedding from CSV row"""
        # Assistant Search specific text extraction
        text_parts = []
        
        if 'Pertanyaan' in row:
            text_parts.append(f"Pertanyaan: {row['Pertanyaan']}")
        if 'Jawaban' in row:
            text_parts.append(f"Jawaban: {row['Jawaban']}")
        if 'Kategori' in row:
            text_parts.append(f"Kategori: {row['Kategori']}")
        if 'Topik' in row:
            text_parts.append(f"Topik: {row['Topik']}")
        if 'Keywords' in row:
            text_parts.append(f"Keywords: {row['Keywords']}")
            
        return " | ".join(text_parts)

def main():
    """Main execution function"""
    print("Starting Assistant Search embedding process...")
    
    try:
        embedder = AssistantSearchEmbedder()
        success = embedder.run_embedding()
        
        if success:
            print("✅ Assistant Search embedding completed successfully!")
            embedder.print_performance_stats()
        else:
            print("❌ Assistant Search embedding failed!")
            return 1
            
    except Exception as e:
        print(f"❌ Error during Assistant Search embedding: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 