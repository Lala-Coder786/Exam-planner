"""
main.py
-------
This is the main application window that opens after a successful login.
It has a sidebar on the left for navigation and a content area on the
right that changes based on which menu item is clicked.

Run this project by starting login.py (not this file directly), because
this file expects a logged-in "user" dictionary to be passed in.
"""

import tkinter as tk
from tkinter import messagebox
import database
import utils
from dashboard import DashboardFrame
from subject import SubjectFrame
from exam import ExamFrame
from planner import PlannerFrame
from progress import ProgressFrame
from reports import ReportsFrame


class MainApplication:
    def __init__(self, root, user):
        self.root = root
        self.user = user  # dictionary with user_id, username, full_name
        self.root.title("Exam Preparation Planner")
        self.root.geometry("1100x650")
        self.root.minsize(950, 600)
        self.root.configure(bg=utils.BG_COLOR)

        self.frames = {}  # cache of already built screens
        self.nav_buttons = {}

        self.build_sidebar()
        self.build_content_area()
        self.show_frame("Dashboard")

    # ---------------- SIDEBAR ----------------
    def build_sidebar(self):
        sidebar = tk.Frame(self.root, bg=utils.SIDEBAR_COLOR, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="📘 Exam Planner", font=("Segoe UI", 14, "bold"),
                 bg=utils.SIDEBAR_COLOR, fg=utils.WHITE).pack(pady=(25, 5))
        tk.Label(sidebar, text=f"Hi, {self.user['full_name']}", font=utils.FONT_NORMAL,
                 bg=utils.SIDEBAR_COLOR, fg="#dfe6e9").pack(pady=(0, 20))

        menu_items = [
            ("🏠  Dashboard", "Dashboard"),
            ("📚  Subjects", "Subjects"),
            ("📝  Exams", "Exams"),
            ("🗓️  Study Planner", "Planner"),
            ("📊  Progress Tracker", "Progress"),
            ("📄  Reports", "Reports"),
        ]

        for label, key in menu_items:
            btn = tk.Button(sidebar, text=label, font=utils.FONT_NORMAL, bg=utils.SIDEBAR_COLOR, fg=utils.WHITE,
                             activebackground=utils.SIDEBAR_HOVER, activeforeground=utils.WHITE,
                             bd=0, anchor="w", padx=25, pady=12, cursor="hand2",
                             command=lambda k=key: self.show_frame(k))
            btn.pack(fill="x")
            self.nav_buttons[key] = btn

        tk.Frame(sidebar, bg=utils.SIDEBAR_HOVER, height=1).pack(fill="x", pady=15)

        logout_btn = tk.Button(sidebar, text="🚪  Logout", font=utils.FONT_NORMAL, bg=utils.SIDEBAR_COLOR,
                                fg="#ff7675", activebackground=utils.SIDEBAR_HOVER, bd=0, anchor="w",
                                padx=25, pady=12, cursor="hand2", command=self.logout)
        logout_btn.pack(fill="x", side="bottom", pady=10)

    def highlight_nav(self, active_key):
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.config(bg=utils.ACCENT_COLOR)
            else:
                btn.config(bg=utils.SIDEBAR_COLOR)

    # ---------------- CONTENT AREA ----------------
    def build_content_area(self):
        self.content_area = tk.Frame(self.root, bg=utils.BG_COLOR)
        self.content_area.pack(side="right", fill="both", expand=True)

    def show_frame(self, key):
        # hide all existing frames
        for frame in self.frames.values():
            frame.pack_forget()

        if key not in self.frames:
            self.frames[key] = self.build_frame(key)

        frame = self.frames[key]
        frame.pack(fill="both", expand=True)

        # refresh data every time a tab is opened, so numbers are always up to date
        if hasattr(frame, "refresh"):
            frame.refresh()
        elif hasattr(frame, "load_subjects"):
            frame.load_subjects()
        elif hasattr(frame, "load_exams"):
            frame.load_exams()
        elif hasattr(frame, "load_plans"):
            frame.load_plans()

        self.highlight_nav(key)

    def build_frame(self, key):
        """Creates the screen only once, the first time it is opened."""
        if key == "Dashboard":
            return DashboardFrame(self.content_area, self.user)
        elif key == "Subjects":
            return SubjectFrame(self.content_area, self.user, on_change=self.notify_dashboard)
        elif key == "Exams":
            return ExamFrame(self.content_area, self.user, on_change=self.notify_dashboard)
        elif key == "Planner":
            return PlannerFrame(self.content_area, self.user, on_change=self.notify_dashboard)
        elif key == "Progress":
            return ProgressFrame(self.content_area, self.user)
        elif key == "Reports":
            return ReportsFrame(self.content_area, self.user)

    def notify_dashboard(self):
        """Called by other modules after add/edit/delete so dashboard + progress
        numbers reflect the latest changes next time they are opened."""
        if "Dashboard" in self.frames:
            self.frames["Dashboard"].refresh()
        if "Progress" in self.frames:
            self.frames["Progress"].refresh()

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            import login
            new_root = tk.Tk()
            login.LoginWindow(new_root)
            new_root.mainloop()


if __name__ == "__main__":
    # allow running main.py directly for quick testing with the demo account
    database.create_tables()
    database.seed_sample_data()
    conn = database.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username='student'")
    demo_user = dict(cur.fetchone())
    conn.close()

    root = tk.Tk()
    MainApplication(root, demo_user)
    root.mainloop()
