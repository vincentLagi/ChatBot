-- Fix RLS for Correction & Case Making Database
-- Run this if you get permission errors during embedding

-- Temporarily allow all access for development
DROP POLICY IF EXISTS "Allow all access to correction casemaking" ON correction_casemaking_documents;

CREATE POLICY "Allow all access to correction casemaking" ON correction_casemaking_documents
    FOR ALL USING (true);

-- Alternative: Disable RLS temporarily (if above doesn't work)
-- ALTER TABLE correction_casemaking_documents DISABLE ROW LEVEL SECURITY;

-- Verify fix
SELECT COUNT(*) as total_procedures FROM correction_casemaking_documents; 