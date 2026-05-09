# =============================================================
# src/extract.py
# Skill Extraction, Text Cleaning, Entity Recognition
# Uses: Regex + fuzzy matching (no heavy NLP models needed)
# =============================================================

import re
from difflib import get_close_matches


# ─────────────────────────────────────────────────────────────
# 1. MASTER SKILLS DICTIONARY
# ─────────────────────────────────────────────────────────────

SKILLS_DICT = [
    # Data & Analytics
    "sql", "excel", "power bi", "tableau", "google sheets", "google data studio",
    "dax", "looker", "qlikview", "sas", "spss", "r", "stata",
    # Python ecosystem
    "python", "pandas", "numpy", "matplotlib", "seaborn", "plotly",
    "scipy", "statsmodels", "openpyxl", "xlrd",
    # Machine Learning
    "scikit-learn", "sklearn", "tensorflow", "pytorch", "keras",
    "xgboost", "lightgbm", "catboost", "mlflow", "optuna",
    # NLP
    "spacy", "nltk", "huggingface", "transformers", "bert", "gpt",
    "sentence-transformers", "gensim", "fasttext",
    # Cloud
    "aws", "azure", "gcp", "google cloud", "sagemaker", "ec2", "s3",
    "bigquery", "redshift", "databricks", "snowflake",
    # Engineering
    "docker", "kubernetes", "airflow", "spark", "hadoop", "kafka",
    "fastapi", "flask", "django", "rest api", "graphql",
    # Databases
    "mysql", "postgresql", "mongodb", "redis", "cassandra",
    "sql server", "oracle", "sqlite",
    # Programming
    "java", "javascript", "typescript", "c++", "c", "scala",
    "go", "rust", "kotlin", "swift", "html", "css",
    # Tools
    "git", "github", "jira", "confluence", "linux", "bash",
    "postman", "jupyter", "vscode", "pycharm",
]

# Build a lowercase set for O(1) lookups
SKILLS_SET = set(SKILLS_DICT)


# ─────────────────────────────────────────────────────────────
# 2. TEXT CLEANING
# ─────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """
    Normalize and clean raw resume text.
    Steps: lowercase → remove special chars → collapse whitespace
    """
    text = text.lower()
    # Keep alphanumeric, spaces, dots, +, #, / (useful for C++, C#, etc.)
    text = re.sub(r'[^\w\s\.\+\#\/\-]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ─────────────────────────────────────────────────────────────
# 3. SKILL EXTRACTION
# ─────────────────────────────────────────────────────────────

def extract_skills_exact(text: str) -> list:
    """
    Exact phrase matching against skills dictionary.
    Handles both single-word and multi-word skills (e.g., 'power bi').
    """
    text_lower = text.lower()
    found = set()

    for skill in SKILLS_DICT:
        # Use word-boundary matching for single-word skills
        if " " in skill:
            if skill in text_lower:
                found.add(skill)
        else:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found.add(skill)

    return sorted(list(found))


def extract_skills_fuzzy(text: str, cutoff: float = 0.82) -> list:
    """
    Fuzzy matching for skill variants and typos.
    Example: 'powerbi' → 'power bi', 'sklearn' → 'scikit-learn'
    """
    # Tokenize the text into candidate terms
    tokens = set(re.findall(r'[a-zA-Z][a-zA-Z0-9\+\#\-\.]{1,}', text.lower()))
    found = set()

    for token in tokens:
        # Check against each skill
        matches = get_close_matches(token, SKILLS_DICT, n=1, cutoff=cutoff)
        if matches:
            found.add(matches[0])

    return sorted(list(found))


def extract_skills(text: str) -> list:
    """
    Combined skill extraction: exact first, then fuzzy for extras.
    Returns deduplicated, sorted list of matched skills.
    """
    exact  = set(extract_skills_exact(text))
    fuzzy  = set(extract_skills_fuzzy(text))
    return sorted(list(exact | fuzzy))


# ─────────────────────────────────────────────────────────────
# 4. EXPERIENCE EXTRACTION
# ─────────────────────────────────────────────────────────────

def extract_years_experience(text: str) -> float:
    """
    Extract maximum years of experience mentioned in resume.
    Handles patterns like: '3 years', '2+ years', '1.5 yrs', '4-year'
    """
    text_lower = text.lower()
    years_found = []

    # Pattern 1: "X years/yrs" or "X+ years"
    pattern1 = r'(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\b'
    for match in re.finditer(pattern1, text_lower):
        val = float(match.group(1))
        if 0 < val <= 40:  # sanity check
            years_found.append(val)

    # Pattern 2: "X-year experience"
    pattern2 = r'(\d+)\s*-\s*year'
    for match in re.finditer(pattern2, text_lower):
        val = float(match.group(1))
        if 0 < val <= 40:
            years_found.append(val)

    return max(years_found) if years_found else 0.0


# ─────────────────────────────────────────────────────────────
# 5. CONTACT EXTRACTION
# ─────────────────────────────────────────────────────────────

def extract_email(text: str) -> str:
    """Extract first email address found in text."""
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    """Extract first phone number found in text."""
    match = re.search(r'[\+\d][\d\s\-\(\)]{8,14}\d', text)
    return match.group(0).strip() if match else ""


def extract_name(text: str) -> str:
    """
    Best-effort name extraction: assumes name is in first 2 lines.
    """
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if lines:
        first_line = lines[0]
        # If first line looks like a name (no digits, reasonable length)
        if re.match(r'^[A-Za-z\s\.]{3,50}$', first_line):
            return first_line
    return ""


def extract_education(text: str) -> list:
    """Extract education levels mentioned in resume."""
    text_lower = text.lower()
    education = []
    degrees = {
        "phd": "PhD",
        "m.tech": "M.Tech",
        "mtech": "M.Tech",
        "m.sc": "M.Sc",
        "msc": "M.Sc",
        "mba": "MBA",
        "b.tech": "B.Tech",
        "btech": "B.Tech",
        "b.sc": "B.Sc",
        "bsc": "B.Sc",
        "b.com": "B.Com",
        "bcom": "B.Com",
        "b.e": "B.E",
    }
    for key, label in degrees.items():
        if key in text_lower:
            education.append(label)
    return list(set(education))


# ─────────────────────────────────────────────────────────────
# 6. MASTER PARSE FUNCTION
# ─────────────────────────────────────────────────────────────

def parse_resume(raw_text: str) -> dict:
    """
    Full resume parsing pipeline.
    Input:  raw text string
    Output: structured dict with all extracted fields
    """
    cleaned = clean_text(raw_text)

    return {
        "name":       extract_name(raw_text),        # use original casing
        "email":      extract_email(raw_text),
        "phone":      extract_phone(raw_text),
        "skills":     extract_skills(cleaned),
        "years_exp":  extract_years_experience(cleaned),
        "education":  extract_education(cleaned),
    }
