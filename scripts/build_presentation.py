#!/usr/bin/env python3
"""
Generate docs/presentation.pdf — Signal-to-Shock hackathon slides.
Exactly 7 slides, A4 landscape, professional financial-risk style.
Run from the repository root with the repo venv active.
"""

import os
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

ROOT = Path(__file__).resolve().parents[1]  # repo root (parent of scripts/)
ARCH_PNG = ROOT / "docs" / "architecture.png"
OUT_PDF = ROOT / "docs" / "presentation.pdf"

# ── Landscape A4 ──────────────────────────────────────────────────────────────
W, H = A4[1], A4[0]  # 297 × 210 mm  →  841.89 × 595.28 pt

# ── Colour palette ────────────────────────────────────────────────────────────
NAVY    = colors.HexColor("#0D2340")
BLUE    = colors.HexColor("#1A4F8A")
STEEL   = colors.HexColor("#2E6DA4")
TEAL    = colors.HexColor("#1B7A7A")
GOLD    = colors.HexColor("#C8A84B")
LGREY   = colors.HexColor("#F4F6F9")
MGREY   = colors.HexColor("#D0D7E2")
WHITE   = colors.white
RED     = colors.HexColor("#C0392B")
GREEN   = colors.HexColor("#1E8449")
AMBER   = colors.HexColor("#D4820A")

MARGIN = 18 * mm
CONTENT_W = W - 2 * MARGIN
HEADER_H  = 48
FOOTER_H  = 20

# ── Paragraph styles ─────────────────────────────────────────────────────────
def style(name, **kw):
    base = ParagraphStyle(name, **kw)
    return base

S_TITLE   = style("title",   fontName="Helvetica-Bold",   fontSize=30, textColor=WHITE,   leading=36, alignment=TA_CENTER)
S_SUBT    = style("subt",    fontName="Helvetica",        fontSize=14, textColor=MGREY,   leading=18, alignment=TA_CENTER)
S_META    = style("meta",    fontName="Helvetica",        fontSize=11, textColor=GOLD,    leading=14, alignment=TA_CENTER)
S_H2      = style("h2",      fontName="Helvetica-Bold",   fontSize=16, textColor=NAVY,    leading=20)
S_BODY    = style("body",    fontName="Helvetica",        fontSize=10, textColor=NAVY,    leading=14)
S_BODYW   = style("bodyw",   fontName="Helvetica",        fontSize=10, textColor=WHITE,   leading=14)
S_SMALL   = style("small",   fontName="Helvetica",        fontSize=8.5,textColor=colors.HexColor("#555555"), leading=12)
S_SMALLW  = style("smallw",  fontName="Helvetica",        fontSize=8.5,textColor=MGREY,   leading=12)
S_BULLET  = style("bullet",  fontName="Helvetica",        fontSize=10, textColor=NAVY,    leading=14,
                  leftIndent=12, bulletIndent=0, bulletFontName="Helvetica", bulletFontSize=10)
S_BULLETW = style("bulletw", fontName="Helvetica",        fontSize=10, textColor=WHITE,   leading=14,
                  leftIndent=12)
S_WARN    = style("warn",    fontName="Helvetica-Oblique",fontSize=9,  textColor=AMBER,   leading=12)
S_WARNW   = style("warnw",   fontName="Helvetica-Oblique",fontSize=9,  textColor=GOLD,    leading=12)
S_LABEL   = style("label",   fontName="Helvetica-Bold",   fontSize=9,  textColor=WHITE,   leading=12, alignment=TA_CENTER)
S_CELL    = style("cell",    fontName="Helvetica",        fontSize=9,  textColor=NAVY,    leading=12, alignment=TA_CENTER)
S_CELLB   = style("cellb",   fontName="Helvetica-Bold",   fontSize=9,  textColor=NAVY,    leading=12, alignment=TA_CENTER)
S_CELLW   = style("cellw",   fontName="Helvetica-Bold",   fontSize=9,  textColor=WHITE,   leading=12, alignment=TA_CENTER)
S_CAPT    = style("capt",    fontName="Helvetica-Oblique",fontSize=8,  textColor=colors.HexColor("#666666"), leading=11, alignment=TA_CENTER)

# ── Drawing helpers ───────────────────────────────────────────────────────────
def draw_bg(canvas, doc, fill_color=NAVY):
    canvas.saveState()
    canvas.setFillColor(fill_color)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    canvas.restoreState()

def draw_header_bar(canvas, title_text, subtitle_text="", dark=True):
    canvas.saveState()
    bar_color = NAVY if dark else BLUE
    canvas.setFillColor(bar_color)
    canvas.rect(0, H - HEADER_H, W, HEADER_H, fill=1, stroke=0)
    # Gold accent line
    canvas.setFillColor(GOLD)
    canvas.rect(0, H - HEADER_H, W, 2.5, fill=1, stroke=0)
    canvas.setFont("Helvetica-Bold", 15)
    canvas.setFillColor(WHITE)
    canvas.drawString(MARGIN, H - HEADER_H + 17, title_text)
    if subtitle_text:
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(MGREY)
        canvas.drawRightString(W - MARGIN, H - HEADER_H + 17, subtitle_text)
    canvas.restoreState()

