"""
report_generator.py
-------------------
Generates output reports:
  1. CSV report (outputs/screening_report.csv)
  2. Text summary report (outputs/screening_summary.txt)
"""

import pandas as pd
import os
from datetime import datetime


def save_csv_report(df: pd.DataFrame, output_path: str = "outputs/screening_report.csv"):
    """
    Save the ranked candidates DataFrame to a CSV file.
    Columns: Rank, Candidate, Score, Status, Skills Matched/Missing, etc.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Select and rename columns for CSV readability
    export_cols = {
        "candidate_name":    "Candidate Name",
        "email":             "Email",
        "final_score_pct":   "Overall Score (%)",
        "tfidf_similarity":  "TF-IDF Similarity",
        "skill_match_pct":   "Skill Match (%)",
        "years_experience":  "Years Experience",
        "matched_skills":    "Matched Skills",
        "missing_skills":    "Missing Must-Have Skills",
        "resume_skills":     "All Detected Skills",
        "status":            "Screening Status",
    }

    # Filter to only columns that exist
    available = [c for c in export_cols if c in df.columns]
    export_df = df[available].rename(columns={c: export_cols[c] for c in available})
    export_df.index.name = "Rank"

    # Clean up list columns for CSV readability
    for col in ["Matched Skills", "Missing Must-Have Skills", "All Detected Skills"]:
        if col in export_df.columns:
            export_df[col] = export_df[col].apply(
                lambda x: ", ".join(x) if isinstance(x, list) else str(x)
            )

    export_df.to_csv(output_path)
    print(f"[✅] CSV report saved: {output_path}")
    return output_path


def save_text_summary(df: pd.DataFrame, jd_path: str,
                      output_path: str = "outputs/screening_summary.txt"):
    """
    Save a human-readable text summary of the screening results.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    shortlisted = df[df['status'].str.contains("SHORTLISTED")]
    borderline  = df[df['status'].str.contains("BORDERLINE")]
    rejected    = df[df['status'].str.contains("REJECTED")]

    lines = [
        "=" * 70,
        "   AUTOMATED RESUME SCREENING TOOL - SUMMARY REPORT",
        "=" * 70,
        f"   Generated: {now}",
        f"   Job Description: {jd_path}",
        f"   Total Candidates Screened: {len(df)}",
        "=" * 70,
        "",
        "── SHORTLISTED CANDIDATES ─────────────────────────────────────────",
    ]

    for rank, row in shortlisted.iterrows():
        lines.append(f"  #{rank}  {row['candidate_name']:<20}  Score: {row['final_score_pct']:.1f}%  Skills: {row['skill_match_pct']:.0f}%  Exp: {row['years_experience']:.0f}yr")

    lines.extend(["", "── BORDERLINE CANDIDATES ──────────────────────────────────────────"])
    for rank, row in borderline.iterrows():
        lines.append(f"  #{rank}  {row['candidate_name']:<20}  Score: {row['final_score_pct']:.1f}%  Skills: {row['skill_match_pct']:.0f}%  Exp: {row['years_experience']:.0f}yr")
        if isinstance(row.get('missing_skills'), list) and row['missing_skills']:
            lines.append(f"       Missing: {', '.join(row['missing_skills'][:3])}")

    lines.extend(["", "── REJECTED CANDIDATES ────────────────────────────────────────────"])
    for rank, row in rejected.iterrows():
        lines.append(f"  #{rank}  {row['candidate_name']:<20}  Score: {row['final_score_pct']:.1f}%  Skills: {row['skill_match_pct']:.0f}%")
        if isinstance(row.get('missing_skills'), list) and row['missing_skills']:
            lines.append(f"       Missing: {', '.join(row['missing_skills'][:5])}")

    lines.extend([
        "",
        "=" * 70,
        f"   SUMMARY: ✅ Shortlisted: {len(shortlisted)}  ⚠️ Borderline: {len(borderline)}  ❌ Rejected: {len(rejected)}",
        "=" * 70,
    ])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[✅] Text summary saved: {output_path}")
    return output_path
