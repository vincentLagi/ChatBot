-- =============================================
-- RULES PRACTICUM DATABASE SETUP
-- Supabase Database untuk Rules & Procedures Practicum
-- =============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- 1. MAIN TABLE: practicum_rules_documents
-- =============================================

CREATE TABLE IF NOT EXISTS practicum_rules_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    keyword TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(768),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add comments for documentation
COMMENT ON TABLE practicum_rules_documents IS 'Storage for Rules & Procedures Practicum with vector embeddings';
COMMENT ON COLUMN practicum_rules_documents.keyword IS 'Keyword/phrase untuk embedding (from Embed column)';
COMMENT ON COLUMN practicum_rules_documents.content IS 'Full content dari rule (from Content column)';
COMMENT ON COLUMN practicum_rules_documents.embedding IS 'Vector embedding dari keyword (768 dimensions)';
COMMENT ON COLUMN practicum_rules_documents.metadata IS 'Additional metadata (source, category, etc)';

-- =============================================
-- 2. INDEXES FOR PERFORMANCE
-- =============================================

-- Vector similarity search index (HNSW for fast nearest neighbor)
CREATE INDEX IF NOT EXISTS practicum_rules_embedding_idx 
ON practicum_rules_documents 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Text search indexes
CREATE INDEX IF NOT EXISTS practicum_rules_keyword_idx 
ON practicum_rules_documents 
USING gin (keyword gin_trgm_ops);

CREATE INDEX IF NOT EXISTS practicum_rules_content_idx 
ON practicum_rules_documents 
USING gin (content gin_trgm_ops);

-- Metadata search indexes
CREATE INDEX IF NOT EXISTS practicum_rules_metadata_idx 
ON practicum_rules_documents 
USING gin (metadata);

-- Timestamp indexes for filtering
CREATE INDEX IF NOT EXISTS practicum_rules_created_at_idx 
ON practicum_rules_documents (created_at DESC);

-- =============================================
-- 3. SEARCH FUNCTIONS
-- =============================================

-- Function: Semantic similarity search
CREATE OR REPLACE FUNCTION match_practicum_rules(
    query_embedding VECTOR(768),
    match_threshold FLOAT DEFAULT 0.5,
    match_count INT DEFAULT 5,
    filter_keyword TEXT DEFAULT NULL,
    filter_category TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    keyword TEXT,
    content TEXT,
    similarity FLOAT,
    metadata JSONB,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pr.id,
        pr.keyword,
        pr.content,
        (1 - (pr.embedding <=> query_embedding))::FLOAT AS similarity,
        pr.metadata,
        pr.created_at
    FROM practicum_rules_documents pr
    WHERE 
        (1 - (pr.embedding <=> query_embedding)) > match_threshold
        AND (filter_keyword IS NULL OR pr.keyword ILIKE '%' || filter_keyword || '%')
        AND (filter_category IS NULL OR pr.metadata->>'category' = filter_category)
    ORDER BY pr.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Function: Keyword text search
CREATE OR REPLACE FUNCTION search_practicum_rules_keyword(
    search_keyword TEXT,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    keyword TEXT,
    content TEXT,
    similarity FLOAT,
    metadata JSONB,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pr.id,
        pr.keyword,
        pr.content,
        1.0::FLOAT AS similarity, -- Full match for keyword search
        pr.metadata,
        pr.created_at
    FROM practicum_rules_documents pr
    WHERE 
        pr.keyword ILIKE '%' || search_keyword || '%'
        OR pr.content ILIKE '%' || search_keyword || '%'
    ORDER BY 
        CASE 
            WHEN pr.keyword ILIKE search_keyword || '%' THEN 1
            WHEN pr.keyword ILIKE '%' || search_keyword || '%' THEN 2
            WHEN pr.content ILIKE '%' || search_keyword || '%' THEN 3
            ELSE 4
        END,
        length(pr.keyword)
    LIMIT match_count;
END;
$$;

-- Function: Get all practicum rules (browse all)
CREATE OR REPLACE FUNCTION get_all_practicum_rules()
RETURNS TABLE (
    id UUID,
    keyword TEXT,
    content TEXT,
    similarity FLOAT,
    metadata JSONB,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pr.id,
        pr.keyword,
        pr.content,
        1.0::FLOAT AS similarity,
        pr.metadata,
        pr.created_at
    FROM practicum_rules_documents pr
    ORDER BY pr.created_at ASC;
END;
$$;

-- =============================================
-- 4. UTILITY FUNCTIONS
-- =============================================

-- Function: Count total practicum rules
CREATE OR REPLACE FUNCTION count_practicum_rules()
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    rule_count INT;
BEGIN
    SELECT COUNT(*) INTO rule_count FROM practicum_rules_documents;
    RETURN rule_count;
END;
$$;

-- Function: Get practicum rules statistics
CREATE OR REPLACE FUNCTION get_practicum_rules_stats()
RETURNS TABLE (
    total_rules INT,
    avg_keyword_length FLOAT,
    avg_content_length FLOAT,
    categories TEXT[]
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INT AS total_rules,
        AVG(length(keyword))::FLOAT AS avg_keyword_length,
        AVG(length(content))::FLOAT AS avg_content_length,
        ARRAY_AGG(DISTINCT metadata->>'category') FILTER (WHERE metadata->>'category' IS NOT NULL) AS categories
    FROM practicum_rules_documents;
END;
$$;

-- =============================================
-- 5. ROW LEVEL SECURITY (RLS)
-- =============================================

-- Enable RLS
ALTER TABLE practicum_rules_documents ENABLE ROW LEVEL SECURITY;

-- Policy: Allow read access to authenticated users
CREATE POLICY "Allow read access to practicum rules" ON practicum_rules_documents
    FOR SELECT USING (true);

-- Policy: Allow insert/update for service role
CREATE POLICY "Allow insert/update for service role" ON practicum_rules_documents
    FOR ALL USING (auth.role() = 'service_role');

-- =============================================
-- 6. TRIGGERS
-- =============================================

-- Trigger function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_practicum_rules_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- Create trigger
CREATE TRIGGER practicum_rules_updated_at_trigger
    BEFORE UPDATE ON practicum_rules_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_practicum_rules_updated_at();

-- =============================================
-- 7. SAMPLE DATA VERIFICATION
-- =============================================

-- Function to verify sample data (for testing)
CREATE OR REPLACE FUNCTION verify_practicum_rules_sample()
RETURNS TABLE (
    rule_count INT,
    sample_keywords TEXT[],
    avg_similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INT AS rule_count,
        ARRAY(SELECT keyword FROM practicum_rules_documents ORDER BY created_at LIMIT 3) AS sample_keywords,
        AVG((embedding <=> '[0.1,0.2,0.3]'::VECTOR))::FLOAT AS avg_similarity
    FROM practicum_rules_documents;
END;
$$;

-- =============================================
-- SETUP COMPLETE
-- =============================================

-- Display setup confirmation
DO $$
BEGIN
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'PRACTICUM RULES DATABASE SETUP COMPLETED';
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'Tables created: practicum_rules_documents';
    RAISE NOTICE 'Functions: match_practicum_rules, search_practicum_rules_keyword, get_all_practicum_rules';
    RAISE NOTICE 'Indexes: Vector HNSW, Text GIN, Metadata GIN';
    RAISE NOTICE 'Security: RLS enabled with policies';
    RAISE NOTICE 'Ready for: Rules&ProceduresPracticum.csv embedding';
    RAISE NOTICE '==============================================';
END;
$$; 