def draw_footer(canvas, slide_num):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, W, FOOTER_H, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, FOOTER_H, W, 1, fill=1, stroke=0)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MGREY)
    canvas.drawString(MARGIN, 6, "Signal-to-Shock  |  S&P Global & CRISIL Campus Hackathon 2026  |  Devanshi Gupta, IGDTUW")
    canvas.drawRightString(W - MARGIN, 6, f"Slide {slide_num} of 7")
    canvas.restoreState()

def draw_side_accent(canvas, color=TEAL, width=5):
    canvas.saveState()
    canvas.setFillColor(color)
    canvas.rect(0, FOOTER_H, width, H - HEADER_H - FOOTER_H, fill=1, stroke=0)
    canvas.restoreState()

# ── Content frame builder ─────────────────────────────────────────────────────
def content_frame(extra_left=8):
    return Frame(
        MARGIN + extra_left, FOOTER_H + 6,
        CONTENT_W - extra_left, H - HEADER_H - FOOTER_H - 12,
        leftPadding=0, rightPadding=0, topPadding=6, bottomPadding=0,
        showBoundary=0,
    )

def sp(h=6):
    return Spacer(1, h)

def bullet(text, style=S_BULLET):
    return Paragraph(f"<bullet>&bull;</bullet> {text}", style)

def para(text, style=S_BODY):
    return Paragraph(text, style)

# ── Page builders ─────────────────────────────────────────────────────────────

def build_slide_1(canvas, doc):
    """Title & Problem"""
    draw_bg(canvas, doc, NAVY)
    # large blue band top
    canvas.saveState()
    canvas.setFillColor(BLUE)
    canvas.rect(0, H - 160, W, 160, fill=1, stroke=0)
    # gold top stripe
    canvas.setFillColor(GOLD)
    canvas.rect(0, H - 2, W, 2, fill=1, stroke=0)
    # gold bottom stripe of band
    canvas.setFillColor(GOLD)
    canvas.rect(0, H - 162, W, 2, fill=1, stroke=0)
    # decorative side bar
    canvas.setFillColor(TEAL)
    canvas.rect(0, 0, 6, H - 162, fill=1, stroke=0)
    canvas.restoreState()

    draw_footer(canvas, 1)

    frame = Frame(MARGIN, FOOTER_H + 4, CONTENT_W, H - FOOTER_H - 8, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, showBoundary=0)
    story = [
        sp(H - 162 - FOOTER_H - 140),
        para("Signal-to-Shock", S_TITLE),
        sp(6),
        para("Financial Event Intelligence & Portfolio Stress Testing", S_SUBT),
        sp(20),
        para("Devanshi Gupta  |  IGDTUW  |  S&amp;P Global &amp; CRISIL Campus Hackathon 2026", S_META),
        sp(28),
    ]

    # Problem box
    problem_style = ParagraphStyle("probh", fontName="Helvetica-Bold", fontSize=13, textColor=GOLD, leading=18)
    prob_body     = ParagraphStyle("probb", fontName="Helvetica", fontSize=10, textColor=WHITE, leading=15)

    story += [
        para("<b>The Problem</b>", ParagraphStyle("ph", fontName="Helvetica-Bold", fontSize=13, textColor=GOLD, leading=16)),
        sp(6),
        para("Financial portfolios are exposed to rapid, unstructured events — earnings surprises, geopolitical shocks, credit downgrades, and cyber incidents. Risk teams need a fast path from <b>news signal</b> to <b>quantified portfolio impact</b>.", ParagraphStyle("pb", fontName="Helvetica", fontSize=10.5, textColor=WHITE, leading=15)),
        sp(10),
        para("Today that gap is bridged manually, slowly, and inconsistently.", ParagraphStyle("pi", fontName="Helvetica-Oblique", fontSize=10, textColor=GOLD, leading=14)),
    ]
    frame.addFromList(story, canvas)


