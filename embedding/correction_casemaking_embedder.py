#!/usr/bin/env python3
"""
Correction and Case Making Embedding Script
Handles embedding for academic integrity and case handling procedures
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.embedding.base_embedder import BaseEmbedder
from unified_system.config.settings import get_settings

class CorrectionCaseMakingEmbedder(BaseEmbedder):
    """Embedder for Correction and Case Making system"""
    
    def __init__(self):
        settings = get_settings()
        super().__init__(
            system_name="correction_casemaking",
            csv_file_path=settings.correction_csv_path,
            database_url=settings.database_url,
            table_name="correction_casemaking_embeddings"
        )
    
    def get_embedding_text(self, row):
        """Extract text for embedding from CSV row"""
        # Correction and Case Making specific text extraction
        text_parts = []
        
        if 'Jenis_Pelanggaran' in row:
            text_parts.append(f"Jenis Pelanggaran: {row['Jenis_Pelanggaran']}")
        if 'Deskripsi_Pelanggaran' in row:
            text_parts.append(f"Deskripsi: {row['Deskripsi_Pelanggaran']}")
        if 'Sanksi' in row:
            text_parts.append(f"Sanksi: {row['Sanksi']}")
        if 'Prosedur_Penanganan' in row:
            text_parts.append(f"Prosedur: {row['Prosedur_Penanganan']}")
        if 'Kategori' in row:
            text_parts.append(f"Kategori: {row['Kategori']}")
            
        return " | ".join(text_parts)

def main():
    """Main execution function"""
    print("Starting Correction and Case Making embedding process...")
    
    try:
        embedder = CorrectionCaseMakingEmbedder()
        success = embedder.run_embedding()
        
        if success:
            print("✅ Correction and Case Making embedding completed successfully!")
            embedder.print_performance_stats()
        else:
            print("❌ Correction and Case Making embedding failed!")
            return 1
            
    except Exception as e:
        print(f"❌ Error during Correction and Case Making embedding: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 