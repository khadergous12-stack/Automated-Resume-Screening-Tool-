"""
main.py
-------
Automated Resume Screening Tool - Main Entry Point

Pipeline:
  1. Load resumes from /resumes folder
  2. Load job description from /data/job_description.txt
  3. Extract and clean text from each resume
  4. Extract skills from each resume
  5. Score each resume vs the job description
  6. Rank candidates and make shortlist decisions
  7. Generate CSV and text reports in /outputs

Usage:
  python main.py
  python main.py --resumes resumes/ --jd data/job_description.txt --threshold 60
"""

import os
import sys
import argparse

# Add src/ to Python path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from resume_extractor  import load_all_resumes
from text_cleaner      import clean_text, extract_candidate_name, extract_email, extract_years_experience
from skill_extractor   import extract_skills, get_matched_skills
from scorer            import score_resume
from ranker            import rank_candidates, print_ranking_table
from report_generator  import save_csv_report, save_text_summary


# ─────────────────────────────────────────────
# Required skills for the Data Analyst role
# (Change these to match your job description!)
# ─────────────────────────────────────────────
REQUIRED_SKILLS = [
    "sql",
    "python",
    "excel",
    "power bi",
    "pandas",
    "statistics",
]

NICE_TO_HAVE = [
    "tableau",
    "r",
    "machine learning",
    "aws",
    "etl",
]


def main(resumes_folder="resumes", jd_path="data/job_description.txt",
         threshold=60.0, required_years=2.0):
    """
    Main screening pipeline.
    """
    print("\n" + "="*60)
    print("  🤖 AUTOMATED RESUME SCREENING TOOL")
    print("="*60)

    # ── Step 1: Load Job Description ────────────────────────────
    print(f"\n[1/6] Loading job description from: {jd_path}")
    try:
        with open(jd_path, "r", encoding="utf-8") as f:
            jd_raw = f.read()
        jd_clean = clean_text(jd_raw)
        print(f"      Job description loaded ({len(jd_raw)} chars)")
    except FileNotFoundError:
        print(f"[ERROR] Job description not found: {jd_path}")
        return

    # ── Step 2: Load Resumes ─────────────────────────────────────
    print(f"\n[2/6] Loading resumes from folder: {resumes_folder}")
    raw_resumes = load_all_resumes(resumes_folder)
    if not raw_resumes:
        print("[ERROR] No resumes found. Check the resumes/ folder.")
        return
    print(f"      {len(raw_resumes)} resume(s) loaded: {list(raw_resumes.keys())}")

    # ── Step 3-5: Process Each Resume ───────────────────────────
    print(f"\n[3/6] Extracting text, cleaning, and scoring each resume...")
    print(f"      Required skills: {REQUIRED_SKILLS}")
    print(f"      Min experience: {required_years} years | Shortlist threshold: {threshold}%\n")

    candidates = []

    for filename_key, raw_text in raw_resumes.items():
        # Extract metadata from raw text
        name    = extract_candidate_name(raw_text)
        email   = extract_email(raw_text)
        years   = extract_years_experience(raw_text)

        # Clean the text
        clean   = clean_text(raw_text)

        # Extract skills
        skills  = extract_skills(clean)
        skill_info = get_matched_skills(skills, REQUIRED_SKILLS)

        # Score the resume
        scores  = score_resume(clean, jd_clean, skill_info, years, required_years)

        candidate = {
            "candidate_name":   name,
            "email":            email,
            "resume_file":      filename_key,
            "years_experience": years,
            "resume_skills":    skills,
            "matched_skills":   skill_info["matched_skills"],
            "missing_skills":   skill_info["missing_skills"],
            "skill_match_pct":  skill_info["match_percentage"],
            **scores,
        }
        candidates.append(candidate)

        print(f"  ✔ {name:<22} | Score: {scores['final_score_pct']:5.1f}% "
              f"| Skills: {skill_info['match_percentage']:5.1f}% "
              f"| Exp: {years:.0f}yr "
              f"| Matched: {skill_info['matched_skills']}")

    # ── Step 6: Rank and Shortlist ───────────────────────────────
    print(f"\n[4/6] Ranking {len(candidates)} candidates...")
    ranked_df = rank_candidates(candidates, threshold=threshold)
    print_ranking_table(ranked_df)

    # ── Step 7: Generate Reports ─────────────────────────────────
    print("[5/6] Generating reports...")
    csv_path  = save_csv_report(ranked_df,  output_path="outputs/screening_report.csv")
    txt_path  = save_text_summary(ranked_df, jd_path, output_path="outputs/screening_summary.txt")

    # ── Done ─────────────────────────────────────────────────────
    print(f"\n[6/6] Done! ✅")
    print(f"      📄 CSV Report : {csv_path}")
    print(f"      📋 Text Summary: {txt_path}")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Resume Screening Tool")
    parser.add_argument("--resumes",   default="resumes",                  help="Folder with resume files")
    parser.add_argument("--jd",        default="data/job_description.txt", help="Path to job description")
    parser.add_argument("--threshold", default=60.0, type=float,           help="Shortlist score threshold (0-100)")
    parser.add_argument("--min-years", default=2.0,  type=float,           help="Minimum required years of experience")
    args = parser.parse_args()

    main(
        resumes_folder=args.resumes,
        jd_path=args.jd,
        threshold=args.threshold,
        required_years=args.min_years,
    )
