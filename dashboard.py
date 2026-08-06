"""
dashboard.py
------------
Shows the home screen after login:
 - Total Subjects
 - Upcoming Exams count
 - Today's Study Plan
 - Completed Topics
 - Overall Progress
"""

import tkinter as tk
from tkinter import ttk
from datetime import date
import database
import utils


class DashboardFrame(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=utils.BG_COLOR)
        self.user = user
        self.build_ui()
        self.refresh()

    def build_ui(self):
        tk.Label(self, text="Dashboard", font=utils.FONT_TITLE, bg=utils.BG_COLOR,
                 fg=utils.TEXT_COLOR).pack(anchor="w", padx=25, pady=(20, 10))

        # ---- Stat cards row ----
        self.cards_frame = tk.Frame(self, bg=utils.BG_COLOR)
        self.cards_frame.pack(fill="x", padx=20)

        self.card_subjects = self.make_card(self.cards_frame, "Total Subjects", "0", "#2e86de")
        self.card_exams = self.make_card(self.cards_frame, "Upcoming Exams", "0", "#e17055")
        self.card_completed = self.make_card(self.cards_frame, "Completed Topics", "0", "#00b894")
        self.card_progress = self.make_card(self.cards_frame, "Overall Progress", "0%", "#6c5ce7")

        # ---- Today's plan + upcoming exams (two columns) ----
        bottom = tk.Frame(self, bg=utils.BG_COLOR)
        bottom.pack(fill="both", expand=True, padx=20, pady=15)

        left = tk.LabelFrame(bottom, text=" Today's Study Plan ", font=utils.FONT_BOLD,
                              bg=utils.WHITE, fg=utils.TEXT_COLOR, bd=1, relief="solid")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.today_list = ttk.Treeview(left, columns=("subject", "topic", "hours", "status"),
                                        show="headings", height=8)
        for col, text, w in [("subject", "Subject", 120), ("topic", "Topic", 160),
                              ("hours", "Hours", 60), ("status", "Status", 90)]:
            self.today_list.heading(col, text=text)
            self.today_list.column(col, width=w, anchor="center")
        self.today_list.pack(fill="both", expand=True, padx=8, pady=8)

        right = tk.LabelFrame(bottom, text=" Upcoming Exams ", font=utils.FONT_BOLD,
                               bg=utils.WHITE, fg=utils.TEXT_COLOR, bd=1, relief="solid")
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))

        self.exam_list = ttk.Treeview(right, columns=("subject", "exam", "date"),
                                       show="headings", height=8)
        for col, text, w in [("subject", "Subject", 110), ("exam", "Exam", 150), ("date", "Date", 100)]:
            self.exam_list.heading(col, text=text)
            self.exam_list.column(col, width=w, anchor="center")
        self.exam_list.pack(fill="both", expand=True, padx=8, pady=8)

    def make_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg=color, width=200, height=90)
        card.pack(side="left", expand=True, fill="both", padx=8, pady=5)
        card.pack_propagate(False)
        value_lbl = tk.Label(card, text=value, font=("Segoe UI", 22, "bold"), bg=color, fg=utils.WHITE)
        value_lbl.pack(pady=(15, 0))
        tk.Label(card, text=title, font=utils.FONT_NORMAL, bg=color, fg=utils.WHITE).pack()
        card.value_label = value_lbl
        return card

    def refresh(self):
        """Re-reads the database and updates all numbers on screen.
        Called every time this tab is opened so the numbers are always fresh."""
        conn = database.get_connection()
        cur = conn.cursor()
        uid = self.user["user_id"]

        cur.execute("SELECT COUNT(*) FROM subjects WHERE user_id=?", (uid,))
        total_subjects = cur.fetchone()[0]

        today = date.today().isoformat()
        cur.execute("SELECT COUNT(*) FROM exams WHERE user_id=? AND exam_date >= ?", (uid, today))
        upcoming_exams = cur.fetchone()[0]

        cur.execute("SELECT COALESCE(SUM(completed_topics),0), COALESCE(SUM(total_topics),0) FROM progress WHERE user_id=?", (uid,))
        completed, total = cur.fetchone()
        overall = int((completed / total) * 100) if total else 0

        self.card_subjects.value_label.config(text=str(total_subjects))
        self.card_exams.value_label.config(text=str(upcoming_exams))
        self.card_completed.value_label.config(text=str(completed))
        self.card_progress.value_label.config(text=f"{overall}%")

        # Today's plan
        for row in self.today_list.get_children():
            self.today_list.delete(row)
        cur.execute("""SELECT s.subject_name, p.topic_name, p.study_hours, p.is_completed
                       FROM study_plans p JOIN subjects s ON p.subject_id = s.subject_id
                       WHERE p.user_id=? AND p.plan_date=? ORDER BY p.plan_id""", (uid, today))
        for r in cur.fetchall():
            status = "Completed" if r["is_completed"] else "Pending"
            self.today_list.insert("", "end", values=(r["subject_name"], r["topic_name"], r["study_hours"], status))

        # Upcoming exams (top 8, sorted by date)
        for row in self.exam_list.get_children():
            self.exam_list.delete(row)
        cur.execute("""SELECT s.subject_name, e.exam_name, e.exam_date
                       FROM exams e JOIN subjects s ON e.subject_id = s.subject_id
                       WHERE e.user_id=? AND e.exam_date >= ?
                       ORDER BY e.exam_date ASC LIMIT 8""", (uid, today))
        for r in cur.fetchall():
            self.exam_list.insert("", "end", values=(r["subject_name"], r["exam_name"], r["exam_date"]))

        conn.close()
