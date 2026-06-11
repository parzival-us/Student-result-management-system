"""
gui/student_form.py - Student list view and add/edit form for the Student Result Management System.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import Student, Marks
from utils import THEME, FONTS, validate_marks, validate_student_fields, StyledWidgets


class StudentListFrame(tk.Frame):
    def __init__(self, parent, db, app, **kwargs):
        super().__init__(parent, bg=THEME["bg"], **kwargs)
        self.db = db
        self.app = app
        self._build_ui()

    def _build_ui(self):
        # ── Header ────────────────────────────────────────────────
        header = tk.Frame(self, bg=THEME["bg"])
        header.pack(fill="x", padx=40, pady=(40, 20))

        tk.Label(
            header, text="Student Directory", font=FONTS["heading"],
            bg=THEME["bg"], fg=THEME["text"],
        ).pack(side="left")

        StyledWidgets.create_button(
            header, "Add New Student", icon="➕",
            command=self._on_add_student
        ).pack(side="right")

        # ── Toolbar ───────────────────────────────────────────────
        toolbar, toolbar_inner = StyledWidgets.create_card(self)
        toolbar.pack(fill="x", padx=40, pady=(0, 20))

        # We want less padding for the toolbar card
        toolbar_inner.pack_configure(pady=(12, 12))

        tk.Label(
            toolbar_inner, text="🔍", font=("Segoe UI", 14),
            bg=THEME["bg_card"], fg=THEME["text_secondary"],
        ).pack(side="left", padx=(0, 10))

        self.search_entry, self.search_var = StyledWidgets.create_entry(
            toolbar_inner, placeholder="Search students by name or roll number...", width=50
        )
        self.search_entry.pack(side="left", ipady=6, fill="x", expand=True)

        clear_btn = StyledWidgets.create_button(toolbar_inner, "Clear", bg=THEME["bg_elevated"], fg=THEME["text_secondary"], command=self._clear_search)
        clear_btn.pack(side="left", padx=10)

        self.count_label = StyledWidgets.create_badge(toolbar_inner, "0 Students", THEME["bg_elevated"], THEME["text_secondary"])
        self.count_label.pack(side="right", padx=(15, 0))

        # ── Data Table ────────────────────────────────────────────
        table_container, inner = StyledWidgets.create_card(self)
        table_container.pack(fill="both", expand=True, padx=40, pady=(0, 30))
        
        # Remove inner padding for flush table
        inner.pack_configure(padx=0, pady=0)

        cols = ("id", "roll", "name", "email", "class", "total", "pct", "grade")
        self.tree = ttk.Treeview(inner, columns=cols, show="headings", style="Custom.Treeview")

        headings = {"id": "ID", "roll": "Roll No", "name": "Name", "email": "Email", "class": "Class", "total": "Total", "pct": "%", "grade": "Grade"}
        widths = {"id": 60, "roll": 110, "name": 220, "email": 220, "class": 100, "total": 80, "pct": 80, "grade": 80}

        for col in cols:
            self.tree.heading(col, text=headings[col])
            anchor = "w" if col in ("name", "email") else "center"
            self.tree.column(col, width=widths[col], anchor=anchor)

        tree_scroll = ttk.Scrollbar(inner, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", self._on_edit_student)

        # ── Action Bar ────────────────────────────────────────────
        actions_frame = tk.Frame(self, bg=THEME["bg"])
        actions_frame.pack(fill="x", padx=40, pady=(0, 40))

        StyledWidgets.create_button(actions_frame, "Edit", bg=THEME["bg_elevated"], fg=THEME["text"], icon="✏️", command=self._on_edit_student).pack(side="left", padx=(0, 10))
        StyledWidgets.create_button(actions_frame, "Delete", bg=THEME["danger_muted"], fg=THEME["danger"], icon="🗑️", command=self._on_delete_student).pack(side="left", padx=(0, 10))
        
        # Spacer
        tk.Frame(actions_frame, bg=THEME["bg"]).pack(side="left", fill="x", expand=True)
        
        StyledWidgets.create_button(actions_frame, "Export PDF", bg=THEME["accent_muted"], fg=THEME["text_accent"], icon="📄", command=self._on_export_pdf).pack(side="right", padx=(10, 0))
        StyledWidgets.create_button(actions_frame, "View Result", bg=THEME["success_muted"], fg=THEME["success"], icon="🎓", command=self._on_view_result).pack(side="right")

        # Init
        self._load_students()
        self.search_var.trace_add("write", self._on_search)

    def _load_students(self, query: str = None):
        self.tree.delete(*self.tree.get_children())
        students = self.db.search_students(query) if query else self.db.get_all_students()

        for s in students:
            m = self.db.get_marks(s.id)
            total = f"{m.total:.0f}" if m else "–"
            pct = f"{m.percentage:.1f}%" if m else "–"
            grade = m.grade if m else "–"
            tag = ("pass",) if m and m.status == "PASS" else ("fail",) if m else ()
            self.tree.insert("", "end", iid=str(s.id), values=(s.id, s.roll_number, s.name, s.email or "–", s.class_name or "–", total, pct, grade), tags=tag)

        self.tree.tag_configure("pass", foreground=THEME["text"])
        self.tree.tag_configure("fail", foreground=THEME["danger"])
        self.count_label.config(text=f"  {len(students)} Students  ")

    def _on_search(self, *args):
        query = self.search_var.get().strip()
        if "Search" in query: query = ""
        self._load_students(query if query else None)

    def _clear_search(self):
        self.search_var.set("")
        self._load_students()

    def _get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Notice", "Please select a student.", parent=self)
            return None
        return int(sel[0])

    def _on_add_student(self): self.app.show_frame(StudentFormFrame)
    def _on_edit_student(self, e=None):
        sid = self._get_selected()
        if sid: self.app.show_frame(StudentFormFrame, student_id=sid)

    def _on_delete_student(self):
        sid = self._get_selected()
        if not sid:
            return
        student = self.db.get_student_by_id(sid)
        if messagebox.askyesno("Confirm Delete", f"Delete student '{student.name}'?\n\nThis action cannot be undone.", parent=self):
            try:
                self.db.delete_student(sid)
                messagebox.showinfo("Success", "Student deleted successfully.", parent=self)
                self._load_students()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete student:\n{str(e)}", parent=self)

    def _on_view_result(self):
        sid = self._get_selected()
        if sid:
            from gui.results import ResultsFrame
            self.app.show_frame(ResultsFrame, student_id=sid)

    def _on_export_pdf(self):
        sid = self._get_selected()
        if not sid:
            return
        s = self.db.get_student_by_id(sid)
        m = self.db.get_marks(sid)
        if not m:
            messagebox.showwarning("No Marks", "No marks found for this student. Add marks to generate a report.", parent=self)
            return
        try:
            from utils import export_to_pdf
            rank = next((r for st, _, r in self.db.get_ranked_students() if st.id == sid), None)
            path = export_to_pdf(s, m, rank=rank)
            messagebox.showinfo("Success", f"Report exported successfully!\n\n{path}", parent=self)
        except ImportError:
            messagebox.showerror("Missing Dependency", "fpdf2 is required for PDF export.\n\nRun: pip install fpdf2", parent=self)
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report:\n{str(e)}", parent=self)


class StudentFormFrame(tk.Frame):
    SUBJECTS = ["Mathematics", "Science", "English", "History", "Computer Science"]

    def __init__(self, parent, db, app, student_id=None, **kwargs):
        super().__init__(parent, bg=THEME["bg"], **kwargs)
        self.db = db
        self.app = app
        self.student_id = student_id
        self.editing = student_id is not None
        
        self.student = self.db.get_student_by_id(student_id) if self.editing else None
        self.marks = self.db.get_marks(student_id) if self.editing else None

        self._build_ui()

    def _build_ui(self):
        # ── Header ────────────────────────────────────────────────
        header = tk.Frame(self, bg=THEME["bg"])
        header.pack(fill="x", padx=40, pady=(40, 20))

        tk.Label(
            header, text="Edit Record" if self.editing else "New Student Registration",
            font=FONTS["heading"], bg=THEME["bg"], fg=THEME["text"],
        ).pack(side="left")

        StyledWidgets.create_outline_button(
            header, "Back to List", color=THEME["text_secondary"], icon="←",
            command=lambda: self.app.show_frame(StudentListFrame)
        ).pack(side="right")

        # ── Form Layout ───────────────────────────────────────────
        content = tk.Frame(self, bg=THEME["bg"])
        content.pack(fill="both", expand=True, padx=35)
        content.columnconfigure(0, weight=1, uniform="c")
        content.columnconfigure(1, weight=1, uniform="c")

        # Left Column
        left_card, left_inner = StyledWidgets.create_card(content, title="Personal Details", title_icon="👤", accent_color=THEME["accent"])
        left_card.grid(row=0, column=0, padx=5, sticky="nsew")
        
        fields = [("Roll Number *", "roll"), ("Full Name *", "name"), ("Email Address", "email"), ("Phone Number", "phone"), ("Class / Section", "class")]
        self.entries = {}
        for lbl, key in fields:
            f = tk.Frame(left_inner, bg=THEME["bg_card"])
            f.pack(fill="x", pady=(0, 15))
            tk.Label(f, text=lbl, font=FONTS["small_bold"], bg=THEME["bg_card"], fg=THEME["text_secondary"]).pack(anchor="w", pady=(0, 4))
            entry, _ = StyledWidgets.create_entry(f)
            entry.pack(fill="x", ipady=5)
            self.entries[key] = entry

        if self.editing:
            self.entries["roll"].insert(0, self.student.roll_number)
            self.entries["name"].insert(0, self.student.name)
            self.entries["email"].insert(0, self.student.email)
            self.entries["phone"].insert(0, self.student.phone)
            self.entries["class"].insert(0, self.student.class_name)

        # Right Column
        right_card, right_inner = StyledWidgets.create_card(content, title="Academic Marks", title_icon="📝")
        right_card.grid(row=0, column=1, padx=5, sticky="nsew")

        self.mark_entries = {}
        for i, sub in enumerate(self.SUBJECTS):
            f = tk.Frame(right_inner, bg=THEME["bg_card"])
            f.pack(fill="x", pady=8)
            tk.Label(f, text=sub, font=FONTS["body_bold"], bg=THEME["bg_card"], fg=THEME["text"], width=16, anchor="w").pack(side="left")
            entry, _ = StyledWidgets.create_entry(f, width=10)
            entry.pack(side="left", ipady=4, padx=10)
            entry.insert(0, str(getattr(self.marks, f"subject{i+1}")) if self.editing and self.marks else "0")
            entry.bind("<KeyRelease>", self._update_preview)
            tk.Label(f, text="/ 100", font=FONTS["small"], bg=THEME["bg_card"], fg=THEME["text_dim"]).pack(side="left")
            self.mark_entries[f"s{i}"] = entry

        # Preview Banner
        self.preview = tk.Frame(right_inner, bg=THEME["bg_elevated"])
        self.preview.pack(fill="x", pady=(20, 0))
        self.p_lbl = tk.Label(self.preview, text="", font=FONTS["body_bold"], bg=THEME["bg_elevated"], fg=THEME["accent_light"])
        self.p_lbl.pack(pady=15)
        self._update_preview()

        # ── Action Buttons ────────────────────────────────────────
        bot = tk.Frame(self, bg=THEME["bg"])
        bot.pack(fill="x", padx=40, pady=30)

        StyledWidgets.create_button(
            bot, "Reset Form", bg=THEME["bg_elevated"], fg=THEME["text"],
            icon="🔄", command=self._on_reset
        ).pack(side="left", padx=(0, 10))

        tk.Frame(bot, bg=THEME["bg"]).pack(side="left", fill="x", expand=True)

        StyledWidgets.create_button(
            bot, "Save Student Record", icon="💾", padx=30, pady=10,
            command=self._on_save
        ).pack(side="right")

    def _update_preview(self, e=None):
        total = 0
        for entry in self.mark_entries.values():
            try:
                val = float(entry.get()) if entry.get().strip() else 0
                if 0 <= val <= 100:
                    total += val
            except (ValueError, AttributeError):
                pass
        pct = (total / 500) * 100
        g = "A+" if pct>=90 else "A" if pct>=80 else "B+" if pct>=70 else "B" if pct>=60 else "C" if pct>=50 else "D" if pct>=40 else "F"
        self.p_lbl.config(text=f"Score: {total:.0f}/500    •    Percentage: {pct:.1f}%    •    Grade: {g}")

    def _on_reset(self):
        if self.editing:
            self.entries["roll"].delete(0, "end")
            self.entries["roll"].insert(0, self.student.roll_number)
            self.entries["name"].delete(0, "end")
            self.entries["name"].insert(0, self.student.name)
            self.entries["email"].delete(0, "end")
            self.entries["email"].insert(0, self.student.email)
            self.entries["phone"].delete(0, "end")
            self.entries["phone"].insert(0, self.student.phone)
            self.entries["class"].delete(0, "end")
            self.entries["class"].insert(0, self.student.class_name)
            for i in range(5):
                self.mark_entries[f"s{i}"].delete(0, "end")
                self.mark_entries[f"s{i}"].insert(0, str(getattr(self.marks, f"subject{i+1}")) if self.marks else "0")
        else:
            for entry in self.entries.values():
                entry.delete(0, "end")
            for entry in self.mark_entries.values():
                entry.delete(0, "end")
                entry.insert(0, "0")
        self._update_preview()

    def _on_save(self):
        try:
            roll, name = self.entries["roll"].get().strip(), self.entries["name"].get().strip()
            validate_student_fields(roll, name)

            marks_vals = []
            for i in range(5):
                try:
                    val = float(self.mark_entries[f"s{i}"].get().strip())
                    marks_vals.append(validate_marks(str(val)))
                except ValueError:
                    raise ValueError(f"Invalid marks for subject {i+1}")

            if self.editing:
                self.db.update_student(Student(self.student_id, roll, name, self.entries["email"].get(), self.entries["phone"].get(), self.entries["class"].get()))
                m = Marks(self.student_id, *marks_vals)
                if self.db.get_marks(self.student_id):
                    self.db.update_marks(m)
                else:
                    self.db.add_marks(m)
                messagebox.showinfo("Success", "Student record updated successfully!", parent=self)
            else:
                sid = self.db.add_student(Student(roll, name, self.entries["email"].get(), self.entries["phone"].get(), self.entries["class"].get()))
                self.db.add_marks(Marks(sid, *marks_vals))
                messagebox.showinfo("Success", "New student added successfully!", parent=self)

            self.app.show_frame(StudentListFrame)
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e), parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}", parent=self)
