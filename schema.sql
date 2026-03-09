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

-- ===========================================
-- DROP EXISTING TABLES (if needed)
-- ===========================================
-- Uncomment these lines if you want to recreate tables from scratch
-- WARNING: This will delete all existing data!

DROP TABLE IF EXISTS poets CASCADE;
DROP TABLE IF EXISTS poems CASCADE;
DROP TABLE IF EXISTS title CASCADE;
DROP TABLE IF EXISTS poem_lines CASCADE;


CREATE TABLE poets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE poems (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    author VARCHAR(255) NOT NULL,
    lines JSONB DEFAULT '[]',
    linecount INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_poems_title ON poems(title);
CREATE INDEX idx_poems_author ON poems(author);

CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE OR REPLACE FUNCTION update_updated_at_column()

RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

INSERT INTO poems(title, author, lines, linecount)
VALUES
    (
        'Not at Home to Callers',
        'Emily Dickinson',
        '[
            "Not at Home to Callers",
            "Says the Naked Tree --",
            "Bonnet due in April --",
            "Wishing you Good Day --"
        ]'::JSONB,
        4
    ),
    (
        'Defrauded I a Butterfly --',
        'Emily Dickinson',
        '[
            "Defrauded I a Butterfly --",
            "The lawful Heir -- for Thee --"
        ]'::JSONB,
        2
    );

INSERT INTO poets (name) VALUES
    ('Emily Dickinson'),
    ('John Charles');

CREATE OR REPLACE VIEW poem_details AS
SELECT 
    id,
    title,
    author,
    lines,
    linecount,
    created_at,
    updated_at
FROM poems
ORDER BY created_at DESC;

CREATE OR REPLACE VIEW poem_statistics AS
SELECT 
    author,
    COUNT(*) as poem_count,
    AVG(linecount) as avg_lines,
    SUM(linecount) as total_lines,
    MIN(created_at) as first_poem,
    MAX(created_at) as last_poem
FROM poems
GROUP BY author
ORDER BY poem_count DESC;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO postgres;