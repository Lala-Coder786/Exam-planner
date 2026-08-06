# Viva Questions and Answers

**Q1. What is the purpose of this project?**
A. It helps a student organise subjects, exams and a study schedule, and
track how much of the syllabus is completed before exams.

**Q2. Which technologies did you use and why?**
A. Python for logic, Tkinter because it comes built-in with Python and
is enough for a desktop GUI, and SQLite because it needs no separate
server and stores data in a single local file - ideal for a small
single-user desktop app.

**Q3. How many tables are there in your database and what are they?**
A. Five tables: `users`, `subjects`, `exams`, `study_plans`, and `progress`.

**Q4. How are the tables related?**
A. `subjects`, `exams`, `study_plans` and `progress` all have a
`user_id` foreign key referencing `users`. `exams`, `study_plans` and
`progress` also have a `subject_id` foreign key referencing `subjects`.
This is a one-to-many relationship in each case.

**Q5. What happens when you delete a subject?**
A. Because foreign keys are defined with `ON DELETE CASCADE`, deleting a
subject automatically deletes its related exams, study plans and
progress row, so there is no leftover/orphan data.

**Q6. How is the password stored securely?**
A. The password is never stored in plain text. It is converted using
SHA-256 hashing (`hashlib.sha256`) before saving to the database, and
during login the entered password is hashed again and compared.

**Q7. How does the Progress Tracker get its numbers?**
A. Every subject has a row in the `progress` table with
`completed_topics` and `total_topics`. Whenever a topic in the Study
Planner is marked completed, the app recounts how many `study_plans`
rows for that subject are completed and updates `progress.completed_topics`.

**Q8. How do you prevent duplicate subjects?**
A. Before inserting, the app runs a SELECT query checking if a subject
with the same name (case-insensitive) already exists for that user; if
it does, it shows an error instead of inserting.

**Q9. How is date validated?**
A. Using Python's `datetime.strptime(value, "%Y-%m-%d")` inside a
try/except block; if the format is wrong or the date doesn't exist, an
error message is shown to the user.

**Q10. What is the use of `PRAGMA foreign_keys = ON`?**
A. SQLite does not enforce foreign key constraints by default. This
PRAGMA statement turns that enforcement on for each connection, so
CASCADE deletes and constraints actually work.

**Q11. Why did you use `sqlite3.Row` as the row factory?**
A. It lets us access columns by name (like `row["subject_name"]`)
instead of only by index (`row[1]`), which makes the code much easier
to read and less error-prone.

**Q12. How is the GUI structured?**
A. `main.py` builds a sidebar with navigation buttons and a content
area. Each menu item (Dashboard, Subjects, Exams, Planner, Progress,
Reports) is its own Tkinter Frame class defined in a separate file,
which keeps the code modular.

**Q13. What is CRUD?**
A. Create, Read, Update, Delete — the four basic database operations.
Every module (Subjects, Exams, Study Plans) supports all four, plus Search.

**Q14. How do you handle errors/exceptions in this project?**
A. All database operations are wrapped in try/except blocks. If
something goes wrong (e.g. database locked), a message box shows the
error instead of the program crashing.

**Q15. Can this project support multiple users at the same time?**
A. Yes, multiple accounts can be created via Register, and each user's
subjects/exams/plans are isolated using the `user_id` foreign key, so
one user cannot see another user's data.

**Q16. Why did you use Treeview widget in Tkinter?**
A. `ttk.Treeview` is used to display tabular data (like subjects,
exams, study plans) in rows and columns, similar to a spreadsheet,
along with click-to-select and click-to-sort behaviour.

**Q17. How would you improve this project further?**
A. Add PDF report export, add exam reminder notifications, add graphs
using matplotlib, and optionally move to a client-server database like
MySQL for multi-device access.
