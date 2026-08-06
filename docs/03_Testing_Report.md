# Testing Report - Exam Preparation Planner

Testing type used: **Manual Black Box Testing** (each feature tested by
using the application like a real user would).

| Test ID | Module | Test Case | Input | Expected Result | Status |
|---|---|---|---|---|---|
| TC01 | Login | Login with correct credentials | student / student123 | Dashboard opens | Pass |
| TC02 | Login | Login with wrong password | student / wrongpass | Error message shown | Pass |
| TC03 | Login | Login with empty username | "" / student123 | "Username cannot be empty" | Pass |
| TC04 | Register | Register new user | valid details | Account created, can login | Pass |
| TC05 | Register | Register with existing username | "student" | "Username already taken" error | Pass |
| TC06 | Register | Password ≠ Confirm Password | mismatched | Error shown, not saved | Pass |
| TC07 | Subject | Add new subject | "Maths", 10 | Row added to table | Pass |
| TC08 | Subject | Add duplicate subject | "Maths" again | "Subject already exists" error | Pass |
| TC09 | Subject | Add subject with empty name | "" | "Subject Name cannot be empty" | Pass |
| TC10 | Subject | Update subject | change topics 10 -> 12 | Table shows updated value | Pass |
| TC11 | Subject | Delete subject | select row -> Delete | Row removed, related exams/plans removed | Pass |
| TC12 | Subject | Search subject | type "Ma" | Only matching rows shown | Pass |
| TC13 | Exam | Add exam with invalid date | "15-09-2026" | "must be in YYYY-MM-DD format" error | Pass |
| TC14 | Exam | Add exam, no subject selected | subject empty | "Please select a valid subject" error | Pass |
| TC15 | Exam | Show upcoming exams only | tick checkbox | Only future-dated exams shown | Pass |
| TC16 | Exam | Sort by date column | click "Date" heading | Table sorted ascending | Pass |
| TC17 | Planner | Add topic and mark completed | tick "Mark as Completed" | Progress tracker updates | Pass |
| TC18 | Planner | Add topic with negative hours | -2 | "must be a valid positive number" error | Pass |
| TC19 | Progress | View subject progress | open Progress tab | Correct % shown, matches completed/total | Pass |
| TC20 | Reports | Generate Daily Report | select "Daily" | Shows today's plan entries | Pass |
| TC21 | Reports | Generate Subject Report | select subject | Shows topics, exams and % progress | Pass |
| TC22 | Reports | Export report to .txt | click Export | File saved successfully at chosen path | Pass |
| TC23 | General | Delete a subject with exams linked | delete "Maths" | Cascade delete works, no orphan rows | Pass |
| TC24 | General | Logout and re-login | click logout | Returns to login screen correctly | Pass |

**Result:** All 24 test cases passed successfully. No critical bugs found.

## Exception Handling Verified
- Database connection errors are caught and shown as message boxes instead
  of crashing the app.
- All Add/Update/Delete operations are wrapped in try/except blocks.
- Form validation prevents bad data from ever reaching the database.
