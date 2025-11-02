-- =============================================
-- CORRECTION AND CASE MAKING DATABASE SETUP
-- Supabase Database untuk Correction and Case Making procedures
-- =============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- 1. MAIN TABLE: correction_casemaking_documents
-- =============================================

CREATE TABLE IF NOT EXISTS correction_casemaking_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    keyword TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(768),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add comments for documentation
COMMENT ON TABLE correction_casemaking_documents IS 'Storage for Correction and Case Making procedures with vector embeddings';
COMMENT ON COLUMN correction_casemaking_documents.keyword IS 'Keyword/phrase untuk embedding (from embed column)';
COMMENT ON COLUMN correction_casemaking_documents.content IS 'Full content dari procedure (from Content column)';
COMMENT ON COLUMN correction_casemaking_documents.embedding IS 'Vector embedding dari keyword (768 dimensions)';
COMMENT ON COLUMN correction_casemaking_documents.metadata IS 'Additional metadata (source, category, procedure_type, etc)';

-- =============================================
-- 2. INDEXES FOR PERFORMANCE
-- =============================================

-- Vector similarity search index (HNSW for fast nearest neighbor)
CREATE INDEX IF NOT EXISTS correction_casemaking_embedding_idx 
ON correction_casemaking_documents 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Text search indexes
CREATE INDEX IF NOT EXISTS correction_casemaking_keyword_idx 
ON correction_casemaking_documents 
USING gin (keyword gin_trgm_ops);

CREATE INDEX IF NOT EXISTS correction_casemaking_content_idx 
ON correction_casemaking_documents 
USING gin (content gin_trgm_ops);

-- Metadata search indexes
CREATE INDEX IF NOT EXISTS correction_casemaking_metadata_idx 
ON correction_casemaking_documents 
USING gin (metadata);

-- Timestamp indexes for filtering
CREATE INDEX IF NOT EXISTS correction_casemaking_created_at_idx 
ON correction_casemaking_documents (created_at DESC);

-- =============================================
-- 3. SEARCH FUNCTIONS
-- =============================================

