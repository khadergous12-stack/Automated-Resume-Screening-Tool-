# =============================================================
# src/features.py
# Feature Engineering: TF-IDF Similarity + Rule-Based Scoring
# =============================================================

import re
import json
import sqlite3
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ─────────────────────────────────────────────────────────────
# 1. TF-IDF COSINE SIMILARITY
# ─────────────────────────────────────────────────────────────

def compute_tfidf_similarity(jd_text: str, resume_text: str) -> float:
    """
    Computes cosine similarity between job description and resume
    using TF-IDF vectorization.

    TF-IDF = Term Frequency × Inverse Document Frequency
    - Words that appear often in a doc but rarely in others = high score
    - Common words (the, a, is) get low weight automatically

    Returns: float between 0.0 (no match) and 1.0 (perfect match)
    """
    # Basic text cleaning
    def clean(txt):
        txt = txt.lower()
        txt = re.sub(r'[^\w\s]', ' ', txt)
        return re.sub(r'\s+', ' ', txt).strip()

    corpus = [clean(jd_text), clean(resume_text)]

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),      # unigrams + bigrams (e.g., "power bi")
        stop_words='english',    # remove 'the', 'is', etc.
        max_features=5000,       # keep top 5000 terms
        sublinear_tf=True        # log(tf) smoothing
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(round(sim, 4))
    except Exception:
        return 0.0


# ─────────────────────────────────────────────────────────────
# 2. MUST-HAVE SKILL COVERAGE
# ─────────────────────────────────────────────────────────────

def compute_musthave_coverage(must_have_skills: list, candidate_skills: list) -> dict:
    """
    Checks how many must-have skills the candidate has.

    Returns:
      hits        - count of must-haves present
      total       - total must-haves required
      matched     - list of skills matched
      missing     - list of skills missing
      coverage    - ratio (0.0 to 1.0)
    """
    must_set  = set(s.lower().strip() for s in must_have_skills)
    cand_set  = set(s.lower().strip() for s in candidate_skills)

    matched = sorted(list(must_set & cand_set))
    missing = sorted(list(must_set - cand_set))

    hits    = len(matched)
    total   = len(must_set)
    coverage = hits / max(1, total)

    return {
        "hits":     hits,
        "total":    total,
        "matched":  matched,
        "missing":  missing,
        "coverage": round(coverage, 4),
    }


# ─────────────────────────────────────────────────────────────
# 3. EXPERIENCE SCORE
# ─────────────────────────────────────────────────────────────

def compute_experience_score(years_exp: float, min_required: float) -> float:
    """
    Normalized experience score: 0.0 to 1.0.
    - Caps at 1.0 (overqualified is not penalized extra)
    - 0 years always returns 0.0
    """
    if min_required <= 0:
        return 1.0
    return float(min(1.0, years_exp / min_required))


# ─────────────────────────────────────────────────────────────
# 4. GAP PENALTY
# ─────────────────────────────────────────────────────────────

def compute_gap_penalty(missing_skills: list, weight: float = 0.08) -> float:
    """
    Each missing must-have skill applies a penalty.
    weight=0.08 means each missing skill subtracts 0.08 from the total score.
    """
    return round(len(missing_skills) * weight, 4)


# ─────────────────────────────────────────────────────────────
# 5. MASTER FEATURE BUILDER
# ─────────────────────────────────────────────────────────────

def build_features(jd_text: str, jd_must_have: list, jd_min_exp: float,
                   candidate_skills: list, candidate_years: float,
                   resume_raw_text: str) -> dict:
    """
    Computes all features for one candidate vs one job description.

    Returns a feature dict ready for scoring.
    """
    sim      = compute_tfidf_similarity(jd_text, resume_raw_text)
    coverage = compute_musthave_coverage(jd_must_have, candidate_skills)
    exp_score = compute_experience_score(candidate_years, jd_min_exp)
    gap_pen  = compute_gap_penalty(coverage["missing"])

    return {
        "sim_tfidf":            sim,
        "rule_musthave_hits":   coverage["hits"],
        "rule_musthave_total":  coverage["total"],
        "musthave_matched":     coverage["matched"],
        "musthave_missing":     coverage["missing"],
        "musthave_coverage":    coverage["coverage"],
        "years_exp":            candidate_years,
        "exp_score":            exp_score,
        "gap_penalty":          gap_pen,
    }


# ─────────────────────────────────────────────────────────────
# 6. DATABASE STORAGE
# ─────────────────────────────────────────────────────────────

def save_features(db_path: str, candidate_id: str, job_id: str, features: dict):
    """Persist feature row to the features table."""
    con = sqlite3.connect(db_path)
    con.execute(
        """INSERT OR REPLACE INTO features
           (candidate_id, job_id, sim_tfidf,
            rule_musthave_hits, rule_musthave_total, years_exp, gap_penalty)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            candidate_id, job_id,
            features["sim_tfidf"],
            features["rule_musthave_hits"],
            features["rule_musthave_total"],
            features["years_exp"],
            features["gap_penalty"],
        )
    )
    con.commit()
    con.close()
