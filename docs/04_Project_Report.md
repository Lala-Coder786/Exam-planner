# Project Report - Exam Preparation Planner

## 1. Introduction
Students often prepare for multiple subjects and exams at the same time
and find it hard to keep track of what to study and how much they have
completed. The **Exam Preparation Planner** is a desktop application
that helps a student organise subjects, exams, and a day-to-day study
plan, and see their preparation progress at a glance.

## 2. Objective
- To build a simple, offline, desktop tool for exam preparation tracking.
- To apply core concepts of Python, GUI programming (Tkinter) and
  database management (SQLite) in one real project.
- To provide full CRUD (Create, Read, Update, Delete) operations with
  proper validation on every module.

## 3. Scope
The application is for a single student to manage their own subjects,
exams and study plans. Multiple users can register and each user's data
is kept separate using `user_id` as a foreign key.

## 4. System Requirements
**Hardware:** Any PC/Laptop capable of running Python (min 2GB RAM)
**Software:** Windows/Linux/Mac, Python 3.8+, VS Code (optional, for editing)

## 5. Modules
1. **Authentication** – Login/Register using SQLite, passwords stored as SHA-256 hash
2. **Dashboard** – summary cards + today's plan + upcoming exams
3. **Subject Management** – CRUD + search
4. **Exam Management** – CRUD + sort by date + upcoming filter
5. **Study Planner** – Daily/Weekly/Monthly topics, hours, completion
6. **Progress Tracker** – subject-wise and overall progress bars
7. **Reports** – Daily/Weekly/Monthly/Subject reports, export to .txt

## 6. Technology Used
| Component | Technology |
|---|---|
| Language | Python 3 |
| GUI | Tkinter |
| Database | SQLite3 |
| IDE | VS Code |

## 7. Database Design
5 tables: `users`, `subjects`, `exams`, `study_plans`, `progress`, connected
using primary/foreign keys with `ON DELETE CASCADE`. See `docs/diagrams/er_diagram.png`.

## 8. Advantages
- Completely offline, no internet required
- Lightweight (SQLite, no server setup)
- Simple, clean interface, easy for anyone to use
- Data is safe per-user (login based)

## 9. Limitations
- Single-machine only (database file is local, not cloud synced)
- No reminders/notifications for exams (could be a future enhancement)
- Currently supports text-based reports (not PDF export)

## 10. Future Enhancements
- Add exam countdown/reminder notifications
- Export reports as PDF
- Add charts (pie/bar) using matplotlib for progress visualization
- Cloud sync using a proper backend server

## 11. Conclusion
The Exam Preparation Planner successfully demonstrates a complete,
working desktop application using Python, Tkinter and SQLite, covering
authentication, full CRUD operations, data validation, and reporting —
built end-to-end as a college mini project.
