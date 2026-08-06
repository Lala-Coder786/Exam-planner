"""
progress.py
-----------
Progress Tracker screen.
Shows subject-wise progress bars, overall progress, completion percentage
and remaining topics. Uses plain tkinter Canvas to draw progress bars
(no external chart library needed - keeps the project simple).
"""

import tkinter as tk
import database
import utils


class ProgressFrame(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=utils.BG_COLOR)
        self.user = user
        self.build_ui()
        self.refresh()

    def build_ui(self):
        tk.Label(self, text="Progress Tracker", font=utils.FONT_TITLE, bg=utils.BG_COLOR,
                 fg=utils.TEXT_COLOR).pack(anchor="w", padx=25, pady=(20, 10))

        # overall progress summary
        self.overall_frame = tk.LabelFrame(self, text=" Overall Progress ", font=utils.FONT_BOLD,
                                            bg=utils.WHITE, bd=1, relief="solid")
        self.overall_frame.pack(fill="x", padx=20, pady=5)

        self.overall_canvas = tk.Canvas(self.overall_frame, height=35, bg=utils.WHITE, highlightthickness=0)
        self.overall_canvas.pack(fill="x", padx=15, pady=10)

        self.overall_label = tk.Label(self.overall_frame, text="", font=utils.FONT_NORMAL, bg=utils.WHITE)
        self.overall_label.pack(anchor="w", padx=15, pady=(0, 10))

        # subject wise progress
        self.subject_frame = tk.LabelFrame(self, text=" Subject-wise Progress ", font=utils.FONT_BOLD,
                                            bg=utils.WHITE, bd=1, relief="solid")
        self.subject_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # scrollable canvas in case of many subjects
        self.canvas_container = tk.Canvas(self.subject_frame, bg=utils.WHITE, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.subject_frame, orient="vertical", command=self.canvas_container.yview)
        self.inner_frame = tk.Frame(self.canvas_container, bg=utils.WHITE)

        self.inner_frame.bind("<Configure>", lambda e: self.canvas_container.configure(
            scrollregion=self.canvas_container.bbox("all")))
        self.canvas_container.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.canvas_container.configure(yscrollcommand=self.scrollbar.set)

        self.canvas_container.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.scrollbar.pack(side="right", fill="y")

    def draw_bar(self, canvas, percent, width=760, height=22, color="#2e86de"):
        canvas.delete("all")
        canvas.config(width=width, height=height)
        canvas.create_rectangle(0, 0, width, height, fill="#dfe6e9", outline="")
        fill_width = int((percent / 100) * width)
        canvas.create_rectangle(0, 0, fill_width, height, fill=color, outline="")
        canvas.create_text(width // 2, height // 2, text=f"{percent}%", font=utils.FONT_BOLD,
                            fill=utils.TEXT_COLOR if percent < 50 else utils.WHITE)

    def refresh(self):
        """Reloads all progress bars from the database. Call whenever this tab opens."""
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        conn = database.get_connection()
        cur = conn.cursor()
        cur.execute("""SELECT s.subject_name, p.completed_topics, p.total_topics
                       FROM subjects s LEFT JOIN progress p ON s.subject_id = p.subject_id
                       WHERE s.user_id=? ORDER BY s.subject_name""", (self.user["user_id"],))
        rows = cur.fetchall()
        conn.close()

        total_completed = sum(r["completed_topics"] or 0 for r in rows)
        total_topics = sum(r["total_topics"] or 0 for r in rows)
        overall_percent = int((total_completed / total_topics) * 100) if total_topics else 0

        self.draw_bar(self.overall_canvas, overall_percent, width=850, height=30, color="#6c5ce7")
        self.overall_label.config(
            text=f"Total Completed: {total_completed} / {total_topics} topics   "
                 f"|   Remaining: {max(total_topics - total_completed, 0)} topics")

        if not rows:
            tk.Label(self.inner_frame, text="No subjects added yet. Add subjects first.",
                     bg=utils.WHITE, font=utils.FONT_NORMAL, fg="#636e72").pack(pady=20)
            return

        for r in rows:
            total = r["total_topics"] or 0
            completed = r["completed_topics"] or 0
            percent = int((completed / total) * 100) if total else 0
            remaining = max(total - completed, 0)

            row_frame = tk.Frame(self.inner_frame, bg=utils.WHITE)
            row_frame.pack(fill="x", pady=8, padx=5)

            tk.Label(row_frame, text=r["subject_name"], font=utils.FONT_BOLD, bg=utils.WHITE,
                     width=22, anchor="w").pack(side="left")

            bar_canvas = tk.Canvas(row_frame, bg=utils.WHITE, highlightthickness=0)
            bar_canvas.pack(side="left", padx=10)
            self.draw_bar(bar_canvas, percent, width=420, height=20)

            tk.Label(row_frame, text=f"{completed}/{total} done  |  {remaining} remaining",
                     font=utils.FONT_NORMAL, bg=utils.WHITE, fg="#636e72").pack(side="left", padx=10)
