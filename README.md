# 🤖 Automated Resume Screening Tool

> **An NLP-powered Python system that automatically extracts skills from resumes, matches them against job descriptions using TF-IDF cosine similarity, ranks candidates, and generates shortlist reports — with an optional Streamlit dashboard and FastAPI REST API.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-TF--IDF-orange)](https://scikit-learn.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009688)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📌 Problem Statement

Recruiters at large companies receive hundreds of resumes per job posting. Manually reading each resume is:
- **Time-consuming** (30–60 seconds per resume × 500 resumes = 8+ hours)
- **Inconsistent** (different recruiters apply different criteria)
- **Prone to bias** (subjective judgements)

This tool solves the problem by automatically extracting skills, scoring candidates against a job description, and producing an explainable, ranked shortlist in seconds.

---

## 🏭 Industry Relevance

| Domain | Application |
|--------|------------|
| HR Tech / ATS | Core shortlisting engine for high-volume hiring |
| Data Science | NLP pipeline + text vectorization + cosine similarity |
| ML Engineering | Feature engineering, scoring, evaluation (ROC/PR AUC) |
| Automation | End-to-end Python pipeline with REST API |
| BI / Analytics | CSV reports, dashboards, ranking tables |

> **Roles this project targets:** Python Developer · Data Analyst · ML Engineer · NLP Engineer · HR Tech · Automation Engineer

---

## ✨ Features

- 📄 **Resume Parsing** — PDF, DOCX, and TXT support
- 🧠 **Skill Extraction** — 60+ skills dictionary with fuzzy matching
- 📐 **TF-IDF Cosine Similarity** — Semantic JD-resume matching
- ✅ **Must-Have Rule Checking** — Hard skill gate with gap penalties
- 📊 **Ranked Shortlist** — Transparent score with reasons
- 📁 **CSV Report** — HR-ready export with all metrics
- 🌐 **Streamlit Dashboard** — Visual recruiter interface
- 🔌 **FastAPI REST API** — Integration-ready endpoints
- 📈 **Evaluation Module** — ROC-AUC, PR-AUC, Top-K Precision
- 🗄️ **SQLite Storage** — Persisted candidates, jobs, rankings

---

## 🗂️ Folder Structure

```
Automated-Resume-Screening-Tool/
│
├── resumes/                    # Input resume files (.txt, .pdf, .docx)
│   ├── alice_johnson.txt
│   ├── bob_kumar.txt
│   ├── carol_patel.txt
│   ├── david_rao.txt
│   └── eva_sharma.txt
│
├── data/
│   ├── job_description.txt     # Job posting config (title, JD, skills, threshold)
│   └── labeled_pairs.csv       # Ground truth labels for evaluation
│
├── src/
│   ├── ingest.py               # File reading + DB storage
│   ├── extract.py              # Skill/entity extraction + text cleaning
│   ├── features.py             # TF-IDF similarity + rule features
│   ├── rank.py                 # Scoring formula + ranking + CSV report
│   └── dashboard.py            # Streamlit UI
│
├── api/
│   └── app.py                  # FastAPI REST API
│
├── notebooks/
│   └── eval.py                 # ROC/PR AUC evaluation script
│
├── db/
│   └── schema.sql              # SQLite schema definition
│
├── outputs/                    # Generated reports (CSV, plots)
│   └── .gitkeep
│
├── docs/                       # Documentation and architecture
├── images/                     # Screenshots for README
│
├── main.py                     # 🚀 Main entry point (run this!)
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🧰 Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | Python 3.10+ | Core development |
| PDF Parsing | pdfplumber / PyPDF2 | Extract text from PDFs |
| DOCX Parsing | python-docx | Extract text from Word files |
| Text Processing | Regex, difflib | Cleaning + fuzzy skill matching |
| Vectorization | scikit-learn TF-IDF | Convert text to vectors |
| Similarity | Cosine Similarity | JD-Resume matching score |
| Data Handling | Pandas, NumPy | Report generation + analysis |
| Storage | SQLite | Candidate/job/ranking persistence |
| Dashboard | Streamlit | Visual recruiter interface |
| REST API | FastAPI + Uvicorn | API endpoints for integration |


---

## ⚙️ Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Automated-Resume-Screening-Tool.git
cd Automated-Resume-Screening-Tool
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run

### Option A: Command Line (Recommended for Beginners)

```bash
python main.py
```
### Option B: Streamlit Dashboard

```bash
streamlit run src/dashboard.py
```
Opens at: `http://localhost:8501`

### Option C: FastAPI REST API

```bash
uvicorn api.app:app --reload
```
API docs at: `http://localhost:8000/docs`
---

## 📊 Sample Output

### Terminal Output

```
============================================================
  🤖 AUTOMATED RESUME SCREENING TOOL
============================================================

[1/5] Initializing database...
[2/5] Loading job description...
      Title:       Data Analyst
      Must-haves:  ['sql', 'excel', 'power bi', 'python', 'pandas']
      Min Exp:     2.0 years

[3/5] Ingesting resumes...
  [INGEST] Processing: alice_johnson.txt
     → Skills: ['excel', 'git', 'matplotlib', 'mysql', 'numpy', 'pandas', 'postgresql', 'power bi', 'python', 'sql']
     → Experience: 3.0 yrs

[4/5] Scoring and ranking candidates...
[5/5] Generating outputs...

================================================================================
RANK  CANDIDATE            SCORE    STATUS         MATCHED    MISSING    EXP(yrs)
================================================================================
1     ALICE JOHNSON        0.7243   ✅ SHORTLISTED  5          0          3.0
2     CAROL PATEL          0.6891   ✅ SHORTLISTED  4          1          4.0
3     EVA SHARMA           0.6512   ✅ SHORTLISTED  4          1          2.0
4     BOB KUMAR            0.3241   ❌ Rejected     2          3          1.5
5     DAVID RAO            0.0412   ❌ Rejected     0          5          0.0

📊 SUMMARY
──────────────────────────────
Total Candidates : 5
✅ Shortlisted   : 3
❌ Rejected      : 2
Threshold Used   : 0.45
🏆 Top Candidate : ALICE JOHNSON (Score: 0.7243)
```

### CSV Report (`outputs/screening_results.csv`)

| Rank | Name | Score | Shortlisted | Years_Exp | Skills_Matched | Skills_Missing |
|------|------|-------|-------------|-----------|----------------|----------------|
| 1 | ALICE JOHNSON | 0.7243 | Yes | 3.0 | sql, excel, power bi, python, pandas | — |
| 2 | CAROL PATEL | 0.6891 | Yes | 4.0 | sql, python, pandas, power bi | excel |
| 3 | EVA SHARMA | 0.6512 | Yes | 2.0 | sql, excel, power bi, python | pandas |
| 4 | BOB KUMAR | 0.3241 | No | 1.5 | sql, python | excel, power bi, pandas |
| 5 | DAVID RAO | 0.0412 | No | 0.0 | — | sql, excel, power bi, python, pandas |

---

## 📐 Scoring Formula

```
SCORE = 0.50 × TF-IDF_Similarity
      + 0.35 × Must-Have_Coverage
      + 0.15 × Experience_Score
      − Gap_Penalty (0.08 per missing must-have)
```

| Component | Weight | Description |
|-----------|--------|-------------|
| TF-IDF Similarity | 50% | Broad semantic match between JD and resume |
| Must-Have Coverage | 35% | Fraction of required skills present |
| Experience Score | 15% | Normalized years (capped at 1.0) |
| Gap Penalty | −0.08/skill | Subtracted for each missing must-have |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/job/create` | Create a job posting |
| POST | `/resume/upload` | Upload and parse a resume |
| POST | `/rank/{job_id}` | Rank all candidates for a job |
| GET | `/jobs` | List all jobs |
| GET | `/rankings/{job_id}` | Get stored rankings |

---

## 📚 Learning Outcomes

After completing this project, you will understand:

- ✅ **Text Extraction** from PDF, DOCX, and TXT files
- ✅ **NLP Preprocessing** — tokenization, stopword removal, normalization
- ✅ **TF-IDF Vectorization** — converting text to numerical features
- ✅ **Cosine Similarity** — measuring document similarity
- ✅ **Rule-Based Systems** — must-have gates + gap penalties
- ✅ **Scoring & Ranking** — weighted formula design
- ✅ **SQLite Database Design** — relational schema for HR data
- ✅ **REST API Design** — FastAPI CRUD endpoints
- ✅ **Model Evaluation** — ROC-AUC, PR-AUC, Top-K Precision
- ✅ **Dashboard Building** — Streamlit UI for non-technical users
- ✅ **Python Project Structure** — modular, production-grade code

---

## 🛡️ Ethics & Compliance

This tool is designed with fairness principles:
- ❌ Never uses gender, age, caste, religion, marital status
- ✅ Only scores on **skills, experience, and education**
- ✅ All decisions are **explainable** (reasons provided per candidate)
- ✅ Threshold is **configurable** by the recruiter
- ✅ Human review is expected before final decisions

---

## 👤 Author

Built as a Python course project for learning NLP, ML, and automation.

**Roles this targets:** Python Developer · Data Analyst · NLP Engineer · HR Tech · ML Engineer · Automation Specialist

---

## 📄 License

MIT License — free to use, modify, and distribute with attribution.
