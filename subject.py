"""
subject.py
----------
Subject Management screen.
Supports Add, Edit, Delete, Search for subjects belonging to the logged in user.
Every subject also gets a matching row in the 'progress' table.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
import utils


class SubjectFrame(tk.Frame):
    def __init__(self, parent, user, on_change=None):
        super().__init__(parent, bg=utils.BG_COLOR)
        self.user = user
        self.on_change = on_change  # callback to refresh dashboard etc. after a change
        self.selected_id = None
        self.build_ui()
        self.load_subjects()

    def build_ui(self):
        tk.Label(self, text="Subject Management", font=utils.FONT_TITLE, bg=utils.BG_COLOR,
                 fg=utils.TEXT_COLOR).pack(anchor="w", padx=25, pady=(20, 10))

        # ---- form ----
        form = tk.LabelFrame(self, text=" Subject Details ", font=utils.FONT_BOLD, bg=utils.WHITE, bd=1, relief="solid")
        form.pack(fill="x", padx=20, pady=5)

        tk.Label(form, text="Subject Name", bg=utils.WHITE, font=utils.FONT_NORMAL).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.name_entry = tk.Entry(form, font=utils.FONT_NORMAL, width=30, relief="solid", bd=1)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(form, text="Total Topics", bg=utils.WHITE, font=utils.FONT_NORMAL).grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.topics_entry = tk.Entry(form, font=utils.FONT_NORMAL, width=10, relief="solid", bd=1)
        self.topics_entry.grid(row=0, column=3, padx=10, pady=10)

        btn_frame = tk.Frame(form, bg=utils.WHITE)
        btn_frame.grid(row=0, column=4, padx=10)
        tk.Button(btn_frame, text="Add", bg=utils.SUCCESS_COLOR, fg=utils.WHITE, font=utils.FONT_BTN,
                  relief="flat", width=8, command=self.add_subject).pack(side="left", padx=3)
        tk.Button(btn_frame, text="Update", bg=utils.ACCENT_COLOR, fg=utils.WHITE, font=utils.FONT_BTN,
                  relief="flat", width=8, command=self.update_subject).pack(side="left", padx=3)
        tk.Button(btn_frame, text="Delete", bg=utils.DANGER_COLOR, fg=utils.WHITE, font=utils.FONT_BTN,
                  relief="flat", width=8, command=self.delete_subject).pack(side="left", padx=3)
        tk.Button(btn_frame, text="Clear", bg="#b2bec3", fg=utils.WHITE, font=utils.FONT_BTN,
                  relief="flat", width=8, command=self.clear_form).pack(side="left", padx=3)

        # ---- search ----
        search_frame = tk.Frame(self, bg=utils.BG_COLOR)
        search_frame.pack(fill="x", padx=20, pady=(10, 0))
        tk.Label(search_frame, text="Search:", bg=utils.BG_COLOR, font=utils.FONT_NORMAL).pack(side="left")
        self.search_entry = tk.Entry(search_frame, font=utils.FONT_NORMAL, width=30, relief="solid", bd=1)
        self.search_entry.pack(side="left", padx=8)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_subjects())

        # ---- table ----
        table_frame = tk.Frame(self, bg=utils.BG_COLOR)
        table_frame.pack(fill="both", expand=True, padx=20, pady=15)

        cols = ("id", "name", "total", "completed", "percent")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=14)
        headings = {"id": "ID", "name": "Subject Name", "total": "Total Topics",
                    "completed": "Completed", "percent": "Progress %"}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=140, anchor="center")
        self.tree.column("id", width=50)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def load_subjects(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        keyword = self.search_entry.get().strip() if hasattr(self, "search_entry") else ""
        conn = database.get_connection()
        cur = conn.cursor()
        cur.execute("""SELECT s.subject_id, s.subject_name, s.total_topics,
                              COALESCE(p.completed_topics,0) as completed
                       FROM subjects s LEFT JOIN progress p ON s.subject_id = p.subject_id
                       WHERE s.user_id=? AND s.subject_name LIKE ?
                       ORDER BY s.subject_name""",
                    (self.user["user_id"], f"%{keyword}%"))
        for r in cur.fetchall():
            percent = int((r["completed"] / r["total_topics"]) * 100) if r["total_topics"] else 0
            self.tree.insert("", "end", values=(r["subject_id"], r["subject_name"], r["total_topics"],
                                                 r["completed"], f"{percent}%"))
        conn.close()

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0])["values"]
        self.selected_id = values[0]
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, values[1])
        self.topics_entry.delete(0, tk.END)
        self.topics_entry.insert(0, values[2])

    def clear_form(self):
        self.selected_id = None
        self.name_entry.delete(0, tk.END)
        self.topics_entry.delete(0, tk.END)
        self.tree.selection_remove(self.tree.selection())

    def add_subject(self):
        name = self.name_entry.get().strip()
        topics = self.topics_entry.get().strip()

        if not utils.validate_not_empty(name, "Subject Name"):
            return
        if not utils.validate_int(topics, "Total Topics"):
            return

        try:
            conn = database.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM subjects WHERE user_id=? AND LOWER(subject_name)=LOWER(?)",
                        (self.user["user_id"], name))
            if cur.fetchone():
                messagebox.showerror("Duplicate Entry", "This subject already exists.")
                conn.close()
                return

            cur.execute("INSERT INTO subjects (user_id, subject_name, total_topics) VALUES (?,?,?)",
                        (self.user["user_id"], name, int(topics)))
            subject_id = cur.lastrowid
            cur.execute("INSERT INTO progress (user_id, subject_id, completed_topics, total_topics) VALUES (?,?,0,?)",
                        (self.user["user_id"], subject_id, int(topics)))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        messagebox.showinfo("Success", "Subject added successfully.")
        self.clear_form()
        self.load_subjects()
        if self.on_change:
            self.on_change()

    def update_subject(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Please select a subject from the table to update.")
            return

        name = self.name_entry.get().strip()
        topics = self.topics_entry.get().strip()

        if not utils.validate_not_empty(name, "Subject Name"):
            return
        if not utils.validate_int(topics, "Total Topics"):
            return

        try:
            conn = database.get_connection()
            cur = conn.cursor()
            cur.execute("""SELECT * FROM subjects WHERE user_id=? AND LOWER(subject_name)=LOWER(?)
                           AND subject_id != ?""", (self.user["user_id"], name, self.selected_id))
            if cur.fetchone():
                messagebox.showerror("Duplicate Entry", "Another subject with this name already exists.")
                conn.close()
                return

            cur.execute("UPDATE subjects SET subject_name=?, total_topics=? WHERE subject_id=? AND user_id=?",
                        (name, int(topics), self.selected_id, self.user["user_id"]))
            cur.execute("UPDATE progress SET total_topics=? WHERE subject_id=?", (int(topics), self.selected_id))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        messagebox.showinfo("Success", "Subject updated successfully.")
        self.clear_form()
        self.load_subjects()
        if self.on_change:
            self.on_change()

    def delete_subject(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Please select a subject from the table to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete",
                                       "Deleting this subject will also delete its exams and study plans.\nAre you sure?")
        if not confirm:
            return

        try:
            conn = database.get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM subjects WHERE subject_id=? AND user_id=?",
                        (self.selected_id, self.user["user_id"]))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        messagebox.showinfo("Deleted", "Subject deleted successfully.")
        self.clear_form()
        self.load_subjects()
        if self.on_change:
            self.on_change()