def build_slide_2(canvas, doc):
    """Why It Matters"""
    draw_bg(canvas, doc, LGREY)
    draw_header_bar(canvas, "Why It Matters", "The signal-to-action gap in portfolio risk", dark=True)
    draw_footer(canvas, 2)
    draw_side_accent(canvas, TEAL)

    frame = content_frame()
    story = [
        sp(4),
        para("External events create portfolio risk faster than manual processes can respond:", S_BODY),
        sp(8),
    ]

    # 3-column event → impact cards
    card_data = [
        ("Credit Event\n(e.g. SVB Collapse)", "Bank-run headlines → regional banking ETF KRE fell −19.9% over 5 trading days vs SPY −0.7%", RED),
        ("Geopolitical Shock\n(e.g. UK Mini-Budget)", "Policy surprise → UK equity EWU fell −5.5% while broad US market fell −4.6%", AMBER),
        ("Macro Announcement\n(e.g. Rate Decision)", "Systemic re-pricing across equities, bonds, derivatives simultaneously", STEEL),
    ]

    def card(title, body, color):
        return [
            [Paragraph(f"<b>{title}</b>", ParagraphStyle("ct", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE, leading=12, alignment=TA_CENTER))],
            [Paragraph(body, ParagraphStyle("cb", fontName="Helvetica", fontSize=8.5, textColor=NAVY, leading=12, alignment=TA_CENTER))],
        ]

    col_w = (CONTENT_W - 14) / 3

    for title, body, color in card_data:
        t = Table(
            [[Paragraph(f"<b>{title}</b>", ParagraphStyle("ct", fontName="Helvetica-Bold", fontSize=9.5, textColor=WHITE, leading=13, alignment=TA_CENTER))],
             [Paragraph(body, ParagraphStyle("cb", fontName="Helvetica", fontSize=9, textColor=NAVY, leading=12, alignment=TA_CENTER))]],
            colWidths=[col_w - 4],
        )
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), color),
            ("BACKGROUND", (0,1), (-1,-1), WHITE),
            ("BOX", (0,0), (-1,-1), 1, MGREY),
            ("TOPPADDING", (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("RIGHTPADDING", (0,0), (-1,-1), 8),
            ("ROWBACKGROUNDS", (0,1), (-1,1), [colors.HexColor("#EEF2F8")]),
        ]))

    cards_row = Table(
        [[t for (title, body, color) in card_data for t in [
            Table(
                [[Paragraph(f"<b>{title}</b>", ParagraphStyle("ct", fontName="Helvetica-Bold", fontSize=9.5, textColor=WHITE, leading=13, alignment=TA_CENTER))],
                 [Paragraph(body, ParagraphStyle("cb", fontName="Helvetica", fontSize=9, textColor=NAVY, leading=12, alignment=TA_LEFT))]],
                colWidths=[col_w - 4],
            )
        ]]],
        colWidths=[col_w] * 3,
        hAlign="LEFT",
    )
    # rebuild cleanly
    def make_card(title, body, color):
        return Table(
            [[Paragraph(f"<b>{title.replace(chr(10), '<br/>')}</b>",
                        ParagraphStyle("ct", fontName="Helvetica-Bold", fontSize=9.5, textColor=WHITE, leading=13, alignment=TA_CENTER))],
             [Paragraph(body,
                        ParagraphStyle("cb", fontName="Helvetica", fontSize=9, textColor=NAVY, leading=13, alignment=TA_LEFT))]],
            colWidths=[col_w - 8],
        )

    tbl_data = [[make_card(t, b, c) for (t, b, c) in card_data]]
    outer = Table(tbl_data, colWidths=[col_w] * 3, hAlign="LEFT")
    for i, (_, _, color) in enumerate(card_data):
        outer.setStyle(TableStyle([
            ("BACKGROUND", (i,0), (i,0), WHITE),
            ("LEFTPADDING", (0,0), (-1,-1), 4),
            ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ]))
    # Use individual tables per card in a row
    card_tables = []
    for (title, body, color) in card_data:
        ct = Table(
            [[Paragraph(f"<b>{title.replace(chr(10), '<br/>')}</b>",
                        ParagraphStyle("cth", fontName="Helvetica-Bold", fontSize=9.5, textColor=WHITE, leading=13, alignment=TA_CENTER))],
             [Paragraph(body,
                        ParagraphStyle("ctb", fontName="Helvetica", fontSize=9, textColor=NAVY, leading=13))]],
            colWidths=[col_w - 10],
        )
        ct.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), color),
            ("BACKGROUND", (0,1), (-1,1), colors.HexColor("#EEF2F8")),
            ("BOX", (0,0), (-1,-1), 1.2, MGREY),
            ("ROUNDEDCORNERS", [4]),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING", (0,0), (-1,-1), 9),
            ("RIGHTPADDING", (0,0), (-1,-1), 9),
        ]))
        card_tables.append(ct)

    row_tbl = Table([card_tables], colWidths=[col_w] * 3)
    row_tbl.setStyle(TableStyle([("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4)]))

    story.append(row_tbl)
    story += [
        sp(14),
        para("Different event <i>types</i> have different <i>scopes</i>: issuer-specific events affect targeted positions; systemic events reprice entire asset classes.", S_BODY),
        sp(8),
        para("Signal-to-Shock automates the <b>news → classification → impact → stress test</b> workflow so risk analysts see quantified exposure in seconds.", S_BODY),
        sp(8),
        para("⚠ Portfolio shock magnitudes in this prototype are <b>illustrative assumptions</b>, not calibrated market forecasts.", S_WARN),
    ]
    frame.addFromList(story, canvas)


def build_slide_3(canvas, doc):
    """Solution & Architecture"""
    draw_bg(canvas, doc, LGREY)
    draw_header_bar(canvas, "Solution & Architecture", "Rule-based NLP pipeline → portfolio stress test", dark=True)
    draw_footer(canvas, 3)
    draw_side_accent(canvas, STEEL)

    # Split: pipeline diagram left, arch image right
    left_w  = CONTENT_W * 0.44
    right_w = CONTENT_W * 0.54
    gap     = CONTENT_W * 0.02

    left_frame = Frame(MARGIN + 6, FOOTER_H + 8, left_w, H - HEADER_H - FOOTER_H - 16, leftPadding=0, rightPadding=4, topPadding=4, bottomPadding=0, showBoundary=0)
    right_frame = Frame(MARGIN + 6 + left_w + gap, FOOTER_H + 8, right_w - 6, H - HEADER_H - FOOTER_H - 16, leftPadding=0, rightPadding=0, topPadding=4, bottomPadding=0, showBoundary=0)

    # Pipeline steps
    steps = [
        (STEEL, "① Input",           "Financial news or social-media text (synthetic demo data)"),
        (TEAL,  "② Sentiment Score", "Keyword rule: (pos_count − neg_count) / (pos_count + neg_count)"),
        (BLUE,  "③ Event Class",     "Rule-based: Credit Event, Geopolitical, Macro, M&A, Cyber, Other"),
        (NAVY,  "④ Impact Score",    "0–10 severity from keyword signals"),
        (RED,   "⑤ Stress Test",     "market_value × (1 + shock × impact/10)  [illustrative shocks]"),
        (GREEN, "⑥ Output",          "Before/after P&L, per-position breakdown, affected flag"),
    ]

    left_story = [sp(2)]
    for color, label, desc in steps:
        step_t = Table(
            [[Paragraph(f"<b>{label}</b>", ParagraphStyle("sl", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE, leading=12)),
              Paragraph(desc, ParagraphStyle("sd", fontName="Helvetica", fontSize=8.5, textColor=NAVY, leading=12))]],
            colWidths=[left_w * 0.30, left_w * 0.68],
        )
        step_t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,0), color),
            ("BACKGROUND", (1,0), (1,0), colors.HexColor("#EEF2F8")),
            ("BOX", (0,0), (-1,-1), 0.8, MGREY),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("LEFTPADDING", (0,0), (-1,-1), 7),
            ("RIGHTPADDING", (0,0), (-1,-1), 7),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ]))
        left_story.append(step_t)
        left_story.append(sp(5))

    left_story += [
        sp(2),
        para("36 unit tests  ·  GitHub Actions CI  ·  Python 3.12", S_SMALL),
    ]
    left_frame.addFromList(left_story, canvas)

    # Architecture image
    try:
        img_h = H - HEADER_H - FOOTER_H - 30
        img_w = right_w - 6
        # maintain aspect ratio: 1600×1050
        aspect = 1600 / 1050
        if img_w / img_h > aspect:
            img_w = img_h * aspect
        else:
            img_h = img_w / aspect
        right_story = [
            sp(4),
            Image(str(ARCH_PNG), width=img_w, height=img_h),
            sp(3),
            para("Architecture diagram — docs/architecture.png", S_CAPT),
        ]
    except Exception:
        right_story = [para("Architecture diagram: docs/architecture.png", S_SMALL)]
    right_frame.addFromList(right_story, canvas)


