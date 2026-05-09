"""
resume_extractor.py
-------------------
Handles text extraction from different resume formats:
  - .txt files  (plain text)
  - .pdf files  (via PyPDF2 / pdfplumber)
  - .docx files (via python-docx)
"""

import os
import re


def extract_from_txt(filepath: str) -> str:
    """Extract text from a plain .txt resume file."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_from_pdf(filepath: str) -> str:
    """
    Extract text from a PDF resume.
    Tries pdfplumber first (better layout), falls back to PyPDF2.
    """
    text = ""
    # Try pdfplumber first
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            return text
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback: PyPDF2
    try:
        import PyPDF2
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    except ImportError:
        print("[WARNING] Neither pdfplumber nor PyPDF2 found. Install: pip install pdfplumber")
    except Exception as e:
        print(f"[ERROR] PDF extraction failed for {filepath}: {e}")

    return text


def extract_from_docx(filepath: str) -> str:
    """Extract text from a .docx resume file."""
    try:
        from docx import Document
        doc = Document(filepath)
        paragraphs = [para.text for para in doc.paragraphs]
        return "\n".join(paragraphs)
    except ImportError:
        print("[WARNING] python-docx not found. Install: pip install python-docx")
        return ""
    except Exception as e:
        print(f"[ERROR] DOCX extraction failed for {filepath}: {e}")
        return ""


def extract_text(filepath: str) -> str:
    """
    Master function: detect file type and extract text.
    Returns raw extracted text string.
    """
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".txt":
        return extract_from_txt(filepath)
    elif ext == ".pdf":
        return extract_from_pdf(filepath)
    elif ext == ".docx":
        return extract_from_docx(filepath)
    else:
        print(f"[WARNING] Unsupported file type: {ext}")
        return ""


def load_all_resumes(resumes_folder: str) -> dict:
    """
    Load all resumes from a folder.
    Returns dict: { candidate_name: raw_text }
    """
    resumes = {}
    supported = {".txt", ".pdf", ".docx"}
    for filename in os.listdir(resumes_folder):
        ext = os.path.splitext(filename)[1].lower()
        if ext in supported:
            filepath = os.path.join(resumes_folder, filename)
            text = extract_text(filepath)
            # Use filename (without extension) as candidate key
            candidate_name = os.path.splitext(filename)[0].replace("_", " ").title()
            if text.strip():
                resumes[candidate_name] = text
            else:
                print(f"[WARNING] Empty text extracted from {filename}")
    return resumes
