-- ============================================================
-- db/schema.sql
-- Automated Resume Screening Tool - Database Schema
-- ============================================================

CREATE TABLE IF NOT EXISTS jobs (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    jd_text     TEXT NOT NULL,
    must_have   TEXT,           -- JSON array of must-have skills
    nice_to_have TEXT,          -- JSON array of nice-to-have skills
    min_exp_years REAL DEFAULT 2.0,
    location    TEXT,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS candidates (
    id          TEXT PRIMARY KEY,
    name        TEXT,
    email       TEXT,
    phone       TEXT,
    location    TEXT
);

CREATE TABLE IF NOT EXISTS resumes (
    candidate_id TEXT PRIMARY KEY REFERENCES candidates(id),
    source      TEXT,           -- 'pdf', 'docx', 'txt'
    raw_text    TEXT,           -- full extracted text
    parsed_json TEXT,           -- structured JSON (skills, exp, edu)
    updated_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS features (
    candidate_id        TEXT REFERENCES candidates(id),
    job_id              TEXT REFERENCES jobs(id),
    sim_tfidf           REAL,   -- TF-IDF cosine similarity (0..1)
    rule_musthave_hits  INTEGER,
    rule_musthave_total INTEGER,
    years_exp           REAL,
    gap_penalty         REAL,
    PRIMARY KEY (candidate_id, job_id)
);

CREATE TABLE IF NOT EXISTS rankings (
    job_id       TEXT,
    candidate_id TEXT,
    score        REAL,
    reasons      TEXT,          -- JSON explanation
    shortlisted  INTEGER DEFAULT 0,  -- 1=yes, 0=no
    created_at   TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (job_id, candidate_id)
);
