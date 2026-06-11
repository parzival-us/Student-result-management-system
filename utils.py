"""
utils.py - Utility functions and shared constants for the Student Result Management System.
Contains theme configuration, styled widget factories, PDF/CSV export, and helpers.
"""

import csv
import os
import tkinter as tk
from datetime import datetime
from typing import List, Tuple

from models import Student, Marks

# ═══════════════════════════════════════════════════════════════════════
#  Dark Theme Color Palette — Premium Edition
# ═══════════════════════════════════════════════════════════════════════

THEME = {
    # Backgrounds (layered depth system)
    "bg":            "#0b0e14",      # Deepest background
    "bg_secondary":  "#111620",      # Content area
    "bg_card":       "#151c28",      # Cards and panels
    "bg_elevated":   "#1a2232",      # Elevated surfaces (popovers, tooltips)
    "sidebar":       "#070a10",      # Sidebar background
    "sidebar_hover": "#0f1520",      # Sidebar item hover

    # Accent colors (refined purple spectrum)
    "accent":        "#8b5cf6",      # Primary accent
    "accent_light":  "#a78bfa",      # Light accent for text
    "accent_dark":   "#6d28d9",      # Dark accent for pressed states
    "accent_glow":   "#8b5cf6",      # Glow/border accent
    "accent_muted":  "#2e1a5e",      # Muted accent for backgrounds

    # Semantic colors
    "success":       "#22c55e",
    "success_dark":  "#16a34a",
    "success_muted": "#0f2a1a",
    "danger":        "#f43f5e",
    "danger_dark":   "#e11d48",
    "danger_muted":  "#2a0f15",
    "warning":       "#eab308",
    "warning_muted": "#2a2408",
    "info":          "#38bdf8",
    "info_dark":     "#0ea5e9",
    "info_muted":    "#0b1f2e",

    # Text hierarchy
    "text":          "#e8edf5",      # Primary text
    "text_secondary":"#8893a7",      # Secondary text
    "text_dim":      "#4a5568",      # Dimmed text
    "text_accent":   "#c4b5fd",      # Accent-tinted text

    # UI elements
    "border":        "#1c2536",      # Default borders
    "border_light":  "#2a3549",      # Lighter borders
    "input_bg":      "#0f1420",      # Input field background
    "input_focus":   "#1a1040",      # Input focus background
    "hover":         "#1a2235",      # General hover state
    "selected":      "#8b5cf6",      # Selection accent
    "scrollbar":     "#2a3549",
    "scrollbar_hover":"#3a4a65",
    "divider":       "#1a2030",      # Subtle dividers

    # Grade colors (vibrant, distinct)
    "grade_a_plus":  "#22c55e",
    "grade_a":       "#4ade80",
    "grade_b_plus":  "#38bdf8",
    "grade_b":       "#60a5fa",
    "grade_c":       "#eab308",
    "grade_d":       "#f97316",
    "grade_f":       "#f43f5e",
}

GRADE_COLORS = {
    "A+": THEME["grade_a_plus"], "A": THEME["grade_a"],
    "B+": THEME["grade_b_plus"], "B": THEME["grade_b"],
    "C": THEME["grade_c"], "D": THEME["grade_d"], "F": THEME["grade_f"],
}

# ═══════════════════════════════════════════════════════════════════════
#  Typography System
# ═══════════════════════════════════════════════════════════════════════

FONTS = {
    "heading":        ("Segoe UI", 24, "bold"),
    "heading_sm":     ("Segoe UI", 18, "bold"),
    "subheading":     ("Segoe UI", 15, "bold"),
    "body":           ("Segoe UI", 11),
    "body_bold":      ("Segoe UI", 11, "bold"),
    "body_lg":        ("Segoe UI", 12),
    "body_lg_bold":   ("Segoe UI", 12, "bold"),
    "small":          ("Segoe UI", 9),
    "small_bold":     ("Segoe UI", 9, "bold"),
    "tiny":           ("Segoe UI", 8),
    "stat_value":     ("Segoe UI", 30, "bold"),
    "stat_label":     ("Segoe UI", 10),
    "button":         ("Segoe UI", 10, "bold"),
    "button_lg":      ("Segoe UI", 11, "bold"),
    "sidebar":        ("Segoe UI", 11),
    "sidebar_active": ("Segoe UI", 11, "bold"),
    "entry":          ("Segoe UI", 11),
    "treeview":       ("Segoe UI", 10),
    "treeview_head":  ("Segoe UI", 10, "bold"),
    "mono":           ("Consolas", 11),
    "logo":           ("Segoe UI", 18, "bold"),
    "logo_sub":       ("Segoe UI", 9),
}


