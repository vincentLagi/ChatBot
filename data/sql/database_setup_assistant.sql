-- Supabase Database Setup for SLC Assistant System
-- Focus: Assistant Documents Table Only

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
    
    -- Metadata sebagai JSONB untuk fleksibilitas
    metadata JSONB NOT NULL,
    
    -- Embedding vector dengan dimensi 768 (Google Generative AI)
    embedding vector(768),
    
    -- Content text untuk display dan backup search
    content TEXT,
    
    -- Source information
    source_file VARCHAR(255) DEFAULT 'output.csv',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create essential indexes untuk assistant search
-- Index untuk initial (most common search)
CREATE INDEX idx_assistant_initial ON assistant_documents ((metadata->>'initial'));

-- Index untuk name dengan fuzzy search
CREATE INDEX idx_assistant_name ON assistant_documents USING GIN ((metadata->>'name') gin_trgm_ops);

-- Index untuk location filtering
CREATE INDEX idx_assistant_location ON assistant_documents ((metadata->>'location'));

-- Index untuk major filtering  
CREATE INDEX idx_assistant_major ON assistant_documents ((metadata->>'major'));

-- Index untuk embedding similarity search (HNSW untuk performa terbaik)
CREATE INDEX idx_assistant_embedding ON assistant_documents 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Index untuk general JSONB queries
CREATE INDEX idx_assistant_metadata ON assistant_documents USING GIN (metadata);

-- Function untuk auto-update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger untuk auto-update updated_at
CREATE TRIGGER update_assistant_updated_at 
    BEFORE UPDATE ON assistant_documents 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Main function: match_assistant_documents
CREATE OR REPLACE FUNCTION match_assistant_documents(
    query_embedding vector(768),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10,
    filter_location text DEFAULT NULL,
    filter_major text DEFAULT NULL
)
RETURNS TABLE (
    id uuid,
    metadata jsonb,
    content text,
    similarity float,
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
        assistant_documents.created_at
    FROM assistant_documents
    WHERE 
        -- Similarity threshold
        (assistant_documents.embedding <=> query_embedding) < (1 - match_threshold)
        -- Optional location filter
        AND (filter_location IS NULL OR assistant_documents.metadata->>'location' = filter_location)
        -- Optional major filter  
        AND (filter_major IS NULL OR assistant_documents.metadata->>'major' = filter_major)
    ORDER BY assistant_documents.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Helper view untuk easy display data
CREATE OR REPLACE VIEW assistant_view AS
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
    content,
    created_at,
    updated_at
FROM assistant_documents
ORDER BY metadata->>'initial';

-- Add table comment
COMMENT ON TABLE assistant_documents IS 'Table khusus untuk data assistant SLC dengan embedding search';
COMMENT ON FUNCTION match_assistant_documents IS 'Function utama untuk semantic search assistant berdasarkan vector similarity';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Assistant database setup completed!';
    RAISE NOTICE '📊 Table: assistant_documents';
    RAISE NOTICE '🔍 Function: match_assistant_documents';
    RAISE NOTICE '👁️ View: assistant_view';
    RAISE NOTICE '🚀 Ready to import CSV data!';
END $$; 