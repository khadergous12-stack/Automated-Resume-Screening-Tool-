"""
scorer.py
---------
Computes the similarity score between a resume and a job description using:
  - TF-IDF Vectorization (converts text to numeric vectors)
  - Cosine Similarity (measures angle between two text vectors)
  - Skill match bonus (rule-based must-have coverage)
  - Experience score (years of experience vs. minimum required)

Final score formula:
  score = 0.50 * tfidf_similarity
        + 0.30 * skill_match_ratio
        + 0.20 * experience_score
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def compute_tfidf_similarity(resume_text: str, jd_text: str) -> float:
    """
    Compute cosine similarity between resume and job description
    using TF-IDF vectors.
    Returns float between 0.0 and 1.0
    """
    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',   # Remove common words like 'the', 'and'
            ngram_range=(1, 2),     # Include both single words and 2-word phrases
            max_features=5000       # Limit vocabulary size for efficiency
        )
        # Fit on both documents together, transform each
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(sim), 4)
    except Exception as e:
        print(f"[ERROR] TF-IDF similarity failed: {e}")
        return 0.0


def compute_experience_score(resume_years: float, required_years: float) -> float:
    """
    Score based on years of experience vs required minimum.
    Returns float 0.0 to 1.0:
      - 0.0 if 0 years experience
      - 1.0 if meets or exceeds requirement
    """
    if required_years <= 0:
        return 1.0
    if resume_years <= 0:
        return 0.0
    score = min(1.0, resume_years / required_years)
    return round(score, 4)


def compute_final_score(
    tfidf_sim: float,
    skill_match_ratio: float,
    experience_score: float,
    weights: dict = None
) -> float:
    """
    Combine all sub-scores into one final score.
    Weights default: 50% TF-IDF, 30% skills, 20% experience.
    Returns float 0.0 to 1.0
    """
    if weights is None:
        weights = {"tfidf": 0.50, "skills": 0.30, "experience": 0.20}

    score = (
        weights["tfidf"]      * tfidf_sim +
        weights["skills"]     * skill_match_ratio +
        weights["experience"] * experience_score
    )
    return round(min(1.0, max(0.0, score)), 4)


def score_resume(
    resume_clean: str,
    jd_clean: str,
    skill_info: dict,
    resume_years: float,
    required_years: float = 2.0
) -> dict:
    """
    Master scoring function. Takes cleaned texts + metadata.
    Returns full scoring breakdown dict.
    """
    tfidf_sim       = compute_tfidf_similarity(resume_clean, jd_clean)
    skill_ratio     = skill_info["match_percentage"] / 100.0
    exp_score       = compute_experience_score(resume_years, required_years)
    final_score     = compute_final_score(tfidf_sim, skill_ratio, exp_score)

    return {
        "tfidf_similarity":    tfidf_sim,
        "skill_match_ratio":   round(skill_ratio, 4),
        "experience_score":    exp_score,
        "final_score":         final_score,
        "final_score_pct":     round(final_score * 100, 2),
    }
