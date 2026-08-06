"""
planner.py
----------
Study Planner screen.
Lets the student add topics to study under Daily / Weekly / Monthly plans,
mark them completed, and enter how many hours were spent.
Marking a topic "completed" automatically updates the progress table
(this is how the Progress Tracker screen gets its numbers).
"""

import tkinter as tk
from tkinter import ttk, messagebox
import database
import utils


class PlannerFrame(tk.Frame):
    def __init__(self, parent, user, on_change=None):
        super().__init__(parent, bg=utils.BG_COLOR)
        self.user = user
        self.on_change = on_change
        self.selected_id = None
        self.subject_map = {}
        self.build_ui()
        self.load_subject_dropdown()
        self.load_plans()

    def build_ui(self):
        tk.Label(self, text="Study Planner", font=utils.FONT_TITLE, bg=utils.BG_COLOR,
                 fg=utils.TEXT_COLOR).pack(anchor="w", padx=25, pady=(20, 10))

        form = tk.LabelFrame(self, text=" Plan a Topic ", font=utils.FONT_BOLD, bg=utils.WHITE, bd=1, relief="solid")
        form.pack(fill="x", padx=20, pady=5)

        tk.Label(form, text="Subject", bg=utils.WHITE).grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.subject_combo = ttk.Combobox(form, width=16, state="readonly")
        self.subject_combo.grid(row=0, column=1, padx=8, pady=8)

        tk.Label(form, text="Topic", bg=utils.WHITE).grid(row=0, column=2, padx=8, pady=8, sticky="w")
        self.topic_entry = tk.Entry(form, width=22, relief="solid", bd=1)
        self.topic_entry.grid(row=0, column=3, padx=8, pady=8)

        tk.Label(form, text="Plan Type", bg=utils.WHITE).grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.type_combo = ttk.Combobox(form, width=16, state="readonly", values=["Daily", "Weekly", "Monthly"])
        self.type_combo.current(0)
        self.type_combo.grid(row=1, column=1, padx=8, pady=8)

        tk.Label(form, text="Date (YYYY-MM-DD)", bg=utils.WHITE).grid(row=1, column=2, padx=8, pady=8, sticky="w")
        self.date_entry = tk.Entry(form, width=22, relief="solid", bd=1)
        self.date_entry.grid(row=1, column=3, padx=8, pady=8)

        tk.Label(form, text="Study Hours", bg=utils.WHITE).grid(row=2, column=0, padx=8, pady=8, sticky="w")
        self.hours_entry = tk.Entry(form, width=16, relief="solid", bd=1)
        self.hours_entry.grid(row=2, column=1, padx=8, pady=8)

        self.completed_var = tk.BooleanVar(value=False)
        tk.Checkbutton(form, text="Mark as Completed", variable=self.completed_var,
                        bg=utils.WHITE, font=utils.FONT_NORMAL).grid(row=2, column=2, padx=8, pady=8, sticky="w")

        btn_frame = tk.Frame(form, bg=utils.WHITE)
        btn_frame.grid(row=2, column=3, padx=8, sticky="e")
        tk.Button(btn_frame, text="Add", bg=utils.SUCCESS_COLOR, fg=utils.WHITE, font=utils.FONT_BTN,
                  relief="flat", width=8, command=self.add_plan).pack(side="left", padx=3)
        tk.Button(btn_frame, text="Update", bg=utils.ACCENT_COLOR, fg=utils.WHITE, font=utils.FONT_BTN,
                  relief="flat", width=8, command=self.update_plan).pack(side="left", padx=3)
        tk.Button(btn_frame, text="Delete", bg=utils.DANGER_COLOR, fg=utils.WHITE, font=utils.FONT_BTN,
                  relief="flat", width=8, command=self.delete_plan).pack(side="left", padx=3)

        clear_frame = tk.Frame(form, bg=utils.WHITE)
        clear_frame.grid(row=3, column=3, padx=8, sticky="e", pady=(0, 8))
        tk.Button(clear_frame, text="Clear", bg="#b2bec3", fg=utils.WHITE, font=utils.FONT_BTN,
                  relief="flat", width=8, command=self.clear_form).pack(side="left", padx=3)

        # ---- filter ----
        filter_frame = tk.Frame(self, bg=utils.BG_COLOR)
        filter_frame.pack(fill="x", padx=20, pady=(10, 0))
        tk.Label(filter_frame, text="View:", bg=utils.BG_COLOR, font=utils.FONT_NORMAL).pack(side="left")
        self.view_combo = ttk.Combobox(filter_frame, width=14, state="readonly",
                                        values=["All", "Daily", "Weekly", "Monthly"])
        self.view_combo.current(0)
        self.view_combo.pack(side="left", padx=8)
        self.view_combo.bind("<<ComboboxSelected>>", lambda e: self.load_plans())
        tk.Label(filter_frame, text="Search:", bg=utils.BG_COLOR, font=utils.FONT_NORMAL).pack(side="left", padx=(15, 0))
        self.search_entry = tk.Entry(filter_frame, width=25, relief="solid", bd=1)
        self.search_entry.pack(side="left", padx=8)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_plans())

        # ---- table ----
        table_frame = tk.Frame(self, bg=utils.BG_COLOR)
        table_frame.pack(fill="both", expand=True, padx=20, pady=15)

        cols = ("id", "subject", "topic", "type", "date", "hours", "status")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=12)
        headings = {"id": "ID", "subject": "Subject", "topic": "Topic", "type": "Type",
                    "date": "Date", "hours": "Hours", "status": "Status"}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=110, anchor="center")
        self.tree.column("id", width=40)
        self.tree.column("topic", width=170)
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

    def load_plans(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        keyword = self.search_entry.get().strip() if hasattr(self, "search_entry") else ""
        view = self.view_combo.get() if hasattr(self, "view_combo") else "All"

        conn = database.get_connection()
        cur = conn.cursor()
        query = """SELECT p.plan_id, s.subject_name, p.topic_name, p.plan_type, p.plan_date,
                          p.study_hours, p.is_completed
                   FROM study_plans p JOIN subjects s ON p.subject_id = s.subject_id
                   WHERE p.user_id=? AND p.topic_name LIKE ?"""
        params = [self.user["user_id"], f"%{keyword}%"]
        if view != "All":
            query += " AND p.plan_type=?"
            params.append(view)
        query += " ORDER BY p.plan_date DESC"
        cur.execute(query, params)
        for r in cur.fetchall():
            status = "Completed" if r["is_completed"] else "Pending"
            self.tree.insert("", "end", values=(r["plan_id"], r["subject_name"], r["topic_name"],
                                                 r["plan_type"], r["plan_date"], r["study_hours"], status))
        conn.close()

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0])["values"]
        self.selected_id = v[0]
        self.subject_combo.set(v[1])
        self.topic_entry.delete(0, tk.END)
        self.topic_entry.insert(0, v[2])
        self.type_combo.set(v[3])
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, v[4])
        self.hours_entry.delete(0, tk.END)
        self.hours_entry.insert(0, v[5])
        self.completed_var.set(v[6] == "Completed")

    def clear_form(self):
        self.selected_id = None
        self.subject_combo.set("")
        self.topic_entry.delete(0, tk.END)
        self.type_combo.current(0)
        self.date_entry.delete(0, tk.END)
        self.hours_entry.delete(0, tk.END)
        self.completed_var.set(False)
        self.tree.selection_remove(self.tree.selection())

    def get_form_values(self):
        subject_name = self.subject_combo.get().strip()
        topic = self.topic_entry.get().strip()
        plan_type = self.type_combo.get().strip()
        plan_date = self.date_entry.get().strip()
        hours = self.hours_entry.get().strip()

        if not utils.validate_not_empty(subject_name, "Subject"):
            return None
        if subject_name not in self.subject_map:
            messagebox.showerror("Validation Error", "Please select a valid subject.")
            return None
        if not utils.validate_not_empty(topic, "Topic"):
            return None
        if not utils.validate_date(plan_date, "Plan Date"):
            return None
        if not utils.validate_number(hours, "Study Hours"):
            return None

        return self.subject_map[subject_name], topic, plan_type, plan_date, float(hours), int(self.completed_var.get())

    def sync_progress(self, subject_id):
        """Recomputes completed_topics for a subject based on completed study_plans rows,
        and writes that number into the progress table."""
        conn = database.get_connection()
        cur = conn.cursor()
        cur.execute("""SELECT COUNT(*) FROM study_plans WHERE subject_id=? AND is_completed=1""", (subject_id,))
        completed = cur.fetchone()[0]
        cur.execute("UPDATE progress SET completed_topics=?, last_updated=datetime('now') WHERE subject_id=?",
                    (completed, subject_id))
        conn.commit()
        conn.close()

    def add_plan(self):
        values = self.get_form_values()
        if values is None:
            return
        subject_id, topic, plan_type, plan_date, hours, completed = values
        try:
            conn = database.get_connection()
            cur = conn.cursor()
            cur.execute("""INSERT INTO study_plans (user_id, subject_id, topic_name, plan_type, plan_date, study_hours, is_completed)
                           VALUES (?,?,?,?,?,?,?)""",
                        (self.user["user_id"], subject_id, topic, plan_type, plan_date, hours, completed))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        self.sync_progress(subject_id)
        messagebox.showinfo("Success", "Study plan added successfully.")
        self.clear_form()
        self.load_plans()
        if self.on_change:
            self.on_change()

    def update_plan(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Please select a plan from the table to update.")
            return
        values = self.get_form_values()
        if values is None:
            return
        subject_id, topic, plan_type, plan_date, hours, completed = values
        try:
            conn = database.get_connection()
            cur = conn.cursor()
            cur.execute("""UPDATE study_plans SET subject_id=?, topic_name=?, plan_type=?, plan_date=?,
                           study_hours=?, is_completed=? WHERE plan_id=? AND user_id=?""",
                        (subject_id, topic, plan_type, plan_date, hours, completed, self.selected_id, self.user["user_id"]))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        self.sync_progress(subject_id)
        messagebox.showinfo("Success", "Study plan updated successfully.")
        self.clear_form()
        self.load_plans()
        if self.on_change:
            self.on_change()

    def delete_plan(self):
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Please select a plan from the table to delete.")
            return
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this plan entry?"):
            return

        conn = database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT subject_id FROM study_plans WHERE plan_id=?", (self.selected_id,))
        row = cur.fetchone()
        subject_id = row["subject_id"] if row else None

        try:
            cur.execute("DELETE FROM study_plans WHERE plan_id=? AND user_id=?", (self.selected_id, self.user["user_id"]))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        if subject_id:
            self.sync_progress(subject_id)
        messagebox.showinfo("Deleted", "Study plan deleted successfully.")
        self.clear_form()
        self.load_plans()
        if self.on_change:
            self.on_change()
