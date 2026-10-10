# SIPOC Process Map & Critical-to-Quality (CTQ) Tree
## BBAT104 TQM Course Project — Online Quiz System

---

## 1. SIPOC Process Map

The SIPOC model (Suppliers, Inputs, Process, Outputs, Customers) systematically defines the end-to-end flow of the Online Quiz System:

```mermaid
flowchart LR
    S["<b>SUPPLIERS</b><br/>• Faculty / Teachers<br/>• Subject Matter Experts<br/>• System Administrators<br/>• AI Knowledge Base"] --> I["<b>INPUTS</b><br/>• Curriculum Topics<br/>• Question Prompts & Keys<br/>• Duration & Pass Criteria<br/>• Student Enrollment Data"]
    I --> P["<b>PROCESS</b><br/>1. Quiz Creation (Manual/AI)<br/>2. Join Code Generation<br/>3. Candidate Exam Launch<br/>4. Anti-Cheat Monitoring<br/>5. Instant Auto-Grading<br/>6. Gradebook Sync & Backup"]
    P --> O["<b>OUTPUTS</b><br/>• Active 6-Char Join Codes<br/>• Proctored Exam Sessions<br/>• Zero-Latency Scorecards<br/>• Faculty Gradebook Reports<br/>• Automated DB Backups"]
    O --> C["<b>CUSTOMERS</b><br/>• Enrolled Students<br/>• Course Instructors<br/>• Academic Audit Committee<br/>• Institutional Administrators"]
```

### Detailed SIPOC Matrix

| Element | Description & Specifications |
|---|---|
| **Suppliers** | • **Faculty/Examiners:** Provide syllabus requirements, question banks, and grading criteria.<br/>• **AI Model / Knowledge Engine:** Generates structured domain questions on-demand.<br/>• **Administrators:** Provision system configurations, monitor SQLite integrity. |
| **Inputs** | • **Question Specifications:** Text, choices, answer keys, explanations, duration (minutes).<br/>• **Student Inputs:** Candidate credentials, 6-character access codes, chosen responses. |
| **Process Steps** | 1. **Assessment Initialization:** Teacher compiles or AI synthesizes quiz; database stores records.<br/>2. **Distribution:** Teacher shares unique join code (`QZ-XXXX`) with students.<br/>3. **Examination Execution:** Student opens test, timer countdown begins, focus monitoring activates.<br/>4. **Submission & Grading:** Server/local engine calculates percentage and pass/fail designation under 250ms.<br/>5. **Archival & Reporting:** Results mirrored to SQLite, teacher gradebook updated, auto-backup executed. |
| **Outputs** | • **Interactive Scorecard:** Immediate student feedback, percentage, question-by-question explanations.<br/>• **Faculty Class Reports:** Complete audit table with scores, timestamps, and violation counts.<br/>• **Audit Trail & Database Snapshots:** Persistent records in SQLite and exported CSV/PDF reports. |
| **Customers** | • **Students:** Benefit from zero-latency results, transparency, and instant feedback.<br/>• **Teachers:** Benefit from reduced manual grading overhead and AI automation.<br/>• **Institution:** Benefits from authenticated academic integrity and audit compliance. |

---

## 2. Critical-to-Quality (CTQ) Tree

The CTQ Tree converts overarching student and instructor expectations into measurable operational engineering metrics:

```mermaid
graph TD
    NEED["<b>Customer Need:</b><br/>High-Integrity, Zero-Latency Examination System"]
    
    DRIVER1["<b>Quality Driver 1:</b><br/>Immediate Feedback & Speed"]
    DRIVER2["<b>Quality Driver 2:</b><br/>Assessment Integrity & Security"]
    DRIVER3["<b>Quality Driver 3:</b><br/>System Reliability & Continuity"]
    
    NEED --> DRIVER1
    NEED --> DRIVER2
    NEED --> DRIVER3
    
    CTQ1["<b>CTQ 1.1: Auto-Grading Latency</b><br/>Requirement: < 250ms per test"]
    CTQ2["<b>CTQ 1.2: Exam Launch Speed</b><br/>Requirement: < 1.0s to load questions"]
    
    CTQ3["<b>CTQ 2.1: Anti-Cheat Focus Tracking</b><br/>Requirement: 100% of window blurs logged"]
    CTQ4["<b>CTQ 2.2: Poka-Yoke Validation</b><br/>Requirement: Zero empty or malformed questions"]
    
    CTQ5["<b>CTQ 3.1: Database Recovery Point</b><br/>Requirement: Automated timestamped backups"]
    CTQ6["<b>CTQ 3.2: Grading Consistency</b><br/>Requirement: 100% match with expected key"]
    
    DRIVER1 --> CTQ1
    DRIVER1 --> CTQ2
    DRIVER2 --> CTQ3
    DRIVER2 --> CTQ4
    DRIVER3 --> CTQ5
    DRIVER3 --> CTQ6
```

### Operational Definitions of CTQ Metrics

1. **Submission-to-Score Latency:** Time elapsed between student pressing "Submit Assessment" and the rendering of the scorecard. (Target: `< 250ms`).
2. **Cheat Detection Efficacy:** Binary capture of OS/browser window focus loss events during active testing. (Target: `100% capture rate`).
3. **Poka-Yoke Input Error Rate:** Percentage of attempts allowed to proceed with unselected choices or negative durations. (Target: `0.0%`).
4. **Data Availability (RPO):** Maximum allowable data loss in the event of hardware failure. (Target: `0 data loss via automated snapshot engine`).