def build_slide_4(canvas, doc):
    """Working Prototype"""
    draw_bg(canvas, doc, LGREY)
    draw_header_bar(canvas, "Working Prototype", "Streamlit application — live demo", dark=True)
    draw_footer(canvas, 4)
    draw_side_accent(canvas, GOLD)

    frame = content_frame()
    story = [sp(4)]

    # User workflow table
    wf_data = [
        [Paragraph("<b>Step</b>", S_CELLW), Paragraph("<b>User Action</b>", S_CELLW), Paragraph("<b>System Response</b>", S_CELLW)],
        ["1", "Select or type financial news / social-media text", "Displayed in the input panel"],
        ["2", "Click Analyse Signal", "Sentiment score, event type, impact score (0–10) computed"],
        ["3", "View Signal Panel", "Structured output: event class, affected issuer, scenario name"],
        ["4", "Inspect Portfolio", "Before/after values, P&L per position, affected positions highlighted"],
        ["5", "Switch event / issuer", "Re-run stress with different scenario scope (issuer vs. systemic)"],
    ]
    col_widths = [CONTENT_W * 0.06, CONTENT_W * 0.42, CONTENT_W * 0.50]
    wf_tbl = Table(wf_data, colWidths=col_widths, repeatRows=1)
    wf_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("TEXTCOLOR", (0,0), (-1,0), WHITE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, colors.HexColor("#EEF2F8")]),
        ("BOX", (0,0), (-1,-1), 0.8, MGREY),
        ("INNERGRID", (0,0), (-1,-1), 0.5, MGREY),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("ALIGN", (0,0), (0,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(wf_tbl)
    story.append(sp(12))

    # Synthetic portfolio summary
    story.append(para("<b>Synthetic Demo Portfolio</b>  (6 positions, total $1,150,000)", S_H2))
    story.append(sp(6))

    port_data = [
        [Paragraph(h, S_CELLW) for h in ["Asset", "Type", "Issuer", "Market Value"]],
        ["Technology Equity", "Equity", "Example Technology Ltd", "$250,000"],
        ["Banking Equity",    "Equity", "Example Bank Ltd",       "$200,000"],
        ["Corporate Bond",    "Bond",   "Example Technology Ltd", "$150,000"],
        ["Bank Loan",         "Loan",   "Example Bank Ltd",       "$250,000"],
        ["Government Bond",   "Bond",   "Example Government",     "$200,000"],
        ["Interest Rate Swap","Derivative","Example Bank Ltd",     "$100,000"],
    ]
    port_tbl = Table(port_data, colWidths=[CONTENT_W*0.28, CONTENT_W*0.13, CONTENT_W*0.37, CONTENT_W*0.20], repeatRows=1)
    port_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), STEEL),
        ("TEXTCOLOR", (0,0), (-1,0), WHITE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, colors.HexColor("#EEF2F8")]),
        ("BOX", (0,0), (-1,-1), 0.8, MGREY),
        ("INNERGRID", (0,0), (-1,-1), 0.5, MGREY),
        ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("ALIGN", (3,0), (3,-1), "RIGHT"),
    ]))
    story.append(port_tbl)
    story += [
        sp(8),
        para("⚠  Portfolio positions and scenario shock magnitudes are <b>synthetic and illustrative</b> — not real financial data or investment advice.", S_WARN),
        sp(4),
        para("Demo video: <i>Pending — URL to be added after upload</i>  ·  Run locally: <font face='Courier' size='9'>streamlit run app.py</font>", S_SMALL),
    ]
    frame.addFromList(story, canvas)


