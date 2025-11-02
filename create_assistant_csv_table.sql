-- SQL untuk membuat table assistant_csv di Supabase
-- Jalankan SQL ini di Supabase SQL Editor

CREATE TABLE IF NOT EXISTS assistant_csv (
    id SERIAL PRIMARY KEY,
    initial TEXT,
    gen TEXT,
    initial_gen TEXT,
    name TEXT,
    binusian_id TEXT,
    nim TEXT,
    email_edu TEXT,
    email_ac_id TEXT,
    leader TEXT,
    major_long TEXT,
    major TEXT,
    streaming TEXT,
    semester TEXT,
    global TEXT,
    location TEXT,
    position TEXT,
    shift TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tambahkan index untuk pencarian yang lebih cepat
CREATE INDEX IF NOT EXISTS idx_assistant_csv_initial ON assistant_csv(initial);
CREATE INDEX IF NOT EXISTS idx_assistant_csv_name ON assistant_csv(name);
CREATE INDEX IF NOT EXISTS idx_assistant_csv_location ON assistant_csv(location);
CREATE INDEX IF NOT EXISTS idx_assistant_csv_major ON assistant_csv(major);

-- Enable Row Level Security (RLS) - opsional
-- ALTER TABLE assistant_csv ENABLE ROW LEVEL SECURITY;

-- Buat policy untuk read access (opsional)
-- CREATE POLICY "Allow read access to assistant_csv" ON assistant_csv
--     FOR SELECT USING (true); 