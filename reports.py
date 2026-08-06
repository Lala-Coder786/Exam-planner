"""
reports.py
----------
Reports screen.
Generates Daily / Weekly / Monthly / Subject-wise text reports
from the study_plans and progress tables, and lets the user
export the currently shown report to a .txt file.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, timedelta
import database
import utils


class ReportsFrame(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=utils.BG_COLOR)
        self.user = user
        self.subject_map = {}
        self.build_ui()
        self.load_subject_dropdown()

    def build_ui(self):
        tk.Label(self, text="Reports", font=utils.FONT_TITLE, bg=utils.BG_COLOR,
                 fg=utils.TEXT_COLOR).pack(anchor="w", padx=25, pady=(20, 10))

        top = tk.Frame(self, bg=utils.BG_COLOR)
        top.pack(fill="x", padx=20)

        tk.Label(top, text="Report Type:", bg=utils.BG_COLOR, font=utils.FONT_NORMAL).pack(side="left")
        self.report_type = ttk.Combobox(top, width=16, state="readonly",
                                         values=["Daily", "Weekly", "Monthly", "Subject Report"])
        self.report_type.current(0)
        self.report_type.pack(side="left", padx=8)
        self.report_type.bind("<<ComboboxSelected>>", lambda e: self.toggle_subject_box())

        tk.Label(top, text="Subject:", bg=utils.BG_COLOR, font=utils.FONT_NORMAL).pack(side="left", padx=(15, 0))
        self.subject_combo = ttk.Combobox(top, width=18, state="disabled")
        self.subject_combo.pack(side="left", padx=8)

        tk.Button(top, text="Generate Report", bg=utils.ACCENT_COLOR, fg=utils.WHITE, font=utils.FONT_BTN,
                  relief="flat", width=16, command=self.generate_report).pack(side="left", padx=15)
        tk.Button(top, text="Export to .txt", bg=utils.SUCCESS_COLOR, fg=utils.WHITE, font=utils.FONT_BTN,
                  relief="flat", width=14, command=self.export_report).pack(side="left")

        # report output box
        out_frame = tk.LabelFrame(self, text=" Report Output ", font=utils.FONT_BOLD, bg=utils.WHITE, bd=1, relief="solid")
        out_frame.pack(fill="both", expand=True, padx=20, pady=15)

        self.output_text = tk.Text(out_frame, font=("Consolas", 10), wrap="word", bg="#fdfdfd")
        self.output_text.pack(fill="both", expand=True, padx=10, pady=10)

    def load_subject_dropdown(self):
        conn = database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT subject_id, subject_name FROM subjects WHERE user_id=? ORDER BY subject_name",
                    (self.user["user_id"],))
        rows = cur.fetchall()
        conn.close()
        self.subject_map = {r["subject_name"]: r["subject_id"] for r in rows}
        self.subject_combo["values"] = list(self.subject_map.keys())

    def toggle_subject_box(self):
        if self.report_type.get() == "Subject Report":
            self.subject_combo.config(state="readonly")
        else:
            self.subject_combo.set("")
            self.subject_combo.config(state="disabled")

    def generate_report(self):
        report_type = self.report_type.get()
        self.output_text.delete("1.0", tk.END)

        conn = database.get_connection()
        cur = conn.cursor()
        uid = self.user["user_id"]

        if report_type in ("Daily", "Weekly", "Monthly"):
            today = date.today()
            if report_type == "Daily":
                start = today
                title = f"DAILY REPORT - {today.isoformat()}"
            elif report_type == "Weekly":
                start = today - timedelta(days=7)
                title = f"WEEKLY REPORT - {start.isoformat()} to {today.isoformat()}"
            else:
                start = today - timedelta(days=30)
                title = f"MONTHLY REPORT - {start.isoformat()} to {today.isoformat()}"

            cur.execute("""SELECT s.subject_name, p.topic_name, p.plan_date, p.study_hours, p.is_completed
                           FROM study_plans p JOIN subjects s ON p.subject_id = s.subject_id
                           WHERE p.user_id=? AND p.plan_date BETWEEN ? AND ?
                           ORDER BY p.plan_date""", (uid, start.isoformat(), today.isoformat()))
            rows = cur.fetchall()

            lines = [title, "=" * len(title), ""]
            if not rows:
                lines.append("No study plan entries found for this period.")
            else:
                total_hours = 0
                completed_count = 0
                for r in rows:
                    status = "Done" if r["is_completed"] else "Pending"
                    lines.append(f"[{r['plan_date']}] {r['subject_name']:<20} {r['topic_name']:<25} "
                                 f"{r['study_hours']:>4} hrs   ({status})")
                    total_hours += r["study_hours"]
                    if r["is_completed"]:
                        completed_count += 1
                lines.append("")
                lines.append(f"Total entries : {len(rows)}")
                lines.append(f"Completed     : {completed_count}")
                lines.append(f"Total Hours   : {total_hours}")

        else:  # Subject Report
            subject_name = self.subject_combo.get()
            if not subject_name:
                messagebox.showwarning("Select Subject", "Please select a subject for the subject report.")
                conn.close()
                return
            subject_id = self.subject_map[subject_name]

            cur.execute("SELECT total_topics, completed_topics FROM progress WHERE subject_id=?", (subject_id,))
            prog = cur.fetchone()
            total = prog["total_topics"] if prog else 0
            completed = prog["completed_topics"] if prog else 0
            percent = int((completed / total) * 100) if total else 0

            cur.execute("""SELECT topic_name, plan_type, plan_date, study_hours, is_completed
                           FROM study_plans WHERE subject_id=? ORDER BY plan_date""", (subject_id,))
            rows = cur.fetchall()

            cur.execute("SELECT exam_name, exam_date FROM exams WHERE subject_id=? ORDER BY exam_date", (subject_id,))
            exams = cur.fetchall()

            title = f"SUBJECT REPORT - {subject_name}"
            lines = [title, "=" * len(title), "",
                     f"Total Topics     : {total}",
                     f"Completed Topics : {completed}",
                     f"Remaining Topics : {max(total - completed, 0)}",
                     f"Progress         : {percent}%",
                     "", "Study Plan Entries:", "-" * 30]
            if rows:
                for r in rows:
                    status = "Done" if r["is_completed"] else "Pending"
                    lines.append(f"[{r['plan_date']}] ({r['plan_type']}) {r['topic_name']:<25} "
                                 f"{r['study_hours']:>4} hrs  ({status})")
            else:
                lines.append("No study plan entries for this subject yet.")

            lines.append("")
            lines.append("Exams:")
            lines.append("-" * 30)
            if exams:
                for e in exams:
                    lines.append(f"{e['exam_name']:<30} {e['exam_date']}")
            else:
                lines.append("No exams scheduled for this subject.")

        conn.close()
        self.output_text.insert("1.0", "\n".join(lines))

    def export_report(self):
        content = self.output_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Nothing to Export", "Please generate a report first.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                   filetypes=[("Text Files", "*.txt")],
                                                   title="Save Report As")
        if not file_path:
            return
        try:
            with open(file_path, "w") as f:
                f.write(content)
            messagebox.showinfo("Exported", f"Report saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