def build_slide_5(canvas, doc):
    """Real-Data Sentiment Evaluation"""
    draw_bg(canvas, doc, LGREY)
    draw_header_bar(canvas, "Real-Data Sentiment Evaluation", "Financial PhraseBank — 3,453 sentences, sentences_75agree", dark=True)
    draw_footer(canvas, 5)
    draw_side_accent(canvas, TEAL)

    left_w  = CONTENT_W * 0.48
    right_w = CONTENT_W * 0.48
    gap     = CONTENT_W * 0.04

    left_frame  = Frame(MARGIN + 6, FOOTER_H + 8, left_w,   H - HEADER_H - FOOTER_H - 16, leftPadding=0, rightPadding=4, topPadding=4, bottomPadding=0, showBoundary=0)
    right_frame = Frame(MARGIN + 6 + left_w + gap, FOOTER_H + 8, right_w, H - HEADER_H - FOOTER_H - 16, leftPadding=0, rightPadding=0, topPadding=4, bottomPadding=0, showBoundary=0)

    left_story = [
        para("<b>Dataset</b>", S_H2), sp(4),
        bullet("Source: Financial PhraseBank (Malo et al., 2014)"),
        bullet("Hugging Face: <font face='Courier' size='9'>takala/financial_phrasebank</font>"),
        bullet("Licence: CC BY-NC-SA 3.0 — evaluation use only,\n  raw text not redistributed"),
        bullet("Config: sentences_75agree (≥75% annotator agreement)"),
        bullet("Size: 3,453 labelled sentences — Neg: 420, Neu: 2,146, Pos: 887"),
        sp(10),
        para("<b>Methodology</b>", S_H2), sp(4),
        bullet("Existing rule-based analyzer applied <i>without any tuning</i>"),
        bullet("Score > 0 → positive  |  Score < 0 → negative  |  Score = 0 → neutral"),
        bullet("No model training; this is a <b>baseline evaluation only</b>"),
        sp(10),
        para("Overall Accuracy: <b>67.30%</b>  |  Macro F1: <b>0.4314</b>",
             ParagraphStyle("big", fontName="Helvetica-Bold", fontSize=12, textColor=NAVY, leading=16)),
        sp(6),
        para("⚠  This evaluates <i>only</i> sentiment extraction. It does not validate event classification, impact scoring, or portfolio stress assumptions.", S_WARN),
    ]
    left_frame.addFromList(left_story, canvas)

    # Per-class table + confusion matrix
    class_data = [
        [Paragraph(h, S_CELLW) for h in ["Class", "Precision", "Recall", "F1"]],
        [Paragraph("Negative", ParagraphStyle("neg", fontName="Helvetica-Bold", fontSize=9, textColor=RED, leading=12, alignment=TA_CENTER)),
         "45.98%", Paragraph("<b>9.52% ⚠</b>", ParagraphStyle("nr", fontName="Helvetica-Bold", fontSize=9, textColor=RED, leading=12, alignment=TA_CENTER)), "0.158"],
        ["Neutral",  "69.29%", "96.83%", "0.808"],
        ["Positive", "56.13%", "23.22%", "0.329"],
    ]
    cw = right_w / 4
    class_tbl = Table(class_data, colWidths=[cw]*4, repeatRows=1)
    class_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("TEXTCOLOR", (0,0), (-1,0), WHITE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, colors.HexColor("#EEF2F8")]),
        ("BOX", (0,0), (-1,-1), 0.8, MGREY),
        ("INNERGRID", (0,0), (-1,-1), 0.5, MGREY),
        ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("ALIGN", (1,0), (-1,-1), "CENTER"),
        ("BACKGROUND", (2,1), (2,1), colors.HexColor("#FDECEA")),
    ]))

    # Confusion matrix
    cm_data = [
        [Paragraph("<b>True \\ Pred</b>", S_SMALL),
         Paragraph("<b>Neg</b>", ParagraphStyle("cmh", fontName="Helvetica-Bold", fontSize=8.5, textColor=RED, leading=11, alignment=TA_CENTER)),
         Paragraph("<b>Neu</b>", ParagraphStyle("cmh2", fontName="Helvetica-Bold", fontSize=8.5, textColor=STEEL, leading=11, alignment=TA_CENTER)),
         Paragraph("<b>Pos</b>", ParagraphStyle("cmh3", fontName="Helvetica-Bold", fontSize=8.5, textColor=GREEN, leading=11, alignment=TA_CENTER))],
        [Paragraph("<b>Neg (420)</b>",  ParagraphStyle("cml", fontName="Helvetica-Bold", fontSize=8.5, textColor=RED,   leading=11)), "40",  "279", "101"],
        [Paragraph("<b>Neu (2146)</b>", ParagraphStyle("cml2",fontName="Helvetica-Bold", fontSize=8.5, textColor=STEEL, leading=11)), "8",  "2078",  "60"],
        [Paragraph("<b>Pos (887)</b>",  ParagraphStyle("cml3",fontName="Helvetica-Bold", fontSize=8.5, textColor=GREEN, leading=11)), "39",  "642", "206"],
    ]
    cw2 = right_w / 4
    cm_tbl = Table(cm_data, colWidths=[cw2 * 1.1, cw2 * 0.9, cw2 * 0.9, cw2 * 1.1])
    cm_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8EEF5")),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#E8EEF5")),
        ("BACKGROUND", (1,1), (1,1), colors.HexColor("#C8E6C9")),
        ("BACKGROUND", (2,2), (2,2), colors.HexColor("#C8E6C9")),
        ("BACKGROUND", (3,3), (3,3), colors.HexColor("#C8E6C9")),
        ("BOX", (0,0), (-1,-1), 0.8, MGREY),
        ("INNERGRID", (0,0), (-1,-1), 0.5, MGREY),
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("ALIGN", (1,0), (-1,-1), "CENTER"),
    ]))

    right_story = [
        sp(2),
        para("<b>Per-Class Performance</b>", S_H2), sp(5),
        class_tbl, sp(8),
        para("<b>Confusion Matrix</b>", S_H2), sp(5),
        cm_tbl, sp(8),
        para("Key finding: The rule-based baseline strongly over-predicts <i>neutral</i>, missing 90.5% of negative and 76.8% of positive sentences. Contextual models (e.g. FinBERT) would perform substantially better.", S_SMALL),
    ]
    right_frame.addFromList(right_story, canvas)


