-- =============================================
-- MATERIAL AND CRITERIA DATABASE SETUP
-- Supabase Database untuk Material and Criteria search system
-- =============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- 1. MAIN TABLE: material_criteria_documents
-- =============================================

CREATE TABLE IF NOT EXISTS material_criteria_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_code TEXT NOT NULL,
    course_name TEXT NOT NULL,
    type TEXT NOT NULL, -- TM1, TM2, PRY, UAP
    link_download TEXT NOT NULL,
    embedding_text TEXT NOT NULL, -- Text that was embedded
    embedding VECTOR(768),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add comments for documentation
COMMENT ON TABLE material_criteria_documents IS 'Storage for course materials and criteria with vector embeddings';
COMMENT ON COLUMN material_criteria_documents.course_code IS 'Course code (e.g., COMP6048)';
COMMENT ON COLUMN material_criteria_documents.course_name IS 'Course name (e.g., Data Structures)';
COMMENT ON COLUMN material_criteria_documents.type IS 'Assessment type: TM1, TM2, PRY, UAP';
COMMENT ON COLUMN material_criteria_documents.link_download IS 'SharePoint download link';
COMMENT ON COLUMN material_criteria_documents.embedding_text IS 'Text used for embedding (course_code + course_name + type)';
COMMENT ON COLUMN material_criteria_documents.embedding IS 'Vector embedding (768 dimensions)';
COMMENT ON COLUMN material_criteria_documents.metadata IS 'Additional metadata (source, category, etc)';

-- =============================================
-- 2. INDEXES FOR PERFORMANCE
-- =============================================

-- Vector similarity search index (HNSW for fast nearest neighbor)
CREATE INDEX IF NOT EXISTS material_criteria_embedding_idx 
ON material_criteria_documents 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Text search indexes
CREATE INDEX IF NOT EXISTS material_criteria_course_code_idx 
ON material_criteria_documents 
USING gin (course_code gin_trgm_ops);

