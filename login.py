"""
login.py
--------
This is the first screen the user sees.
It lets the user:
  - Login with username/password (checked against SQLite 'users' table)
  - Register a new account if they don't have one

Once login is successful, it closes this window and opens the
main dashboard window (from main.py).
"""

import tkinter as tk
from tkinter import messagebox
import database
import utils


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Exam Preparation Planner - Login")
        self.root.geometry("420x430")
        self.root.resizable(False, False)
        self.root.configure(bg=utils.BG_COLOR)

        self.build_ui()

    def build_ui(self):
        card = tk.Frame(self.root, bg=utils.WHITE, bd=0)
        card.place(relx=0.5, rely=0.5, anchor="center", width=340, height=380)

        tk.Label(card, text="📘 Exam Prep Planner", font=utils.FONT_TITLE,
                 bg=utils.WHITE, fg=utils.SIDEBAR_COLOR).pack(pady=(25, 5))
        tk.Label(card, text="Login to continue", font=utils.FONT_NORMAL,
                 bg=utils.WHITE, fg="#636e72").pack(pady=(0, 20))

        # Username
        tk.Label(card, text="Username", font=utils.FONT_BOLD, bg=utils.WHITE).pack(anchor="w", padx=40)
        self.username_entry = tk.Entry(card, font=utils.FONT_NORMAL, width=27, relief="solid", bd=1)
        self.username_entry.pack(pady=(2, 12), padx=40)

        # Password
        tk.Label(card, text="Password", font=utils.FONT_BOLD, bg=utils.WHITE).pack(anchor="w", padx=40)
        self.password_entry = tk.Entry(card, font=utils.FONT_NORMAL, width=27, relief="solid", bd=1, show="*")
        self.password_entry.pack(pady=(2, 18), padx=40)
        self.password_entry.bind("<Return>", lambda e: self.login())

        # Login button
        login_btn = tk.Button(card, text="LOGIN", font=utils.FONT_BTN, bg=utils.ACCENT_COLOR, fg=utils.WHITE,
                               activebackground=utils.SIDEBAR_HOVER, activeforeground=utils.WHITE,
                               relief="flat", width=25, height=1, cursor="hand2", command=self.login)
        login_btn.pack(pady=5)

        # Register link
        reg_btn = tk.Button(card, text="New user? Create an account", font=("Segoe UI", 9, "underline"),
                             bg=utils.WHITE, fg=utils.ACCENT_COLOR, bd=0, cursor="hand2",
                             command=self.open_register)
        reg_btn.pack(pady=10)

        tk.Label(card, text="Demo Login -> student / student123", font=("Segoe UI", 8),
                 bg=utils.WHITE, fg="#b2bec3").pack(side="bottom", pady=8)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not utils.validate_not_empty(username, "Username"):
            return
        if not utils.validate_not_empty(password, "Password"):
            return

        try:
            conn = database.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username=?", (username,))
            user = cur.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not connect to database.\n{e}")
            return

        if user is None:
            messagebox.showerror("Login Failed", "No account found with this username.")
            return

        if user["password"] != database.hash_password(password):
            messagebox.showerror("Login Failed", "Incorrect password. Please try again.")
            return

        messagebox.showinfo("Welcome", f"Welcome back, {user['full_name']}!")
        self.root.destroy()

        # open the main application window after successful login
        import main
        new_root = tk.Tk()
        main.MainApplication(new_root, dict(user))
        new_root.mainloop()

    def open_register(self):
        RegisterWindow(self.root)


class RegisterWindow:
    """A small popup window used to create a new account."""

    def __init__(self, parent):
        self.win = tk.Toplevel(parent)
        self.win.title("Create Account")
        self.win.geometry("360x400")
        self.win.resizable(False, False)
        self.win.configure(bg=utils.WHITE)
        self.win.grab_set()  # makes this popup modal

        tk.Label(self.win, text="Create New Account", font=utils.FONT_HEADING,
                 bg=utils.WHITE, fg=utils.SIDEBAR_COLOR).pack(pady=(20, 15))

        self.full_name = self.labeled_entry("Full Name")
        self.username = self.labeled_entry("Username")
        self.password = self.labeled_entry("Password", show="*")
        self.confirm = self.labeled_entry("Confirm Password", show="*")

        tk.Button(self.win, text="REGISTER", font=utils.FONT_BTN, bg=utils.SUCCESS_COLOR, fg=utils.WHITE,
                  relief="flat", width=22, cursor="hand2", command=self.register).pack(pady=20)

    def labeled_entry(self, label, show=None):
        tk.Label(self.win, text=label, font=utils.FONT_BOLD, bg=utils.WHITE).pack(anchor="w", padx=40)
        e = tk.Entry(self.win, font=utils.FONT_NORMAL, width=27, relief="solid", bd=1, show=show)
        e.pack(pady=(2, 10), padx=40)
        return e

    def register(self):
        full_name = self.full_name.get().strip()
        username = self.username.get().strip()
        password = self.password.get().strip()
        confirm = self.confirm.get().strip()

        for value, name in [(full_name, "Full Name"), (username, "Username"),
                             (password, "Password"), (confirm, "Confirm Password")]:
            if not utils.validate_not_empty(value, name):
                return

        if password != confirm:
            messagebox.showerror("Validation Error", "Password and Confirm Password do not match.")
            return

        if len(password) < 4:
            messagebox.showerror("Validation Error", "Password should be at least 4 characters long.")
            return

        try:
            conn = database.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username=?", (username,))
            if cur.fetchone() is not None:
                messagebox.showerror("Validation Error", "This username is already taken.")
                conn.close()
                return

            cur.execute("INSERT INTO users (username, password, full_name) VALUES (?,?,?)",
                        (username, database.hash_password(password), full_name))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return

        messagebox.showinfo("Success", "Account created successfully! You can now login.")
        self.win.destroy()


if __name__ == "__main__":
    database.create_tables()
    database.seed_sample_data()
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
