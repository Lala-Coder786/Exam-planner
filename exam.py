"""
exam.py
-------
Exam Management screen.
Add / Edit / Delete exams, each exam is linked to a subject.
Also supports viewing only upcoming exams and sorting by date.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import database
import utils


class ExamFrame(tk.Frame):
    def __init__(self, parent, user, on_change=None):
        super().__init__(parent, bg=utils.BG_COLOR)
        self.user = user
        self.on_change = on_change
        self.selected_id = None
        self.subject_map = {}  # name -> id
        self.build_ui()
        self.load_subject_dropdown()
        self.load_exams()

    def build_ui(self):
        tk.Label(self, text="Exam Management", font=utils.FONT_TITLE, bg=utils.BG_COLOR,
                 fg=utils.TEXT_COLOR).pack(anchor="w", padx=25, pady=(20, 10))

        form = tk.LabelFrame(self, text=" Exam Details ", font=utils.FONT_BOLD, bg=utils.WHITE, bd=1, relief="solid")
        form.pack(fill="x", padx=20, pady=5)

        tk.Label(form, text="Subject", bg=utils.WHITE, font=utils.FONT_NORMAL).grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.subject_combo = ttk.Combobox(form, font=utils.FONT_NORMAL, width=18, state="readonly")
        self.subject_combo.grid(row=0, column=1, padx=8, pady=8)

        tk.Label(form, text="Exam Name", bg=utils.WHITE, font=utils.FONT_NORMAL).grid(row=0, column=2, padx=8, pady=8, sticky="w")
        self.exam_name_entry = tk.Entry(form, font=utils.FONT_NORMAL, width=22, relief="solid", bd=1)
        self.exam_name_entry.grid(row=0, column=3, padx=8, pady=8)

        tk.Label(form, text="Date (YYYY-MM-DD)", bg=utils.WHITE, font=utils.FONT_NORMAL).grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.date_entry = tk.Entry(form, font=utils.FONT_NORMAL, width=18, relief="solid", bd=1)
        self.date_entry.grid(row=1, column=1, padx=8, pady=8)

        tk.Label(form, text="Time", bg=utils.WHITE, font=utils.FONT_NORMAL).grid(row=1, column=2, padx=8, pady=8, sticky="w")
        self.time_entry = tk.Entry(form, font=utils.FONT_NORMAL, width=22, relief="solid", bd=1)
        self.time_entry.grid(row=1, column=3, padx=8, pady=8)

        tk.Label(form, text="Venue", bg=utils.WHITE, font=utils.FONT_NORMAL).grid(row=2, column=0, padx=8, pady=8, sticky="w")
        self.venue_entry = tk.Entry(form, font=utils.FONT_NORMAL, width=18, relief="solid", bd=1)
        self.venue_entry.grid(row=2, column=1, padx=8, pady=8)

        btn_frame = tk.Frame(form, bg=utils.WHITE)
        btn_frame.grid(row=2, column=3, padx=8, sticky="e")
        tk.Button(btn_frame, text="Add", bg=utils.SUCCESS_COLOR, fg=utils.WHITE, font=utils.FONT_BTN,
                  relief="flat", width=8, command=self.add_exam).pack(side="left", padx=3)
        tk.Button(btn_frame, text="Update", bg=utils.ACCENT_COLOR, fg=utils.WHITE, font=utils.FONT_BTN,
                  relief="flat", width=8, command=self.update_exam).pack(side="left", padx=3)
        tk.Button(btn_frame, text="Delete", bg=utils.DANGER_COLOR, fg=utils.WHITE, font=utils.FONT_BTN,
                  relief="flat", width=8, command=self.delete_exam).pack(side="left", padx=3)
        tk.Button(btn_frame, text="Clear", bg="#b2bec3", fg=utils.WHITE, font=utils.FONT_BTN,
                  relief="flat", width=8, command=self.clear_form).pack(side="left", padx=3)

        # ---- filter row ----
        filter_frame = tk.Frame(self, bg=utils.BG_COLOR)
        filter_frame.pack(fill="x", padx=20, pady=(10, 0))
        self.upcoming_only = tk.BooleanVar(value=False)
        tk.Checkbutton(filter_frame, text="Show Upcoming Exams Only", variable=self.upcoming_only,
                        bg=utils.BG_COLOR, font=utils.FONT_NORMAL, command=self.load_exams).pack(side="left")
        tk.Label(filter_frame, text="   Search:", bg=utils.BG_COLOR, font=utils.FONT_NORMAL).pack(side="left")
        self.search_entry = tk.Entry(filter_frame, font=utils.FONT_NORMAL, width=25, relief="solid", bd=1)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_exams())

        # ---- table (sorted by date, click heading to sort) ----
        table_frame = tk.Frame(self, bg=utils.BG_COLOR)
        table_frame.pack(fill="both", expand=True, padx=20, pady=15)

        cols = ("id", "subject", "exam", "date", "time", "venue")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=12)
        headings = {"id": "ID", "subject": "Subject", "exam": "Exam Name", "date": "Date",
                    "time": "Time", "venue": "Venue"}
        for c in cols:
            self.tree.heading(c, text=headings[c], command=lambda col=c: self.sort_by(col))
            self.tree.column(c, width=120, anchor="center")
        self.tree.column("id", width=40)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def load_subject_dropdown(self):
        conn = database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT subject_id, subject_name FROM subjects WHERE user_id=? ORDER BY subject_name",
                    (self.user["user_id"],))
        rows = cur.fetchall()
        conn.close()
        self.subject_map = {r["subject_name"]: r["subject_id"] for r in rows}
        self.subject_combo["values"] = list(self.subject_map.keys())

    def sort_by(self, col):
        """Simple click-to-sort on any column heading."""
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        items.sort()
        for index, (val, k) in enumerate(items):
            self.tree.move(k, "", index)

    def load_exams(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        keyword = self.search_entry.get().strip() if hasattr(self, "search_entry") else ""
        conn = database.get_connection()
        cur = conn.cursor()

        query = """SELECT e.exam_id, s.subject_name, e.exam_name, e.exam_date, e.exam_time, e.venue
                   FROM exams e JOIN subjects s ON e.subject_id = s.subject_id
                   WHERE e.user_id=? AND (e.exam_name LIKE ? OR s.subject_name LIKE ?)"""
        params = [self.user["user_id"], f"%{keyword}%", f"%{keyword}%"]

        if self.upcoming_only.get():
            query += " AND e.exam_date >= ?"
            params.append(date.today().isoformat())

        query += " ORDER BY e.exam_date ASC"
        cur.execute(query, params)
        for r in cur.fetchall():
            self.tree.insert("", "end", values=(r["exam_id"], r["subject_name"], r["exam_name"],
                                                 r["exam_date"], r["exam_time"] or "-", r["venue"] or "-"))
        conn.close()

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0])["values"]
        self.selected_id = v[0]
        self.subject_combo.set(v[1])
        self.exam_name_entry.delete(0, tk.END)
        self.exam_name_entry.insert(0, v[2])
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, v[3])
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, "" if v[4] == "-" else v[4])
        self.venue_entry.delete(0, tk.END)
        self.venue_entry.insert(0, "" if v[5] == "-" else v[5])

    def clear_form(self):
        self.selected_id = None
        self.subject_combo.set("")
        self.exam_name_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.venue_entry.delete(0, tk.END)
        self.tree.selection_remove(self.tree.selection())

    def get_form_values(self):
        subject_name = self.subject_combo.get().strip()
        exam_name = self.exam_name_entry.get().strip()
        exam_date = self.date_entry.get().strip()
        exam_time = self.time_entry.get().strip()
        venue = self.venue_entry.get().strip()

        if not utils.validate_not_empty(subject_name, "Subject"):
            return None
        if subject_name not in self.subject_map:
            messagebox.showerror("Validation Error", "Please select a valid subject from the list.")
            return None
        if not utils.validate_not_empty(exam_name, "Exam Name"):
            return None
        if not utils.validate_date(exam_date, "Exam Date"):
            return None
        return self.subject_map[subject_name], exam_name, exam_date, exam_time, venue

    def add_exam(self):
        values = self.get_form_values()
        if values is None:
            return
        subject_id, exam_name, exam_date, exam_time, venue = values
        try:
            conn = database.get_connection()
            cur = conn.cursor()
            cur.execute("""INSERT INTO exams (user_id, subject_id, exam_name, exam_date, exam_time, venue)
                           VALUES (?,?,?,?,?,?)""",
                        (self.user["user_id"], subject_id, exam_name, exam_date, exam_time, venue))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        messagebox.showinfo("Success", "Exam added successfully.")
        self.clear_form()
        self.load_exams()
        if self.on_change:
            self.on_change()

    def update_exam(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Please select an exam from the table to update.")
            return
        values = self.get_form_values()
        if values is None:
            return
        subject_id, exam_name, exam_date, exam_time, venue = values
        try:
            conn = database.get_connection()
            cur = conn.cursor()
            cur.execute("""UPDATE exams SET subject_id=?, exam_name=?, exam_date=?, exam_time=?, venue=?
                           WHERE exam_id=? AND user_id=?""",
                        (subject_id, exam_name, exam_date, exam_time, venue, self.selected_id, self.user["user_id"]))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        messagebox.showinfo("Success", "Exam updated successfully.")
        self.clear_form()
        self.load_exams()
        if self.on_change:
            self.on_change()

    def delete_exam(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Please select an exam from the table to delete.")
            return
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this exam?"):
            return
        try:
            conn = database.get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM exams WHERE exam_id=? AND user_id=?", (self.selected_id, self.user["user_id"]))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        messagebox.showinfo("Deleted", "Exam deleted successfully.")
        self.clear_form()
        self.load_exams()
        if self.on_change:
            self.on_change()