def build_slide_6(canvas, doc):
    """Historical Market Analysis"""
    draw_bg(canvas, doc, LGREY)
    draw_header_bar(canvas, "Historical Market Analysis", "T−1 to T+5 observed returns · yfinance · verified sources", dark=True)
    draw_footer(canvas, 6)
    draw_side_accent(canvas, BLUE)

    frame = content_frame()
    story = [
        sp(4),
        para("Three documented financial events analysed: daily adjusted close prices retrieved via <b>yfinance</b> and cached locally. Window: last trading close before event (T−1) to close five trading sessions after (T+5).", S_BODY),
        sp(4),
        para("Return formula: <font face='Courier' size='9'>(Price_end − Price_start) / Price_start</font>. Benchmark: SPY (SPDR S&amp;P 500 ETF).", S_BODY),
        sp(10),
    ]

    events = [
        ("SVB Collapse — Bank Run Starts",
         "2023-03-09", "KRE", "SPDR Regional Banking ETF",
         "2023-03-08", "2023-03-16",
         "-19.91%", "-0.70%", "-19.21%",
         RED, "Wikipedia: Collapse of Silicon Valley Bank"),
        ("Credit Suisse Liquidity Crisis",
         "2023-03-15", "XLF", "Financial Select Sector SPDR",
         "2023-03-14", "2023-03-22",
         "-2.77%", "+0.48%", "-3.25%",
         AMBER, "Wikipedia: Collapse of Credit Suisse"),
        ("UK Mini-Budget Market Crash",
         "2022-09-23", "EWU", "iShares MSCI United Kingdom ETF",
         "2022-09-22", "2022-09-30",
         "-5.52%", "-4.55%", "-0.96%",
         STEEL, "Wikipedia: September 2022 UK mini-budget"),
    ]

    tbl_data = [[Paragraph(h, S_CELLW) for h in
                 ["Event", "Date", "Ticker", "Window Start→End",
                  "Ticker Return", "SPY Return", "Excess Return"]]]

    def ret_cell(val, positive_is_good=False):
        v = float(val.replace('%','').replace('+',''))
        col = GREEN if v > 0 else RED if v < 0 else NAVY
        return Paragraph(f"<b>{val}</b>", ParagraphStyle("rc", fontName="Helvetica-Bold", fontSize=9, textColor=col, leading=12, alignment=TA_CENTER))

    for (name, date, ticker, desc, ws, we, tr, br, er, color, src) in events:
        tbl_data.append([
            Paragraph(f"<b>{name}</b><br/><font size='7.5' color='#666666'>{desc}</font>",
                      ParagraphStyle("en", fontName="Helvetica", fontSize=9, leading=12)),
            Paragraph(date, ParagraphStyle("dt", fontName="Helvetica", fontSize=9, leading=12, alignment=TA_CENTER)),
            Paragraph(f"<b>{ticker}</b>", ParagraphStyle("tk", fontName="Helvetica-Bold", fontSize=9, textColor=NAVY, leading=12, alignment=TA_CENTER)),
            Paragraph(f"{ws}<br/>→ {we}", ParagraphStyle("wd", fontName="Helvetica", fontSize=8.5, leading=12, alignment=TA_CENTER)),
            ret_cell(tr), ret_cell(br), ret_cell(er),
        ])

    col_widths = [CONTENT_W*0.26, CONTENT_W*0.09, CONTENT_W*0.07,
                  CONTENT_W*0.14, CONTENT_W*0.12, CONTENT_W*0.12, CONTENT_W*0.12]
    ev_tbl = Table(tbl_data, colWidths=col_widths, repeatRows=1)
    ev_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("TEXTCOLOR", (0,0), (-1,0), WHITE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, colors.HexColor("#EEF2F8")]),
        ("BOX", (0,0), (-1,-1), 0.8, MGREY),
        ("INNERGRID", (0,0), (-1,-1), 0.5, MGREY),
        ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING", (0,0), (-1,-1), 7), ("RIGHTPADDING", (0,0), (-1,-1), 7),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(ev_tbl)
    story += [
        sp(10),
        para("Sources: Wikipedia articles for each event (URLs recorded in <font face='Courier' size='9'>results/market_data/event_returns.csv</font>). Prices from Yahoo Finance via yfinance. Cached in <font face='Courier' size='9'>results/market_data/price_cache.csv</font>.", S_SMALL),
        sp(6),
        para("⚠  <b>These are historical observations, not causal proof.</b> Multiple confounding factors affect prices over any 5-day window. These returns do <i>not</i> validate the illustrative portfolio shock percentages used in the stress-test prototype.", S_WARN),
    ]
    frame.addFromList(story, canvas)


