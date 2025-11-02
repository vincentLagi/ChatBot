-- ================================================
-- Database Setup for Rules & Procedure UAP System
-- ================================================

-- Enable necessary extensions (matching assistant system)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Drop existing table if exists
DROP TABLE IF EXISTS rules_procedure_uap CASCADE;

-- Create rules_procedure_uap table (matching assistant system structure)
CREATE TABLE rules_procedure_uap (
    -- Primary key dengan UUID (matching assistant system)
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Keyword untuk search dan display
    keyword TEXT NOT NULL,
    
    -- Content text untuk detailed rules
    content TEXT NOT NULL,
    
    -- Embedding vector dengan dimensi 768 (Google Generative AI)
    embedding vector(768),
    
    -- Metadata sebagai JSONB untuk fleksibilitas (matching assistant system)
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Source information (matching assistant system)
    source_file VARCHAR(255) DEFAULT 'Rules&ProcedureUAP.csv',
    
    -- Timestamps (matching assistant system)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create essential indexes untuk rules search (matching assistant system approach)
-- Index untuk keyword dengan fuzzy search
CREATE INDEX idx_rules_keyword ON rules_procedure_uap USING GIN (keyword gin_trgm_ops);

-- Index untuk content search
CREATE INDEX idx_rules_content ON rules_procedure_uap USING GIN (content gin_trgm_ops);

-- Index untuk embedding similarity search (HNSW untuk performa terbaik, matching assistant system)
CREATE INDEX idx_rules_embedding ON rules_procedure_uap 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Index untuk general JSONB queries (matching assistant system)
CREATE INDEX idx_rules_metadata ON rules_procedure_uap USING GIN (metadata);

-- Index untuk timestamps (matching assistant system)
CREATE INDEX idx_rules_created_at ON rules_procedure_uap (created_at);

-- Function untuk auto-update timestamps (matching assistant system)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger untuk auto-update updated_at (matching assistant system)
CREATE TRIGGER update_rules_uap_updated_at 
    BEFORE UPDATE ON rules_procedure_uap 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Main function: match_rules_procedure_uap (matching assistant system approach)
CREATE OR REPLACE FUNCTION match_rules_procedure_uap(
    query_embedding vector(768),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10,
    filter_keyword text DEFAULT NULL,
    filter_category text DEFAULT NULL
)
RETURNS TABLE (
    id uuid,
    keyword text,
    content text,
    metadata jsonb,
    similarity float,
    created_at timestamp with time zone
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        rules_procedure_uap.id,
        rules_procedure_uap.keyword,
        rules_procedure_uap.content,
        rules_procedure_uap.metadata,
        1 - (rules_procedure_uap.embedding <=> query_embedding) as similarity,
        rules_procedure_uap.created_at
    FROM rules_procedure_uap
    WHERE 
        -- Similarity threshold
        (rules_procedure_uap.embedding <=> query_embedding) < (1 - match_threshold)
        -- Optional keyword filter
        AND (filter_keyword IS NULL OR rules_procedure_uap.keyword ILIKE '%' || filter_keyword || '%')
        -- Optional category filter  
        AND (filter_category IS NULL OR rules_procedure_uap.metadata->>'category' = filter_category)
    ORDER BY rules_procedure_uap.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Function to search by keyword using full-text search (enhanced to match assistant system style)
CREATE OR REPLACE FUNCTION search_rules_by_keyword(
    search_keyword text,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id uuid,
    keyword text,
    content text,
    metadata jsonb,
    relevance float,
    created_at timestamp with time zone
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        rules_procedure_uap.id,
        rules_procedure_uap.keyword,
        rules_procedure_uap.content,
        rules_procedure_uap.metadata,
        similarity(rules_procedure_uap.keyword, search_keyword) AS relevance,
        rules_procedure_uap.created_at
    FROM rules_procedure_uap
    WHERE keyword ILIKE '%' || search_keyword || '%'
       OR content ILIKE '%' || search_keyword || '%'
    ORDER BY similarity(rules_procedure_uap.keyword, search_keyword) DESC
    LIMIT match_count;
END;
$$;

-- Function to get all rules (enhanced to match assistant system style)
CREATE OR REPLACE FUNCTION get_all_rules_uap(
    offset_count int DEFAULT 0,
    limit_count int DEFAULT 50
)
RETURNS TABLE (
    id uuid,
    keyword text,
    content text,
    metadata jsonb,
    created_at timestamp with time zone
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        rules_procedure_uap.id,
        rules_procedure_uap.keyword,
        rules_procedure_uap.content,
        rules_procedure_uap.metadata,
        rules_procedure_uap.created_at
    FROM rules_procedure_uap
    ORDER BY rules_procedure_uap.created_at DESC
    OFFSET offset_count
    LIMIT limit_count;
END;
$$;

-- Function to insert new rule (updated for UUID)
CREATE OR REPLACE FUNCTION insert_rule_uap(
    p_keyword text,
    p_content text,
    p_embedding vector(768),
    p_metadata jsonb DEFAULT '{}'::jsonb
)
RETURNS uuid
LANGUAGE plpgsql
AS $$
DECLARE
    new_id uuid;
BEGIN
    INSERT INTO rules_procedure_uap (keyword, content, embedding, metadata)
    VALUES (p_keyword, p_content, p_embedding, p_metadata)
    RETURNING id INTO new_id;
    
    RETURN new_id;
END;
$$;

-- Function to update rule embedding (updated for UUID)
CREATE OR REPLACE FUNCTION update_rule_embedding(
    p_id uuid,
    p_embedding vector(768)
)
RETURNS boolean
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE rules_procedure_uap 
    SET embedding = p_embedding, updated_at = NOW()
    WHERE id = p_id;
    
    RETURN FOUND;
END;
$$;

-- Helper view untuk easy display data (matching assistant system approach)
CREATE OR REPLACE VIEW rules_uap_view AS
SELECT 
    id,
    keyword,
    content,
    metadata->>'category' as category,
    metadata->>'source' as source,
    metadata->>'priority' as priority,
    created_at,
    updated_at
FROM rules_procedure_uap
ORDER BY created_at DESC;

-- Add table comment (matching assistant system)
COMMENT ON TABLE rules_procedure_uap IS 'Table storing Rules & Procedure UAP with vector embeddings for semantic search';
COMMENT ON FUNCTION match_rules_procedure_uap IS 'Function utama untuk semantic search rules berdasarkan vector similarity';
COMMENT ON COLUMN rules_procedure_uap.keyword IS 'Keyword or topic from Embed column';
COMMENT ON COLUMN rules_procedure_uap.content IS 'Detailed rules and procedures content';
COMMENT ON COLUMN rules_procedure_uap.embedding IS 'Vector embedding of the keyword for semantic search';
COMMENT ON COLUMN rules_procedure_uap.metadata IS 'Additional metadata in JSON format';

-- Success message (matching assistant system)
DO $$
BEGIN
    RAISE NOTICE '✅ Rules UAP database setup completed!';
    RAISE NOTICE '📊 Table: rules_procedure_uap';
    RAISE NOTICE '🔍 Function: match_rules_procedure_uap';
    RAISE NOTICE '👁️ View: rules_uap_view';
    RAISE NOTICE '🚀 Ready to import CSV data!';
END $$; 