-- Function: Semantic similarity search
CREATE OR REPLACE FUNCTION match_correction_casemaking(
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
        cc.id,
        cc.keyword,
        cc.content,
        (1 - (cc.embedding <=> query_embedding))::FLOAT AS similarity,
        cc.metadata,
        cc.created_at
    FROM correction_casemaking_documents cc
    WHERE 
        (1 - (cc.embedding <=> query_embedding)) > match_threshold
        AND (filter_keyword IS NULL OR cc.keyword ILIKE '%' || filter_keyword || '%')
        AND (filter_category IS NULL OR cc.metadata->>'category' = filter_category)
    ORDER BY cc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Function: Keyword text search
CREATE OR REPLACE FUNCTION search_correction_casemaking_keyword(
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
        cc.id,
        cc.keyword,
        cc.content,
        1.0::FLOAT AS similarity, -- Full match for keyword search
        cc.metadata,
        cc.created_at
    FROM correction_casemaking_documents cc
    WHERE 
        cc.keyword ILIKE '%' || search_keyword || '%'
        OR cc.content ILIKE '%' || search_keyword || '%'
    ORDER BY 
        CASE 
            WHEN cc.keyword ILIKE search_keyword || '%' THEN 1
            WHEN cc.keyword ILIKE '%' || search_keyword || '%' THEN 2
            WHEN cc.content ILIKE '%' || search_keyword || '%' THEN 3
            ELSE 4
        END,
        length(cc.keyword)
    LIMIT match_count;
END;
$$;

-- Function: Get all correction & case making procedures (browse all)
CREATE OR REPLACE FUNCTION get_all_correction_casemaking()
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
        cc.id,
        cc.keyword,
        cc.content,
        1.0::FLOAT AS similarity,
        cc.metadata,
        cc.created_at
    FROM correction_casemaking_documents cc
    ORDER BY cc.created_at ASC;
END;
$$;

-- Function: Search by procedure type (correction vs case making)
CREATE OR REPLACE FUNCTION search_correction_casemaking_by_type(
    procedure_type TEXT, -- 'correction' or 'case_making'
    match_count INT DEFAULT 10
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
        cc.id,
        cc.keyword,
        cc.content,
        1.0::FLOAT AS similarity,
        cc.metadata,
        cc.created_at
    FROM correction_casemaking_documents cc
    WHERE 
        cc.metadata->>'procedure_type' = procedure_type
        OR cc.keyword ILIKE '%' || procedure_type || '%'
    ORDER BY cc.created_at ASC
    LIMIT match_count;
END;
$$;

-- =============================================
-- 4. UTILITY FUNCTIONS
-- =============================================

-- Function: Count total correction & case making procedures
CREATE OR REPLACE FUNCTION count_correction_casemaking()
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    procedure_count INT;
BEGIN
    SELECT COUNT(*) INTO procedure_count FROM correction_casemaking_documents;
    RETURN procedure_count;
END;
$$;

-- Function: Get correction & case making statistics
CREATE OR REPLACE FUNCTION get_correction_casemaking_stats()
RETURNS TABLE (
    total_procedures INT,
    correction_procedures INT,
    casemaking_procedures INT,
    avg_keyword_length FLOAT,
    avg_content_length FLOAT,
    categories TEXT[]
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INT AS total_procedures,
        COUNT(*) FILTER (WHERE keyword ILIKE '%koreks%' OR keyword ILIKE '%correction%')::INT AS correction_procedures,
        COUNT(*) FILTER (WHERE keyword ILIKE '%case%' OR keyword ILIKE '%making%')::INT AS casemaking_procedures,
        AVG(length(keyword))::FLOAT AS avg_keyword_length,
        AVG(length(content))::FLOAT AS avg_content_length,
        ARRAY_AGG(DISTINCT metadata->>'category') FILTER (WHERE metadata->>'category' IS NOT NULL) AS categories
    FROM correction_casemaking_documents;
END;
$$;

-- =============================================
-- 5. ROW LEVEL SECURITY (RLS)
-- =============================================

-- Enable RLS
ALTER TABLE correction_casemaking_documents ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all access for development (permissive policy)
CREATE POLICY "Allow all access to correction casemaking" ON correction_casemaking_documents
    FOR ALL USING (true);

-- =============================================
-- 6. TRIGGERS
-- =============================================

-- Trigger function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_correction_casemaking_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- Create trigger
CREATE TRIGGER correction_casemaking_updated_at_trigger
    BEFORE UPDATE ON correction_casemaking_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_correction_casemaking_updated_at();

-- =============================================
-- 7. SAMPLE DATA VERIFICATION
-- =============================================

-- Function to verify sample data (for testing)
CREATE OR REPLACE FUNCTION verify_correction_casemaking_sample()
RETURNS TABLE (
    procedure_count INT,
    sample_keywords TEXT[],
    avg_similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INT AS procedure_count,
        ARRAY(SELECT keyword FROM correction_casemaking_documents ORDER BY created_at LIMIT 3) AS sample_keywords,
        AVG((embedding <=> '[0.1,0.2,0.3]'::VECTOR))::FLOAT AS avg_similarity
    FROM correction_casemaking_documents;
END;
$$;

-- =============================================
-- SETUP COMPLETE
-- =============================================

-- Display setup confirmation
DO $$
BEGIN
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'CORRECTION & CASE MAKING DATABASE SETUP COMPLETED';
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'Tables created: correction_casemaking_documents';
    RAISE NOTICE 'Functions: match_correction_casemaking, search_correction_casemaking_keyword, get_all_correction_casemaking';
    RAISE NOTICE 'Special: search_correction_casemaking_by_type for filtering';
    RAISE NOTICE 'Indexes: Vector HNSW, Text GIN, Metadata GIN';
    RAISE NOTICE 'Security: RLS enabled with permissive policies';
    RAISE NOTICE 'Ready for: CorrectionAndCaseMaking.csv embedding';
    RAISE NOTICE '==============================================';
END;
$$; 