# =============================================================
# src/ingest.py
# Resume Text Extraction Module
# Supports: .txt, .pdf (via pdfplumber/PyPDF2), .docx
# =============================================================

import re
import os
import json
import sqlite3
from pathlib import Path

# ── Try importing optional PDF and DOCX libraries ──────────────
try:
    import pdfplumber
    PDF_BACKEND = "pdfplumber"
except ImportError:
    try:
        import PyPDF2
        PDF_BACKEND = "PyPDF2"
    except ImportError:
        PDF_BACKEND = None

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


# ─────────────────────────────────────────────────────────────
# 1. TEXT EXTRACTION
# ─────────────────────────────────────────────────────────────

def extract_text_from_txt(path: str) -> str:
    """Read plain text resume files."""
    return Path(path).read_text(encoding="utf-8", errors="ignore")


def extract_text_from_pdf(path: str) -> str:
    """Extract text from PDF using pdfplumber (preferred) or PyPDF2."""
    text = ""
    if PDF_BACKEND == "pdfplumber":
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    elif PDF_BACKEND == "PyPDF2":
        import PyPDF2
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    else:
        raise ImportError("No PDF library found. Install: pip install pdfplumber")
    return text


def extract_text_from_docx(path: str) -> str:
    """Extract text from Microsoft Word .docx files."""
    if not DOCX_AVAILABLE:
        raise ImportError("python-docx not found. Install: pip install python-docx")
    doc = DocxDocument(path)
    return "\n".join([para.text for para in doc.paragraphs])


def read_resume(path: str) -> str:
    """
    Master function: detects file type and extracts text.
    Returns cleaned raw text string.
    """
    ext = Path(path).suffix.lower()
    if ext == ".txt":
        raw = extract_text_from_txt(path)
    elif ext == ".pdf":
        raw = extract_text_from_pdf(path)
    elif ext == ".docx":
        raw = extract_text_from_docx(path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Use .txt, .pdf, or .docx")

    # Normalize whitespace
    raw = re.sub(r'\s+', ' ', raw).strip()
    return raw


# ─────────────────────────────────────────────────────────────
# 2. DATABASE STORAGE
# ─────────────────────────────────────────────────────────────

def init_db(db_path: str):
    """Initialize SQLite database using schema.sql."""
    schema_path = Path(__file__).parent.parent / "db" / "schema.sql"
    con = sqlite3.connect(db_path)
    with open(schema_path, "r") as f:
        con.executescript(f.read())
    con.commit()
    con.close()
    print(f"  [DB] Initialized database at: {db_path}")


def save_candidate(db_path: str, candidate_id: str, name: str = "", email: str = ""):
    """Insert or update a candidate record."""
    con = sqlite3.connect(db_path)
    con.execute(
        "INSERT OR REPLACE INTO candidates(id, name, email) VALUES (?, ?, ?)",
        (candidate_id, name, email)
    )
    con.commit()
    con.close()


def save_resume(db_path: str, candidate_id: str, raw_text: str,
                parsed: dict, source: str = "txt"):
    """Store raw text and parsed JSON for a resume."""
    con = sqlite3.connect(db_path)
    con.execute(
        """INSERT OR REPLACE INTO resumes
           (candidate_id, source, raw_text, parsed_json, updated_at)
           VALUES (?, ?, ?, ?, datetime('now'))""",
        (candidate_id, source, raw_text, json.dumps(parsed))
    )
    con.commit()
    con.close()


# ─────────────────────────────────────────────────────────────
# 3. BULK INGESTION
# ─────────────────────────────────────────────────────────────

def ingest_all_resumes(resumes_dir: str, db_path: str, parse_fn) -> list:
    """
    Reads all resumes in a directory, extracts text, parses, and stores.
    Returns list of (candidate_id, parsed_data) tuples.
    """
    results = []
    resume_files = list(Path(resumes_dir).glob("*"))
    supported = {".txt", ".pdf", ".docx"}

    for fpath in resume_files:
        if fpath.suffix.lower() not in supported:
            continue

        candidate_id = fpath.stem  # use filename (without ext) as ID
        print(f"  [INGEST] Processing: {fpath.name}")

        try:
            raw_text = read_resume(str(fpath))
            parsed   = parse_fn(raw_text)

            save_candidate(db_path, candidate_id,
                           name=parsed.get("name", candidate_id),
                           email=parsed.get("email", ""))
            save_resume(db_path, candidate_id, raw_text, parsed,
                        source=fpath.suffix.lower().strip("."))

            results.append((candidate_id, parsed))
            print(f"     → Skills found: {parsed.get('skills', [])}")
            print(f"     → Experience:   {parsed.get('years_exp', 0)} yrs")
        except Exception as e:
            print(f"  [ERROR] Could not process {fpath.name}: {e}")

    return results
