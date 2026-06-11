"""
main.py - Entry point for the Student Result Management System.
Sets up the Tkinter root window, configures the dark theme, creates the sidebar
navigation, and manages frame-switching.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Ensure the project root is on sys.path so modules can import each other
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database
from utils import THEME, FONTS, export_to_csv, export_all_to_pdf, StyledWidgets
from gui.dashboard import DashboardFrame
from gui.student_form import StudentListFrame, StudentFormFrame
from gui.results import ResultsFrame


class App(tk.Tk):
    """
    Main application window.
    """
    SIDEBAR_WIDTH = 260

    def __init__(self):
        super().__init__()

        # ── Window Configuration ──────────────────────────────────
        self.title("Student Result Management System")
        self.geometry("1280x800")
        self.minsize(1050, 650)
        self.configure(bg=THEME["bg"])

        try:
            self.db = Database()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to initialize database:\n{str(e)}")
            self.destroy()
            return

        self._configure_styles()

        # Main layout container
        self.main_container = tk.Frame(self, bg=THEME["bg"])
        self.main_container.pack(fill="both", expand=True)

        self._create_sidebar()
        self._create_content_area()

        self.current_frame = None
        self.active_nav = None

        # Start app
        self.show_frame(DashboardFrame)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _configure_styles(self):
        """Configure ttk styles for the premium dark theme."""
        style = ttk.Style(self)
        style.theme_use("clam")

        # Base elements
        style.configure(".", background=THEME["bg"], foreground=THEME["text"], font=FONTS["body"])

        # Treeview (Tables)
        style.configure("Custom.Treeview",
            background=THEME["bg_card"],
            foreground=THEME["text"],
            fieldbackground=THEME["bg_card"],
            borderwidth=0,
            font=FONTS["treeview"],
            rowheight=38,
        )
        style.configure("Custom.Treeview.Heading",
            background=THEME["bg_secondary"],
            foreground=THEME["text_secondary"],
            font=FONTS["treeview_head"],
            borderwidth=0,
            relief="flat",
            padding=(0, 10),
        )
        style.map("Custom.Treeview",
            background=[("selected", THEME["accent_muted"])],
            foreground=[("selected", THEME["text"])],
        )
        style.map("Custom.Treeview.Heading",
            background=[("active", THEME["hover"])],
            foreground=[("active", THEME["text"])],
        )
        
        # Dashboard Treeview
        style.configure("Dashboard.Treeview",
            background=THEME["bg_card"],
            foreground=THEME["text"],
            fieldbackground=THEME["bg_card"],
            borderwidth=0,
            font=FONTS["treeview"],
            rowheight=34,
        )
        style.configure("Dashboard.Treeview.Heading",
            background=THEME["bg_secondary"],
            foreground=THEME["text_secondary"],
            font=FONTS["treeview_head"],
            borderwidth=0,
            relief="flat",
            padding=(0, 8),
        )
        style.map("Dashboard.Treeview",
            background=[("selected", THEME["accent_muted"])],
            foreground=[("selected", THEME["text"])],
        )

        # Scrollbar (Sleeker)
        style.configure("Vertical.TScrollbar",
            background=THEME["scrollbar"],
            troughcolor=THEME["bg_card"],
            borderwidth=0,
            arrowsize=0,
            width=10,
        )
        style.map("Vertical.TScrollbar",
            background=[("active", THEME["scrollbar_hover"])],
        )

        # Combobox
        style.configure("TCombobox",
            fieldbackground=THEME["input_bg"],
            background=THEME["scrollbar"],
            foreground=THEME["text"],
            borderwidth=0,
            arrowsize=14,
        )
        style.map("TCombobox",
            fieldbackground=[("readonly", THEME["input_bg"]), ("focus", THEME["input_focus"])],
            foreground=[("readonly", THEME["text"])],
        )
        self.option_add("*TCombobox*Listbox.background", THEME["bg_elevated"])
        self.option_add("*TCombobox*Listbox.foreground", THEME["text"])
        self.option_add("*TCombobox*Listbox.selectBackground", THEME["accent"])
        self.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
        self.option_add("*TCombobox*Listbox.font", FONTS["entry"])
        self.option_add("*TCombobox*Listbox.borderwidth", "0")
        self.option_add("*TCombobox*Listbox.relief", "flat")

    def _create_sidebar(self):
        """Build the stylish left sidebar."""
        self.sidebar = tk.Frame(self.main_container, bg=THEME["sidebar"], width=self.SIDEBAR_WIDTH)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # ── Logo Area ─────────────────────────────────────────────
        logo_frame = tk.Frame(self.sidebar, bg=THEME["sidebar"])
        logo_frame.pack(fill="x", padx=25, pady=(35, 25))

        # Modern logo layout (icon + text side by side)
        icon_lbl = tk.Label(logo_frame, text="✨", font=("Segoe UI", 24), 
                           bg=THEME["sidebar"], fg=THEME["accent"])
        icon_lbl.pack(side="left", padx=(0, 12))
        
        text_frame = tk.Frame(logo_frame, bg=THEME["sidebar"])
        text_frame.pack(side="left", fill="x")
        
        tk.Label(text_frame, text="Antigravity", font=FONTS["logo"],
                bg=THEME["sidebar"], fg=THEME["text"]).pack(anchor="w")
        tk.Label(text_frame, text="Academy", font=FONTS["logo_sub"],
                bg=THEME["sidebar"], fg=THEME["accent_light"]).pack(anchor="w", pady=(0, 0))

        # ── Navigation Buttons ────────────────────────────────────
        self.nav_buttons = {}
        nav_container = tk.Frame(self.sidebar, bg=THEME["sidebar"])
        nav_container.pack(fill="x", pady=10)

        nav_items = [
            ("📊", "Dashboard", DashboardFrame, "dashboard"),
            ("👥", "Students", StudentListFrame, "students"),
            ("✨", "Add Student", StudentFormFrame, "add_student"),
            ("🎓", "Results", ResultsFrame, "results"),
        ]

        for icon, text, frame_class, key in nav_items:
            # We use a custom frame for each nav item to allow for an active indicator strip
            item_frame = tk.Frame(nav_container, bg=THEME["sidebar"], height=48)
            item_frame.pack(fill="x", padx=12, pady=4)
            item_frame.pack_propagate(False)
            
            # Active indicator (hidden by default)
            indicator = tk.Frame(item_frame, bg=THEME["sidebar"], width=4)
            indicator.pack(side="left", fill="y", pady=4, padx=(0, 8))
            
            # The actual button
            btn = tk.Button(
                item_frame, text=f"{icon}   {text}", font=FONTS["sidebar"],
                bg=THEME["sidebar"], fg=THEME["text_secondary"],
                activebackground=THEME["sidebar_hover"], activeforeground=THEME["text"],
                relief="flat", anchor="w", padx=15, cursor="hand2", bd=0,
                command=lambda fc=frame_class, k=key: self._on_nav_click(fc, k),
            )
            btn.pack(side="left", fill="both", expand=True)
            
            # Bind hover events to both the frame and button
            def on_enter(e, b=btn, k=key): self._on_nav_hover(b, k, True)
            def on_leave(e, b=btn, k=key): self._on_nav_hover(b, k, False)
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            
            self.nav_buttons[key] = {"btn": btn, "indicator": indicator, "frame": item_frame}

        # ── Export Section ────────────────────────────────────────
        tk.Frame(self.sidebar, bg=THEME["divider"], height=1).pack(fill="x", padx=25, pady=25)

        tk.Label(
            self.sidebar, text="ACTIONS", font=("Segoe UI", 8, "bold"),
            bg=THEME["sidebar"], fg=THEME["text_dim"],
        ).pack(anchor="w", padx=30, pady=(0, 10))

        export_items = [
            ("⬇️   Export CSV Data", self._export_csv),
            ("🖨️   Generate Reports", self._export_all_pdfs),
        ]
        
        for text, command in export_items:
            btn = tk.Button(
                self.sidebar, text=text, font=FONTS["small"],
                bg=THEME["sidebar"], fg=THEME["text_secondary"],
                activebackground=THEME["sidebar_hover"], activeforeground=THEME["text"],
                relief="flat", anchor="w", padx=30, pady=8,
                cursor="hand2", bd=0, command=command,
            )
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=THEME["sidebar_hover"], fg=THEME["text"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=THEME["sidebar"], fg=THEME["text_secondary"]))

        # ── Bottom Profile/Status ─────────────────────────────────
        bottom = tk.Frame(self.sidebar, bg=THEME["sidebar"])
        bottom.pack(side="bottom", fill="x", pady=25)
        
        StyledWidgets.create_divider(bottom).pack(fill="x", padx=25, pady=(0, 20))
        
        tk.Label(
            bottom, text="Database: Connected", font=FONTS["tiny"],
            bg=THEME["sidebar"], fg=THEME["success"],
        ).pack()

    def _on_nav_click(self, frame_class, key):
        self.show_frame(frame_class)

    def _on_nav_hover(self, button, key, entering):
        if key == self.active_nav:
            return
        if entering:
            button.config(bg=THEME["sidebar_hover"], fg=THEME["text"])
        else:
            button.config(bg=THEME["sidebar"], fg=THEME["text_secondary"])

    def _update_nav_active(self, frame_class):
        nav_map = {
            DashboardFrame: "dashboard",
            StudentListFrame: "students",
            StudentFormFrame: "add_student",
            ResultsFrame: "results",
        }
        new_active = nav_map.get(frame_class)

        for key, elements in self.nav_buttons.items():
            btn = elements["btn"]
            indicator = elements["indicator"]
            frame = elements["frame"]
            
            if key == new_active:
                btn.config(bg=THEME["accent_muted"], fg=THEME["text_accent"], font=FONTS["sidebar_active"])
                frame.config(bg=THEME["accent_muted"])
                indicator.config(bg=THEME["accent"])
            else:
                btn.config(bg=THEME["sidebar"], fg=THEME["text_secondary"], font=FONTS["sidebar"])
                frame.config(bg=THEME["sidebar"])
                indicator.config(bg=THEME["sidebar"])

        self.active_nav = new_active

    def _create_content_area(self):
        self.content = tk.Frame(self.main_container, bg=THEME["bg"])
        self.content.pack(side="right", fill="both", expand=True)

    def show_frame(self, frame_class, **kwargs):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_class(self.content, self.db, self, **kwargs)
        self.current_frame.pack(fill="both", expand=True)
        self._update_nav_active(frame_class)

    def _export_csv(self):
        ranked = self.db.get_ranked_students()
        if not ranked:
            messagebox.showwarning("No Data", "No student data to export. Add students with marks first.", parent=self)
            return
        try:
            path = export_to_csv(ranked)
            messagebox.showinfo("Success", f"Data exported successfully!\n\n{path}", parent=self)
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV:\n{str(e)}", parent=self)

    def _export_all_pdfs(self):
        ranked = self.db.get_ranked_students()
        if not ranked:
            messagebox.showwarning("No Data", "No student data to export. Add students with marks first.", parent=self)
            return
        try:
            path = export_all_to_pdf(ranked)
            messagebox.showinfo("Success", f"Reports generated successfully!\n\n{path}", parent=self)
        except ImportError:
            messagebox.showerror("Missing Dependency", "fpdf2 is required for PDF export.\n\nRun: pip install fpdf2", parent=self)
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to generate reports:\n{str(e)}", parent=self)

    def _on_close(self):
        try:
            self.db.close()
        except Exception:
            pass
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
