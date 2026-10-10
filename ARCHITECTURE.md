# Online Quiz System - Architecture Design

## 1. System Overview

The **Online Quiz System** is a multi-platform platform designed to deliver secure, responsive, and real-time assessments across both **Desktop** and **Mobile** environments, backed by a unified backend service.

```mermaid
graph TD
    subgraph Clients ["Client Applications"]
        D[Desktop App<br/>Admin / Examiner / Candidate]
        M[Mobile App<br/>Candidate / Quiz Taker]
    end

    subgraph Gateway ["API & Network Layer"]
        AG[API Gateway / Reverse Proxy]
        WS[WebSocket / Real-Time Gateway]
    end

    subgraph Backend ["Backend Services"]
        AUTH[Auth & User Service]
        QUIZ[Quiz & Question Bank Service]
        SESSION[Exam Session & Timer Engine]
        PROCTOR[Proctoring & Anti-Cheating Service]
        ANALYTICS[Grading & Analytics Service]
    end

    subgraph Data ["Data Storage & Caching"]
        DB[(Primary Database: PostgreSQL)]
        CACHE[(Cache & PubSub: Redis)]
        STORAGE[(Blob Storage: S3 / Cloud Storage)]
    end

    D -->|HTTPS REST| AG
    D -->|WSS Socket| WS
    M -->|HTTPS REST| AG
    M -->|WSS Socket| WS

    AG --> AUTH
    AG --> QUIZ
    AG --> PROCTOR
    AG --> ANALYTICS

    WS --> SESSION

    AUTH --> DB
    QUIZ --> DB
    SESSION --> CACHE
    PROCTOR --> STORAGE
    ANALYTICS --> DB
```

---

## 2. Platform Requirements & Roles

### 2.1 User Roles
1. **Candidate / Student (Mobile & Desktop):**
   - Browse public quizzes or join via invite/code.
   - Timed quiz taking with offline/intermittent connectivity recovery.
   - Instant review, scorecards, leaderboards, and detailed explanations.
2. **Examiner / Instructor (Primarily Desktop):**
   - Rich quiz builder (Multiple choice, code snippet, true/false, subjective, fill-in-the-blank).
   - Question banks with tagging, difficulty levels, and automated randomization.
   - Live monitoring of active candidates (progress, live score tracker).
3. **Administrator (Desktop):**
   - Role-based access control (RBAC), user management, compliance, and audit logs.

---

## 3. Recommended Technology Stack

| Layer | Selected Architecture | Implementation Details |
|---|---|---|
| **Client UI (Desktop & Mobile)** | **Responsive Progressive Web App (PWA)** | Built with semantic HTML5, modern vanilla CSS3 (design tokens, glassmorphism, micro-animations), and modular ES6 JavaScript. Fully installable as a standalone app on Windows, macOS, Android, and iOS. |
| **Backend & Real-Time Sync** | **Firebase / Supabase** | Real-time database, Firestore/PostgreSQL, authentication, and live presence/session synchronization with offline-first local persistence. |
| **State & Storage Engine** | **Dual Engine (Cloud + Local)** | Active test state, question responses, and countdown timer are mirrored in local storage and synced with Firebase in real time for resilience against network loss. |
| **Security & Proctoring** | **Browser Event Monitor** | Fullscreen API lockdown, Page Visibility API (`visibilitychange`), window blur/focus tracking, and clipboard restriction. |

---

## 4. Key Architectural Modules

### 4.1 Quiz & Question Engine
- **Question Schema:** JSON-driven flexible question types (Single Choice, Multi-Select, Numerical, Code Snippet, Matching).
- **Randomization & Shuffling:** Seeded shuffling per candidate to minimize collusion while ensuring uniform grading.
- **Auto-Grading Pipeline:** Immediate calculation for objective questions, queued asynchronous evaluation for complex submissions.

### 4.2 Real-time Exam Session & Timer Service
- **Server-Authoritative Clock:** Prevents device clock manipulation.
- **Heartbeat & Reconnection:** Automatic state recovery if network drops; local caching of answers until verified by server.
- **Anti-Cheating / Proctoring Basics:**
  - Desktop: Focus-loss / window-blur tracking, full-screen lock mode.
  - Mobile: App minimize / background detection, screen-lock alerts.

### 4.3 Analytics & Reporting
- Detailed question-wise breakdown (accuracy, average time per question).
- Score normalization, percentile calculations, and PDF certificate/report generation.

---

## 5. Proposed Project Folder Structure

```text
Online_Quiz_System/
├── apps/
│   ├── client/                  # Cross-platform Client (Flutter or React Native/Desktop)
│   │   ├── lib/
│   │   │   ├── core/            # Network, auth tokens, themes, router
│   │   │   ├── features/
│   │   │   │   ├── auth/        # Login, registration, profile
│   │   │   │   ├── quiz_taker/  # Exam view, question card, timer, review
│   │   │   │   ├── quiz_maker/  # Question builder, quiz settings (Desktop)
│   │   │   │   ├── dashboard/   # Recent tests, analytics, reports
│   │   │   └── main.dart
│   │   └── pubspec.yaml
│   └── server/                  # Backend API & WebSocket Server
│       ├── src/
│       │   ├── auth/
│       │   ├── quiz/
│       │   ├── session/
│       │   ├── analytics/
│       │   └── common/
│       └── package.json
├── docs/                        # Architecture diagrams, API specs
├── .gitignore
├── ARCHITECTURE.md
└── README.md
```
