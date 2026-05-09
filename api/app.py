# =============================================================
# api/app.py
# FastAPI REST API for Resume Screening Tool
#
# Run: uvicorn api.app:app --reload
# Docs: http://localhost:8000/docs
# =============================================================

import os
import sys
import json
import uuid
import sqlite3
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add src/ to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ingest import init_db, save_candidate, save_resume
from extract import parse_resume
from rank import rank_all_candidates, generate_csv_report

# ─────────────────────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Resume Screening API",
    description="Automated resume screening using TF-IDF + skill matching",
    version="1.0.0",
)

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "db/screening.db"

# Initialize DB on startup
os.makedirs("db", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

try:
    init_db(DB_PATH)
except Exception:
    pass   # Already initialized


# ─────────────────────────────────────────────────────────────
# PYDANTIC SCHEMAS
# ─────────────────────────────────────────────────────────────

class JobCreate(BaseModel):
    title:         str
    jd_text:       str
    must_have:     List[str] = []
    nice_to_have:  List[str] = []
    min_exp_years: float = 2.0
    location:      Optional[str] = None


class JobResponse(BaseModel):
    job_id:  str
    message: str


class RankResponse(BaseModel):
    candidate_id:    str
    name:            str
    score:           float
    shortlisted:     bool
    skills_matched:  List[str]
    skills_missing:  List[str]
    years_exp:       float
    reasons:         dict


# ─────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message":  "Resume Screening API is running 🚀",
        "docs":     "/docs",
        "endpoints": ["/job/create", "/resume/upload", "/rank/{job_id}"]
    }


@app.post("/job/create", response_model=JobResponse)
def create_job(job: JobCreate):
    """Create a new job posting with description and required skills."""
    job_id = str(uuid.uuid4())[:8]
    con = sqlite3.connect(DB_PATH)
    try:
        con.execute(
            """INSERT INTO jobs(id, title, jd_text, must_have, nice_to_have, min_exp_years, location)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                job_id, job.title, job.jd_text,
                json.dumps(job.must_have), json.dumps(job.nice_to_have),
                job.min_exp_years, job.location,
            )
        )
        con.commit()
    finally:
        con.close()

    return {"job_id": job_id, "message": f"Job '{job.title}' created with ID: {job_id}"}


@app.post("/resume/upload")
async def upload_resume(
    candidate_id: str = Form(...),
    file: UploadFile = File(...),
):
    """Upload a resume file (TXT/PDF/DOCX) and extract skills."""
    content = await file.read()
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()

    # For demo: handle text directly; PDF/DOCX need temp file
    if ext == ".txt":
        raw_text = content.decode("utf-8", errors="ignore")
    elif ext in (".pdf", ".docx"):
        # Save temp file and extract
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            from ingest import read_resume
            raw_text = read_resume(tmp_path)
        finally:
            os.unlink(tmp_path)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use .txt, .pdf, or .docx")

    parsed = parse_resume(raw_text)
    save_candidate(DB_PATH, candidate_id,
                   name=parsed.get("name", candidate_id),
                   email=parsed.get("email", ""))
    save_resume(DB_PATH, candidate_id, raw_text, parsed, source=ext.strip("."))

    return {
        "ok":          True,
        "candidate_id": candidate_id,
        "skills":      parsed.get("skills", []),
        "years_exp":   parsed.get("years_exp", 0),
        "education":   parsed.get("education", []),
    }


@app.post("/rank/{job_id}")
def rank_candidates(job_id: str, threshold: float = 0.45):
    """Score and rank all uploaded resumes against a job."""
    con = sqlite3.connect(DB_PATH)
    job = con.execute("SELECT id FROM jobs WHERE id=?", (job_id,)).fetchone()
    con.close()

    if not job:
        raise HTTPException(status_code=404, detail=f"Job ID '{job_id}' not found")

    results = rank_all_candidates(DB_PATH, job_id, threshold=threshold)

    # Save CSV report
    csv_path = f"outputs/results_{job_id}.csv"
    generate_csv_report(results, csv_path)

    return [
        {
            "rank":           i + 1,
            "candidate_id":   r["candidate_id"],
            "name":           r["name"],
            "score":          round(r["score"], 4),
            "shortlisted":    r["shortlisted"],
            "skills_matched": r["skills_matched"],
            "skills_missing": r["skills_missing"],
            "years_exp":      r["years_exp"],
            "reasons":        r["reasons"],
        }
        for i, r in enumerate(results)
    ]


@app.get("/jobs")
def list_jobs():
    """List all job postings."""
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute("SELECT id, title, min_exp_years, location FROM jobs").fetchall()
    con.close()
    return [dict(r) for r in rows]


@app.get("/rankings/{job_id}")
def get_rankings(job_id: str):
    """Get stored rankings for a job."""
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        """SELECT r.candidate_id, c.name, r.score, r.shortlisted, r.reasons
           FROM rankings r LEFT JOIN candidates c ON r.candidate_id=c.id
           WHERE r.job_id=? ORDER BY r.score DESC""",
        (job_id,)
    ).fetchall()
    con.close()

    return [
        {**dict(r), "reasons": json.loads(r["reasons"] or "{}")}
        for r in rows
    ]