# ═══════════════════════════════════════════════════════════════════════
#  Styled Widget Factories
# ═══════════════════════════════════════════════════════════════════════

class StyledWidgets:
    """Factory class for creating consistently styled Tkinter widgets."""

    @staticmethod
    def create_button(parent, text, bg=None, fg="#fff", command=None,
                      font=None, padx=16, pady=6, icon=""):
        """
        Create a styled flat button with hover effects.
        Returns the button widget.
        """
        if bg is None:
            bg = THEME["accent"]
        if font is None:
            font = FONTS["button"]

        display = f"{icon}  {text}" if icon else text

        # Calculate darker hover color
        hex_c = bg.lstrip("#")
        r, g, b = int(hex_c[:2], 16), int(hex_c[2:4], 16), int(hex_c[4:6], 16)
        dr, dg, db = max(0, int(r * 0.82)), max(0, int(g * 0.82)), max(0, int(b * 0.82))
        hover_bg = f"#{dr:02x}{dg:02x}{db:02x}"

        btn = tk.Button(
            parent, text=display, font=font,
            bg=bg, fg=fg, activebackground=hover_bg, activeforeground=fg,
            relief="flat", cursor="hand2", bd=0,
            padx=padx, pady=pady, command=command,
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn

    @staticmethod
    def create_outline_button(parent, text, color=None, command=None,
                              font=None, padx=14, pady=5, icon=""):
        """Create a button with outline style (transparent bg with colored border)."""
        if color is None:
            color = THEME["accent"]
        if font is None:
            font = FONTS["button"]

        display = f"{icon}  {text}" if icon else text

        btn = tk.Button(
            parent, text=display, font=font,
            bg=THEME["bg_card"], fg=color,
            activebackground=THEME["hover"], activeforeground=color,
            relief="flat", cursor="hand2", bd=0,
            padx=padx, pady=pady, command=command,
            highlightthickness=1, highlightbackground=color, highlightcolor=color,
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=THEME["hover"]))
        btn.bind("<Leave>", lambda e: btn.config(bg=THEME["bg_card"]))
        return btn

    @staticmethod
    def create_entry(parent, placeholder="", width=None):
        """
        Create a styled entry with placeholder text and focus glow.
        Returns (entry_widget, string_var).
        """
        var = tk.StringVar()

        entry = tk.Entry(
            parent, textvariable=var, font=FONTS["entry"],
            bg=THEME["input_bg"], fg=THEME["text"], insertbackground=THEME["accent_light"],
            relief="flat", highlightthickness=2,
            highlightcolor=THEME["accent"], highlightbackground=THEME["border"],
        )
        if width:
            entry.config(width=width)

        # Placeholder logic
        if placeholder:
            entry.insert(0, placeholder)
            entry.config(fg=THEME["text_dim"])

            def _focus_in(e):
                if entry.get() == placeholder:
                    entry.delete(0, "end")
                    entry.config(fg=THEME["text"])
                entry.config(highlightbackground=THEME["accent"])

            def _focus_out(e):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.config(fg=THEME["text_dim"])
                entry.config(highlightbackground=THEME["border"])

            entry.bind("<FocusIn>", _focus_in)
            entry.bind("<FocusOut>", _focus_out)

        return entry, var

    @staticmethod
    def create_card(parent, title="", title_icon="", accent_color=None):
        """
        Create a styled card frame with optional title and accent bar.
        Returns (outer_frame, content_frame).
        """
        # Shadow effect via layered frames
        shadow = tk.Frame(parent, bg=THEME["border"], padx=1, pady=1)

        outer = tk.Frame(shadow, bg=THEME["bg_card"])
        outer.pack(fill="both", expand=True)

        # Accent bar at top
        if accent_color:
            accent = tk.Frame(outer, bg=accent_color, height=3)
            accent.pack(fill="x")

        # Title
        if title:
            title_frame = tk.Frame(outer, bg=THEME["bg_card"])
            title_frame.pack(fill="x", padx=20, pady=(16, 8))
            display = f"{title_icon}  {title}" if title_icon else title
            tk.Label(
                title_frame, text=display, font=FONTS["subheading"],
                bg=THEME["bg_card"], fg=THEME["text"],
            ).pack(side="left")

        content = tk.Frame(outer, bg=THEME["bg_card"])
        content.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        return shadow, content

    @staticmethod
    def create_divider(parent, color=None):
        """Create a horizontal divider line."""
        c = color or THEME["divider"]
        d = tk.Frame(parent, bg=c, height=1)
        return d

    @staticmethod
    def create_badge(parent, text, bg, fg="#fff"):
        """Create a small colored badge label."""
        badge = tk.Label(
            parent, text=f"  {text}  ", font=FONTS["small_bold"],
            bg=bg, fg=fg,
        )
        return badge


