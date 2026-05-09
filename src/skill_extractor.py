"""
skill_extractor.py
------------------
Extracts skills from resume text using:
  1. A curated skills dictionary with aliases
  2. Regex-based pattern matching
  3. Simple fuzzy matching for slight variations
"""

import re
from typing import List, Dict

# ─────────────────────────────────────────────
# Curated Skills Dictionary
# Key = canonical skill name
# Value = list of aliases/variations to match
# ─────────────────────────────────────────────
SKILLS_DICT: Dict[str, List[str]] = {
    # Programming Languages
    "python":        ["python", "python3", "python 3"],
    "sql":           ["sql", "mysql", "postgresql", "postgres", "t-sql", "pl/sql", "sqlite", "mssql"],
    "r":             [r"\br\b", "r programming", "r language"],
    "java":          ["java", "java se", "java ee"],
    "javascript":    ["javascript", "js", "node.js", "nodejs"],
    "scala":         ["scala"],
    "c++":           ["c\\+\\+", "cpp"],
    "c":             [r"\bc\b programming"],

    # Data Analysis / Science Tools
    "pandas":        ["pandas"],
    "numpy":         ["numpy"],
    "matplotlib":    ["matplotlib"],
    "seaborn":       ["seaborn"],
    "plotly":        ["plotly"],
    "scikit-learn":  ["scikit-learn", "sklearn", "scikit learn"],
    "tensorflow":    ["tensorflow", "tf"],
    "pytorch":       ["pytorch", "torch"],
    "xgboost":       ["xgboost"],

    # BI & Visualization
    "power bi":      ["power bi", "powerbi", "power-bi"],
    "tableau":       ["tableau"],
    "excel":         ["excel", "ms excel", "microsoft excel", "advanced excel"],
    "google sheets": ["google sheets"],

    # Databases
    "postgresql":    ["postgresql", "postgres"],
    "mongodb":       ["mongodb", "mongo"],
    "snowflake":     ["snowflake"],
    "oracle":        ["oracle", "oracle db"],

    # Cloud
    "aws":           ["aws", "amazon web services"],
    "azure":         ["azure", "microsoft azure"],
    "gcp":           ["gcp", "google cloud", "google cloud platform"],

    # DevOps / Other
    "docker":        ["docker"],
    "git":           ["git", "github", "gitlab"],
    "airflow":       ["airflow", "apache airflow"],

    # Concepts
    "machine learning": ["machine learning", "ml", "predictive modeling"],
    "deep learning":    ["deep learning", "dl", "neural network", "neural networks"],
    "nlp":              ["nlp", "natural language processing", "text mining"],
    "etl":              ["etl", "etl pipeline", "data pipeline"],
    "data warehousing": ["data warehouse", "data warehousing", "dwh"],
    "statistics":       ["statistics", "statistical analysis", "statistical modeling"],
}


def extract_skills(text: str, skills_dict: Dict[str, List[str]] = None) -> List[str]:
    """
    Extract skills from text using the skills dictionary.
    Returns a sorted list of matched canonical skill names.
    """
    if skills_dict is None:
        skills_dict = SKILLS_DICT

    found_skills = set()
    text_lower = text.lower()

    for canonical, aliases in skills_dict.items():
        for alias in aliases:
            try:
                # Use word-boundary matching for precise hits
                pattern = r'\b' + re.escape(alias) + r'\b'
                # Some aliases already have regex (like r"\br\b")
                if alias.startswith(r'\b') or alias.startswith('\\b'):
                    pattern = alias
                if re.search(pattern, text_lower):
                    found_skills.add(canonical)
                    break
            except re.error:
                # If regex fails, do simple substring match
                if alias.lower() in text_lower:
                    found_skills.add(canonical)
                    break

    return sorted(list(found_skills))


def get_matched_skills(resume_skills: List[str], required_skills: List[str]) -> Dict:
    """
    Compare resume skills against required skills.
    Returns dict with matched, missing, and match percentage.
    """
    required_lower = [s.lower() for s in required_skills]
    resume_lower = [s.lower() for s in resume_skills]

    matched = [s for s in required_lower if s in resume_lower]
    missing = [s for s in required_lower if s not in resume_lower]

    match_pct = round(len(matched) / len(required_lower) * 100, 1) if required_lower else 0.0

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "match_percentage": match_pct,
        "matched_count": len(matched),
        "required_count": len(required_lower),
    }
