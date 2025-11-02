-- =============================================
-- QUICK FIX: Practicum RLS Policy for Development
-- Run this in Supabase SQL Editor to allow data insertion
-- =============================================

-- 1. Drop existing restrictive policies
DROP POLICY IF EXISTS "Allow read access to practicum rules" ON practicum_rules_documents;
DROP POLICY IF EXISTS "Allow insert/update for service role" ON practicum_rules_documents;

-- 2. Create permissive policies for development
CREATE POLICY "Allow all access to practicum rules" ON practicum_rules_documents
    FOR ALL USING (true);

-- 3. Verify the policy change
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE tablename = 'practicum_rules_documents';

-- =============================================
-- CONFIRMATION
-- =============================================
DO $$
BEGIN
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'PRACTICUM RLS POLICY UPDATED';
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'Policy: Allow all access for development';
    RAISE NOTICE 'Status: Ready for embedding script';
    RAISE NOTICE 'Security: TEMPORARY - Restrict after development';
    RAISE NOTICE '==============================================';
END;
$$; 