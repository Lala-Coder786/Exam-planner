# Exam Preparation Planner

A desktop application built with **Python, Tkinter and SQLite** to help
students plan and track their exam preparation. This was built as a
college mini-project.

## Features
- User Login / Registration (SQLite based authentication)
- Dashboard with quick stats (subjects, upcoming exams, today's plan, progress)
- Subject Management (Add / Edit / Delete / Search)
- Exam Management (Add / Edit / Delete / Sort by date / Upcoming exams filter)
- Study Planner (Daily / Weekly / Monthly plans, mark topics completed, track hours)
- Progress Tracker (subject-wise and overall progress bars)
- Reports (Daily, Weekly, Monthly, Subject-wise, export to .txt)

## Tech Stack
- Python 3
- Tkinter (GUI)
- SQLite3 (Database)

## Folder Structure
```
ExamPreparationPlanner/
│
├── main.py            -> Main window after login (sidebar + navigation)
├── database.py         -> All database table creation & connection code
├── login.py             -> Login + Register screen (run this file to start the app)
├── dashboard.py       -> Dashboard screen
├── subject.py           -> Subject management screen
├── exam.py               -> Exam management screen
├── planner.py           -> Study planner screen
├── progress.py         -> Progress tracker screen
├── reports.py           -> Reports screen
├── utils.py               -> Validation helpers + colour/font theme
├── planner.db           -> SQLite database file (auto-created on first run)
├── assets/                -> (icons / images, optional)
├── docs/                   -> Project documentation
└── README.md
```

## How to Run
1. Make sure Python 3.8+ is installed (tkinter comes built in with Python on Windows).
2. Open a terminal inside the `ExamPreparationPlanner` folder.
3. Run:
   ```
   python login.py
   ```
4. The database (`planner.db`) and a demo account are created automatically
   the first time you run it.

## Demo Login
```
Username: student
Password: student123
```
(You can also click "New user? Create an account" to make your own login.)

## Database Design (short)
- `users` — stores login details (password is stored as SHA-256 hash, not plain text)
- `subjects` — subjects added by a user
- `exams` — exams linked to a subject
- `study_plans` — daily/weekly/monthly topics with hours & completion status
- `progress` — auto-updated completed/total topic count per subject

All child tables use `FOREIGN KEY ... ON DELETE CASCADE`, so deleting a
subject automatically removes its exams, plans and progress row.

## Notes
- Everything is validated (no empty fields, correct date format, no duplicate
  subject names, numbers can't be negative, etc.)
- All errors are caught using try/except and shown as friendly message boxes.

## Author
Made as a Computer Science mini project.
