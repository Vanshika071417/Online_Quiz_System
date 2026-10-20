"""
Generate a high-resolution, professional Entity-Relationship (ER) Diagram
image for the Online Quiz System (QuizSphere Pro).
Saves to: docs/assets/er_diagram.png
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_er_diagram():
    os.makedirs('docs/assets', exist_ok=True)
    os.makedirs('assets', exist_ok=True)

    fig, ax = plt.subplots(figsize=(24, 15), facecolor='#0B0F19')
    ax.set_facecolor('#0B0F19')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Color tokens
    C_HEADER = '#1E293B'
    C_BORDER = '#334155'
    C_PK = '#F59E0B'      # Amber
    C_FK = '#38BDF8'      # Sky Blue
    C_ATTR = '#E2E8F0'    # Slate light
    C_TYPE = '#94A3B8'    # Slate muted
    C_CONN = '#64748B'    # Connector line

    # Domain Header Colors
    DOM_TENANCY = '#3B82F6'   # Blue
    DOM_QUIZ = '#8B5CF6'      # Violet
    DOM_ATTEMPT = '#10B981'   # Emerald
    DOM_GRADE = '#F43F5E'     # Rose
    DOM_AUDIT = '#F59E0B'     # Amber
    DOM_CORE = '#06B6D4'      # Cyan

    # Title Block
    ax.text(50, 97.5, "QuizSphere Pro — Complete Entity-Relationship (ER) Architecture",
            ha='center', va='center', fontsize=22, fontweight='bold', color='#FFFFFF')
    ax.text(50, 95.2, "Production Multi-Tenant Modular Schema & Core SQLite Runtime Engine · BBAT104 TQM Q20",
            ha='center', va='center', fontsize=12, color='#94A3B8')

    def draw_entity(x, y, w, h, title, domain_color, fields):
        """Draw an entity box with header, field rows, PK/FK flags, and types."""
        # Main background box
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2,rounding_size=0.8",
                                      linewidth=1.2, edgecolor=C_BORDER, facecolor='#151E2E')
        ax.add_patch(rect)

        # Header box
        hdr_h = 3.2
        hdr_rect = patches.FancyBboxPatch((x, y + h - hdr_h), w, hdr_h,
                                          boxstyle="round,pad=0.2,rounding_size=0.8",
                                          linewidth=1.2, edgecolor=C_BORDER, facecolor=C_HEADER)
        ax.add_patch(hdr_rect)

        # Domain accent strip
        accent = patches.Rectangle((x, y + h - 0.5), w, 0.5, facecolor=domain_color, edgecolor='none')
        ax.add_patch(accent)

        # Header title
        ax.text(x + w / 2, y + h - 1.8, title, ha='center', va='center',
                fontsize=11.5, fontweight='bold', color='#FFFFFF')

        # Fields
        row_y = y + h - 4.5
        for field in fields:
            name = field['name']
            ftype = field.get('type', '')
            is_pk = field.get('pk', False)
            is_fk = field.get('fk', False)

            # Prefix badge
            if is_pk and is_fk:
                tag = "PK, FK"
                tag_color = C_PK
            elif is_pk:
                tag = "PK"
                tag_color = C_PK
            elif is_fk:
                tag = "FK"
                tag_color = C_FK
            else:
                tag = "  "
                tag_color = C_TYPE

            ax.text(x + 1.2, row_y, tag, ha='left', va='center', fontsize=8.5, fontweight='bold', color=tag_color)
            ax.text(x + 5.0, row_y, name, ha='left', va='center', fontsize=9.2, color=C_ATTR)
            ax.text(x + w - 1.2, row_y, ftype, ha='right', va='center', fontsize=8.2, color=C_TYPE)
            row_y -= 1.8

    # ---------------- ENTITY DEFINITIONS ----------------

    # 1. TENANTS (Col 1, Top)
    tenants_fields = [
        {'name': 'id', 'type': 'VARCHAR(64)', 'pk': True},
        {'name': 'name', 'type': 'VARCHAR(255)'},
        {'name': 'domain', 'type': 'VARCHAR(255)'},
        {'name': 'settings_json', 'type': 'TEXT'},
        {'name': 'created_at', 'type': 'DATETIME'}
    ]
    draw_entity(3, 76, 21, 15, "tenants", DOM_TENANCY, tenants_fields)

    # 2. PLATFORM USERS (Col 1, Mid)
    users_fields = [
        {'name': 'id', 'type': 'VARCHAR(64)', 'pk': True},
        {'name': 'tenant_id', 'type': 'VARCHAR(64)', 'fk': True},
        {'name': 'username', 'type': 'VARCHAR(100)'},
        {'name': 'email', 'type': 'VARCHAR(255)'},
        {'name': 'hashed_password', 'type': 'VARCHAR(255)'},
        {'name': 'full_name', 'type': 'VARCHAR(255)'},
        {'name': 'role', 'type': 'VARCHAR(50)'},
        {'name': 'department', 'type': 'VARCHAR(150)'},
        {'name': 'is_active', 'type': 'BOOLEAN'},
        {'name': 'extra_time_percent', 'type': 'INTEGER'},
        {'name': 'created_at', 'type': 'DATETIME'}
    ]
    draw_entity(3, 44, 21, 26, "platform_users", DOM_TENANCY, users_fields)

    # 3. QUIZZES_V2 (Col 2, Top)
    quizzes_fields = [
        {'name': 'id', 'type': 'VARCHAR(64)', 'pk': True},
        {'name': 'tenant_id', 'type': 'VARCHAR(64)', 'fk': True},
        {'name': 'title', 'type': 'VARCHAR(255)'},
        {'name': 'category', 'type': 'VARCHAR(100)'},
        {'name': 'join_code', 'type': 'VARCHAR(20)'},
        {'name': 'teacher_name', 'type': 'VARCHAR(150)'},
        {'name': 'duration_minutes', 'type': 'INTEGER'},
        {'name': 'passing_score', 'type': 'INTEGER'},
        {'name': 'status', 'type': 'VARCHAR(30)'},
        {'name': 'current_version_id', 'type': 'VARCHAR(64)'},
        {'name': 'created_at', 'type': 'DATETIME'}
    ]
    draw_entity(27, 69, 21, 25, "quizzes_v2", DOM_QUIZ, quizzes_fields)

    # 4. QUIZ_VERSIONS (Col 2, Mid)
    quiz_ver_fields = [
        {'name': 'id', 'type': 'VARCHAR(64)', 'pk': True},
        {'name': 'quiz_id', 'type': 'VARCHAR(64)', 'fk': True},
        {'name': 'version_number', 'type': 'INTEGER'},
        {'name': 'snapshot_json', 'type': 'TEXT'},
        {'name': 'published_by_id', 'type': 'VARCHAR(64)'},
        {'name': 'published_at', 'type': 'DATETIME'}
    ]
    draw_entity(27, 44, 21, 18, "quiz_versions", DOM_QUIZ, quiz_ver_fields)

    # 5. ATTEMPTS_V2 (Col 3, Mid-Top)
    attempts_fields = [
        {'name': 'id', 'type': 'VARCHAR(64)', 'pk': True},
        {'name': 'tenant_id', 'type': 'VARCHAR(64)', 'fk': True},
        {'name': 'quiz_id', 'type': 'VARCHAR(64)', 'fk': True},
        {'name': 'quiz_version_id', 'type': 'VARCHAR(64)', 'fk': True},
        {'name': 'learner_id', 'type': 'VARCHAR(64)', 'fk': True},
        {'name': 'learner_name', 'type': 'VARCHAR(255)'},
        {'name': 'state', 'type': 'VARCHAR(30)'},
        {'name': 'started_at', 'type': 'DATETIME'},
        {'name': 'deadline_at', 'type': 'DATETIME'},
        {'name': 'submitted_at', 'type': 'DATETIME'},
        {'name': 'form_seed', 'type': 'INTEGER'},
        {'name': 'cheat_violations', 'type': 'INTEGER'},
        {'name': 'idempotency_key', 'type': 'VARCHAR(128)'}
    ]
    draw_entity(51, 52, 22, 30, "attempts_v2", DOM_ATTEMPT, attempts_fields)

    # 6. ATTEMPT_ANSWERS_V2 (Col 3, Low)
    answers_fields = [
        {'name': 'id', 'type': 'VARCHAR(64)', 'pk': True},
        {'name': 'attempt_id', 'type': 'VARCHAR(64)', 'fk': True},
        {'name': 'item_id', 'type': 'VARCHAR(64)'},
        {'name': 'answer_payload_json', 'type': 'TEXT'},
        {'name': 'revision', 'type': 'INTEGER'},
        {'name': 'idempotency_key', 'type': 'VARCHAR(128)'},
        {'name': 'saved_at', 'type': 'DATETIME'}
    ]
    draw_entity(51, 27, 22, 19, "attempt_answers_v2", DOM_ATTEMPT, answers_fields)

    # 7. GRADES_V2 (Col 4, Top)
    grades_fields = [
        {'name': 'id', 'type': 'VARCHAR(64)', 'pk': True},
        {'name': 'attempt_id', 'type': 'VARCHAR(64)', 'fk': True},
        {'name': 'score', 'type': 'FLOAT'},
        {'name': 'total_points', 'type': 'FLOAT'},
        {'name': 'percentage', 'type': 'FLOAT'},
        {'name': 'passed', 'type': 'BOOLEAN'},
        {'name': 'grading_policy_ver', 'type': 'VARCHAR(32)'},
        {'name': 'status', 'type': 'VARCHAR(30)'},
        {'name': 'released_at', 'type': 'DATETIME'},
        {'name': 'created_at', 'type': 'DATETIME'}
    ]
    draw_entity(76, 68, 21, 24, "grades_v2", DOM_GRADE, grades_fields)

    # 8. GRADE_FEEDBACKS_V2 (Col 4, Mid)
    feedback_fields = [
        {'name': 'id', 'type': 'VARCHAR(64)', 'pk': True},
        {'name': 'grade_id', 'type': 'VARCHAR(64)', 'fk': True},
        {'name': 'feedback_text', 'type': 'TEXT'},
        {'name': 'item_breakdown_json', 'type': 'TEXT'},
        {'name': 'created_at', 'type': 'DATETIME'}
    ]
    draw_entity(76, 47, 21, 15, "grade_feedbacks_v2", DOM_GRADE, feedback_fields)

    # 9. GRADE_APPEALS_V2 (Col 4, Low)
    appeal_fields = [
        {'name': 'id', 'type': 'VARCHAR(64)', 'pk': True},
        {'name': 'grade_id', 'type': 'VARCHAR(64)', 'fk': True},
        {'name': 'learner_id', 'type': 'VARCHAR(64)'},
        {'name': 'reason', 'type': 'TEXT'},
        {'name': 'status', 'type': 'VARCHAR(30)'},
        {'name': 'reviewer_notes', 'type': 'TEXT'},
        {'name': 'resolved_at', 'type': 'DATETIME'}
    ]
    draw_entity(76, 23, 21, 19, "grade_appeals_v2", DOM_GRADE, appeal_fields)

    # 10. AUDIT_EVENTS_V2 (Col 1, Low)
    audit_fields = [
        {'name': 'id', 'type': 'VARCHAR(64)', 'pk': True},
        {'name': 'tenant_id', 'type': 'VARCHAR(64)'},
        {'name': 'actor_id', 'type': 'VARCHAR(64)'},
        {'name': 'actor_name', 'type': 'VARCHAR(255)'},
        {'name': 'action', 'type': 'VARCHAR(100)'},
        {'name': 'target_resource', 'type': 'VARCHAR(255)'},
        {'name': 'request_id', 'type': 'VARCHAR(64)'},
        {'name': 'payload_json', 'type': 'TEXT'},
        {'name': 'timestamp', 'type': 'DATETIME'}
    ]
    draw_entity(3, 19, 21, 21, "audit_events_v2", DOM_AUDIT, audit_fields)

    # 11. OUTBOX_EVENTS_V2 (Col 2, Low)
    outbox_fields = [
        {'name': 'id', 'type': 'VARCHAR(64)', 'pk': True},
        {'name': 'event_type', 'type': 'VARCHAR(100)'},
        {'name': 'aggregate_type', 'type': 'VARCHAR(100)'},
        {'name': 'aggregate_id', 'type': 'VARCHAR(64)'},
        {'name': 'payload_json', 'type': 'TEXT'},
        {'name': 'status', 'type': 'VARCHAR(30)'},
        {'name': 'retry_count', 'type': 'VARCHAR(10)'},
        {'name': 'created_at', 'type': 'DATETIME'}
    ]
    draw_entity(27, 21, 21, 19, "outbox_events_v2", DOM_AUDIT, outbox_fields)

    # 12. RUNTIME CORE SYSTEM (Bottom Panel: users, quizzes, attempts)
    core_box = patches.FancyBboxPatch((3, 2.5), 94, 15, boxstyle="round,pad=0.2,rounding_size=0.8",
                                      linewidth=1.2, edgecolor='#0E7490', facecolor='#082F49')
    ax.add_patch(core_box)
    ax.text(50, 16.0, "CORE RUNTIME DESKTOP & LOCAL DATABASE ENGINE (Direct SQLite / Fast MVP Model)",
            ha='center', va='center', fontsize=11, fontweight='bold', color='#38BDF8')

    core_u = [
        {'name': 'id', 'type': 'TEXT', 'pk': True},
        {'name': 'username', 'type': 'TEXT UNIQUE'},
        {'name': 'password', 'type': 'TEXT (Hashed)'},
        {'name': 'role', 'type': 'TEXT'},
        {'name': 'full_name', 'type': 'TEXT'}
    ]
    draw_entity(5, 3.5, 27, 11, "users (Core Runtime)", DOM_CORE, core_u)

    core_q = [
        {'name': 'id', 'type': 'TEXT', 'pk': True},
        {'name': 'title', 'type': 'TEXT'},
        {'name': 'join_code', 'type': 'TEXT UNIQUE'},
        {'name': 'questions_json', 'type': 'TEXT (MCQ Bank)'},
        {'name': 'duration_minutes', 'type': 'INTEGER'}
    ]
    draw_entity(36.5, 3.5, 27, 11, "quizzes (Core Runtime)", DOM_CORE, core_q)

    core_a = [
        {'name': 'id', 'type': 'TEXT', 'pk': True},
        {'name': 'quiz_id', 'type': 'TEXT', 'fk': True},
        {'name': 'candidate_name', 'type': 'TEXT'},
        {'name': 'score', 'type': 'INTEGER'},
        {'name': 'cheat_violations', 'type': 'INTEGER'}
    ]
    draw_entity(68, 3.5, 27, 11, "attempts (Core Runtime)", DOM_CORE, core_a)

    # ---------------- CONNECTORS / RELATIONSHIPS ----------------
    def draw_arrow(x1, y1, x2, y2, label="", color=C_CONN):
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6",
                            color=color, lw=1.5, ls='--')
        )
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mx, my + 0.8, label, fontsize=8.5, fontweight='bold',
                    color='#CBD5E1', ha='center', va='center',
                    bbox=dict(boxstyle="round,pad=0.2", fc='#0B0F19', ec='none'))

    # tenants -> platform_users (1:N)
    draw_arrow(13.5, 76, 13.5, 70, "1 : N", DOM_TENANCY)

    # tenants -> quizzes_v2 (1:N)
    draw_arrow(24, 83.5, 27, 81.5, "1 : N", DOM_TENANCY)

    # quizzes_v2 -> quiz_versions (1:N)
    draw_arrow(37.5, 69, 37.5, 62, "1 : N (Snapshots)", DOM_QUIZ)

    # quizzes_v2 -> attempts_v2 (1:N)
    draw_arrow(48, 81.5, 51, 79, "1 : N", DOM_QUIZ)

    # quiz_versions -> attempts_v2 (1:N)
    draw_arrow(48, 53, 51, 62, "1 : N", DOM_QUIZ)

    # platform_users -> attempts_v2 (1:N)
    draw_arrow(24, 57, 51, 57, "1 : N (Submits)", DOM_TENANCY)

    # attempts_v2 -> attempt_answers_v2 (1:N)
    draw_arrow(62, 52, 62, 46, "1 : N (Monotonic)", DOM_ATTEMPT)

    # attempts_v2 -> grades_v2 (1:1)
    draw_arrow(73, 75, 76, 75, "1 : 1", DOM_GRADE)

    # grades_v2 -> grade_feedbacks_v2 (1:N)
    draw_arrow(86.5, 68, 86.5, 62, "1 : N", DOM_GRADE)

    # grades_v2 -> grade_appeals_v2 (1:N)
    draw_arrow(86.5, 47, 86.5, 42, "1 : N", DOM_GRADE)

    # core_quizzes -> core_attempts (1:N)
    draw_arrow(63.5, 9, 68, 9, "1 : N", DOM_CORE)

    # Save figure
    out_path_1 = os.path.abspath('docs/assets/er_diagram.png')
    out_path_2 = os.path.abspath('assets/er_diagram.png')
    plt.tight_layout()
    plt.savefig(out_path_1, dpi=200, bbox_inches='tight', facecolor='#0B0F19')
    plt.savefig(out_path_2, dpi=200, bbox_inches='tight', facecolor='#0B0F19')
    plt.close()
    print(f"ER diagram successfully generated:\n - {out_path_1}\n - {out_path_2}")

if __name__ == "__main__":
    draw_er_diagram()
