#!/usr/bin/env python3
"""
Practicum Rules Embedding Script
Handles embedding for laboratory procedures and practicum setup
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.embedding.base_embedder import BaseEmbedder
from unified_system.config.settings import get_settings

class PracticumEmbedder(BaseEmbedder):
    """Embedder for Practicum Rules system"""
    
    def __init__(self):
        settings = get_settings()
        super().__init__(
            system_name="practicum_rules",
            csv_file_path=settings.practicum_csv_path,
            database_url=settings.database_url,
            table_name="practicum_embeddings"
        )
    
    def get_embedding_text(self, row):
        """Extract text for embedding from CSV row"""
        # Practicum Rules specific text extraction
        text_parts = []
        
        if 'Prosedur' in row:
            text_parts.append(f"Prosedur: {row['Prosedur']}")
        if 'Deskripsi' in row:
            text_parts.append(f"Deskripsi: {row['Deskripsi']}")
        if 'Ruangan' in row:
            text_parts.append(f"Ruangan: {row['Ruangan']}")
        if 'Equipment' in row:
            text_parts.append(f"Equipment: {row['Equipment']}")
        if 'Setup' in row:
            text_parts.append(f"Setup: {row['Setup']}")
        if 'Kategori' in row:
            text_parts.append(f"Kategori: {row['Kategori']}")
            
        return " | ".join(text_parts)

def main():
    """Main execution function"""
    print("Starting Practicum Rules embedding process...")
    
    try:
        embedder = PracticumEmbedder()
        success = embedder.run_embedding()
        
        if success:
            print("✅ Practicum Rules embedding completed successfully!")
            embedder.print_performance_stats()
        else:
            print("❌ Practicum Rules embedding failed!")
            return 1
            
    except Exception as e:
        print(f"❌ Error during Practicum Rules embedding: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 