-- Supabase Database Setup for SLC Assistant System
-- Table untuk menyimpan data assistant dengan embedding dan metadata

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Drop table if exists (untuk development)
DROP TABLE IF EXISTS assistant_documents CASCADE;

-- Create main table untuk assistant documents
CREATE TABLE assistant_documents (
    -- Primary key dengan UUID
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Metadata sebagai JSONB untuk fleksibilitas dan performa query
    metadata JSONB NOT NULL,
    
    -- Embedding vector dengan dimensi 768 (sesuai Google Generative AI)
    embedding vector(768),
    
    -- Content text untuk full-text search backup
    content TEXT,
    
    -- Source information
    source_file VARCHAR(255),
    source_type VARCHAR(50) DEFAULT 'csv',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes untuk optimasi query
-- Index untuk metadata fields yang sering dicari (menggunakan btree untuk exact matches)
CREATE INDEX idx_assistant_metadata_initial ON assistant_documents ((metadata->>'initial'));
CREATE INDEX idx_assistant_metadata_name ON assistant_documents USING GIN ((metadata->>'name') gin_trgm_ops);
CREATE INDEX idx_assistant_metadata_nim ON assistant_documents ((metadata->>'nim'));
CREATE INDEX idx_assistant_metadata_binusian_id ON assistant_documents ((metadata->>'binusian_id'));
CREATE INDEX idx_assistant_metadata_location ON assistant_documents ((metadata->>'location'));
CREATE INDEX idx_assistant_metadata_major ON assistant_documents USING GIN ((metadata->>'major') gin_trgm_ops);
CREATE INDEX idx_assistant_metadata_position ON assistant_documents ((metadata->>'position'));

-- Index untuk embedding similarity search (HNSW untuk performa terbaik)
CREATE INDEX idx_assistant_embedding_hnsw ON assistant_documents 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Index untuk full-text search pada content
CREATE INDEX idx_assistant_content_fts ON assistant_documents USING GIN (to_tsvector('english', content));

-- Index untuk general JSONB queries
CREATE INDEX idx_assistant_metadata_gin ON assistant_documents USING GIN (metadata);

-- Index untuk source dan timestamps
CREATE INDEX idx_assistant_source ON assistant_documents (source_file, source_type);
CREATE INDEX idx_assistant_created_at ON assistant_documents (created_at);

-- Function untuk auto-update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger untuk auto-update updated_at
CREATE TRIGGER update_assistant_documents_updated_at 
    BEFORE UPDATE ON assistant_documents 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Function untuk mencari assistant berdasarkan similarity
CREATE OR REPLACE FUNCTION match_assistant_documents(
    query_embedding vector(768),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10,
    filter_metadata jsonb DEFAULT '{}'::jsonb
)
RETURNS TABLE (
    id uuid,
    metadata jsonb,
    content text,
    similarity float,
    source_file varchar,
    created_at timestamp with time zone
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        assistant_documents.id,
        assistant_documents.metadata,
        assistant_documents.content,
        1 - (assistant_documents.embedding <=> query_embedding) as similarity,
        assistant_documents.source_file,
        assistant_documents.created_at
    FROM assistant_documents
    WHERE 
        (assistant_documents.embedding <=> query_embedding) < (1 - match_threshold)
        AND (
            filter_metadata = '{}'::jsonb 
            OR assistant_documents.metadata @> filter_metadata
        )
    ORDER BY assistant_documents.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Function untuk hybrid search (semantic + keyword)
CREATE OR REPLACE FUNCTION hybrid_search_assistants(
    query_text text,
    query_embedding vector(768),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id uuid,
    metadata jsonb,
    content text,
    similarity float,
    text_rank float,
    combined_score float,
    source_file varchar
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH semantic_search AS (
        SELECT 
            ad.id,
            ad.metadata,
            ad.content,
            ad.source_file,
            1 - (ad.embedding <=> query_embedding) as similarity
        FROM assistant_documents ad
        WHERE (ad.embedding <=> query_embedding) < (1 - match_threshold)
    ),
    keyword_search AS (
        SELECT 
            ad.id,
            ad.metadata,
            ad.content,
            ad.source_file,
            ts_rank_cd(to_tsvector('english', ad.content), plainto_tsquery('english', query_text)) as text_rank
        FROM assistant_documents ad
        WHERE to_tsvector('english', ad.content) @@ plainto_tsquery('english', query_text)
    )
    SELECT 
        COALESCE(s.id, k.id) as id,
        COALESCE(s.metadata, k.metadata) as metadata,
        COALESCE(s.content, k.content) as content,
        COALESCE(s.similarity, 0) as similarity,
        COALESCE(k.text_rank, 0) as text_rank,
        (COALESCE(s.similarity, 0) * 0.7 + COALESCE(k.text_rank, 0) * 0.3) as combined_score,
        COALESCE(s.source_file, k.source_file) as source_file
    FROM semantic_search s
    FULL OUTER JOIN keyword_search k ON s.id = k.id
    ORDER BY combined_score DESC
    LIMIT match_count;
END;
$$;

-- Create RLS (Row Level Security) policies if needed
-- ALTER TABLE assistant_documents ENABLE ROW LEVEL SECURITY;

-- Example policy (uncomment if you need RLS)
-- CREATE POLICY "Allow authenticated users to read assistant documents" 
-- ON assistant_documents FOR SELECT 
-- TO authenticated 
-- USING (true);

-- Create view untuk easy querying
CREATE OR REPLACE VIEW assistant_summary AS
SELECT 
    id,
    metadata->>'initial' as initial,
    metadata->>'name' as name,
    metadata->>'nim' as nim,
    metadata->>'binusian_id' as binusian_id,
    metadata->>'email_edu' as email_edu,
    metadata->>'email_ac_id' as email_ac_id,
    metadata->>'is_leader' as is_leader,
    metadata->>'major_long' as major_long,
    metadata->>'major' as major,
    metadata->>'streaming' as streaming,
    metadata->>'semester' as semester,
    metadata->>'global' as global_status,
    metadata->>'location' as location,
    metadata->>'position' as position,
    metadata->>'shift' as shift,
    source_file,
    created_at,
    updated_at
FROM assistant_documents;

-- Grant necessary permissions
-- GRANT ALL ON assistant_documents TO authenticated;
-- GRANT ALL ON assistant_summary TO authenticated;

-- Insert sample comment for documentation
COMMENT ON TABLE assistant_documents IS 'Table untuk menyimpan data assistant SLC dengan embedding dan metadata';
COMMENT ON COLUMN assistant_documents.metadata IS 'JSONB field berisi semua informasi assistant dari CSV';
COMMENT ON COLUMN assistant_documents.embedding IS 'Vector embedding 768 dimensi untuk semantic search';
COMMENT ON COLUMN assistant_documents.content IS 'Text content untuk backup full-text search';

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Database setup completed successfully!';
    RAISE NOTICE 'Table created: assistant_documents';
    RAISE NOTICE 'Functions created: match_assistant_documents, hybrid_search_assistants';
    RAISE NOTICE 'View created: assistant_summary';
    RAISE NOTICE 'Ready to import CSV data!';
END $$; 