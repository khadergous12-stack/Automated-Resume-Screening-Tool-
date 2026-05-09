# =============================================================
# src/rank.py
# Scoring Formula, Ranking, Shortlisting, Report Generation
# =============================================================

import json
import sqlite3
import datetime
import pandas as pd
from pathlib import Path


# ─────────────────────────────────────────────────────────────
# 1. SCORING FORMULA
# ─────────────────────────────────────────────────────────────
#
# SCORE = w1*sim_tfidf + w2*musthave_coverage + w3*exp_score - gap_penalty
#
# Weights (sum to ~1.0):
#   w1 = 0.50  →  TF-IDF semantic similarity (broad match quality)
#   w2 = 0.35  →  Must-have skill coverage   (rule compliance)
#   w3 = 0.15  →  Experience adequacy        (seniority fit)
#  penalty     →  Missing must-haves subtract from total
#
# Score range: ~0.0 (poor match) to ~1.0 (perfect match)
# ─────────────────────────────────────────────────────────────

WEIGHTS = {
    "sim_tfidf":          0.50,
    "musthave_coverage":  0.35,
    "exp_score":          0.15,
}

DEFAULT_THRESHOLD = 0.45   # candidates at/above this score → shortlisted


def calculate_score(features: dict) -> float:
    """
    Applies weighted scoring formula to feature dict.
    Returns a float score (typically 0.0 – 1.0, may go slightly outside).
    """
    raw_score = (
        WEIGHTS["sim_tfidf"]         * features["sim_tfidf"]          +
        WEIGHTS["musthave_coverage"] * features["musthave_coverage"]  +
        WEIGHTS["exp_score"]         * features["exp_score"]
    )
    final_score = raw_score - features["gap_penalty"]
    return round(max(0.0, final_score), 4)   # clip at 0


def generate_reasons(features: dict, score: float) -> dict:
    """
    Build a human-readable explanation dict for the recruiter.
    This is what makes the system explainable (not a black box).
    """
    return {
        "score":               score,
        "tfidf_similarity":    features["sim_tfidf"],
        "musthave_hits":       f"{features['rule_musthave_hits']}/{features['rule_musthave_total']}",
        "skills_matched":      features.get("musthave_matched", []),
        "skills_missing":      features.get("musthave_missing", []),
        "experience_years":    features["years_exp"],
        "experience_adequate": features["exp_score"] >= 1.0,
        "gap_penalty_applied": features["gap_penalty"],
    }


# ─────────────────────────────────────────────────────────────
# 2. RANK ALL CANDIDATES FOR A JOB
# ─────────────────────────────────────────────────────────────

def rank_all_candidates(db_path: str, job_id: str,
                        threshold: float = DEFAULT_THRESHOLD) -> list:
    """
    Reads all resumes from DB, computes features + scores,
    ranks candidates, and stores results.

    Returns: sorted list of result dicts (best first).
    """
    from features import build_features, save_features

    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row

    # Load job details
    job_row = con.execute(
        "SELECT * FROM jobs WHERE id=?", (job_id,)
    ).fetchone()

    if not job_row:
        con.close()
        raise ValueError(f"Job ID '{job_id}' not found in database.")

    jd_text    = job_row["jd_text"]
    must_have  = json.loads(job_row["must_have"] or "[]")
    min_exp    = job_row["min_exp_years"] or 2.0

    # Load all resumes
    resumes = con.execute(
        "SELECT candidate_id, raw_text, parsed_json FROM resumes"
    ).fetchall()
    con.close()

    results = []

    for row in resumes:
        cid      = row["candidate_id"]
        raw_text = row["raw_text"] or ""
        parsed   = json.loads(row["parsed_json"] or "{}")

        candidate_skills = parsed.get("skills", [])
        candidate_years  = parsed.get("years_exp", 0.0)

        # Compute features
        feats = build_features(
            jd_text, must_have, min_exp,
            candidate_skills, candidate_years, raw_text
        )

        # Compute score
        score = calculate_score(feats)

        # Generate explanation
        reasons = generate_reasons(feats, score)

        # Shortlist decision
        shortlisted = score >= threshold and feats["rule_musthave_hits"] > 0

        # Save to DB
        save_features(db_path, cid, job_id, feats)
        _save_ranking(db_path, job_id, cid, score, reasons, shortlisted)

        results.append({
            "candidate_id":   cid,
            "name":           parsed.get("name", cid),
            "score":          score,
            "shortlisted":    shortlisted,
            "skills_found":   candidate_skills,
            "skills_matched": feats.get("musthave_matched", []),
            "skills_missing": feats.get("musthave_missing", []),
            "years_exp":      candidate_years,
            "tfidf_sim":      feats["sim_tfidf"],
            "musthave_cov":   feats["musthave_coverage"],
            "gap_penalty":    feats["gap_penalty"],
            "reasons":        reasons,
        })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def _save_ranking(db_path, job_id, cid, score, reasons, shortlisted):
    """Store final ranking row."""
    con = sqlite3.connect(db_path)
    con.execute(
        """INSERT OR REPLACE INTO rankings
           (job_id, candidate_id, score, reasons, shortlisted, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (job_id, cid, score, json.dumps(reasons),
         int(shortlisted), datetime.datetime.utcnow().isoformat())
    )
    con.commit()
    con.close()


# ─────────────────────────────────────────────────────────────
# 3. PRINT RANKING TABLE
# ─────────────────────────────────────────────────────────────

def print_ranking_table(results: list):
    """Pretty-print the ranking results to terminal."""
    print("\n" + "=" * 80)
    print(f"{'RANK':<5} {'CANDIDATE':<20} {'SCORE':<8} {'STATUS':<14} "
          f"{'MATCHED':<10} {'MISSING':<10} {'EXP(yrs)':<10}")
    print("=" * 80)

    for rank, r in enumerate(results, 1):
        status  = "✅ SHORTLISTED" if r["shortlisted"] else "❌ Rejected"
        matched = len(r["skills_matched"])
        missing = len(r["skills_missing"])
        print(
            f"{rank:<5} {r['name']:<20} {r['score']:<8.4f} "
            f"{status:<14} {matched:<10} {missing:<10} {r['years_exp']:<10}"
        )
        if r["skills_missing"]:
            print(f"       ⚠ Missing must-haves: {', '.join(r['skills_missing'])}")

    print("=" * 80)


# ─────────────────────────────────────────────────────────────
# 4. REPORT GENERATION
# ─────────────────────────────────────────────────────────────

def generate_csv_report(results: list, output_path: str):
    """
    Export ranking results to a CSV file.
    This is the main deliverable for HR teams.
    """
    rows = []
    for rank, r in enumerate(results, 1):
        rows.append({
            "Rank":              rank,
            "Candidate_ID":     r["candidate_id"],
            "Name":             r["name"],
            "Score":            r["score"],
            "Shortlisted":      "Yes" if r["shortlisted"] else "No",
            "TFIDF_Similarity": r["tfidf_sim"],
            "Musthave_Coverage": r["musthave_cov"],
            "Years_Experience": r["years_exp"],
            "Gap_Penalty":      r["gap_penalty"],
            "Skills_Matched":   ", ".join(r["skills_matched"]),
            "Skills_Missing":   ", ".join(r["skills_missing"]),
            "All_Skills_Found": ", ".join(r["skills_found"]),
        })

    df = pd.DataFrame(rows)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\n  [REPORT] CSV saved to: {output_path}")
    return df
