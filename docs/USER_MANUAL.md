# User Manual & Operational Guide
## Online Quiz System (BBAT104: Fundamentals of TQM)

---

## 1. System Requirements & Quick Start

### 1.1 Prerequisites
* **Operating System:** Windows 10 / 11, macOS, or Linux.
* **Python Runtime:** Python 3.10+ installed and on system PATH.
* **Core Dependencies:**
  ```powershell
  pip install -r requirements.txt
  ```

### 1.2 Launching the Application
To start the native **Desktop Application**:
```powershell
python desktop_app.py
```

To start the **FastAPI Backend Server** (for mobile & network client access):
```powershell
python server.py
```

To generate the **TQM SQC Pareto & Fishbone charts** and database backups:
```powershell
python tqm_sqc_tools.py
```

---

## 2. Navigating the 3 Role Dashboards

### 🛡️ 2.1 Administrator Mode
1. In the top-left sidebar dropdown, select **"🛡️ Administrator"**.
2. **System Overview:** View real-time platform metrics:
   - Total Quizzes created across faculty.
   - Aggregate candidate submissions.
   - Platform-wide average pass rate.
   - Active faculty and student counts.
3. **Audit Activity Feed:** Scroll through recent submissions with scores, timestamps, and proctor violation flags.
4. **Maintenance:** Trigger automated SQLite snapshots into `backups/`.

---

### 👩‍🏫 2.2 Teacher / Faculty Mode
1. In the top-left sidebar dropdown, select **"👩‍🏫 Teacher / Faculty"**.
2. **Creating a Quiz via AI:**
   - Click **"🤖 Generate with AI"** in the sidebar.
   - Enter your topic (e.g. *Operating Systems Memory Paging*, *Python OOP*, *SQL Joins*).
   - Select question count (3, 5, 8, 10), difficulty (*Beginner, Medium, Advanced*), and exam duration.
   - Click **"⚡ Generate & Publish Quiz with AI"**.
   - Note the generated **Student Join Code** (e.g. `QZ-1001`).
3. **Creating a Quiz Manually:**
   - Click **"+ Manual Create"** from the Question Banks view.
   - Enter assessment title, duration, question text, 4 choices, and select the correct answer.
   - Click **"Publish Quiz"**.
4. **Class Reports & Submissions:**
   - Click **"📊 Class Reports"** to view individual student scorecards, percentage, pass/fail status, and anti-cheat infraction logs.

---

### 🎓 2.3 Student / Candidate Mode
1. In the top-left sidebar dropdown, select **"🎓 Student"**.
2. **Joining with a Code:**
   - In the **"🔑 Enter Quiz Code to Join"** box, type the 6-character code given by your teacher (e.g. `QZ-1001`).
   - Enter your candidate name.
   - Click **"Join Assessment ⚡"**.
3. **Taking the Exam:**
   - View the active question, code snippet (if present), and choices.
   - Watch the live **⏱️ Countdown Timer** in the top right.
   - **Anti-Cheat Warning:** Do not switch windows or minimize the application. Any window blur will trigger an immediate alert and increment your violation counter.
   - Use **"← Previous"** and **"Next Question →"** to navigate.
4. **Submitting & Reviewing Results:**
   - Click **"Finalize & Submit"**.
   - Your scorecard will appear immediately with your percentage and pass/fail badge.
   - Scroll down to inspect the detailed answer breakdown with explanations.
   - Your report is automatically recorded into your instructor's gradebook.

---

## 3. Mobile / Android Client Access

1. Ensure `python server.py` is running on your host machine.
2. Note your computer's local IP address (e.g. `192.168.1.15`).
3. On your Android phone, open Chrome or Firefox and navigate to `http://192.168.1.15:8000`.
4. Enter the same **Quiz Code** (`QZ-1001`) to complete the assessment on your mobile device.