CREATE INDEX IF NOT EXISTS material_criteria_course_name_idx 
ON material_criteria_documents 
USING gin (course_name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS material_criteria_embedding_text_idx 
ON material_criteria_documents 
USING gin (embedding_text gin_trgm_ops);

-- Category indexes
CREATE INDEX IF NOT EXISTS material_criteria_type_idx 
ON material_criteria_documents (type);

-- Metadata search indexes
CREATE INDEX IF NOT EXISTS material_criteria_metadata_idx 
ON material_criteria_documents 
USING gin (metadata);

-- Timestamp indexes for filtering
CREATE INDEX IF NOT EXISTS material_criteria_created_at_idx 
ON material_criteria_documents (created_at DESC);

-- =============================================
-- 3. SEARCH FUNCTIONS
-- =============================================

-- Function: Semantic similarity search
CREATE OR REPLACE FUNCTION match_material_criteria(
    query_embedding VECTOR(768),
    match_threshold FLOAT DEFAULT 0.3,
    match_count INT DEFAULT 5,
    filter_course_code TEXT DEFAULT NULL,
    filter_type TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    course_code TEXT,
    course_name TEXT,
    type TEXT,
    link_download TEXT,
    embedding_text TEXT,
    similarity FLOAT,
    metadata JSONB,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        mc.id,
        mc.course_code,
        mc.course_name,
        mc.type,
        mc.link_download,
        mc.embedding_text,
        (1 - (mc.embedding <=> query_embedding))::FLOAT AS similarity,
        mc.metadata,
        mc.created_at
    FROM material_criteria_documents mc
    WHERE 
        (1 - (mc.embedding <=> query_embedding)) > match_threshold
        AND (filter_course_code IS NULL OR mc.course_code ILIKE '%' || filter_course_code || '%')
        AND (filter_type IS NULL OR mc.type = filter_type)
    ORDER BY mc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Function: Keyword text search
CREATE OR REPLACE FUNCTION search_material_criteria_keyword(
    search_keyword TEXT,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    course_code TEXT,
    course_name TEXT,
    type TEXT,
    link_download TEXT,
    embedding_text TEXT,
    similarity FLOAT,
    metadata JSONB,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        mc.id,
        mc.course_code,
        mc.course_name,
        mc.type,
        mc.link_download,
        mc.embedding_text,
        1.0::FLOAT AS similarity, -- Full match for keyword search
        mc.metadata,
        mc.created_at
    FROM material_criteria_documents mc
    WHERE 
        mc.course_code ILIKE '%' || search_keyword || '%'
        OR mc.course_name ILIKE '%' || search_keyword || '%'
        OR mc.embedding_text ILIKE '%' || search_keyword || '%'
    ORDER BY 
        CASE 
            WHEN mc.course_code ILIKE search_keyword || '%' THEN 1
            WHEN mc.course_name ILIKE search_keyword || '%' THEN 2
            WHEN mc.embedding_text ILIKE '%' || search_keyword || '%' THEN 3
            ELSE 4
        END,
        mc.course_code,
        mc.type
    LIMIT match_count;
END;
$$;

-- Function: Get all materials for a specific course
CREATE OR REPLACE FUNCTION get_all_course_materials(
    course_identifier TEXT
)
RETURNS TABLE (
    id UUID,
    course_code TEXT,
    course_name TEXT,
    type TEXT,
    link_download TEXT,
    embedding_text TEXT,
    similarity FLOAT,
    metadata JSONB,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        mc.id,
        mc.course_code,
        mc.course_name,
        mc.type,
        mc.link_download,
        mc.embedding_text,
        1.0::FLOAT AS similarity,
        mc.metadata,
        mc.created_at
    FROM material_criteria_documents mc
    WHERE 
        mc.course_code ILIKE '%' || course_identifier || '%'
        OR mc.course_name ILIKE '%' || course_identifier || '%'
    ORDER BY 
        mc.course_code,
        CASE 
            WHEN mc.type = 'TM1' THEN 1
            WHEN mc.type = 'TM2' THEN 2
            WHEN mc.type = 'PRY' THEN 3
            WHEN mc.type = 'UAP' THEN 4
            ELSE 5
        END;
END;
$$;

-- Function: Search materials by type (TM1, TM2, PRY, UAP)
CREATE OR REPLACE FUNCTION search_material_criteria_by_type(
    assessment_type TEXT, -- 'TM1', 'TM2', 'PRY', 'UAP'
    course_filter TEXT DEFAULT NULL,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    course_code TEXT,
    course_name TEXT,
    type TEXT,
    link_download TEXT,
    embedding_text TEXT,
    similarity FLOAT,
    metadata JSONB,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        mc.id,
        mc.course_code,
        mc.course_name,
        mc.type,
        mc.link_download,
        mc.embedding_text,
        1.0::FLOAT AS similarity,
        mc.metadata,
        mc.created_at
    FROM material_criteria_documents mc
    WHERE 
        mc.type = assessment_type
        AND (course_filter IS NULL OR mc.course_code ILIKE '%' || course_filter || '%' OR mc.course_name ILIKE '%' || course_filter || '%')
    ORDER BY mc.course_code
    LIMIT match_count;
END;
$$;

-- Function: Get all materials (browse all)
CREATE OR REPLACE FUNCTION get_all_material_criteria()
RETURNS TABLE (
    id UUID,
    course_code TEXT,
    course_name TEXT,
    type TEXT,
    link_download TEXT,
    embedding_text TEXT,
    similarity FLOAT,
    metadata JSONB,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        mc.id,
        mc.course_code,
        mc.course_name,
        mc.type,
        mc.link_download,
        mc.embedding_text,
        1.0::FLOAT AS similarity,
        mc.metadata,
        mc.created_at
    FROM material_criteria_documents mc
    ORDER BY mc.course_code, mc.type;
END;
$$;

-- =============================================
-- 4. UTILITY FUNCTIONS
-- =============================================

-- Function: Count total materials
CREATE OR REPLACE FUNCTION count_material_criteria()
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    material_count INT;
BEGIN
    SELECT COUNT(*) INTO material_count FROM material_criteria_documents;
    RETURN material_count;
END;
$$;

-- Function: Get material criteria statistics
CREATE OR REPLACE FUNCTION get_material_criteria_stats()
RETURNS TABLE (
    total_materials INT,
    tm1_count INT,
    tm2_count INT,
    pry_count INT,
    uap_count INT,
    unique_courses INT,
    course_codes TEXT[]
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INT AS total_materials,
        COUNT(*) FILTER (WHERE type = 'TM1')::INT AS tm1_count,
        COUNT(*) FILTER (WHERE type = 'TM2')::INT AS tm2_count,
        COUNT(*) FILTER (WHERE type = 'PRY')::INT AS pry_count,
        COUNT(*) FILTER (WHERE type = 'UAP')::INT AS uap_count,
        COUNT(DISTINCT course_code)::INT AS unique_courses,
        ARRAY_AGG(DISTINCT course_code ORDER BY course_code) AS course_codes
    FROM material_criteria_documents;
END;
$$;

-- =============================================
-- 5. ROW LEVEL SECURITY (RLS)
-- =============================================

-- Enable RLS
ALTER TABLE material_criteria_documents ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all access for development (permissive policy)
CREATE POLICY "Allow all access to material criteria" ON material_criteria_documents
    FOR ALL USING (true);

-- =============================================
-- 6. TRIGGERS
-- =============================================

-- Trigger function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_material_criteria_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- Create trigger
CREATE TRIGGER material_criteria_updated_at_trigger
    BEFORE UPDATE ON material_criteria_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_material_criteria_updated_at();

-- =============================================
-- 7. SAMPLE DATA VERIFICATION
-- =============================================

-- Function to verify sample data (for testing)
CREATE OR REPLACE FUNCTION verify_material_criteria_sample()
RETURNS TABLE (
    material_count INT,
    sample_courses TEXT[],
    sample_types TEXT[]
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INT AS material_count,
        ARRAY(SELECT DISTINCT course_code FROM material_criteria_documents ORDER BY course_code LIMIT 5) AS sample_courses,
        ARRAY(SELECT DISTINCT type FROM material_criteria_documents ORDER BY type) AS sample_types
    FROM material_criteria_documents;
END;
$$;

-- =============================================
-- SETUP COMPLETE
-- =============================================

-- Display setup confirmation
DO $$
BEGIN
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'MATERIAL & CRITERIA DATABASE SETUP COMPLETED';
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'Tables created: material_criteria_documents';
    RAISE NOTICE 'Functions: match_material_criteria, search_material_criteria_keyword, get_all_course_materials';
    RAISE NOTICE 'Special: search_material_criteria_by_type, get_all_material_criteria';
    RAISE NOTICE 'Indexes: Vector HNSW, Text GIN, Type, Metadata GIN';
    RAISE NOTICE 'Security: RLS enabled with permissive policies';
    RAISE NOTICE 'Ready for: MaterialAndCriteriaDataset.csv embedding';
    RAISE NOTICE '==============================================';
END;
$$; 