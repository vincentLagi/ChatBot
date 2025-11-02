"""
Practicum Rules Embedder
Specialized embedder for practicum rules using keyword-only embedding strategy

Reduces from 329 lines to ~60 lines by inheriting from BaseEmbedder
"""

import sys
from pathlib import Path
from typing import List
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

# Import base embedder with absolute path
try:
    from ..base_embedder import BaseEmbedder
except ImportError:
    # Fallback for direct execution
    sys.path.append(str(Path(__file__).parent.parent))
    from base_embedder import BaseEmbedder

class PracticumEmbedder(BaseEmbedder):
    """
    🎯 Practicum-specific embedding logic
    Only ~60 lines instead of 329 lines!
    """
    
    def __init__(self):
        super().__init__(
            system_name="Practicum Rules",
            table_name="practicum_documents", 
            csv_file="Rules&ProceduresPracticum.csv"
        )
    
    def get_required_columns(self) -> List[str]:
        """Practicum CSV requires Embed and Content columns"""
        return ['Embed', 'Content']
    
    def get_sample_description(self, row: pd.Series) -> str:
        """Custom sample data display for practicum"""
        return f"Embed: '{row['Embed']}' | Content: {row['Content'][:50]}..."
    
    def process_single_row(self, row: pd.Series, index: int, total: int) -> bool:
        """Practicum-specific processing"""
        
        keyword = row['Embed']
        content = row['Content']
        
        print(f"\n📝 Processing practicum rule {index+1}/{total}")
        print(f"🔑 Keyword: '{keyword}'")
        print(f"📄 Content: {content[:80]}...")
        
        # Generate embedding for keyword only (practicum strategy)
        print("🧠 Generating embedding...")
        embedding = self.generate_embedding(keyword)
        if embedding is None:
            print(f"❌ Failed to generate embedding for: {keyword}")
            return False
        
        print(f"✅ Generated embedding: {len(embedding)} dimensions")
        
        # Insert with practicum-specific metadata
        print("💾 Inserting to database...")
        success = self.insert_document(
            keyword=keyword,
            content=content,
            embedding=embedding,
            metadata={
                "keyword_length": len(keyword),
                "content_length": len(content),
                "source": self.csv_file,
                "category": "Practicum_Rules",
                "embedding_strategy": "keyword_only",
                "procedure_type": self.determine_procedure_type(keyword),
                "full_content": content
            }
        )
        
        if success:
            print(f"✅ Successfully inserted: {keyword}")
        else:
            print(f"❌ Failed to insert: {keyword}")
        
        return success
    
    def determine_procedure_type(self, keyword: str) -> str:
        """Practicum-specific categorization"""
        keyword_lower = keyword.lower()
        
        if any(term in keyword_lower for term in ['setup', 'install', 'konfigurasi']):
            return 'setup'
        elif any(term in keyword_lower for term in ['lab', 'komputer', 'room']):
            return 'lab_procedure'
        elif any(term in keyword_lower for term in ['jadwal', 'schedule', 'waktu']):
            return 'scheduling'
        elif any(term in keyword_lower for term in ['aturan', 'rules', 'ketentuan']):
            return 'rules'
        else:
            return 'general'
    
    def get_row_identifier(self, row: pd.Series) -> str:
        """Meaningful identifier for tracking"""
        return f"practicum_{row['Embed'][:20].replace(' ', '_')}"

# Factory function for easy usage
def create_practicum_embedder() -> PracticumEmbedder:
    """Create and return a practicum embedder instance"""
    return PracticumEmbedder()

if __name__ == "__main__":
    # Test the embedder
    print("🧪 Testing Practicum Embedder")
    print("=" * 40)
    
    embedder = create_practicum_embedder()
    success = embedder.process_embeddings()
    
    if success:
        embedder.verify_database()
        print("\n🎯 Practicum embedding completed successfully!")
    else:
        print("\n💥 Practicum embedding failed!")
        sys.exit(1) 