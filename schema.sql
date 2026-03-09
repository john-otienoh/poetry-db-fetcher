-- ===========================================
-- POETRY DATA STORAGE SCHEMA
-- ===========================================
-- PostgreSQL database schema for storing poetries from PoetryDB API
-- 
-- Created: 2026
-- Database: poetry_data
-- 
-- Usage:
--   psql -U postgres -d poetry_data -f schema.sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS poems (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(500)             NOT NULL,
    author      VARCHAR(255)             NOT NULL,
    lines       JSONB                    NOT NULL DEFAULT '[]',
    linecount   INTEGER                  NOT NULL DEFAULT 0,
    created_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);


CREATE INDEX IF NOT EXISTS idx_poems_author    ON poems (author);
CREATE INDEX IF NOT EXISTS idx_poems_title_trgm  ON poems USING gin (title  gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_poems_author_trgm ON poems USING gin (author gin_trgm_ops);


CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_poems_updated_at ON poems;
CREATE TRIGGER trg_poems_updated_at
    BEFORE UPDATE ON poems
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE VIEW poem_details AS
SELECT id, title, author, lines, linecount, created_at, updated_at
FROM poems
ORDER BY created_at DESC;

CREATE OR REPLACE VIEW poem_statistics AS
SELECT
    author,
    COUNT(*)           AS poem_count,
    AVG(linecount)::int AS avg_lines,
    SUM(linecount)     AS total_lines,
    MIN(created_at)    AS first_added,
    MAX(created_at)    AS last_added
FROM poems
GROUP BY author
ORDER BY poem_count DESC;


INSERT INTO poems (title, author, lines, linecount)
SELECT * FROM (VALUES
    (
        'Not at Home to Callers',
        'Emily Dickinson',
        '["Not at Home to Callers","Says the Naked Tree --","Bonnet due in April --","Wishing you Good Day --"]'::jsonb,
        4
    ),
    (
        'Defrauded I a Butterfly --',
        'Emily Dickinson',
        '["Defrauded I a Butterfly --","The lawful Heir -- for Thee --"]'::jsonb,
        2
    )
) AS seed(title, author, lines, linecount)
WHERE NOT EXISTS (
    SELECT 1 FROM poems WHERE title = seed.title AND author = seed.author
);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO postgres;
