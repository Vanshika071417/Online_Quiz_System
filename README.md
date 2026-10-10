# Online Quiz System

A high-performance, cross-platform online examination and quiz platform for **Desktop** and **Mobile** devices.

## Repository Overview
- **Documentation:** See [ARCHITECTURE.md](file:///c:/Users/piyush/Documents/Online_Quiz_System/ARCHITECTURE.md) for complete architecture, modules, and data flow.
- **Remote Repository:** [Vanshika071417/Online_Quiz_System](https://github.com/Vanshika071417/Online_Quiz_System)

## Core Applications & Architecture

This project provides a complete dual-layer Online Quiz System built with **Python**:

1. 🖥️ **Native Python Desktop App (`desktop_app.py`)**:
   - Built with **CustomTkinter** for modern, sleek dark-themed desktop experience on Windows.
   - **Candidate Arena:** Timed tests, anti-cheat detection on focus loss, instant scorecard.
   - **Examiner Studio:** Visual quiz and question builder, difficulty, and pass-mark settings.
   - **Local SQLite & Cloud Sync:** Offline-first architecture.
   - **To Run:**
     ```bash
     python desktop_app.py
     ```

2. ⚡ **Python FastAPI Backend & Real-Time Server (`server.py`)**:
   - RESTful API for quizzes, question banks, submissions, and analytics.
   - Real-time WebSocket hub for timer sync and proctor events.
   - Also serves the responsive mobile/web assessment client (`index.html`) on any device.
   - **To Run:**
     ```bash
     python server.py
     ```

3. 📱 **Mobile & Web Responsive Client (`index.html`)**:
   - Accessible from any mobile browser or desktop browser on `http://localhost:8000`.
   - Installable PWA with offline Service Worker support and Canvas achievement certificates.
