/**
 * QuizSphere Pro 2.0 - Enterprise Admin Panel Controller
 * Handles user management, scorecard inspection, quiz performance analytics, and report exports.
 */

(function(window) {
  'use strict';

  class AdminPanel {
    constructor() {
      this.users = [];
      this.analytics = null;
      this.currentSubTab = "users"; // users | quizzes | submissions
      this.userFilterRole = "all";
      this.userSearchQuery = "";
      this.quizSearchQuery = "";
      this.subSearchQuery = "";
      this.subResultFilter = "all";
    }

    async init() {
      await this.loadAllData();
      this.setupEventListeners();
    }

    async loadAllData() {
      if (!this._eventsBound) {
        this.setupEventListeners();
        this._eventsBound = true;
      }
      try {
        await Promise.all([
          this.fetchUsers(),
          this.fetchAnalytics()
        ]);
        this.renderKPIs();
        this.renderActiveSubTab();
      } catch (err) {
        console.error("Failed to load admin panel data:", err);
      }
    }

    async fetchUsers() {
      try {
        const res = await fetch("/api/admin/users");
        if (res.ok) {
          this.users = await res.json();
          return;
        }
      } catch (e) {
        console.warn("Server unavailable for admin users, falling back to local storage:", e);
      }

      // Offline / LocalStorage Fallback
      let localReg = [];
      try {
        localReg = JSON.parse(localStorage.getItem("quizsphere_registered_users") || "[]");
      } catch (e) {}

      const baseUsers = [
        { id: "usr-admin", username: "admin", role: "admin", full_name: "System Administrator", department: "Operations & Quality Assurance", created_at: "2026-10-01 10:00:00" },
        { id: "usr-fac-1", username: "faculty", role: "faculty", full_name: "Prof. Alan Turing", department: "Computer Science & Engineering", created_at: "2026-10-02 11:30:00" },
        { id: "usr-stu-1", username: "student", role: "student", full_name: "Alex Mercer", department: "B.Tech CSE - 2026", created_at: "2026-10-03 09:15:00" },
        ...localReg
      ];

      const attempts = (window.quizStorage && window.quizStorage.getAttempts) ? window.quizStorage.getAttempts() : [];

      this.users = baseUsers.map((u, idx) => {
        const userAttempts = attempts.filter(a => 
          (a.studentName && a.studentName.toLowerCase() === (u.full_name || "").toLowerCase()) ||
          (a.candidateName && a.candidateName.toLowerCase() === (u.full_name || "").toLowerCase()) ||
          (a.studentName && a.studentName.toLowerCase() === (u.username || "").toLowerCase())
        );

        const count = userAttempts.length;
        const passedCount = userAttempts.filter(a => a.passed).length;
        const avg = count > 0 ? Math.round(userAttempts.reduce((s, a) => s + (a.percentage || 0), 0) / count) : 0;
        const highest = count > 0 ? Math.max(...userAttempts.map(a => a.percentage || 0)) : 0;
        const violations = userAttempts.reduce((s, a) => s + (a.cheatViolations || 0), 0);

        return {
          userNo: idx + 1,
          id: u.id,
          username: u.username,
          fullName: u.full_name || u.fullName || u.username,
          role: (u.role || "student").toLowerCase(),
          department: u.department || "General",
          createdAt: u.created_at || u.createdAt || "2026-10-10 12:00:00",
          totalAttempts: count,
          passedAttempts: passedCount,
          failedAttempts: count - passedCount,
          passRate: count > 0 ? Math.round((passedCount / count) * 100) : 0,
          avgScore: avg,
          highestScore: highest,
          totalViolations: violations
        };
      });
    }

    async fetchAnalytics() {
      try {
        const res = await fetch("/api/admin/analytics");
        if (res.ok) {
          this.analytics = await res.json();
          return;
        }
      } catch (e) {
        console.warn("Server unavailable for admin analytics, falling back to local storage:", e);
      }

      // Offline fallback from window.quizStorage
      const quizzes = (window.quizStorage && window.quizStorage.getQuizzes) ? window.quizStorage.getQuizzes() : [];
      const attempts = (window.quizStorage && window.quizStorage.getAttempts) ? window.quizStorage.getAttempts() : [];

      const totalAttempts = attempts.length;
      const passedAttempts = attempts.filter(a => a.passed).length;
      const overallPassRate = totalAttempts > 0 ? Math.round((passedAttempts / totalAttempts) * 100) : 0;
      const platformAvg = totalAttempts > 0 ? Math.round(attempts.reduce((s, a) => s + (a.percentage || 0), 0) / totalAttempts) : 0;
      const totalViolations = attempts.reduce((s, a) => s + (a.cheatViolations || 0), 0);

      const quizzesAnalytics = quizzes.map(q => {
        const qAttempts = attempts.filter(a => a.quizId === q.id || a.joinCode === q.joinCode);
        const count = qAttempts.length;
        const passed = qAttempts.filter(a => a.passed).length;
        const passRate = count > 0 ? Math.round((passed / count) * 100) : 0;
        const avg = count > 0 ? Math.round(qAttempts.reduce((s, a) => s + (a.percentage || 0), 0) / count) : 0;
        const highest = count > 0 ? Math.max(...qAttempts.map(a => a.percentage || 0)) : 0;
        const lowest = count > 0 ? Math.min(...qAttempts.map(a => a.percentage || 0)) : 0;
        const viols = qAttempts.reduce((s, a) => s + (a.cheatViolations || 0), 0);

        let difficulty = "Balanced";
        if (count === 0) difficulty = "Balanced";
        else if (passRate >= 80) difficulty = "Beginner (High Pass)";
        else if (passRate >= 50) difficulty = "Balanced (Standard)";
        else difficulty = "Rigorous (Challenging)";

        return {
          id: q.id,
          title: q.title,
          category: q.category || "General",
          joinCode: q.joinCode || "QZ-1001",
          teacherName: q.author || "Prof. Alan Turing",
          durationMinutes: q.durationMinutes || 15,
          passingScore: q.passingScore || 70,
          attemptsCount: count,
          passRate: passRate,
          avgScore: avg,
          highestScore: highest,
          lowestScore: lowest,
          totalViolations: viols,
          difficultyRating: difficulty
        };
      });

      this.analytics = {
        kpis: {
          totalUsers: this.users.length,
          totalStudents: this.users.filter(u => u.role === "student").length,
          totalFaculty: this.users.filter(u => u.role === "faculty").length,
          totalQuizzes: quizzes.length,
          totalAttempts: totalAttempts,
          overallPassRate: overallPassRate,
          platformAvgScore: platformAvg,
          totalViolations: totalViolations
        },
        quizzesAnalytics: quizzesAnalytics,
        recentSubmissions: attempts.slice(0, 50).map(a => ({
          id: a.id,
          quizTitle: a.quizTitle || "Assessment",
          joinCode: a.joinCode || "QZ-1001",
          teacherName: a.teacherName || "Examiner",
          studentName: a.studentName || a.candidateName || "Candidate",
          score: a.score,
          totalQuestions: a.totalQuestions,
          percentage: a.percentage,
          passed: a.passed,
          cheatViolations: a.cheatViolations || 0,
          submittedAt: a.submittedAt || new Date().toISOString()
        }))
      };
    }

    renderKPIs() {
      if (!this.analytics || !this.analytics.kpis) return;
      const kpis = this.analytics.kpis;

      const elUsers = document.getElementById("adminKpiTotalUsers");
      const elQuizzes = document.getElementById("adminKpiTotalQuizzes");
      const elAttempts = document.getElementById("adminKpiTotalAttempts");
      const elPassRate = document.getElementById("adminKpiPassRate");
      const elAvgScore = document.getElementById("adminKpiAvgScore");
      const elViolations = document.getElementById("adminKpiViolations");

      if (elUsers) elUsers.textContent = kpis.totalUsers;
      if (elQuizzes) elQuizzes.textContent = kpis.totalQuizzes;
      if (elAttempts) elAttempts.textContent = kpis.totalAttempts;
      if (elPassRate) elPassRate.textContent = `${kpis.overallPassRate}%`;
      if (elAvgScore) elAvgScore.textContent = `${kpis.platformAvgScore}%`;
      if (elViolations) elViolations.textContent = kpis.totalViolations;
    }

    switchSubTab(tabName) {
      this.currentSubTab = tabName;
      document.querySelectorAll(".admin-sub-tab-btn").forEach(btn => btn.classList.remove("active"));
      const targetBtn = document.getElementById(`adminSubTabBtn-${tabName}`);
      if (targetBtn) targetBtn.classList.add("active");

      document.querySelectorAll(".admin-sub-view").forEach(view => view.style.display = "none");
      const targetView = document.getElementById(`adminSubView-${tabName}`);
      if (targetView) targetView.style.display = "block";

      this.renderActiveSubTab();
    }

    renderActiveSubTab() {
      if (this.currentSubTab === "users") {
        this.renderUsersTable();
      } else if (this.currentSubTab === "quizzes") {
        this.renderQuizzesAnalytics();
      } else if (this.currentSubTab === "submissions") {
        this.renderSubmissionsAudit();
      }
    }

    // -------------------------------------------------------------
    // SUB-TAB 1: USERS ROSTER & REPORTS
    // -------------------------------------------------------------
    renderUsersTable() {
      const container = document.getElementById("adminUsersTableBody");
      const countLabel = document.getElementById("adminUsersFilteredCount");
      if (!container) return;

      let filtered = this.users;

      if (this.userFilterRole !== "all") {
        filtered = filtered.filter(u => u.role === this.userFilterRole);
      }

      if (this.userSearchQuery) {
        const q = this.userSearchQuery.toLowerCase();
        filtered = filtered.filter(u => 
          (u.fullName && u.fullName.toLowerCase().includes(q)) ||
          (u.username && u.username.toLowerCase().includes(q)) ||
          (u.department && u.department.toLowerCase().includes(q)) ||
          (u.id && u.id.toLowerCase().includes(q))
        );
      }

      if (countLabel) {
        countLabel.textContent = `Showing ${filtered.length} of ${this.users.length} registered accounts`;
      }

      if (filtered.length === 0) {
        container.innerHTML = `
          <tr>
            <td colspan="8" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">
              🔍 No users found matching the selected filters.
            </td>
          </tr>
        `;
        return;
      }

      container.innerHTML = filtered.map(u => {
        let roleBadge = "";
        if (u.role === "admin") {
          roleBadge = `<span class="badge" style="background: rgba(245, 158, 11, 0.15); color: #d97706; border: 1px solid rgba(245, 158, 11, 0.3); font-weight: 700;">🛡️ ADMIN</span>`;
        } else if (u.role === "faculty" || u.role === "teacher" || u.role === "examiner") {
          roleBadge = `<span class="badge" style="background: rgba(99, 102, 241, 0.15); color: #6366f1; border: 1px solid rgba(99, 102, 241, 0.3); font-weight: 700;">🛠️ FACULTY</span>`;
        } else {
          roleBadge = `<span class="badge" style="background: rgba(56, 189, 248, 0.15); color: var(--accent-cyan); border: 1px solid rgba(56, 189, 248, 0.3); font-weight: 700;">🎓 STUDENT</span>`;
        }

        let scoreBadge = `<span style="color: var(--text-dim); font-weight: 600;">—</span>`;
        if (u.totalAttempts > 0) {
          const scoreColor = u.avgScore >= 75 ? "var(--accent-success)" : (u.avgScore >= 50 ? "var(--accent-warning)" : "var(--accent-danger)");
          scoreBadge = `<span style="font-weight: 700; color: ${scoreColor}; font-size: 0.95rem;">${u.avgScore}%</span>`;
        }

        const violText = u.totalViolations > 0 
          ? `<span style="color: var(--accent-danger); font-weight: 700;">⚠️ ${u.totalViolations}</span>`
          : `<span style="color: var(--accent-success);">0</span>`;

        return `
          <tr style="border-bottom: 1px solid var(--border-subtle); transition: background 0.15s ease;">
            <td style="padding: 0.9rem 1rem; font-family: var(--font-mono); font-size: 0.825rem; color: var(--text-dim); font-weight: 700;">
              #${u.userNo}
            </td>
            <td style="padding: 0.9rem 1rem;">
              <div style="font-weight: 700; color: var(--text-main); font-size: 0.95rem;">${u.fullName}</div>
              <div style="font-size: 0.775rem; color: var(--text-muted); font-family: var(--font-mono);">@${u.username} &bull; <span style="color: var(--text-dim);">${u.id}</span></div>
            </td>
            <td style="padding: 0.9rem 1rem;">${roleBadge}</td>
            <td style="padding: 0.9rem 1rem; font-size: 0.85rem; color: var(--text-muted);">${u.department}</td>
            <td style="padding: 0.9rem 1rem; text-align: center; font-weight: 600; color: var(--text-main);">
              ${u.totalAttempts}
            </td>
            <td style="padding: 0.9rem 1rem; text-align: center;">${scoreBadge}</td>
            <td style="padding: 0.9rem 1rem; text-align: center; font-weight: 600; font-size: 0.875rem;">
              ${u.totalAttempts > 0 ? `${u.passRate}% <span style="font-size: 0.75rem; color: var(--text-dim);">(${u.passedAttempts}/${u.totalAttempts})</span>` : '—'}
            </td>
            <td style="padding: 0.9rem 1rem; text-align: center;">${violText}</td>
            <td style="padding: 0.9rem 1rem; text-align: right;">
              <button class="btn btn-secondary btn-sm" onclick="adminPanel.openUserReportModal('${u.id}')" style="font-size: 0.8rem; font-weight: 700;">
                📊 View Report
              </button>
            </td>
          </tr>
        `;
      }).join('');
    }

    // -------------------------------------------------------------
    // SUB-TAB 2: QUIZ PERFORMANCE & DIFFICULTY ANALYTICS
    // -------------------------------------------------------------
    renderQuizzesAnalytics() {
      const container = document.getElementById("adminQuizzesAnalyticsContainer");
      if (!container || !this.analytics) return;

      let quizzes = this.analytics.quizzesAnalytics || [];

      if (this.quizSearchQuery) {
        const q = this.quizSearchQuery.toLowerCase();
        quizzes = quizzes.filter(quiz => 
          quiz.title.toLowerCase().includes(q) ||
          quiz.category.toLowerCase().includes(q) ||
          quiz.joinCode.toLowerCase().includes(q) ||
          quiz.teacherName.toLowerCase().includes(q)
        );
      }

      if (quizzes.length === 0) {
        container.innerHTML = `
          <div class="card" style="grid-column: 1 / -1; text-align: center; padding: 2.5rem; color: var(--text-muted);">
            🔍 No quiz performance metrics found matching the search criteria.
          </div>
        `;
        return;
      }

      container.innerHTML = quizzes.map(q => {
        let diffColor = "#10b981"; // green
        if (q.difficultyRating.includes("Rigorous")) diffColor = "#ef4444";
        else if (q.difficultyRating.includes("Balanced")) diffColor = "#3b82f6";

        return `
          <div class="card" style="padding: 1.5rem; display: flex; flex-direction: column; justify-content: space-between; border-radius: var(--radius-lg); border: 1px solid var(--border-medium); background: var(--bg-card); box-shadow: var(--shadow-sm);">
            <div>
              <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem; gap: 0.5rem;">
                <span class="badge badge-cyan" style="font-weight: 700;">${q.category}</span>
                <span class="badge" style="background: rgba(139, 92, 246, 0.15); color: #8b5cf6; border: 1px solid rgba(139, 92, 246, 0.3); font-family: var(--font-mono); font-weight: 700;">
                  🔑 ${q.joinCode}
                </span>
              </div>
              <h3 style="font-size: 1.15rem; font-weight: 700; color: var(--text-main); margin-bottom: 0.35rem; line-height: 1.3;">
                ${q.title}
              </h3>
              <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 1.25rem;">
                Author: <strong style="color: var(--text-main);">${q.teacherName}</strong> &bull; Duration: ${q.durationMinutes}m &bull; Pass Threshold: ${q.passingScore}%
              </p>

              <!-- Progress & Accuracy Bar -->
              <div style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.35rem;">
                  <span style="color: var(--text-muted);">Candidate Pass Rate:</span>
                  <span style="color: ${q.passRate >= 70 ? 'var(--accent-success)' : 'var(--accent-warning)'}; font-weight: 800;">${q.passRate}%</span>
                </div>
                <div style="width: 100%; height: 8px; background: var(--bg-tertiary); border-radius: var(--radius-pill); overflow: hidden;">
                  <div style="width: ${q.passRate}%; height: 100%; background: ${q.passRate >= 70 ? 'var(--accent-success)' : 'var(--accent-warning)'}; transition: width 0.4s ease;"></div>
                </div>
              </div>

              <!-- Metrics Grid -->
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.65rem; margin-bottom: 1.25rem; font-size: 0.825rem;">
                <div style="background: var(--bg-tertiary); padding: 0.65rem; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
                  <div style="color: var(--text-muted); font-size: 0.725rem;">Total Attempts</div>
                  <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-main);">${q.attemptsCount}</div>
                </div>
                <div style="background: var(--bg-tertiary); padding: 0.65rem; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
                  <div style="color: var(--text-muted); font-size: 0.725rem;">Class Avg Score</div>
                  <div style="font-size: 1.1rem; font-weight: 700; color: var(--accent-cyan);">${q.avgScore}%</div>
                </div>
                <div style="background: var(--bg-tertiary); padding: 0.65rem; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
                  <div style="color: var(--text-muted); font-size: 0.725rem;">Score Span (Min/Max)</div>
                  <div style="font-size: 0.9rem; font-weight: 700; color: var(--text-main);">${q.lowestScore}% &bull; ${q.highestScore}%</div>
                </div>
                <div style="background: var(--bg-tertiary); padding: 0.65rem; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
                  <div style="color: var(--text-muted); font-size: 0.725rem;">Security Violations</div>
                  <div style="font-size: 1rem; font-weight: 700; color: ${q.totalViolations > 0 ? 'var(--accent-danger)' : 'var(--accent-success)'};">
                    ${q.totalViolations > 0 ? `⚠️ ${q.totalViolations}` : '0 Clean'}
                  </div>
                </div>
              </div>
            </div>

            <!-- Footer Diagnosis -->
            <div style="padding-top: 0.75rem; border-top: 1px solid var(--border-subtle); display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 0.775rem; color: var(--text-muted);">Difficulty Rating:</span>
              <span style="font-size: 0.8rem; font-weight: 700; color: ${diffColor};">
                ${q.difficultyRating}
              </span>
            </div>
          </div>
        `;
      }).join('');
    }

    // -------------------------------------------------------------
    // SUB-TAB 3: GLOBAL SUBMISSIONS AUDIT TRAIL
    // -------------------------------------------------------------
    renderSubmissionsAudit() {
      const container = document.getElementById("adminSubmissionsTableBody");
      const countLabel = document.getElementById("adminSubmissionsFilteredCount");
      if (!container || !this.analytics) return;

      let subs = this.analytics.recentSubmissions || [];

      if (this.subResultFilter !== "all") {
        const wantPassed = this.subResultFilter === "passed";
        subs = subs.filter(s => s.passed === wantPassed);
      }

      if (this.subSearchQuery) {
        const q = this.subSearchQuery.toLowerCase();
        subs = subs.filter(s => 
          s.studentName.toLowerCase().includes(q) ||
          s.quizTitle.toLowerCase().includes(q) ||
          s.joinCode.toLowerCase().includes(q) ||
          s.teacherName.toLowerCase().includes(q)
        );
      }

      if (countLabel) {
        countLabel.textContent = `Showing ${subs.length} recent exam submissions`;
      }

      if (subs.length === 0) {
        container.innerHTML = `
          <tr>
            <td colspan="7" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">
              📋 No examination submissions recorded matching the selected filter.
            </td>
          </tr>
        `;
        return;
      }

      container.innerHTML = subs.map(s => {
        const resultBadge = s.passed
          ? `<span class="badge badge-success" style="font-weight: 700;">PASSED</span>`
          : `<span class="badge badge-danger" style="font-weight: 700;">FAILED</span>`;

        const violBadge = s.cheatViolations > 0
          ? `<span style="color: var(--accent-danger); font-weight: 700;">⚠️ ${s.cheatViolations} Flag(s)</span>`
          : `<span style="color: var(--accent-success); font-size: 0.85rem;">0 Clean</span>`;

        return `
          <tr style="border-bottom: 1px solid var(--border-subtle);">
            <td style="padding: 0.9rem 1rem; font-weight: 700; color: var(--text-main);">
              ${s.studentName}
            </td>
            <td style="padding: 0.9rem 1rem;">
              <div style="font-weight: 600; color: var(--text-main); font-size: 0.9rem;">${s.quizTitle}</div>
              <div style="font-size: 0.775rem; color: var(--text-muted); font-family: var(--font-mono);">Code: ${s.joinCode} &bull; Examiner: ${s.teacherName}</div>
            </td>
            <td style="padding: 0.9rem 1rem; text-align: center; font-weight: 700; color: var(--text-main);">
              ${s.score} / ${s.totalQuestions}
            </td>
            <td style="padding: 0.9rem 1rem; text-align: center; font-weight: 800; font-size: 0.95rem; color: ${s.percentage >= 70 ? 'var(--accent-success)' : 'var(--accent-danger)'};">
              ${s.percentage}%
            </td>
            <td style="padding: 0.9rem 1rem; text-align: center;">${resultBadge}</td>
            <td style="padding: 0.9rem 1rem; text-align: center;">${violBadge}</td>
            <td style="padding: 0.9rem 1rem; text-align: right; font-size: 0.8rem; color: var(--text-muted); font-family: var(--font-mono);">
              ${s.submittedAt}
            </td>
          </tr>
        `;
      }).join('');
    }

    // -------------------------------------------------------------
    // MODAL: USER DETAILED REPORT & SCORECARD HISTORY
    // -------------------------------------------------------------
    async openUserReportModal(userId) {
      const modal = document.getElementById("adminUserReportModal");
      if (!modal) return;

      const titleEl = document.getElementById("adminReportModalUserName");
      const bodyEl = document.getElementById("adminReportModalBody");

      if (titleEl) titleEl.textContent = "Loading Report...";
      if (bodyEl) bodyEl.innerHTML = `<div style="text-align: center; padding: 3rem; color: var(--text-muted);">⏳ Retrieving detailed scorecard history...</div>`;
      modal.classList.add("open");

      let reportData = null;

      try {
        const res = await fetch(`/api/admin/users/${userId}/report`);
        if (res.ok) {
          reportData = await res.json();
        }
      } catch (e) {
        console.warn("API report failed, computing locally:", e);
      }

      if (!reportData) {
        // Find user from memory
        const u = this.users.find(x => x.id === userId);
        if (!u) {
          if (bodyEl) bodyEl.innerHTML = `<div style="padding: 2rem; color: var(--accent-danger);">User not found.</div>`;
          return;
        }

        const attempts = (window.quizStorage && window.quizStorage.getAttempts) ? window.quizStorage.getAttempts() : [];
        const userAttempts = attempts.filter(a => 
          (a.studentName && a.studentName.toLowerCase() === (u.fullName || "").toLowerCase()) ||
          (a.candidateName && a.candidateName.toLowerCase() === (u.fullName || "").toLowerCase()) ||
          (a.studentName && a.studentName.toLowerCase() === (u.username || "").toLowerCase())
        );

        const count = userAttempts.length;
        const passedCount = userAttempts.filter(a => a.passed).length;
        const avg = count > 0 ? Math.round(userAttempts.reduce((s, a) => s + (a.percentage || 0), 0) / count) : 0;
        const highest = count > 0 ? Math.max(...userAttempts.map(a => a.percentage || 0)) : 0;
        const lowest = count > 0 ? Math.min(...userAttempts.map(a => a.percentage || 0)) : 0;
        const viols = userAttempts.reduce((s, a) => s + (a.cheatViolations || 0), 0);

        reportData = {
          user: u,
          summary: {
            totalAttempts: count,
            passedAttempts: passedCount,
            failedAttempts: count - passedCount,
            passRate: count > 0 ? Math.round((passedCount / count) * 100) : 0,
            avgScore: avg,
            highestScore: highest,
            lowestScore: lowest,
            totalViolations: viols
          },
          attempts: userAttempts.map(a => ({
            id: a.id,
            quizTitle: a.quizTitle || "Assessment",
            joinCode: a.joinCode || "QZ-1001",
            teacherName: a.teacherName || "Examiner",
            score: a.score,
            totalQuestions: a.totalQuestions,
            percentage: a.percentage,
            passed: a.passed,
            cheatViolations: a.cheatViolations || 0,
            submittedAt: a.submittedAt || "Recent"
          }))
        };
      }

      const u = reportData.user;
      const s = reportData.summary;

      if (titleEl) {
        titleEl.textContent = `Performance Report — ${u.fullName || u.full_name}`;
      }

      bodyEl.innerHTML = `
        <!-- Candidate Overview Card -->
        <div style="display: flex; gap: 1.25rem; align-items: center; padding: 1.25rem; background: var(--bg-tertiary); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); margin-bottom: 1.5rem;">
          <div style="width: 56px; height: 56px; border-radius: 50%; background: var(--gradient-primary); display: flex; align-items: center; justify-content: center; font-size: 1.75rem; color: #fff; box-shadow: var(--shadow-sm); flex-shrink: 0;">
            🎓
          </div>
          <div style="flex: 1;">
            <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
              <h4 style="font-size: 1.25rem; font-weight: 800; color: var(--text-main);">${u.fullName || u.full_name}</h4>
              <span class="badge" style="background: rgba(56, 189, 248, 0.15); color: var(--accent-cyan); text-transform: uppercase; font-weight: 700; font-size: 0.7rem;">
                ${u.role}
              </span>
            </div>
            <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.2rem;">
              @${u.username} &bull; ${u.department || 'General'} &bull; <span style="font-family: var(--font-mono); font-size: 0.775rem;">ID: ${u.id}</span>
            </div>
          </div>
        </div>

        <!-- Metric Stat Tiles -->
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem; margin-bottom: 1.5rem;">
          <div class="card" style="padding: 0.85rem; text-align: center; background: var(--bg-tertiary);">
            <div style="font-size: 0.75rem; color: var(--text-muted);">Total Quizzes</div>
            <div style="font-size: 1.35rem; font-weight: 800; color: var(--text-main);">${s.totalAttempts}</div>
          </div>
          <div class="card" style="padding: 0.85rem; text-align: center; background: var(--bg-tertiary);">
            <div style="font-size: 0.75rem; color: var(--text-muted);">Average Score</div>
            <div style="font-size: 1.35rem; font-weight: 800; color: var(--accent-cyan);">${s.avgScore}%</div>
          </div>
          <div class="card" style="padding: 0.85rem; text-align: center; background: var(--bg-tertiary);">
            <div style="font-size: 0.75rem; color: var(--text-muted);">Pass Rate</div>
            <div style="font-size: 1.35rem; font-weight: 800; color: var(--accent-success);">${s.passRate}%</div>
          </div>
          <div class="card" style="padding: 0.85rem; text-align: center; background: var(--bg-tertiary);">
            <div style="font-size: 0.75rem; color: var(--text-muted);">Violations</div>
            <div style="font-size: 1.35rem; font-weight: 800; color: ${s.totalViolations > 0 ? 'var(--accent-danger)' : 'var(--accent-success)'};">
              ${s.totalViolations}
            </div>
          </div>
        </div>

        <!-- Attempt History -->
        <h5 style="font-size: 1rem; font-weight: 700; color: var(--text-main); margin-bottom: 0.75rem; display: flex; justify-content: space-between; align-items: center;">
          <span>📝 Examination History & Scorecards (${reportData.attempts.length})</span>
          <span style="font-size: 0.8rem; font-weight: normal; color: var(--text-muted);">High: ${s.highestScore}% &bull; Low: ${s.lowestScore}%</span>
        </h5>

        ${reportData.attempts.length === 0 ? `
          <div style="padding: 2rem; text-align: center; color: var(--text-muted); background: var(--bg-tertiary); border-radius: var(--radius-md);">
            This candidate has not attempted any quizzes yet.
          </div>
        ` : `
          <div style="max-height: 280px; overflow-y: auto; border: 1px solid var(--border-subtle); border-radius: var(--radius-md);">
            <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem;">
              <thead style="background: var(--bg-tertiary); position: sticky; top: 0;">
                <tr style="text-align: left; color: var(--text-muted); font-size: 0.75rem;">
                  <th style="padding: 0.65rem 0.85rem;">Quiz Title</th>
                  <th style="padding: 0.65rem 0.85rem;">Code</th>
                  <th style="padding: 0.65rem 0.85rem; text-align: center;">Score</th>
                  <th style="padding: 0.65rem 0.85rem; text-align: center;">Accuracy</th>
                  <th style="padding: 0.65rem 0.85rem; text-align: center;">Outcome</th>
                  <th style="padding: 0.65rem 0.85rem; text-align: center;">Flags</th>
                  <th style="padding: 0.65rem 0.85rem; text-align: right;">Date</th>
                </tr>
              </thead>
              <tbody>
                ${reportData.attempts.map(a => `
                  <tr style="border-top: 1px solid var(--border-subtle);">
                    <td style="padding: 0.65rem 0.85rem; font-weight: 600; color: var(--text-main);">${a.quizTitle}</td>
                    <td style="padding: 0.65rem 0.85rem; font-family: var(--font-mono); color: var(--text-muted); font-size: 0.8rem;">${a.joinCode}</td>
                    <td style="padding: 0.65rem 0.85rem; text-align: center; font-weight: 700;">${a.score}/${a.totalQuestions}</td>
                    <td style="padding: 0.65rem 0.85rem; text-align: center; font-weight: 700; color: ${a.percentage >= 70 ? 'var(--accent-success)' : 'var(--accent-danger)'};">
                      ${a.percentage}%
                    </td>
                    <td style="padding: 0.65rem 0.85rem; text-align: center;">
                      ${a.passed ? '<span class="badge badge-success" style="font-size: 0.65rem; padding: 0.1rem 0.4rem;">PASS</span>' : '<span class="badge badge-danger" style="font-size: 0.65rem; padding: 0.1rem 0.4rem;">FAIL</span>'}
                    </td>
                    <td style="padding: 0.65rem 0.85rem; text-align: center; color: ${a.cheatViolations > 0 ? 'var(--accent-danger)' : 'var(--text-dim)'}; font-weight: ${a.cheatViolations > 0 ? '700' : 'normal'};">
                      ${a.cheatViolations > 0 ? `⚠️ ${a.cheatViolations}` : '0'}
                    </td>
                    <td style="padding: 0.65rem 0.85rem; text-align: right; color: var(--text-muted); font-size: 0.75rem; font-family: var(--font-mono);">${a.submittedAt}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        `}
      `;
    }

    closeUserReportModal() {
      const modal = document.getElementById("adminUserReportModal");
      if (modal) modal.classList.remove("open");
    }

    exportUsersCSV() {
      window.open("/api/admin/export/users.csv", "_blank");
      if (typeof window.showToast === "function") {
        window.showToast("Exporting registered users roster to CSV...", "info");
      }
    }

    exportSubmissionsCSV() {
      window.open("/api/admin/export/submissions.csv", "_blank");
      if (typeof window.showToast === "function") {
        window.showToast("Exporting comprehensive submissions audit to CSV...", "info");
      }
    }

    setupEventListeners() {
      const userSearch = document.getElementById("adminUserSearchInput");
      if (userSearch) {
        userSearch.addEventListener("input", (e) => {
          this.userSearchQuery = e.target.value.trim();
          this.renderUsersTable();
        });
      }

      const roleFilter = document.getElementById("adminUserRoleFilter");
      if (roleFilter) {
        roleFilter.addEventListener("change", (e) => {
          this.userFilterRole = e.target.value;
          this.renderUsersTable();
        });
      }

      const quizSearch = document.getElementById("adminQuizSearchInput");
      if (quizSearch) {
        quizSearch.addEventListener("input", (e) => {
          this.quizSearchQuery = e.target.value.trim();
          this.renderQuizzesAnalytics();
        });
      }

      const subSearch = document.getElementById("adminSubmissionsSearchInput");
      if (subSearch) {
        subSearch.addEventListener("input", (e) => {
          this.subSearchQuery = e.target.value.trim();
          this.renderSubmissionsAudit();
        });
      }

      const subFilter = document.getElementById("adminSubmissionsResultFilter");
      if (subFilter) {
        subFilter.addEventListener("change", (e) => {
          this.subResultFilter = e.target.value;
          this.renderSubmissionsAudit();
        });
      }
    }
  }

  window.adminPanel = new AdminPanel();
})(window);