def build_slide_7(canvas, doc):
    """Impact, Limitations & Next Steps"""
    draw_bg(canvas, doc, NAVY)
    draw_header_bar(canvas, "Impact, Limitations & Next Steps", "Honest assessment and forward path", dark=True)
    draw_footer(canvas, 7)

    # Gold accent side
    canvas.saveState()
    canvas.setFillColor(GOLD)
    canvas.rect(0, FOOTER_H, 6, H - HEADER_H - FOOTER_H, fill=1, stroke=0)
    canvas.restoreState()

    left_w  = CONTENT_W * 0.48
    right_w = CONTENT_W * 0.48
    gap     = CONTENT_W * 0.04

    left_frame  = Frame(MARGIN + 10, FOOTER_H + 8, left_w,   H - HEADER_H - FOOTER_H - 16, leftPadding=0, rightPadding=4, topPadding=4, bottomPadding=0, showBoundary=0)
    right_frame = Frame(MARGIN + 10 + left_w + gap, FOOTER_H + 8, right_w, H - HEADER_H - FOOTER_H - 16, leftPadding=0, rightPadding=0, topPadding=4, bottomPadding=0, showBoundary=0)

    hs = ParagraphStyle("wh2", fontName="Helvetica-Bold", fontSize=12, textColor=GOLD, leading=16)
    bs = ParagraphStyle("wb",  fontName="Helvetica",      fontSize=9.5, textColor=WHITE, leading=14, leftIndent=12)
    ws = ParagraphStyle("ww",  fontName="Helvetica-Oblique", fontSize=8.5, textColor=GOLD, leading=12)

    left_story = [
        para("<b>What This Prototype Demonstrates</b>", hs), sp(6),
        Paragraph("• End-to-end pipeline from unstructured text to portfolio risk output", bs),
        Paragraph("• Rule-based NLP evaluated against 3,453 real labelled sentences", bs),
        Paragraph("• Observed market returns for 3 documented financial events", bs),
        Paragraph("• 36 automated unit tests with GitHub Actions CI", bs),
        Paragraph("• Clean separation of synthetic shocks from real-data evidence", bs),
        sp(12),
        para("<b>Honest Limitations</b>", hs), sp(6),
        Paragraph("• Sentiment recall: only 9.52% for negative class (rule-based baseline)", bs),
        Paragraph("• Portfolio shocks are illustrative assumptions — not calibrated to data", bs),
        Paragraph("• Event dates are pre-selected; no live news ingestion", bs),
        Paragraph("• Historical returns show correlation only — not causal validation", bs),
        Paragraph("• Synthetic portfolio; no real positions or confidential data used", bs),
    ]
    left_frame.addFromList(left_story, canvas)

    ns_items = [
        ("NLP Upgrade",       "Replace keyword rules with FinBERT or a fine-tuned transformer for domain-accurate sentiment"),
        ("Shock Calibration", "Estimate shock distributions from historical event studies rather than fixed assumptions"),
        ("Live Data Feed",    "Connect to real-time news APIs (e.g. NewsAPI, Bloomberg) with deduplication"),
        ("Broader Events",    "Expand event taxonomy with more granular geopolitical and sector-specific triggers"),
        ("Portfolio Scale",   "Generalise to arbitrary portfolios with full position data ingestion"),
    ]
    right_story = [
        para("<b>Realistic Next Steps</b>", hs), sp(6),
    ]
    for label, desc in ns_items:
        t = Table(
            [[Paragraph(f"<b>{label}</b>", ParagraphStyle("nsl", fontName="Helvetica-Bold", fontSize=9, textColor=NAVY, leading=12)),
              Paragraph(desc, ParagraphStyle("nsd", fontName="Helvetica", fontSize=8.5, textColor=NAVY, leading=12))]],
            colWidths=[right_w * 0.28, right_w * 0.70],
        )
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#EEF2F8")),
            ("BACKGROUND", (0,0), (0,0), STEEL),
            ("TEXTCOLOR", (0,0), (0,0), WHITE),
            ("BOX", (0,0), (-1,-1), 0.8, MGREY),
            ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
        ]))
        right_story.append(t)
        right_story.append(sp(5))

    right_story += [
        sp(4),
        para("Devanshi Gupta  ·  IGDTUW  ·  S&amp;P Global &amp; CRISIL Campus Hackathon 2026", ParagraphStyle("fin", fontName="Helvetica", fontSize=8.5, textColor=MGREY, leading=12, alignment=TA_CENTER)),
        sp(2),
        para("College email: <i>[Pending — add before submission]</i>", ParagraphStyle("em", fontName="Helvetica-Oblique", fontSize=8, textColor=GOLD, leading=11, alignment=TA_CENTER)),
    ]
    right_frame.addFromList(right_story, canvas)


