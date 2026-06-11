"""
gui/dashboard.py - Dashboard page for the Student Result Management System.
Displays statistics cards, grade distribution chart, and subject-average chart.
"""

import tkinter as tk
from tkinter import ttk
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import THEME, FONTS, GRADE_COLORS, StyledWidgets, animate_counter


class DashboardFrame(tk.Frame):
    def __init__(self, parent, db, app, **kwargs):
        super().__init__(parent, bg=THEME["bg"], **kwargs)
        self.db = db
        self.app = app
        self._build_ui()

    def _build_ui(self):
        # ── Scrollable Container ──────────────────────────────────
        canvas = tk.Canvas(self, bg=THEME["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=THEME["bg"])

        self.scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", width=canvas.winfo_width())
        self.bind("<Configure>", lambda e: canvas.itemconfig(canvas.find_all()[0], width=e.width))
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # ── Header ────────────────────────────────────────────────
        header = tk.Frame(self.scroll_frame, bg=THEME["bg"])
        header.pack(fill="x", padx=40, pady=(40, 20))

        tk.Label(
            header, text="Overview Dashboard", font=FONTS["heading"],
            bg=THEME["bg"], fg=THEME["text"],
        ).pack(side="left")

        # Quick action button
        StyledWidgets.create_button(
            header, "New Student", icon="✨",
            command=lambda: self.app.show_frame(sys.modules['gui.student_form'].StudentFormFrame)
        ).pack(side="right")

        # ── Stat Cards ────────────────────────────────────────────
        self._build_stat_cards()

        # ── Charts ────────────────────────────────────────────────
        self._build_charts()

        # ── Top Performers ────────────────────────────────────────
        self._build_top_students()

    def _build_stat_cards(self):
        cards_frame = tk.Frame(self.scroll_frame, bg=THEME["bg"])
        cards_frame.pack(fill="x", padx=35, pady=(0, 20))

        total_students = self.db.get_student_count()
        pass_count, fail_count = self.db.get_pass_fail_counts()
        avg_pct = self.db.get_average_percentage()
        top = self.db.get_top_performer()

        total = pass_count + fail_count
        pass_rate = (pass_count / total * 100) if total > 0 else 0

        # Data: (title, value, suffix, icon, color)
        stats = [
            ("Total Students", total_students, "", "👥", THEME["info"]),
            ("Overall Pass Rate", pass_rate, "%", "📈", THEME["success"]),
            ("Average Score", avg_pct, "%", "🎯", THEME["warning"]),
            ("Top Performer", top[0].name if top else "N/A", f"\n{top[1].percentage}%" if top else "", "🏆", THEME["accent"]),
        ]

        for i, (title, val, suffix, icon, color) in enumerate(stats):
            cards_frame.columnconfigure(i, weight=1, uniform="card")
            
            # Using the styled card factory
            _, inner = StyledWidgets.create_card(cards_frame, accent_color=color)
            inner.master.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")

            # Icon & Title
            top_row = tk.Frame(inner, bg=THEME["bg_card"])
            top_row.pack(fill="x", pady=(0, 10))
            tk.Label(top_row, text=icon, font=("Segoe UI", 16), bg=THEME["bg_card"], fg=color).pack(side="left")
            tk.Label(top_row, text=f"  {title}", font=FONTS["stat_label"], bg=THEME["bg_card"], fg=THEME["text_secondary"]).pack(side="left", pady=3)

            # Value
            val_lbl = tk.Label(inner, text="", font=FONTS["stat_value"], bg=THEME["bg_card"], fg=THEME["text"])
            val_lbl.pack(anchor="w")

            # Animation
            if isinstance(val, (int, float)):
                animate_counter(val_lbl, val, suffix=suffix)
            else:
                val_lbl.config(text=str(val))
                if suffix:
                    tk.Label(inner, text=suffix.strip(), font=FONTS["small"], bg=THEME["bg_card"], fg=THEME["text_accent"]).pack(anchor="w")

    def _build_charts(self):
        charts_frame = tk.Frame(self.scroll_frame, bg=THEME["bg"])
        charts_frame.pack(fill="x", padx=35, pady=10)
        charts_frame.columnconfigure(0, weight=1, uniform="chart")
        charts_frame.columnconfigure(1, weight=1, uniform="chart")

        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure

            self._build_grade_chart(charts_frame, Figure, FigureCanvasTkAgg)
            self._build_subject_chart(charts_frame, Figure, FigureCanvasTkAgg)

        except ImportError:
            _, inner = StyledWidgets.create_card(charts_frame)
            inner.master.grid(row=0, column=0, columnspan=2, padx=5, sticky="nsew")
            tk.Label(
                inner, text="Matplotlib is required for charts.\nRun: pip install matplotlib",
                font=FONTS["body"], bg=THEME["bg_card"], fg=THEME["text_dim"]
            ).pack(pady=40)

    def _build_grade_chart(self, parent, Figure, FigureCanvasTkAgg):
        _, inner = StyledWidgets.create_card(parent, title="Grade Distribution", title_icon="📊")
        inner.master.grid(row=0, column=0, padx=5, sticky="nsew")

        dist = self.db.get_grade_distribution()
        grades = [g for g, c in dist.items() if c > 0]
        counts = [dist[g] for g in grades]
        colors = [GRADE_COLORS.get(g, THEME["text_dim"]) for g in grades]

        fig = Figure(figsize=(5, 3.5), dpi=100, facecolor=THEME["bg_card"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(THEME["bg_card"])

        if counts:
            wedges, texts, autotexts = ax.pie(
                counts, labels=grades, colors=colors, autopct="%1.0f%%",
                startangle=90, textprops={"color": THEME["text_secondary"], "fontsize": 10, "fontweight": "bold"},
                pctdistance=0.75, wedgeprops={"linewidth": 3, "edgecolor": THEME["bg_card"]},
            )
            for t in autotexts:
                t.set_color(THEME["bg"])
        else:
            ax.text(0.5, 0.5, "No data available", transform=ax.transAxes, ha="center", va="center", color=THEME["text_dim"])

        fig.tight_layout(pad=0)
        canvas = FigureCanvasTkAgg(fig, master=inner)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _build_subject_chart(self, parent, Figure, FigureCanvasTkAgg):
        _, inner = StyledWidgets.create_card(parent, title="Subject Averages", title_icon="📉")
        inner.master.grid(row=0, column=1, padx=5, sticky="nsew")

        averages = self.db.get_subject_averages()
        subjects = [s[:8]+"." if len(s)>8 else s for s in averages.keys()]
        values = list(averages.values())

        fig = Figure(figsize=(5, 3.5), dpi=100, facecolor=THEME["bg_card"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(THEME["bg_card"])

        if values:
            colors = [THEME["success"] if v >= 70 else THEME["info"] if v >= 50 else THEME["warning"] if v >= 33 else THEME["danger"] for v in values]
            bars = ax.bar(subjects, values, color=colors, width=0.5, edgecolor="none", alpha=0.9)
            
            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                        f"{val:.1f}", ha="center", va="bottom", color=THEME["text"], fontsize=9, fontweight="bold")

            ax.set_ylim(0, 110)
            ax.tick_params(axis="x", colors=THEME["text_secondary"], length=0, pad=10)
            ax.tick_params(axis="y", colors=THEME["text_secondary"], length=0)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color(THEME["border"])
            ax.spines["bottom"].set_color(THEME["border"])
            ax.grid(axis='y', color=THEME["border_light"], linestyle='-', alpha=0.3)
        else:
            ax.text(0.5, 0.5, "No data available", transform=ax.transAxes, ha="center", va="center", color=THEME["text_dim"])
            ax.axis('off')

        fig.tight_layout(pad=1)
        canvas = FigureCanvasTkAgg(fig, master=inner)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _build_top_students(self):
        _, inner = StyledWidgets.create_card(self.scroll_frame, title="Top Performers", title_icon="⭐")
        inner.master.pack(fill="x", padx=40, pady=(10, 40))

        cols = ("rank", "roll", "name", "pct", "grade")
        tree = ttk.Treeview(inner, columns=cols, show="headings", height=6, style="Dashboard.Treeview")

        headings = {"rank": "Rank", "roll": "Roll No", "name": "Name", "pct": "Score", "grade": "Grade"}
        widths = {"rank": 80, "roll": 120, "name": 250, "pct": 100, "grade": 100}

        for col in cols:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="center" if col != "name" else "w")

        ranked = self.db.get_ranked_students()
        for i, (student, marks, rank) in enumerate(ranked[:6]):
            tree.insert("", "end", values=(
                f"#{rank}", student.roll_number, student.name, f"{marks.percentage}%", marks.grade
            ))

        tree.pack(fill="x", pady=(0, 5))

        if not ranked:
            tk.Label(inner, text="Add student records to generate rankings.", font=FONTS["body"], 
                     bg=THEME["bg_card"], fg=THEME["text_dim"]).pack(pady=20)