# ═══════════════════════════════════════════════════════════════════════
#  Animation Helpers
# ═══════════════════════════════════════════════════════════════════════

def animate_counter(widget, target, duration_ms=800, prefix="", suffix=""):
    """Animate a label's text from 0 to target value."""
    steps = 20
    delay = max(1, duration_ms // steps)
    current = [0]

    def _step():
        current[0] += target / steps
        if current[0] >= target:
            current[0] = target
            widget.config(text=f"{prefix}{target}{suffix}")
            return
        if isinstance(target, int):
            widget.config(text=f"{prefix}{int(current[0])}{suffix}")
        else:
            widget.config(text=f"{prefix}{current[0]:.1f}{suffix}")
        widget.after(delay, _step)

    widget.config(text=f"{prefix}0{suffix}")
    widget.after(100, _step)


# ═══════════════════════════════════════════════════════════════════════
#  Export Helpers
# ═══════════════════════════════════════════════════════════════════════

def get_exports_dir() -> str:
    """Get or create the exports directory next to this script."""
    exports = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
    os.makedirs(exports, exist_ok=True)
    return exports


def export_to_csv(ranked_data: List[Tuple[Student, Marks, int]], filepath: str = None) -> str:
    """Export student results to a CSV file. Returns the filepath."""
    if filepath is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(get_exports_dir(), f"results_{timestamp}.csv")

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Rank", "Roll Number", "Name", "Class",
            "Subject 1", "Subject 2", "Subject 3", "Subject 4", "Subject 5",
            "Total", "Percentage", "Grade", "Status",
        ])
        for student, marks, rank in ranked_data:
            writer.writerow([
                rank, student.roll_number, student.name, student.class_name,
                marks.subject1, marks.subject2, marks.subject3, marks.subject4, marks.subject5,
                marks.total, f"{marks.percentage}%", marks.grade, marks.status,
            ])
    return filepath


