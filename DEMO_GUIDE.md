# Live Demonstration Guide & Examiner Evaluation Script
## Online Quiz System (QuizSphere Pro) — Review 1

This guide provides exact, step-by-step walkthroughs to demonstrate the fully functional **Web Application** and **Desktop Application** to the evaluation committee.

---

## 1. Quick Launch Summary

### Terminal 1: Start the Web Backend & SPA Server
```powershell
# In project root:
python server.py
```
> Server will boot at **`http://localhost:8000`** with real-time reload, zero startup warnings, and auto-seeded database.

### Terminal 2: Start the Standalone Desktop Application
```powershell
# In project root:
python desktop_app.py
```
> The native CustomTkinter desktop interface will launch immediately.

### Terminal 3: Run Automated Verification Tests
```powershell
python -m pytest tests/
```
> Executes all 22 automated unit tests across web auth, desktop auth, join code workflows, admin analytics, and architectural specs.

---

## 2. Test Account Credentials

| Role | Username | Password | Full Name | Department / Purpose |
|---|---|---|---|---|
| **Student** | `student` | `student123` | Alex Mercer | B.Tech CSE - 2026 (Assessment & Proctoring Demo) |
| **Faculty** | `faculty` | `faculty123` | Prof. Alan Turing | Computer Science (Quiz Creation & Gradebook Demo) |
| **Admin** | `admin` | `admin123` | System Administrator | Quality Assurance (Telemetry & CSV Export Demo) |

---

## 3. Web Application Demonstration Walkthrough

### Scenario A: Student Assessment & Anti-Cheat Demonstration
1. Open your browser and navigate to **`http://localhost:8000`**.
2. Click **Sign In** in the top navigation bar.
3. Enter credentials:
   - **Username:** `student`
   - **Password:** `student123`
4. Notice the navigation dynamically updates:
   - Displays **`Alex Mercer (Student)`**.
   - **Examiner Studio** and **Admin Panel** tabs are cleanly removed to enforce Role-Based Access Control (RBAC).
5. In the **Candidate Arena**, locate the **Join Code** input field.
6. Enter active quiz code: **`QZ-1001`** and click **Start Assessment**.
7. The assessment loads instantly (<25ms):
   - Notice the authoritative countdown timer ticking down in the header.
   - Click between questions using the question palette.
   - Select answers for questions 1 through 5.
8. **Demonstrate Anti-Cheat Proctoring:**
   - Switch browser tabs or minimize the browser window.
   - Switch back to the quiz tab.
   - Observe the live notification: **"Proctor Alert: Tab switch or focus loss detected!"**
   - The proctor violation counter increments in real time.
9. Click **Submit Assessment**.
10. **Demonstrate Zero-Latency Grading:**
    - Within 25 milliseconds, the **Performance Scorecard** appears showing:
      - Final percentage score and Pass/Fail badge.
      - Proctor violation tally.
      - Question-by-question breakdown with green/red answer keys and educational explanations.

---

### Scenario B: Faculty/Examiner Studio Demonstration
1. Click the user profile chip in the top nav and click **Sign Out**.
2. Sign in with Faculty credentials:
   - **Username:** `faculty`
   - **Password:** `faculty123`
3. Notice the navigation changes:
   - Displays **`Prof. Alan Turing (Faculty)`**.
   - Student Arena and Admin Panel are hidden; **Examiner Studio** is front and center.
4. **Demonstrate Manual & AI Quiz Creation (CRUD - Create):**
   - Click the **AI Quiz Generator** button.
   - Enter topic: `"Data Structures & Algorithms"`, Difficulty: `"Medium"`, Questions: `5`.
   - Click **Generate with AI**. Within seconds, 5 verified questions with options and explanations populate the builder.
   - Set Title: `"Data Structures Review Test"`, Duration: `15 mins`, Passing Mark: `70%`.
   - Click **Save & Publish Quiz**.
   - The system displays a newly minted unique 6-character code (e.g., **`QZ-3942`**).
5. **Demonstrate Class Gradebook (CRUD - Read):**
   - Click **Class Submission Gradebook**.
   - View student submissions for your quizzes, showing Candidate Names, Join Codes, Percentages, and any Proctor Violations logged during their attempt.

---

### Scenario C: Admin Governance & Telemetry Demonstration
1. Sign out and sign in with Admin credentials:
   - **Username:** `admin`
   - **Password:** `admin123`
2. Click **Admin Panel** in the top navigation.
3. **Demonstrate Platform Telemetry:**
   - View top KPI cards: Total Registered Accounts, Enrolled Candidates, Faculty & Examiners, and Proctor Violations.
4. **Demonstrate User Governance Roster:**
   - Filter by role (e.g., select *Student* or *Faculty*).
   - Use the live search bar to search for `"Alex Mercer"` or `"student"`.
   - Table updates instantly showing quizzes taken, average scores, and violation flags.
5. **Demonstrate Candidate Performance Drill-down:**
   - Click **View Report** on any student row.
   - A modal scorecard opens showing their entire historical attempt record.
6. **Demonstrate CSV Export Reports:**
   - Click **Export Roster CSV** — downloads `quizsphere_users_roster.csv`.
   - Click **Export Submissions CSV** — downloads `all_quiz_submissions_audit.csv`.

---

## 4. Desktop Application Demonstration Walkthrough

1. Run `python desktop_app.py` in your terminal.
2. The native desktop authentication screen appears.
3. Sign in as **`admin`** / **`admin123`**.
4. **Demonstrate UI & Layout Excellence:**
   - Notice the top navigation bar with clean modern typography (`Candidate Arena`, `Examiner Studio`, `Admin Panel`, `Light`/`Dark`, `Contrast`, `Focus`, `Sign Out`).
   - Click **Admin Panel**:
     - View 4 colored metric cards with accent indicator stripes (`#3b82f6` Blue, `#10b981` Green, `#8b5cf6` Purple, `#f59e0b` Amber).
     - Inspect the table: compact 44px rows, perfect grid column alignment, candidate names and usernames properly grouped with zero vertical detachment.
     - Click **View Report** on any user to inspect the desktop modal scorecard.
5. **Demonstrate Theme & Accessibility:**
   - Click the **Light / Dark** button to toggle between Warm Cream Mode and High-Contrast Dark Mode.
   - Click **A+** and **A-** to show dynamic responsive font scaling.
   - Click **Focus** to toggle minimal distraction mode.
6. Click **Sign Out** to show the crimson `#dc2626` styled button and return to the login screen.

---

## 5. Automated Unit Test Suite Verification

Run the test suite in front of evaluators to verify defect prevention:
```powershell
python -m pytest tests/ -v
```

### Expected Output Summary:
```
tests/test_admin_panel.py .....                                          [ 22%]
tests/test_architecture_spec.py ......                                   [ 50%]
tests/test_desktop_auth.py ...                                           [ 63%]
tests/test_join_code_workflow.py .                                       [ 68%]
tests/test_web_auth.py .......                                            [100%]

============================== 22 passed in ~3.5s ==============================
```

All 22 tests pass with zero errors, verifying:
- Authentication, session caching, and password hashing.
- Role-based tab segregation on both Web and Desktop.
- Join code generation, lookup, and atomic exam submission.
- Admin KPI aggregation and user report data pipelines.
- FastAPI lifespan handlers and zero deprecated startup warnings.
