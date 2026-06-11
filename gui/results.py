"""
gui/results.py - Results viewing and report generation interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import THEME, FONTS, GRADE_COLORS, StyledWidgets


class ResultsFrame(tk.Frame):
    def __init__(self, parent, db, app, student_id=None, **kwargs):
        super().__init__(parent, bg=THEME["bg"], **kwargs)
        self.db = db
        self.app = app
        self.init_student = student_id
        
        self.notebook = None
        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self, bg=THEME["bg"])
        header.pack(fill="x", padx=40, pady=(40, 20))

        tk.Label(
            header, text="Results & Leaderboard", font=FONTS["heading"],
            bg=THEME["bg"], fg=THEME["text"],
        ).pack(side="left")

        # ── Custom Tabs ───────────────────────────────────────────
        self.notebook = ttk.Notebook(self)
        
        # Style notebook to blend in
        style = ttk.Style()
        style.configure("TNotebook", background=THEME["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=THEME["bg_secondary"], foreground=THEME["text_secondary"], 
                        padding=(20, 10), font=FONTS["body_bold"], borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", THEME["bg_card"])], foreground=[("selected", THEME["accent_light"])])

        self.tab_individual = tk.Frame(self.notebook, bg=THEME["bg"])
        self.tab_class = tk.Frame(self.notebook, bg=THEME["bg"])

        self.notebook.add(self.tab_individual, text="   👤 Individual Report   ")
        self.notebook.add(self.tab_class, text="   🏆 Class Rankings   ")
        self.notebook.pack(fill="both", expand=True, padx=40, pady=(0, 40))

        self._build_individual_tab()
        self._build_class_tab()

        if self.init_student:
            self.notebook.select(self.tab_individual)
            self._load_report(self.init_student)
        else:
            self.notebook.select(self.tab_class)

    # ══════════════════════════════════════════════════════════════════
    #  Individual Report Tab
    # ══════════════════════════════════════════════════════════════════

    def _build_individual_tab(self):
        top_bar, inner_bar = StyledWidgets.create_card(self.tab_individual)
        top_bar.pack(fill="x", pady=10)
        inner_bar.pack_configure(pady=10)

        tk.Label(inner_bar, text="Select Student:  ", font=FONTS["body_bold"], bg=THEME["bg_card"], fg=THEME["text_secondary"]).pack(side="left", padx=(10,0))
        
        self.student_cb = ttk.Combobox(inner_bar, state="readonly", width=40, font=FONTS["entry"])
        self.student_cb.pack(side="left", ipady=4)
        self.student_cb.bind("<<ComboboxSelected>>", lambda e: self._on_student_selected())
        
        self.btn_export = StyledWidgets.create_button(inner_bar, "Export Report", icon="📥", command=self._export_single_pdf)
        self.btn_export.pack(side="right", padx=10)

        self.report_container = tk.Frame(self.tab_individual, bg=THEME["bg"])
        self.report_container.pack(fill="both", expand=True, pady=(10, 0))

        # Placeholder
        self.placeholder = tk.Label(self.report_container, text="Select a student to view their report card.", 
                                   font=FONTS["body_lg"], bg=THEME["bg"], fg=THEME["text_dim"])
        self.placeholder.pack(expand=True)

        self._populate_combobox()

    def _populate_combobox(self):
        students = self.db.get_all_students()
        self.student_map = {f"{s.roll_number} - {s.name}": s.id for s in students}
        self.student_cb["values"] = list(self.student_map.keys())

    def _on_student_selected(self):
        val = self.student_cb.get()
        if val in self.student_map:
            self._load_report(self.student_map[val])

    def _load_report(self, student_id):
        self.selected_student_id = student_id
        student = self.db.get_student_by_id(student_id)
        marks = self.db.get_marks(student_id)

        # Clear container
        for widget in self.report_container.winfo_children():
            widget.destroy()

        if not marks:
            tk.Label(self.report_container, text="No marks found for this student.", 
                     font=FONTS["body_lg"], bg=THEME["bg"], fg=THEME["text_dim"]).pack(expand=True)
            return

        # Rank
        rank = next((r for s, m, r in self.db.get_ranked_students() if s.id == student_id), "N/A")

        # Report Card UI
        card, inner = StyledWidgets.create_card(self.report_container, accent_color=THEME["accent"])
        card.pack(fill="both", expand=True, padx=10)

        # Banner
        banner = tk.Frame(inner, bg=THEME["accent_muted"])
        banner.pack(fill="x", padx=0, pady=(0, 20))
        tk.Label(banner, text=student.name, font=("Segoe UI", 24, "bold"), bg=THEME["accent_muted"], fg=THEME["text"]).pack(anchor="w", padx=30, pady=(20, 0))
        tk.Label(banner, text=f"Roll No: {student.roll_number}   |   Class: {student.class_name}", font=FONTS["body"], bg=THEME["accent_muted"], fg=THEME["text_accent"]).pack(anchor="w", padx=30, pady=(5, 20))

        # Two columns for Marks and Summary
        cols = tk.Frame(inner, bg=THEME["bg_card"])
        cols.pack(fill="both", expand=True, padx=30)
        
        # Left: Marks
        left = tk.Frame(cols, bg=THEME["bg_card"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        tk.Label(left, text="Subject Performance", font=FONTS["subheading"], bg=THEME["bg_card"], fg=THEME["text"]).pack(anchor="w", pady=(0, 15))
        
        # Table Header
        th = tk.Frame(left, bg=THEME["bg_secondary"])
        th.pack(fill="x")
        tk.Label(th, text="Subject", font=FONTS["small_bold"], bg=THEME["bg_secondary"], fg=THEME["text_secondary"], width=25, anchor="w").pack(side="left", padx=10, pady=8)
        tk.Label(th, text="Marks", font=FONTS["small_bold"], bg=THEME["bg_secondary"], fg=THEME["text_secondary"], width=10).pack(side="left")
        tk.Label(th, text="Status", font=FONTS["small_bold"], bg=THEME["bg_secondary"], fg=THEME["text_secondary"], width=10).pack(side="left")

        # Table Rows
        for i, (sub, val) in enumerate(marks.get_subjects_dict().items()):
            row_bg = THEME["bg_card"] if i % 2 == 0 else THEME["bg_elevated"]
            tr = tk.Frame(left, bg=row_bg)
            tr.pack(fill="x")
            
            tk.Label(tr, text=sub, font=FONTS["body"], bg=row_bg, fg=THEME["text"], width=25, anchor="w").pack(side="left", padx=10, pady=10)
            tk.Label(tr, text=f"{val}/100", font=FONTS["body_bold"], bg=row_bg, fg=THEME["text"]).pack(side="left", width=10)
            
            status_text = "Pass" if val >= 33 else "Fail"
            status_color = THEME["success"] if val >= 33 else THEME["danger"]
            tk.Label(tr, text=status_text, font=FONTS["body_bold"], bg=row_bg, fg=status_color).pack(side="left", width=10)

        # Right: Summary
        right = tk.Frame(cols, bg=THEME["bg_card"])
        right.pack(side="right", fill="y", padx=20)
        
        tk.Label(right, text="Overall Summary", font=FONTS["subheading"], bg=THEME["bg_card"], fg=THEME["text"]).pack(anchor="w", pady=(0, 15))

        stat_box = tk.Frame(right, bg=THEME["bg_elevated"], highlightthickness=1, highlightbackground=THEME["border"])
        stat_box.pack(fill="x")

        summary_data = [
            ("Total Score", f"{marks.total} / 500", THEME["text"]),
            ("Percentage", f"{marks.percentage}%", THEME["text"]),
            ("Final Grade", marks.grade, GRADE_COLORS.get(marks.grade, THEME["text"])),
            ("Class Rank", f"#{rank}", THEME["warning"]),
            ("Status", marks.status, THEME["success"] if marks.status == "PASS" else THEME["danger"]),
        ]

        for lbl, val, color in summary_data:
            f = tk.Frame(stat_box, bg=THEME["bg_elevated"])
            f.pack(fill="x", padx=20, pady=12)
            tk.Label(f, text=lbl, font=FONTS["body"], bg=THEME["bg_elevated"], fg=THEME["text_secondary"]).pack(side="left")
            tk.Label(f, text=val, font=FONTS["subheading"], bg=THEME["bg_elevated"], fg=color).pack(side="right")
            StyledWidgets.create_divider(stat_box).pack(fill="x")

    def _export_single_pdf(self):
        if not hasattr(self, 'selected_student_id'): return
        try:
            from utils import export_to_pdf
            s = self.db.get_student_by_id(self.selected_student_id)
            m = self.db.get_marks(self.selected_student_id)
            rank = next((r for st, _, r in self.db.get_ranked_students() if st.id == self.selected_student_id), None)
            path = export_to_pdf(s, m, rank=rank)
            messagebox.showinfo("Success", f"Report saved:\n{path}", parent=self)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

    # ══════════════════════════════════════════════════════════════════
    #  Class Rankings Tab
    # ══════════════════════════════════════════════════════════════════

    def _build_class_tab(self):
        toolbar, inner = StyledWidgets.create_card(self.tab_class)
        toolbar.pack(fill="x", pady=10)
        inner.pack_configure(pady=10)

        StyledWidgets.create_button(inner, "Export Full PDF", icon="📄", command=self._export_all_pdf).pack(side="right", padx=(10, 0))
        StyledWidgets.create_outline_button(inner, "Export CSV", icon="📊", color=THEME["success"], command=self._export_csv).pack(side="right")

        table_card, t_inner = StyledWidgets.create_card(self.tab_class)
        table_card.pack(fill="both", expand=True, pady=(10, 0))
        t_inner.pack_configure(padx=0, pady=0)

        cols = ("rank", "roll", "name", "class", "total", "pct", "grade", "status")
        self.tree = ttk.Treeview(t_inner, columns=cols, show="headings", style="Custom.Treeview")

        headings = {"rank": "Rank", "roll": "Roll No", "name": "Name", "class": "Class", "total": "Total", "pct": "%", "grade": "Grade", "status": "Status"}
        widths = {"rank": 80, "roll": 100, "name": 220, "class": 100, "total": 80, "pct": 80, "grade": 80, "status": 100}

        for col in cols:
            self.tree.heading(col, text=headings[col])
            anchor = "w" if col == "name" else "center"
            self.tree.column(col, width=widths[col], anchor=anchor)

        tree_scroll = ttk.Scrollbar(t_inner, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        self.tree.tag_configure("rank1", foreground=THEME["warning"], font=FONTS["treeview_head"])
        self.tree.tag_configure("rank2", foreground="#94a3b8", font=FONTS["treeview_head"])
        self.tree.tag_configure("rank3", foreground="#b45309", font=FONTS["treeview_head"])
        self.tree.tag_configure("fail", foreground=THEME["danger"])

        ranked = self.db.get_ranked_students()
        for s, m, r in ranked:
            tag = f"rank{r}" if r <= 3 else "fail" if m.status == "FAIL" else ""
            self.tree.insert("", "end", values=(
                f"#{r}", s.roll_number, s.name, s.class_name, m.total, f"{m.percentage}%", m.grade, m.status
            ), tags=(tag,))

    def _export_csv(self):
        try:
            from utils import export_to_csv
            path = export_to_csv(self.db.get_ranked_students())
            messagebox.showinfo("Success", f"CSV exported to:\n{path}", parent=self)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _export_all_pdf(self):
        try:
            from utils import export_all_to_pdf
            path = export_all_to_pdf(self.db.get_ranked_students())
            messagebox.showinfo("Success", f"PDFs exported to:\n{path}", parent=self)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)
