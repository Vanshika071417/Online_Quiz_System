/**
 * QuizSphere Pro 2.0 - Client-Side Authentication & Session Controller
 * Mirrors the native desktop application authentication workflow.
 */

(function(window) {
  'use strict';

  // In-memory fallback demo users if server is running offline
  const DEMO_USERS = [
    {
      id: "usr-admin",
      username: "admin",
      password: "admin123",
      role: "admin",
      full_name: "System Administrator",
      department: "Operations & Quality Assurance"
    },
    {
      id: "usr-fac-1",
      username: "faculty",
      password: "faculty123",
      role: "faculty",
      full_name: "Prof. Alan Turing",
      department: "Computer Science & Engineering"
    },
    {
      id: "usr-stu-1",
      username: "student",
      password: "student123",
      role: "student",
      full_name: "Alex Mercer",
      department: "B.Tech CSE - 2026"
    }
  ];

  class AuthManager {
    constructor() {
      this.currentUser = null;
      this.init();
    }

    init() {
      // Restore active session from localStorage
      try {
        const stored = localStorage.getItem("quizsphere_user");
        if (stored) {
          this.currentUser = JSON.parse(stored);
        }
      } catch (e) {
        console.warn("Failed to parse cached user session:", e);
        this.currentUser = null;
      }
    }

    getCurrentUser() {
      return this.currentUser;
    }

    async login(username, password) {
      username = (username || "").trim();
      password = (password || "").trim();

      if (!username || !password) {
        throw new Error("Please enter both username and password.");
      }

      // Try server API first
      try {
        const res = await fetch("/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password })
        });

        if (res.ok) {
          const user = await res.json();
          this.setSession(user);
          return user;
        } else {
          const errData = await res.json().catch(() => ({}));
          // If 401 unauthorized, reject directly
          if (res.status === 401 || res.status === 400) {
            throw new Error(errData.detail || "Invalid credentials. Check your username and password.");
          }
        }
      } catch (err) {
        // If it was a credential mismatch error thrown above, re-throw
        if (err.message && (err.message.includes("Invalid credentials") || err.message.includes("Please enter"))) {
          throw err;
        }
        // Otherwise network or offline - proceed to offline fallback
      }

      // Offline / Local Demo Fallback
      let localRegistered = [];
      try {
        localRegistered = JSON.parse(localStorage.getItem("quizsphere_registered_users") || "[]");
      } catch (e) {}

      const allUsers = [...DEMO_USERS, ...localRegistered];
      const match = allUsers.find(u => u.username.toLowerCase() === username.toLowerCase());

      if (match && match.password === password) {
        const sessionUser = {
          id: match.id,
          username: match.username,
          role: match.role.toLowerCase(),
          full_name: match.full_name,
          department: match.department || "General"
        };
        this.setSession(sessionUser);
        return sessionUser;
      }

      throw new Error("Invalid credentials. Check your username and password.");
    }

    async register(username, password, role, fullName, department) {
      username = (username || "").trim();
      password = (password || "").trim();
      fullName = (fullName || "").trim();
      department = (department || "General").trim();
      role = (role || "student").trim().toLowerCase();

      if (!username || !password || !fullName) {
        throw new Error("Username, password, and full name are required.");
      }
      if (username.length < 3) {
        throw new Error("Username must be at least 3 characters.");
      }
      if (password.length < 4) {
        throw new Error("Password must be at least 4 characters.");
      }

      // Try server API first
      try {
        const res = await fetch("/api/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username,
            password,
            role,
            full_name: fullName,
            department
          })
        });

        if (res.ok) {
          const user = await res.json();
          this.setSession(user);
          return user;
        } else {
          const errData = await res.json().catch(() => ({}));
          if (res.status === 400) {
            throw new Error(errData.detail || "Registration failed.");
          }
        }
      } catch (err) {
        if (err.message && (err.message.includes("already exists") || err.message.includes("must be"))) {
          throw err;
        }
      }

      // Offline / Local Demo Registration Fallback
      let localRegistered = [];
      try {
        localRegistered = JSON.parse(localStorage.getItem("quizsphere_registered_users") || "[]");
      } catch (e) {}

      const allUsers = [...DEMO_USERS, ...localRegistered];
      if (allUsers.some(u => u.username.toLowerCase() === username.toLowerCase())) {
        throw new Error(`Username '${username}' already exists. Please choose a different username.`);
      }

      const newUser = {
        id: `usr-${Date.now()}-${Math.floor(Math.random() * 900 + 100)}`,
        username,
        password,
        role,
        full_name: fullName,
        department
      };

      localRegistered.push(newUser);
      localStorage.setItem("quizsphere_registered_users", JSON.stringify(localRegistered));

      const sessionUser = {
        id: newUser.id,
        username: newUser.username,
        role: newUser.role,
        full_name: newUser.full_name,
        department: newUser.department
      };
      this.setSession(sessionUser);
      return sessionUser;
    }

    setSession(user) {
      this.currentUser = user;
      try {
        localStorage.setItem("quizsphere_user", JSON.stringify(user));
      } catch (e) {
        console.error("Could not cache user session:", e);
      }
      this.updateNavSessionState();
    }

    logout() {
      this.currentUser = null;
      try {
        localStorage.removeItem("quizsphere_user");
      } catch (e) {}
      this.updateNavSessionState();
      window.switchView("login");
      if (typeof window.showToast === "function") {
        window.showToast("Signed out of QuizSphere Pro.", "info");
      }
    }

    updateNavSessionState() {
      const navRoleSwitcher = document.getElementById("navRoleSwitcher");
      const tabBtnStudent = document.getElementById("tabBtnStudent");
      const tabBtnExaminer = document.getElementById("tabBtnExaminer");
      const tabBtnAdmin = document.getElementById("tabBtnAdmin");
      const navUserChip = document.getElementById("navUserChip");
      const navLogoutBtn = document.getElementById("navLogoutBtn");

      if (!this.currentUser) {
        // Logged Out State
        if (navRoleSwitcher) navRoleSwitcher.style.display = "none";
        if (tabBtnAdmin) tabBtnAdmin.style.display = "none";
        if (navLogoutBtn) navLogoutBtn.style.display = "none";
        if (navUserChip) {
          navUserChip.innerHTML = "<span>🔒</span> <span class='tab-text'>Sign In</span>";
          navUserChip.className = "access-btn badge-cyan";
          navUserChip.title = "Sign in with student or faculty credentials";
        }
      } else {
        // Logged In State
        const role = (this.currentUser.role || "student").toLowerCase();
        const name = this.currentUser.full_name || "User";

        if (navRoleSwitcher) navRoleSwitcher.style.display = "flex";
        if (navLogoutBtn) navLogoutBtn.style.display = "inline-flex";

        if (navUserChip) {
          const roleDisplay = role.charAt(0).toUpperCase() + role.slice(1);
          navUserChip.innerHTML = `<span>👤</span> <span class="tab-text">${name} (${roleDisplay})</span>`;
          navUserChip.className = "access-btn badge-cyan";
          navUserChip.title = "View User Profile & Credentials";
        }

        // Role-tailored Navigation Tabs:
        // - Student: Show ONLY Candidate Arena; remove Examiner Studio and Admin Panel
        // - Faculty / Examiner: Show ONLY Examiner Studio; remove Candidate Arena and Admin Panel
        // - Admin: Show Candidate Arena, Examiner Studio, AND Admin Panel
        if (role === "student" || role === "learner") {
          if (tabBtnStudent) tabBtnStudent.style.display = "inline-flex";
          if (tabBtnExaminer) tabBtnExaminer.style.display = "none";
          if (tabBtnAdmin) tabBtnAdmin.style.display = "none";
        } else if (role === "faculty" || role === "instructor" || role === "examiner" || role === "teacher") {
          if (tabBtnStudent) tabBtnStudent.style.display = "none";
          if (tabBtnExaminer) tabBtnExaminer.style.display = "inline-flex";
          if (tabBtnAdmin) tabBtnAdmin.style.display = "none";
        } else { // Admin
          if (tabBtnStudent) tabBtnStudent.style.display = "inline-flex";
          if (tabBtnExaminer) tabBtnExaminer.style.display = "inline-flex";
          if (tabBtnAdmin) tabBtnAdmin.style.display = "inline-flex";
        }

        // Pre-fill candidate name across the app
        const candidateInput = document.getElementById("candidateNameInput");
        if (candidateInput) {
          candidateInput.value = name;
        }
      }
    }

    openUserProfileModal() {
      if (!this.currentUser) {
        window.switchView("login");
        return;
      }
      const modal = document.getElementById("userProfileModal");
      if (!modal) return;

      document.getElementById("profileFullName").textContent = this.currentUser.full_name || "—";
      document.getElementById("profileUsername").textContent = this.currentUser.username || "—";
      document.getElementById("profileRole").textContent = (this.currentUser.role || "STUDENT").toUpperCase();
      document.getElementById("profileDept").textContent = this.currentUser.department || "General";
      document.getElementById("profileUserId").textContent = this.currentUser.id || "—";

      modal.classList.add("open");
    }

    closeUserProfileModal() {
      const modal = document.getElementById("userProfileModal");
      if (modal) modal.classList.remove("open");
    }
  }

  // Export singleton instance
  window.authManager = new AuthManager();

  // Helper bindings for UI
  window.handleWebUserChipClick = function() {
    if (!window.authManager.getCurrentUser()) {
      window.switchView("login");
    } else {
      window.authManager.openUserProfileModal();
    }
  };

  window.handleWebLogout = function() {
    window.authManager.closeUserProfileModal();
    window.authManager.logout();
  };

  window.closeUserProfileModal = function() {
    window.authManager.closeUserProfileModal();
  };

})(window);
