"""
ranker.py
---------
Ranks candidates based on their scores and makes shortlist decisions.
Generates the final ranked dataframe with all details.
"""

import pandas as pd
from typing import List, Dict


def shortlist_decision(score: float, skill_match_pct: float, threshold: float = 60.0) -> str:
    """
    Make shortlist/reject decision based on score and skill match.
    Rules:
      - SHORTLISTED: final score >= threshold AND skill match >= 50%
      - BORDERLINE:  final score >= (threshold - 10) but below threshold
      - REJECTED:    otherwise
    """
    score_pct = score * 100
    if score_pct >= threshold and skill_match_pct >= 50.0:
        return "✅ SHORTLISTED"
    elif score_pct >= (threshold - 10):
        return "⚠️ BORDERLINE"
    else:
        return "❌ REJECTED"


def rank_candidates(candidates_data: List[Dict], threshold: float = 60.0) -> pd.DataFrame:
    """
    Sort candidates by final_score descending and assign ranks.
    Returns a formatted DataFrame.
    """
    if not candidates_data:
        return pd.DataFrame()

    df = pd.DataFrame(candidates_data)

    # Sort by final score descending
    df = df.sort_values("final_score", ascending=False).reset_index(drop=True)
    df.index += 1  # Rank starts from 1
    df.index.name = "Rank"

    # Add shortlist status
    df["status"] = df.apply(
        lambda row: shortlist_decision(
            row["final_score"],
            row["skill_match_pct"],
            threshold
        ),
        axis=1
    )

    return df


def print_ranking_table(df: pd.DataFrame):
    """Print a formatted ranking table to terminal."""
    print("\n" + "="*90)
    print("  AUTOMATED RESUME SCREENING - CANDIDATE RANKING REPORT")
    print("="*90)

    if df.empty:
        print("  No candidates to display.")
        return

    # Header
    print(f"{'Rank':<5} {'Candidate':<22} {'Score%':<8} {'TF-IDF':<8} "
          f"{'Skills%':<9} {'Exp(yr)':<9} {'Status':<18}")
    print("-"*90)

    for rank, row in df.iterrows():
        print(
            f"{rank:<5} "
            f"{row['candidate_name']:<22} "
            f"{row['final_score_pct']:<8.1f} "
            f"{row['tfidf_similarity']:<8.3f} "
            f"{row['skill_match_pct']:<9.1f} "
            f"{row['years_experience']:<9.1f} "
            f"{row['status']:<18}"
        )

    print("="*90)
    shortlisted = df[df['status'].str.contains("SHORTLISTED")].shape[0]
    borderline  = df[df['status'].str.contains("BORDERLINE")].shape[0]
    rejected    = df[df['status'].str.contains("REJECTED")].shape[0]
    print(f"\n  SUMMARY: {len(df)} candidates | "
          f"✅ Shortlisted: {shortlisted} | "
          f"⚠️ Borderline: {borderline} | "
          f"❌ Rejected: {rejected}")
    print("="*90 + "\n")