# ── Main builder ──────────────────────────────────────────────────────────────

SLIDE_BUILDERS = [
    build_slide_1,
    build_slide_2,
    build_slide_3,
    build_slide_4,
    build_slide_5,
    build_slide_6,
    build_slide_7,
]


def build_pdf():
    from reportlab.platypus import SimpleDocTemplate

    # We use canvas-level drawing, so we use a minimal doc just to iterate pages.
    from reportlab.pdfgen import canvas as canvas_mod

    c = canvas_mod.Canvas(str(OUT_PDF), pagesize=(W, H))
    c.setTitle("Signal-to-Shock — S&P Global & CRISIL Campus Hackathon 2026")
    c.setAuthor("Devanshi Gupta")
    c.setSubject("Financial Event Intelligence & Portfolio Stress Testing")

    for i, builder in enumerate(SLIDE_BUILDERS, 1):
        builder(c, None)
        c.showPage()

    c.save()
    print(f"✓ PDF written: {OUT_PDF}")
    print(f"  Size: {OUT_PDF.stat().st_size:,} bytes")

    # Verify page count
    try:
        from reportlab.lib.utils import open_for_read
        # Quick check using PyPDF or pdfinfo if available
        import subprocess
        result = subprocess.run(["pdfinfo", str(OUT_PDF)], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "Pages:" in line:
                    print(f"  {line.strip()}")
    except Exception:
        pass


if __name__ == "__main__":
    build_pdf()