def export_to_pdf(student: Student, marks: Marks, rank: int = None, filepath: str = None) -> str:
    """Export a single student's report card to PDF."""
    try:
        from fpdf import FPDF
    except ImportError:
        raise ImportError("fpdf2 is required for PDF export. Install with: pip install fpdf2")

    if filepath is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_roll = student.roll_number.replace("/", "-").replace("\\", "-")
        filepath = os.path.join(get_exports_dir(), f"{safe_roll}_report_{timestamp}.pdf")

    pdf = FPDF()
    pdf.add_page()
    page_w = pdf.w - 2 * pdf.l_margin

    # Header
    pdf.set_fill_color(124, 58, 237)
    pdf.rect(0, 0, 210, 45, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_y(10)
    pdf.cell(page_w, 10, "STUDENT REPORT CARD", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(page_w, 8, "Student Result Management System", align="C", new_x="LMARGIN", new_y="NEXT")

    # Student info
    pdf.set_y(55)
    pdf.set_text_color(50, 50, 50)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(page_w, 10, "Student Information", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(124, 58, 237)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + page_w, pdf.get_y())
    pdf.ln(5)

    pdf.set_font("Helvetica", "", 11)
    for label, value in [("Name", student.name), ("Roll Number", student.roll_number),
                         ("Class", student.class_name or "N/A"), ("Email", student.email or "N/A"),
                         ("Phone", student.phone or "N/A")]:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(45, 8, f"{label}:")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, value, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)

    # Marks table
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(page_w, 10, "Subject-wise Marks", new_x="LMARGIN", new_y="NEXT")
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + page_w, pdf.get_y())
    pdf.ln(3)

    col_w = [page_w * 0.45, page_w * 0.25, page_w * 0.15, page_w * 0.15]
    pdf.set_fill_color(124, 58, 237)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    for txt, w in zip(["  Subject", "Marks", "Max", "Status"], col_w):
        pdf.cell(w, 9, txt, align="C" if txt != "  Subject" else "", fill=True)
    pdf.ln()

    pdf.set_text_color(50, 50, 50)
    for i, (subject, score) in enumerate(marks.get_subjects_dict().items()):
        bg = (245, 245, 250) if i % 2 == 0 else (255, 255, 255)
        pdf.set_fill_color(*bg)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(col_w[0], 8, f"  {subject}", fill=True)
        pdf.cell(col_w[1], 8, str(score), align="C", fill=True)
        pdf.cell(col_w[2], 8, "100", align="C", fill=True)
        st = "Pass" if score >= 33 else "Fail"
        pdf.set_text_color(16, 185, 129) if score >= 33 else pdf.set_text_color(239, 68, 68)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(col_w[3], 8, st, align="C", fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(50, 50, 50)

    pdf.ln(8)

    # Summary
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(page_w, 10, "Result Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + page_w, pdf.get_y())
    pdf.ln(5)

    summary = [("Total Marks", f"{marks.total} / 500"), ("Percentage", f"{marks.percentage}%"),
               ("Grade", marks.grade), ("Overall Status", marks.status)]
    if rank is not None:
        summary.append(("Class Rank", f"#{rank}"))

    for label, value in summary:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(50, 9, f"{label}:")
        pdf.set_font("Helvetica", "", 12)
        if "FAIL" in value:
            pdf.set_text_color(239, 68, 68)
        elif "PASS" in value or "A" in value:
            pdf.set_text_color(16, 185, 129)
        else:
            pdf.set_text_color(50, 50, 50)
        pdf.cell(0, 9, value, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(50, 50, 50)

    # Footer
    pdf.set_y(-30)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + page_w, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(page_w, 5,
             f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | Student Result Management System",
             align="C")
    pdf.output(filepath)
    return filepath


def export_all_to_pdf(ranked_data: List[Tuple[Student, Marks, int]], filepath: str = None) -> str:
    """Export all student results to a single multi-page PDF."""
    try:
        from fpdf import FPDF
    except ImportError:
        raise ImportError("fpdf2 is required. Install with: pip install fpdf2")

    if filepath is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(get_exports_dir(), f"all_results_{timestamp}.pdf")

    pdf = FPDF()
    page_w = 210 - 20

    for student, marks, rank in ranked_data:
        pdf.add_page()
        pdf.set_fill_color(124, 58, 237)
        pdf.rect(0, 0, 210, 35, "F")
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_y(8)
        pdf.cell(page_w, 10, "STUDENT REPORT CARD", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(page_w, 7, f"Rank #{rank}", align="C", new_x="LMARGIN", new_y="NEXT")

        pdf.set_y(45)
        pdf.set_text_color(50, 50, 50)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(30, 7, "Name:")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(60, 7, student.name)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(30, 7, "Roll No:")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, student.roll_number, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(30, 7, "Class:")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, student.class_name or "N/A", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        col_w = page_w / 3
        pdf.set_fill_color(124, 58, 237)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(col_w * 1.5, 8, "  Subject", fill=True)
        pdf.cell(col_w * 0.75, 8, "Marks", align="C", fill=True)
        pdf.cell(col_w * 0.75, 8, "Status", align="C", fill=True, new_x="LMARGIN", new_y="NEXT")

        pdf.set_text_color(50, 50, 50)
        for i, (sub, sc) in enumerate(marks.get_subjects_dict().items()):
            bg = (245, 245, 250) if i % 2 == 0 else (255, 255, 255)
            pdf.set_fill_color(*bg)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(col_w * 1.5, 7, f"  {sub}", fill=True)
            pdf.cell(col_w * 0.75, 7, f"{sc}/100", align="C", fill=True)
            pdf.set_font("Helvetica", "B", 10)
            st = "Pass" if sc >= 33 else "Fail"
            pdf.set_text_color(16, 185, 129) if sc >= 33 else pdf.set_text_color(239, 68, 68)
            pdf.cell(col_w * 0.75, 7, st, align="C", fill=True, new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(50, 50, 50)

        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(40, 8, f"Total: {marks.total}/500")
        pdf.cell(40, 8, f"Percentage: {marks.percentage}%")
        pdf.cell(30, 8, f"Grade: {marks.grade}")
        sc = (16, 185, 129) if marks.status == "PASS" else (239, 68, 68)
        pdf.set_text_color(*sc)
        pdf.cell(0, 8, f"Status: {marks.status}", new_x="LMARGIN", new_y="NEXT")

    pdf.output(filepath)
    return filepath


# ═══════════════════════════════════════════════════════════════════════
#  Validation Helpers
# ═══════════════════════════════════════════════════════════════════════

def validate_marks(value: str) -> float:
    """Validate marks string is a number between 0 and 100."""
    try:
        num = float(value)
    except (ValueError, TypeError):
        raise ValueError("Marks must be a number.")
    if num < 0 or num > 100:
        raise ValueError("Marks must be between 0 and 100.")
    return num


def validate_student_fields(roll: str, name: str) -> None:
    """Validate that required student fields are provided."""
    if not roll or not roll.strip():
        raise ValueError("Roll number is required.")
    if not name or not name.strip():
        raise ValueError("Student name is required.")
