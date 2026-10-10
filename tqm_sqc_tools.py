"""
Statistical Quality Control (SQC) & TQM Tools Automation
Generates:
1. Pareto Analysis (80/20 Rule) Chart via Matplotlib
2. Ishikawa (Fishbone) Diagram (Root Cause Analysis)
3. Automated SQLite Database Backup Engine (Q20: Auto Backup)
4. CSV Class Gradebook Export Engine (Q20: Export Reports)
"""

import os
import shutil
import sqlite3
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

CHARTS_DIR = "sqc_charts"
BACKUPS_DIR = "backups"
REPORTS_DIR = "reports"
DB_PATH = "quiz_system.db"

os.makedirs(CHARTS_DIR, exist_ok=True)
os.makedirs(BACKUPS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)


def generate_pareto_chart():
    """Generates an 80/20 Pareto Chart analyzing defects and failure categories."""
    defect_data = {
        "Defect Category": [
            "Window Focus Loss / App Switch",
            "Typo in Quiz Join Code",
            "Network Latency Hiccup",
            "Unanswered / Skipped Questions",
            "Option Radio Misclick",
            "Database Lock Contention"
        ],
        "Frequency": [48, 22, 14, 9, 5, 2]
    }

    df = pd.DataFrame(defect_data)
    df = df.sort_values(by="Frequency", ascending=False).reset_index(drop=True)
    df["CumulativePercentage"] = (df["Frequency"].cumsum() / df["Frequency"].sum()) * 100

    fig, ax1 = plt.subplots(figsize=(10, 6), dpi=150)
    plt.title("Pareto Analysis of Assessment System Quality Defects (80/20 Rule)", fontsize=14, fontweight="bold", pad=15)

    # Bar Chart for Defect Frequencies
    ax1.set_xticks(range(len(df["Defect Category"])))
    bars = ax1.bar(range(len(df["Defect Category"])), df["Frequency"], color="#4f46e5", edgecolor="#312e81", width=0.6)
    ax1.set_ylabel("Defect Frequency (Count)", color="#4f46e5", fontsize=11, fontweight="bold")
    ax1.set_xticklabels(df["Defect Category"], rotation=25, ha="right", fontsize=9)
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    for bar in bars:
        height = bar.get_height()
        ax1.annotate(f"{height}",
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points",
                     ha="center", va="bottom", fontsize=9, fontweight="bold")

    # Secondary Axis for Cumulative Percentage Line
    ax2 = ax1.twinx()
    ax2.plot(range(len(df["Defect Category"])), df["CumulativePercentage"], color="#ef4444", marker="o", linewidth=2.5, markersize=6)
    ax2.set_ylabel("Cumulative Percentage (%)", color="#ef4444", fontsize=11, fontweight="bold")
    ax2.set_ylim(0, 110)
    ax2.yaxis.set_major_formatter(ticker.PercentFormatter())

    # 80% Threshold reference line
    ax2.axhline(80, color="#f59e0b", linestyle="--", linewidth=1.5, label="80% Vital Few Threshold")
    ax2.legend(loc="center right")

    output_path = os.path.join(CHARTS_DIR, "pareto_analysis.png")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"[SQC] Pareto Chart successfully generated: {output_path}")
    return output_path


