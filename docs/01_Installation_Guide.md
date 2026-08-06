# Installation Guide - Exam Preparation Planner

## Step 1: Install Python
Download and install Python 3.8 or above from https://python.org
(While installing on Windows, tick the box "Add Python to PATH")

Tkinter and SQLite3 already come packaged with Python, so no extra
installation is normally required.

**Linux users only** - if you get a "No module named tkinter" error, run:
```
sudo apt-get install python3-tk
```

## Step 2: Get the Project Folder
Copy the `ExamPreparationPlanner` folder to your computer
(for example, on the Desktop or in Documents).

## Step 3: Open a Terminal / Command Prompt
Open the folder in VS Code, or open Command Prompt / Terminal and
navigate into the folder:
```
cd path/to/ExamPreparationPlanner
```

## Step 4: Run the Application
```
python login.py
```
(On some systems the command is `python3 login.py`)

The first time you run it:
- `planner.db` (the SQLite database file) is created automatically
- Sample/demo data is inserted automatically

## Step 5: Login
Use the demo account:
```
Username: student
Password: student123
```
Or click "New user? Create an account" to register your own login.

## Common Problems
| Problem | Solution |
|---|---|
| `ModuleNotFoundError: No module named tkinter` | Install python3-tk (Linux) or reinstall Python with tcl/tk option checked (Windows) |
| Database locked / errors | Close any other program (like DB Browser) that has `planner.db` open |
| Window looks too small/big | The window is resizable, just drag the edges |
