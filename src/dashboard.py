# =============================================================
# src/dashboard.py
# Automated Resume Screening Tool — Streamlit Dashboard
#
# Run: streamlit run src/dashboard.py
# Developer: Khadergouse Savanur
# =============================================================

import io
import os
import sys
import tempfile
import pathlib
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Make both the project root AND src/ importable
_ROOT = Path(__file__).parent.parent
_SRC  = Path(__file__).parent
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_SRC))

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Resume Screening Tool",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# GLOBAL CSS — light theme, vibrant accent colours
# ─────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: #fafaf8 !important;
    color: #111827 !important;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="collapsedControl"] { display: none; }
.block-container { max-width: 1100px !important; padding: 2rem 2rem 3rem !important; }

.hero-header {
    display: flex; align-items: center; gap: 1rem;
    margin-bottom: 2rem; padding: 1.75rem 2rem;
    background: #ffffff; border: 1px solid #e5e7eb;
    border-radius: 18px; border-left: 6px solid #6c3de8;
}
.hero-logo {
    width: 56px; height: 56px;
    background: linear-gradient(135deg, #6c3de8, #e8386c);
    border-radius: 14px; display: flex; align-items: center;
    justify-content: center; font-size: 26px; flex-shrink: 0;
}
.hero-title {
    font-family: 'Sora', sans-serif !important;
    font-size: 1.6rem !important; font-weight: 700 !important;
    color: #111827 !important; margin: 0 !important;
}
.hero-sub { font-size: 0.85rem; color: #6b7280; margin-top: 3px; }
.ai-badge {
    display: inline-flex; align-items: center; gap: 4px;
    background: #ede9fd; color: #5b21b6; font-size: 11px;
    font-weight: 700; padding: 3px 10px; border-radius: 20px;
    text-transform: uppercase; letter-spacing: .5px;
    margin-left: 10px; vertical-align: middle;
}

.steps-row {
    display: flex; align-items: center; background: #ffffff;
    border: 1px solid #e5e7eb; border-radius: 14px;
    padding: 1rem 1.75rem; margin-bottom: 2rem;
}
.step-item { display: flex; align-items: center; gap: 10px; flex: 1; }
.step-divider { width: 28px; height: 1px; background: #d1d5db; flex-shrink: 0; }
.step-num {
    width: 32px; height: 32px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700; flex-shrink: 0;
}
.step-num.active { background: #6c3de8; color: #fff; }
.step-num.idle   { background: #f3f4f6; color: #9ca3af; }
.step-label small { display: block; font-size: 10px; text-transform: uppercase; letter-spacing: .5px; color: #9ca3af; font-weight: 600; }
.step-label span  { font-size: 13px; font-weight: 500; color: #374151; }

.upload-label { font-size: .85rem; font-weight: 600; color: #374151; margin-bottom: .3rem; }
.upload-hint  { font-size: .75rem; color: #9ca3af; margin-bottom: .6rem; }

textarea {
    font-family: 'DM Sans', sans-serif !important; font-size: .82rem !important;
    border-radius: 10px !important; border: 1.5px solid #d1d5db !important;
    background: #f9fafb !important; color: #111827 !important;
}
textarea:focus { border-color: #6c3de8 !important; }

.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #6c3de8 0%, #e8386c 100%) !important;
    color: #ffffff !important; border: none !important; border-radius: 12px !important;
    padding: .85rem 1.5rem !important; font-family: 'Sora', sans-serif !important;
    font-size: 1rem !important; font-weight: 600 !important; letter-spacing: .3px !important;
    transition: transform .2s, box-shadow .2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(108,61,232,.35) !important;
}

[data-testid="stMetric"] {
    background: #ffffff !important; border: 1px solid #e5e7eb !important;
    border-radius: 14px !important; padding: 1.1rem 1.25rem !important;
}
[data-testid="stMetricLabel"] { font-size:.75rem !important; color:#9ca3af !important; text-transform:uppercase; letter-spacing:.5px; }
[data-testid="stMetricValue"] { font-family:'Sora',sans-serif !important; font-size:1.8rem !important; font-weight:700 !important; color:#111827 !important; }

.streamlit-expanderHeader {
    background: #f9fafb !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: .9rem !important; color: #111827 !important;
}
.streamlit-expanderContent {
    background: #ffffff !important; border: 1px solid #e5e7eb !important;
    border-top: none !important; border-radius: 0 0 10px 10px !important;
}

.skill-pill-match { display:inline-block; background:#dcfce7; color:#166534; font-size:11px; font-weight:500; padding:2px 9px; border-radius:20px; margin:2px; }
.skill-pill-miss  { display:inline-block; background:#fee2e2; color:#991b1b; font-size:11px; font-weight:500; padding:2px 9px; border-radius:20px; margin:2px; }

.how-card { background:#ffffff; border:1px solid #e5e7eb; border-radius:14px; padding:1.25rem; text-align:center; }
.how-step { font-size:10px; font-weight:700; color:#d1d5db; text-transform:uppercase; letter-spacing:1px; margin-bottom:.5rem; }
.how-card h4 { font-family:'Sora',sans-serif; font-size:.9rem; font-weight:700; color:#111827; margin-bottom:.35rem; }
.how-card p  { font-size:.78rem; color:#9ca3af; line-height:1.55; margin:0; }

.stDownloadButton > button {
    background:#111827 !important; color:#ffffff !important;
    border-radius:10px !important; border:none !important;
    padding:.6rem 1.25rem !important; font-size:.85rem !important; font-weight:600 !important;
}
.stDownloadButton > button:hover { background:#1f2937 !important; }

.roadmap-box {
    margin-top:1rem; padding:1.4rem 1.5rem;
    background:linear-gradient(135deg,#fffbeb,#fff7ed);
    border:2px solid #fcd34d; border-radius:16px;
}
.roadmap-title {
    font-size:1.05rem; font-weight:800; color:#78350f;
    margin-bottom:1rem; display:flex; align-items:center; gap:8px;
    letter-spacing:-.2px;
}
.roadmap-action {
    display:flex; gap:14px; align-items:flex-start;
    margin-bottom:.9rem; padding:.75rem 1rem;
    background:#ffffff; border-radius:12px;
    border:1px solid #fde68a;
    box-shadow:0 1px 4px rgba(0,0,0,.06);
}
.roadmap-action-icon { font-size:26px; flex-shrink:0; line-height:1; margin-top:2px; }
.roadmap-action-title {
    font-size:.95rem; font-weight:800; color:#1f2937;
    margin-bottom:4px; letter-spacing:-.1px; line-height:1.3;
}
.roadmap-action-desc {
    font-size:.82rem; color:#4b5563; margin-top:2px;
    line-height:1.6; font-weight:400;
}

.dev-footer { margin-top:3rem; padding-top:2rem; border-top:1px solid #e5e7eb; display:flex; justify-content:center; }
.dev-card {
    display:inline-flex; align-items:center; gap:12px;
    background:#ffffff; border:1px solid #e5e7eb; border-radius:50px;
    padding:.65rem 1.5rem .65rem 1rem;
    box-shadow:0 2px 8px rgba(0,0,0,.06);
    transition:transform .25s, box-shadow .25s, border-color .25s; cursor:default;
}
.dev-card:hover { transform:translateY(-4px); box-shadow:0 12px 32px rgba(108,61,232,.22); border-color:#a78bfa; }
.dev-avatar {
    width:38px; height:38px; background:linear-gradient(135deg,#6c3de8,#e8386c);
    border-radius:50%; display:flex; align-items:center; justify-content:center;
    font-family:'Sora',sans-serif; font-size:13px; font-weight:700; color:#fff; flex-shrink:0;
}
.dev-info small { display:block; font-size:10px; color:#9ca3af; font-weight:500; text-transform:uppercase; letter-spacing:.5px; }
.dev-info strong { display:block; font-family:'Sora',sans-serif; font-size:.95rem; font-weight:700; color:#111827; margin-top:1px; }
.dev-badge { background:linear-gradient(135deg,#ede9fd,#fde8ef); color:#6c3de8; font-size:11px; font-weight:700; padding:4px 14px; border-radius:20px; letter-spacing:.3px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# PDF REPORT GENERATOR
# ─────────────────────────────────────────────────────────────

def generate_pdf_report(ranked_df, candidates_detail, required_skills,
                        name_col, score_col, short_col, skill_col,
                        years_col, rank_col, threshold=60.0):
    """Generate a polished PDF report and return bytes."""

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    # ── Colour palette ────────────────────────────────────────
    PURPLE   = colors.HexColor("#6c3de8")
    PINK     = colors.HexColor("#e8386c")
    GREEN    = colors.HexColor("#16a34a")
    RED      = colors.HexColor("#dc2626")
    AMBER    = colors.HexColor("#d97706")
    LIGHT_BG = colors.HexColor("#f9fafb")
    BORDER   = colors.HexColor("#e5e7eb")
    DARK     = colors.HexColor("#111827")
    GREY     = colors.HexColor("#6b7280")
    GREEN_BG = colors.HexColor("#dcfce7")
    RED_BG   = colors.HexColor("#fee2e2")
    AMBER_BG = colors.HexColor("#fef3c7")

    base_styles = getSampleStyleSheet()

    def ps(name, **kw):
        return ParagraphStyle(name, parent=base_styles["Normal"], **kw)

    title_style   = ps("Title",   fontSize=20, textColor=DARK,   fontName="Helvetica-Bold",
                       alignment=TA_CENTER, spaceAfter=4)
    sub_style     = ps("Sub",     fontSize=9,  textColor=GREY,   alignment=TA_CENTER, spaceAfter=2)
    h1_style      = ps("H1",      fontSize=13, textColor=PURPLE, fontName="Helvetica-Bold",
                       spaceBefore=14, spaceAfter=6)
    h2_style      = ps("H2",      fontSize=10, textColor=DARK,   fontName="Helvetica-Bold",
                       spaceBefore=10, spaceAfter=4)
    body_style    = ps("Body",    fontSize=8.5, textColor=DARK,  leading=13)
    small_style   = ps("Small",   fontSize=7.5, textColor=GREY,  leading=11)
    badge_green   = ps("BG",      fontSize=8,  textColor=GREEN,  fontName="Helvetica-Bold")
    badge_red     = ps("BR",      fontSize=8,  textColor=RED,    fontName="Helvetica-Bold")
    roadmap_title = ps("RMT",     fontSize=9,  textColor=colors.HexColor("#92400e"),
                       fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=3)
    roadmap_body  = ps("RMB",     fontSize=8,  textColor=GREY,   leading=12)
    caption_style = ps("Cap",     fontSize=7.5, textColor=GREY,  leading=11, fontName="Helvetica-Oblique")

    story = []

    # ── Cover banner ─────────────────────────────────────────
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("🤖  Automated Resume Screening Report", title_style))
    story.append(Paragraph("AI-Powered Candidate Ranking &amp; Shortlist Analysis", sub_style))
    story.append(Paragraph("Developed by Khadergouse Savanur", sub_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=PURPLE))
    story.append(Spacer(1, 0.4*cm))

    # ── Summary metrics table ─────────────────────────────────
    story.append(Paragraph("Screening Summary", h1_style))

    total       = len(ranked_df)
    shortlisted = int((ranked_df[short_col] == "Yes").sum()) if short_col else 0
    rejected    = total - shortlisted
    avg_score   = float(ranked_df[score_col].mean()) if score_col else 0.0
    pass_rate   = shortlisted / max(1, total) * 100

    metric_data = [
        ["Total Candidates", "Shortlisted ✓", "Not Shortlisted ✗", "Avg Score"],
        [str(total), str(shortlisted), str(rejected), f"{avg_score:.1f}%"],
        ["", f"{pass_rate:.0f}% pass rate", f"{100-pass_rate:.0f}% rejection rate", ""],
    ]
    metric_table = Table(metric_data, colWidths=["25%","25%","25%","25%"])
    metric_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), LIGHT_BG),
        ("TEXTCOLOR",   (0,0), (-1,0), GREY),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica"),
        ("FONTSIZE",    (0,0), (-1,0), 7),
        ("FONTNAME",    (0,1), (-1,1), "Helvetica-Bold"),
        ("FONTSIZE",    (0,1), (-1,1), 16),
        ("TEXTCOLOR",   (0,1), (0,1), DARK),
        ("TEXTCOLOR",   (1,1), (1,1), GREEN),
        ("TEXTCOLOR",   (2,1), (2,1), RED),
        ("TEXTCOLOR",   (3,1), (3,1), PURPLE),
        ("FONTSIZE",    (0,2), (-1,2), 7),
        ("TEXTCOLOR",   (0,2), (-1,2), GREY),
        ("ALIGN",       (0,0), (-1,-1), "CENTER"),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [LIGHT_BG, colors.white, colors.white]),
        ("BOX",         (0,0), (-1,-1), 0.5, BORDER),
        ("INNERGRID",   (0,0), (-1,-1), 0.5, BORDER),
        ("TOPPADDING",  (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("ROUNDEDCORNERS", [4]),
    ]))
    story.append(metric_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Rankings table ────────────────────────────────────────
    story.append(Paragraph("Candidate Rankings", h1_style))

    show_cols = [c for c in [rank_col, name_col, score_col, short_col, skill_col, years_col] if c]
    header_labels = {
        rank_col:  "Rank", name_col: "Candidate Name",
        score_col: "Score (%)", short_col: "Status",
        skill_col: "Skill Match (%)", years_col: "Experience (yrs)",
    }
    headers  = [header_labels.get(c, c) for c in show_cols]
    col_widths = []
    for c in show_cols:
        if c == name_col: col_widths.append(4.5*cm)
        elif c == rank_col: col_widths.append(1.2*cm)
        else: col_widths.append(3*cm)

    table_data = [headers]
    for _, row in ranked_df[show_cols].iterrows():
        r = []
        for c in show_cols:
            v = row[c]
            if c == score_col and v is not None:
                r.append(f"{float(v):.1f}%")
            elif c == skill_col and v is not None:
                r.append(f"{float(v):.1f}%")
            elif c == years_col and v is not None:
                r.append(f"{float(v):.1f} yrs")
            else:
                r.append(str(v))
        table_data.append(r)

    rank_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    ts = TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), PURPLE),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0), 8),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("FONTSIZE",      (0,1), (-1,-1), 8),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ("BOX",           (0,0), (-1,-1), 0.5, BORDER),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ])
    # Colour the status column
    if short_col in show_cols:
        si = show_cols.index(short_col)
        for row_idx, (_, row) in enumerate(ranked_df.iterrows(), start=1):
            if str(row.get(short_col,"")) == "Yes":
                ts.add("TEXTCOLOR",  (si,row_idx), (si,row_idx), GREEN)
                ts.add("FONTNAME",   (si,row_idx), (si,row_idx), "Helvetica-Bold")
                ts.add("BACKGROUND", (si,row_idx), (si,row_idx), GREEN_BG)
            else:
                ts.add("TEXTCOLOR",  (si,row_idx), (si,row_idx), RED)
                ts.add("FONTNAME",   (si,row_idx), (si,row_idx), "Helvetica-Bold")
                ts.add("BACKGROUND", (si,row_idx), (si,row_idx), RED_BG)
    # Colour the score column
    if score_col in show_cols:
        sc = show_cols.index(score_col)
        for row_idx, (_, row) in enumerate(ranked_df.iterrows(), start=1):
            try:
                v = float(row.get(score_col, 0))
                clr = GREEN if v >= 60 else (AMBER if v >= 40 else RED)
                ts.add("TEXTCOLOR", (sc,row_idx), (sc,row_idx), clr)
                ts.add("FONTNAME",  (sc,row_idx), (sc,row_idx), "Helvetica-Bold")
            except Exception:
                pass
    rank_table.setStyle(ts)
    story.append(rank_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Per-candidate detail pages ────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Candidate Detail Report", h1_style))
    story.append(Spacer(1, 0.2*cm))

    REQUIRED_SKILLS = required_skills

    for i, (_, row) in enumerate(ranked_df.iterrows()):
        cname   = str(row.get(name_col,  "Candidate"))
        cscore  = float(row.get(score_col, 0)) if score_col else 0.0
        cyears  = float(row.get(years_col, 0)) if years_col else 0.0
        cshort  = str(row.get(short_col,  "No")) if short_col else "No"
        cskill  = float(row.get(skill_col, 0) or 0) if skill_col else 0.0
        matched = list(row.get("matched_skills", []) or [])
        missing = list(row.get("missing_skills", []) or [])
        all_sk  = list(row.get("resume_skills",  []) or [])
        rank_n  = str(row.get(rank_col, i+1)) if rank_col else str(i+1)

        status_txt   = "SHORTLISTED ✓" if cshort == "Yes" else "NOT SHORTLISTED ✗"
        status_color = GREEN if cshort == "Yes" else RED
        status_bg    = GREEN_BG if cshort == "Yes" else RED_BG

        # Candidate header block
        header_data = [[
            Paragraph(f"#{rank_n}  {cname}", ps("ch", fontSize=11, textColor=DARK,
                       fontName="Helvetica-Bold")),
            Paragraph(status_txt, ps("cs", fontSize=9, textColor=status_color,
                       fontName="Helvetica-Bold", alignment=TA_RIGHT)),
        ]]
        header_tbl = Table(header_data, colWidths=["70%","30%"])
        header_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), LIGHT_BG),
            ("BOX",           (0,0), (-1,-1), 1, PURPLE if cshort=="Yes" else RED),
            ("LEFTPADDING",   (0,0), (-1,-1), 10),
            ("RIGHTPADDING",  (0,0), (-1,-1), 10),
            ("TOPPADDING",    (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
            ("BACKGROUND",    (1,0), (1,0), status_bg),
        ]))
        story.append(header_tbl)
        story.append(Spacer(1, 0.2*cm))

        # Metrics row
        metrics_data = [
            ["Score", "Experience", "Skill Match"],
            [f"{cscore:.1f}%", f"{cyears:.1f} yrs", f"{cskill:.1f}%"],
        ]
        metrics_tbl = Table(metrics_data, colWidths=["33%","33%","34%"])
        score_clr = GREEN if cscore >= 60 else (AMBER if cscore >= 40 else RED)
        metrics_tbl.setStyle(TableStyle([
            ("FONTNAME",      (0,0), (-1,0), "Helvetica"),
            ("FONTSIZE",      (0,0), (-1,0), 7),
            ("TEXTCOLOR",     (0,0), (-1,0), GREY),
            ("FONTNAME",      (0,1), (-1,1), "Helvetica-Bold"),
            ("FONTSIZE",      (0,1), (-1,1), 13),
            ("TEXTCOLOR",     (0,1), (0,1), score_clr),
            ("TEXTCOLOR",     (1,1), (1,1), PURPLE),
            ("TEXTCOLOR",     (2,1), (2,1), DARK),
            ("ALIGN",         (0,0), (-1,-1), "CENTER"),
            ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
            ("BOX",           (0,0), (-1,-1), 0.5, BORDER),
            ("INNERGRID",     (0,0), (-1,-1), 0.3, BORDER),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("BACKGROUND",    (0,0), (-1,-1), colors.white),
        ]))
        story.append(metrics_tbl)
        story.append(Spacer(1, 0.2*cm))

        # Skills section
        if matched:
            story.append(Paragraph(
                "<b>Matched Skills:</b>  " + "  |  ".join(s.title() for s in matched),
                ps("sm", fontSize=8, textColor=GREEN, leading=12)))
        if missing:
            story.append(Paragraph(
                "<b>Missing Skills:</b>  " + "  |  ".join(s.title() for s in missing),
                ps("sm2", fontSize=8, textColor=RED, leading=12)))
        if all_sk:
            story.append(Paragraph(
                "All detected skills:  " + ", ".join(str(s) for s in all_sk),
                caption_style))

        story.append(Spacer(1, 0.15*cm))

        # ── IMPROVEMENT ROADMAP (rejected only) ───────────────
        if cshort != "Yes":
            gap           = round(threshold - cscore, 1)
            total_req     = len(REQUIRED_SKILLS)
            skill_boost   = round((100.0 / max(1, total_req)) * 0.4, 1)
            skills_needed = max(1, int(
                (gap / skill_boost) + (0 if gap % skill_boost == 0 else 1)
            )) if skill_boost > 0 else len(missing)

            roadmap_rows = []

            # Title
            roadmap_rows.append([
                Paragraph("🚀  What this candidate needs to get shortlisted", roadmap_title)
            ])

            # Score progress bar (text representation)
            bar_filled  = min(int(cscore), 100)
            bar_empty   = 100 - bar_filled
            bar_str     = ("█" * (bar_filled // 5)) + ("░" * (bar_empty // 5))
            roadmap_rows.append([
                Paragraph(
                    f"Current score: <b>{cscore:.1f}%</b>  →  Need: <b>60%</b>  "
                    f"(+{gap}% gap)<br/>"
                    f"<font color='#e8386c'>{bar_str[:20]}</font>"
                    f"<font color='#d1d5db'>{bar_str[20:]}</font>  "
                    f"Threshold: 60%",
                    ps("bar", fontSize=8, textColor=DARK, leading=14))
            ])

            # Action 1: Missing skills
            if missing:
                top_skills  = missing[:skills_needed]
                skill_names = ", ".join(s.title() for s in top_skills)
                est_boost   = min(len(top_skills) * skill_boost, gap)
                roadmap_rows.append([
                    Paragraph(
                        f"<b>📚  Learn {len(top_skills)} missing skill(s): {skill_names}</b><br/>"
                        f"Each required skill adds ~{skill_boost:.0f}% to the score. "
                        f"Adding these {len(top_skills)} skill(s) could boost the score "
                        f"by ~{est_boost:.0f}% — bringing you to ~{min(cscore+est_boost,100):.0f}%.",
                        ps("ra1", fontSize=8, textColor=DARK, leading=13))
                ])

            # Action 2: Experience gap
            if cyears < 2.0:
                exp_gap = round(2.0 - cyears, 1)
                roadmap_rows.append([
                    Paragraph(
                        f"<b>🗓️  Gain {exp_gap:.1f} more year(s) of experience</b><br/>"
                        "The role requires at least 2 years. Consider internships, "
                        "freelance projects, or open-source contributions to build "
                        "relevant experience faster.",
                        ps("ra2", fontSize=8, textColor=DARK, leading=13))
                ])

            # Action 3: Keyword alignment
            roadmap_rows.append([
                Paragraph(
                    "<b>📝  Improve resume keywords to match the JD</b><br/>"
                    "Use the exact terminology from the job description. "
                    "Higher keyword overlap directly improves the TF-IDF similarity "
                    "score, which is a major scoring factor.",
                    ps("ra3", fontSize=8, textColor=DARK, leading=13))
            ])

            # Action 4: tailored quantified summary
            roadmap_rows.append([
                Paragraph(
                    "<b>✍️  Add a tailored professional summary</b><br/>"
                    "A 3-4 line summary at the top of the resume that mirrors the JD "
                    "language can significantly boost keyword similarity scoring.",
                    ps("ra4", fontSize=8, textColor=DARK, leading=13))
            ])

            roadmap_tbl = Table(roadmap_rows, colWidths=["100%"])
            roadmap_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0,0), (-1,-1), AMBER_BG),
                ("BOX",           (0,0), (-1,-1), 1,   colors.HexColor("#fcd34d")),
                ("INNERGRID",     (0,0), (-1,-1), 0.3, colors.HexColor("#fde68a")),
                ("TOPPADDING",    (0,0), (-1,-1), 6),
                ("BOTTOMPADDING", (0,0), (-1,-1), 6),
                ("LEFTPADDING",   (0,0), (-1,-1), 10),
                ("RIGHTPADDING",  (0,0), (-1,-1), 10),
                ("VALIGN",        (0,0), (-1,-1), "TOP"),
            ]))
            story.append(roadmap_tbl)

        story.append(Spacer(1, 0.5*cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
        story.append(Spacer(1, 0.3*cm))

    # ── Footer note ───────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=PURPLE))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "Generated by Automated Resume Screening Tool  •  Developed by Khadergouse Savanur  "
        "•  Scoring: TF-IDF similarity + skill matching + experience weighting",
        ps("foot", fontSize=7, textColor=GREY, alignment=TA_CENTER)))

    doc.build(story)
    buf.seek(0)
    return buf.read()


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def color_shortlisted(val):
    if str(val).lower() in ("yes", "true", "shortlisted"):
        return "background-color:#dcfce7;color:#166534;font-weight:700"
    return "background-color:#fee2e2;color:#991b1b"


def color_score(val):
    try:
        v = float(str(val).replace("%",""))
        if v >= 60: return "color:#16a34a;font-weight:700"
        if v >= 40: return "color:#d97706;font-weight:600"
        return "color:#dc2626"
    except Exception:
        return ""


# ─────────────────────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-header">
  <div class="hero-logo">🤖</div>
  <div>
    <div class="hero-title">
      Automated Resume Screening Tool
      <span class="ai-badge">✦ AI-Powered</span>
    </div>
    <div class="hero-sub">Upload resumes · Paste job description · Get ranked candidates instantly</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# STEP INDICATOR
# ─────────────────────────────────────────────────────────────

st.markdown("""
<div class="steps-row">
  <div class="step-item">
    <div class="step-num active">1</div>
    <div class="step-label"><small>Step 1</small><span>Upload Resumes</span></div>
  </div>
  <div class="step-divider"></div>
  <div class="step-item">
    <div class="step-num active">2</div>
    <div class="step-label"><small>Step 2</small><span>Paste Job Description</span></div>
  </div>
  <div class="step-divider"></div>
  <div class="step-item">
    <div class="step-num idle">3</div>
    <div class="step-label"><small>Step 3</small><span>Run Screening</span></div>
  </div>
  <div class="step-divider"></div>
  <div class="step-item">
    <div class="step-num idle">4</div>
    <div class="step-label"><small>Step 4</small><span>View Results</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# INPUTS
# ─────────────────────────────────────────────────────────────

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown('<div class="upload-label">📄 Upload Resumes</div>', unsafe_allow_html=True)
    st.markdown('<div class="upload-hint">PDF, DOCX, or TXT · multiple files supported</div>', unsafe_allow_html=True)
    uploaded_resumes = st.file_uploader(
        label="resumes", type=["pdf", "docx", "txt"],
        accept_multiple_files=True, label_visibility="collapsed",
        key="resumes_uploader",
    )
    if uploaded_resumes:
        st.success(f"✅ {len(uploaded_resumes)} resume(s) ready")

with col_right:
    st.markdown('<div class="upload-label">📋 Paste Job Description</div>', unsafe_allow_html=True)
    st.markdown('<div class="upload-hint">Copy and paste the full job description text below</div>', unsafe_allow_html=True)
    jd_text = st.text_area(
        label="jd",
        placeholder=(
            "Paste the job description here...\n\n"
            "Example:\nWe are looking for a Data Analyst with 2+ years of experience "
            "in SQL, Python, Excel, and Power BI. Strong knowledge of statistics, "
            "data visualisation, and reporting required."
        ),
        height=240, label_visibility="collapsed", key="jd_textarea",
    )

st.markdown("<br>", unsafe_allow_html=True)
run_btn = st.button("🚀  Run Screening", type="primary", use_container_width=True)

# ─────────────────────────────────────────────────────────────
# HOW IT WORKS  (shown before first run)
# ─────────────────────────────────────────────────────────────

if not run_btn:
    st.markdown("---")
    st.markdown("### 🔄 How It Works")
    h1, h2, h3, h4 = st.columns(4, gap="small")
    with h1:
        st.markdown("""<div class="how-card"><div class="how-step">Step 01</div>
          <div style="font-size:26px;margin-bottom:.5rem">📤</div>
          <h4>Upload Resumes</h4><p>Drop in PDF, DOCX, or TXT resumes — multiple candidates at once</p>
        </div>""", unsafe_allow_html=True)
    with h2:
        st.markdown("""<div class="how-card"><div class="how-step">Step 02</div>
          <div style="font-size:26px;margin-bottom:.5rem">📋</div>
          <h4>Paste JD</h4><p>Copy-paste the full job description — skills are auto-detected from it</p>
        </div>""", unsafe_allow_html=True)
    with h3:
        st.markdown("""<div class="how-card"><div class="how-step">Step 03</div>
          <div style="font-size:26px;margin-bottom:.5rem">🧮</div>
          <h4>Auto Score</h4><p>TF-IDF similarity + must-have skill rules generate a composite score</p>
        </div>""", unsafe_allow_html=True)
    with h4:
        st.markdown("""<div class="how-card"><div class="how-step">Step 04</div>
          <div style="font-size:26px;margin-bottom:.5rem">🏆</div>
          <h4>Rank & Export</h4><p>Sorted shortlist with scores, skill gaps, and a downloadable PDF report</p>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# PIPELINE
# ─────────────────────────────────────────────────────────────

if run_btn:

    if not uploaded_resumes:
        st.error("⚠️  Please upload at least one resume before running.")
        st.stop()
    if not jd_text or len(jd_text.strip()) < 30:
        st.error("⚠️  Please paste a job description (minimum 30 characters).")
        st.stop()

    # Write everything to a temp directory
    tmp_dir     = pathlib.Path(tempfile.mkdtemp())
    resumes_dir = tmp_dir / "resumes"
    resumes_dir.mkdir()

    jd_path = tmp_dir / "job_description.txt"
    jd_path.write_text(jd_text.strip(), encoding="utf-8")

    for f in uploaded_resumes:
        (resumes_dir / f.name).write_bytes(f.read())

    with st.spinner("⏳ Screening in progress — please wait..."):
        try:
            from resume_extractor import load_all_resumes
            from text_cleaner     import (clean_text, extract_candidate_name,
                                          extract_email, extract_years_experience)
            from skill_extractor  import extract_skills, get_matched_skills
            from scorer           import score_resume
            from ranker           import rank_candidates

            REQUIRED_SKILLS = [
                "sql", "python", "excel", "power bi", "pandas", "statistics",
            ]

            jd_raw   = jd_path.read_text(encoding="utf-8")
            jd_clean = clean_text(jd_raw)

            raw_resumes = load_all_resumes(str(resumes_dir))
            if not raw_resumes:
                st.error("❌ No readable content found in the uploaded resumes.")
                st.stop()

            candidates = []
            for fname, raw_text in raw_resumes.items():
                name       = extract_candidate_name(raw_text)
                email      = extract_email(raw_text)
                years      = extract_years_experience(raw_text)
                clean      = clean_text(raw_text)
                skills     = extract_skills(clean)
                skill_info = get_matched_skills(skills, REQUIRED_SKILLS)
                scores     = score_resume(clean, jd_clean, skill_info, years, required_years=2.0)

                candidates.append({
                    "candidate_name":   name,
                    "email":            email,
                    "resume_file":      fname,
                    "years_experience": years,
                    "resume_skills":    skills,
                    "matched_skills":   skill_info["matched_skills"],
                    "missing_skills":   skill_info["missing_skills"],
                    "skill_match_pct":  skill_info["match_percentage"],
                    **scores,
                })

            ranked_df = rank_candidates(candidates, threshold=60.0)

            # ── Figure out column names ──────────────────────
            cols      = ranked_df.columns.tolist()
            name_col  = next((c for c in ["Name","candidate_name"]              if c in cols), cols[0])
            score_col = next((c for c in ["Score","final_score_pct"]            if c in cols), None)
            short_col = next((c for c in ["Shortlisted"]                        if c in cols), None)
            rank_col  = next((c for c in ["Rank"]                               if c in cols), None)
            skill_col = next((c for c in ["Skill_Match_Pct","skill_match_pct"]  if c in cols), None)
            years_col = next((c for c in ["Years_Experience","years_experience"] if c in cols), None)

            # ── SUCCESS ──────────────────────────────────────
            st.success(f"✅ Screening complete — {len(candidates)} candidate(s) analysed!")
            st.markdown("---")

            # ── METRICS ──────────────────────────────────────
            st.markdown("### 📊 Screening Summary")

            total       = len(ranked_df)
            shortlisted = int((ranked_df[short_col]=="Yes").sum()) if short_col else 0
            rejected    = total - shortlisted
            avg_score   = float(ranked_df[score_col].mean()) if score_col else 0.0

            m1, m2, m3, m4 = st.columns(4, gap="small")
            m1.metric("Total Candidates", total)
            m2.metric("✅ Shortlisted",    shortlisted,
                      delta=f"{shortlisted/max(1,total)*100:.0f}% pass rate")
            m3.metric("❌ Not Shortlisted", rejected)
            m4.metric("⭐ Avg Score",       f"{avg_score:.1f}%")

            st.markdown("---")

            # ── RANKING TABLE ─────────────────────────────────
            st.markdown("### 📋 Candidate Rankings")

            show_cols  = [c for c in [rank_col, name_col, score_col,
                                      short_col, skill_col, years_col] if c]
            display_df = ranked_df[show_cols].copy()

            styled = display_df.style
            if short_col and short_col in display_df.columns:
                styled = styled.applymap(color_shortlisted, subset=[short_col])
            if score_col and score_col in display_df.columns:
                styled = styled.applymap(color_score, subset=[score_col])

            fmt = {}
            if score_col  and score_col  in display_df.columns: fmt[score_col]  = "{:.1f}%"
            if skill_col  and skill_col  in display_df.columns: fmt[skill_col]  = "{:.1f}%"
            if years_col  and years_col  in display_df.columns: fmt[years_col]  = "{:.1f} yrs"
            if fmt:
                styled = styled.format(fmt)

            st.dataframe(styled, use_container_width=True, height=300)
            st.markdown("---")

            # ── CHARTS ───────────────────────────────────────
            st.markdown("### 📈 Score Distribution")

            names  = ranked_df[name_col].tolist()  if name_col  else []
            scores = ranked_df[score_col].tolist() if score_col else [0]*total
            is_sl  = (ranked_df[short_col]=="Yes").tolist() if short_col else [False]*total
            colors_bars = ["#16a34a" if s else "#e8386c" for s in is_sl]

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, max(4, total*0.55+1.5)))
            fig.patch.set_facecolor("#fafaf8")

            ax1.barh(names, scores, color=colors_bars, height=0.55, edgecolor="none")
            ax1.axvline(x=60, color="#f59e0b", linestyle="--", linewidth=1.5)
            ax1.set_xlabel("Score (%)", fontsize=10, color="#6b7280")
            ax1.set_title("Candidate Scores", fontsize=12, fontweight="bold",
                          color="#111827", pad=10)
            ax1.set_facecolor("#f9fafb")
            ax1.spines[["top","right","left"]].set_visible(False)
            ax1.tick_params(colors="#374151", labelsize=9)
            green_p  = mpatches.Patch(color="#16a34a", label="Shortlisted")
            red_p    = mpatches.Patch(color="#e8386c", label="Not Shortlisted")
            thresh_p = mpatches.Patch(color="#f59e0b", label="Auto threshold (60%)")
            ax1.legend(handles=[green_p, red_p, thresh_p], fontsize=9,
                       frameon=True, facecolor="#ffffff", edgecolor="#e5e7eb")

            ax2.pie(
                [max(shortlisted, 0.0001), max(rejected, 0.0001)],
                labels=["Shortlisted", "Not Shortlisted"],
                colors=["#16a34a", "#e8386c"],
                autopct="%1.0f%%", startangle=90,
                wedgeprops={"edgecolor":"#fafaf8","linewidth":2},
                textprops={"fontsize":10,"color":"#374151"},
            )
            ax2.set_title("Shortlist Split", fontsize=12, fontweight="bold",
                          color="#111827", pad=10)
            ax2.set_facecolor("#fafaf8")
            plt.tight_layout()
            st.pyplot(fig)
            st.markdown("---")

            # ── CANDIDATE CARDS ───────────────────────────────
            st.markdown("### 👤 Candidate Details")

            avatar_colors = [
                ("#ede9fd","#5b21b6"),("#dbeafe","#1e40af"),
                ("#fde8ef","#9d174d"),("#dcfce7","#166534"),
                ("#fef3c7","#92400e"),("#ccfbf1","#115e59"),
            ]

            for i, (_, row) in enumerate(ranked_df.iterrows()):
                bg, fg  = avatar_colors[i % len(avatar_colors)]
                cname   = str(row.get(name_col,  "Candidate"))
                cscore  = float(row.get(score_col, 0)) if score_col else 0.0
                cyears  = float(row.get(years_col, 0)) if years_col else 0.0
                cshort  = str(row.get(short_col,  "No")) if short_col else "No"
                matched = list(row.get("matched_skills", []) or [])
                missing = list(row.get("missing_skills", []) or [])
                all_sk  = list(row.get("resume_skills",  []) or [])
                skill_pct = float(row.get("skill_match_pct", 0) or 0)
                icon    = "✅" if cshort == "Yes" else "❌"

                with st.expander(f"{icon}  #{i+1}  {cname}  —  Score: {cscore:.1f}%"):
                    ca, cb, cc = st.columns(3)
                    ca.metric("Score",      f"{cscore:.1f}%")
                    cb.metric("Experience", f"{cyears:.1f} yrs")
                    cc.metric("Status",     "Shortlisted ✅" if cshort=="Yes"
                                            else "Not Shortlisted ❌")
                    if matched:
                        pills = " ".join(
                            f'<span class="skill-pill-match">{s}</span>' for s in matched)
                        st.markdown(f"**✅ Skills matched:** {pills}", unsafe_allow_html=True)
                    if missing:
                        pills = " ".join(
                            f'<span class="skill-pill-miss">{s}</span>' for s in missing)
                        st.markdown(f"**⚠️ Skills missing:** {pills}", unsafe_allow_html=True)
                    if all_sk:
                        st.caption(f"All skills found: {', '.join(str(s) for s in all_sk)}")

                    # ── IMPROVEMENT ROADMAP (rejected only) ───
                    if cshort != "Yes":
                        gap           = round(60.0 - cscore, 1)
                        total_req     = len(REQUIRED_SKILLS)
                        skill_boost   = round((100.0 / max(1, total_req)) * 0.4, 1)
                        skills_needed = max(1, int(
                            (gap / skill_boost) + (0 if gap % skill_boost == 0 else 1)
                        )) if skill_boost > 0 else len(missing)

                        st.markdown("""
                        <div class="roadmap-box">
                          <div class="roadmap-title">
                            🚀 &nbsp;What this candidate needs to get shortlisted
                          </div>
                        """, unsafe_allow_html=True)

                        # Score gap progress bar
                        bar_filled = min(int(cscore), 100)
                        st.markdown(f"""
                        <div style="margin-bottom:1rem">
                          <div style="display:flex;justify-content:space-between;
                                      font-size:.88rem;font-weight:600;color:#374151;margin-bottom:6px">
                            <span>Current score</span>
                            <span>
                              <b style="color:#e8386c;font-size:1rem">{cscore:.1f}%</b>
                              &nbsp;→&nbsp; need
                              <b style="color:#16a34a;font-size:1rem">60%</b>
                              &nbsp;<span style="color:#92400e">(+{gap}% gap to shortlist)</span>
                            </span>
                          </div>
                          <div style="background:#fee2e2;border-radius:10px;height:20px;
                                      overflow:hidden;position:relative">
                            <div style="width:{bar_filled}%;height:100%;
                                        background:linear-gradient(90deg,#e8386c,#f59e0b);
                                        border-radius:10px;position:relative">
                              <div style="position:absolute;right:8px;top:0;bottom:0;
                                          display:flex;align-items:center;
                                          font-size:11px;font-weight:800;color:#fff">
                                {cscore:.0f}%
                              </div>
                            </div>
                          </div>
                          <div style="font-size:.78rem;color:#6b7280;margin-top:4px;
                                      display:flex;justify-content:space-between;font-weight:500">
                            <span>0%</span>
                            <span style="color:#16a34a;font-weight:700">
                              ▲ Shortlist threshold: 60%
                            </span>
                            <span>100%</span>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Action block HTML
                        action_html = ""

                        # 1. Missing skills
                        if missing:
                            top_skills  = missing[:skills_needed]
                            skill_list  = ", ".join(
                                f"<b>{s.title()}</b>" for s in top_skills)
                            est_boost   = min(len(top_skills) * skill_boost, gap)
                            projected   = min(cscore + est_boost, 100)
                            action_html += f"""
                            <div class="roadmap-action">
                              <span class="roadmap-action-icon">📚</span>
                              <div>
                                <div class="roadmap-action-title">
                                  Learn {len(top_skills)} missing skill(s): {skill_list}
                                </div>
                                <div class="roadmap-action-desc">
                                  Each required skill adds <b style="color:#d97706">~{skill_boost:.0f}%</b> to the score.
                                  Adding these could boost by <b style="color:#16a34a">~{est_boost:.0f}%</b> →
                                  projected score: <b style="color:#16a34a;font-size:.88rem">~{projected:.0f}%</b>
                                  {"&nbsp;✅ <b style='color:#16a34a'>Above threshold!</b>" if projected >= 60 else "&nbsp;📈 Getting closer!"}
                                </div>
                              </div>
                            </div>"""

                        # 2. Experience gap
                        if cyears < 2.0:
                            exp_gap = round(2.0 - cyears, 1)
                            action_html += f"""
                            <div class="roadmap-action">
                              <span class="roadmap-action-icon">🗓️</span>
                              <div>
                                <div class="roadmap-action-title">
                                  Gain {exp_gap:.1f} more year(s) of relevant experience
                                </div>
                                <div class="roadmap-action-desc">
                                  This role requires at least <b style="color:#d97706">2 years</b>.
                                  Consider internships, freelance projects, or open-source contributions
                                  to build relevant experience faster — experience directly weights the score.
                                </div>
                              </div>
                            </div>"""

                        # 3. Keyword alignment
                        action_html += """
                            <div class="roadmap-action">
                              <span class="roadmap-action-icon">📝</span>
                              <div>
                                <div class="roadmap-action-title">
                                  Mirror the JD's exact keywords in the resume
                                </div>
                                <div class="roadmap-action-desc">
                                  Higher keyword overlap directly improves the
                                  <b style="color:#6c3de8">TF-IDF similarity score</b> — a major scoring factor.
                                  Use the same terminology as the job description word-for-word.
                                </div>
                              </div>
                            </div>"""

                        # 4. Professional summary tip
                        action_html += """
                            <div class="roadmap-action">
                              <span class="roadmap-action-icon">✍️</span>
                              <div>
                                <div class="roadmap-action-title">
                                  Add a tailored professional summary at the top
                                </div>
                                <div class="roadmap-action-desc">
                                  A <b style="color:#6c3de8">3-4 line summary</b> at the top of the resume
                                  that mirrors the JD's language can significantly boost keyword
                                  similarity scoring. Make it specific to this exact role.
                                </div>
                              </div>
                            </div>"""

                        st.markdown(action_html + "</div>", unsafe_allow_html=True)

            # ── DOWNLOAD PDF ──────────────────────────────────
            st.markdown("---")
            st.markdown("### 💾 Download Report")

            pdf_bytes = generate_pdf_report(
                ranked_df       = ranked_df,
                candidates_detail = candidates,
                required_skills = REQUIRED_SKILLS,
                name_col        = name_col,
                score_col       = score_col,
                short_col       = short_col,
                skill_col       = skill_col,
                years_col       = years_col,
                rank_col        = rank_col,
                threshold       = 60.0,
            )

            st.download_button(
                label     = "⬇️  Download PDF Report",
                data      = pdf_bytes,
                file_name = "screening_results.pdf",
                mime      = "application/pdf",
            )

        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.exception(e)

# ─────────────────────────────────────────────────────────────
# DEVELOPER FOOTER
# ─────────────────────────────────────────────────────────────

st.markdown("""
<div class="dev-footer">
  <div class="dev-card">
    <div class="dev-avatar">KS</div>
    <div class="dev-info">
      <small>Developed by</small>
      <strong>Khadergouse Savanur</strong>
    </div>
    <div class="dev-badge">✦ Developer</div>
  </div>
</div>
""", unsafe_allow_html=True)