def generate_fishbone_diagram():
    """Generates an Ishikawa (Fishbone) Diagram for Root Cause Analysis."""
    fig, ax = plt.subplots(figsize=(12, 7), dpi=150)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")

    # Main Backbone
    ax.annotate("", xy=(8.5, 4), xytext=(1.0, 4), arrowprops=dict(arrowstyle="->", lw=3.5, color="#0f172a"))
    ax.text(8.7, 4, "Submission &\nGrading Latency\n(Quality Defect)", fontsize=11, fontweight="bold",
            color="white", va="center", bbox=dict(boxstyle="round,pad=0.5", facecolor="#ef4444", edgecolor="#991b1b", alpha=0.9))

    # Major Rib Categories: People, Process, Software Code, Infrastructure
    categories = [
        ("PEOPLE\n(User Behavior)", 2.5, 4, 2.5, 6.5, [
            "Lack of exam familiarity", "Window/App switching", "Accidental clicks"
        ]),
        ("SOFTWARE CODE\n(Algorithm & Logic)", 5.5, 4, 5.5, 6.5, [
            "Synchronous nested loops", "Unindexed SQL lookups", "Missing input validation"
        ]),
        ("PROCESS\n(Workflow & Rules)", 2.5, 4, 2.5, 1.5, [
            "Ambiguous quiz rules", "Manual grading delays", "No retry on timeout"
        ]),
        ("INFRASTRUCTURE\n(Hardware & Network)", 5.5, 4, 5.5, 1.5, [
            "Unstable Wi-Fi drops", "Database disk contention", "Memory constraints"
        ]),
    ]

    for title, x_start, y_start, x_end, y_end, causes in categories:
        # Rib line
        ax.plot([x_start, x_end], [y_start, y_end], lw=2.2, color="#4f46e5")
        ax.text(x_end, y_end + (0.3 if y_end > y_start else -0.5), title, fontsize=10,
                fontweight="bold", ha="center", bbox=dict(boxstyle="square,pad=0.3", facecolor="#e0e7ff", edgecolor="#4f46e5"))

        # Branches / Causes
        step = (y_end - y_start) / (len(causes) + 1)
        for i, cause in enumerate(causes):
            branch_y = y_start + step * (i + 1)
            branch_x = x_start + ((x_end - x_start) / (len(causes) + 1)) * (i + 1)
            offset = -1.2 if y_end > y_start else -1.2
            ax.plot([branch_x, branch_x + offset], [branch_y, branch_y], lw=1.2, color="#64748b", linestyle=":")
            ax.text(branch_x + offset, branch_y + 0.1, cause, fontsize=8, ha="right" if offset < 0 else "left", color="#1e293b")

    plt.title("Ishikawa (Fishbone) Cause-and-Effect Diagram for Zero-Latency Auto-Grading",
              fontsize=13, fontweight="bold", pad=20)

    output_path = os.path.join(CHARTS_DIR, "ishikawa_fishbone.png")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"[SQC] Fishbone Diagram successfully generated: {output_path}")
    return output_path


def run_automated_db_backup():
    """Automates SQLite database backup snapshot into backups/ folder (Q20 Quality Goal)."""
    if not os.path.exists(DB_PATH):
        print(f"[Backup] Database {DB_PATH} not yet created.")
        return None

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUPS_DIR, f"quiz_backup_{timestamp}.db")
    shutil.copy2(DB_PATH, backup_file)
    print(f"[Backup] Successfully generated database snapshot: {backup_file}")
    return backup_file


def export_class_reports_to_csv():
    """Exports structured student submission gradebook to CSV format (Q20: Export Reports)."""
    if not os.path.exists(DB_PATH):
        return None

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cols = [c[1] for c in cursor.execute("PRAGMA table_info(attempts)").fetchall()]
    if "join_code" not in cols:
        cursor.execute("ALTER TABLE attempts ADD COLUMN join_code TEXT DEFAULT 'QZ-1001'")
    if "teacher_name" not in cols:
        cursor.execute("ALTER TABLE attempts ADD COLUMN teacher_name TEXT DEFAULT 'Prof. Alan Turing'")
    if "student_name" not in cols:
        if "candidate_name" in cols:
            name_col = "candidate_name AS student_name"
        else:
            cursor.execute("ALTER TABLE attempts ADD COLUMN student_name TEXT DEFAULT 'Student'")
            name_col = "student_name"
    else:
        name_col = "student_name"
    conn.commit()

    query = f"""
        SELECT id, quiz_title, join_code, teacher_name, {name_col}, score, total_questions,
               percentage, CASE WHEN passed = 1 THEN 'PASSED' ELSE 'FAILED' END AS result_status,
               cheat_violations, submitted_at
        FROM attempts
        ORDER BY submitted_at DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    csv_file = os.path.join(REPORTS_DIR, f"Class_Gradebook_Report_{timestamp}.csv")
    df.to_csv(csv_file, index=False)
    print(f"[Reports] Exported class gradebook to CSV: {csv_file}")
    return csv_file


if __name__ == "__main__":
    print("Executing Statistical Quality Control (SQC) Analysis...")
    pareto = generate_pareto_chart()
    fishbone = generate_fishbone_diagram()
    backup = run_automated_db_backup()
    report = export_class_reports_to_csv()
    print("SQC Automation Cycle Complete! All quality artefacts ready.")
