// Main Application Controller & View Router

window.currentView = "login";

window.switchView = function(viewName) {
  const currentUser = window.authManager ? window.authManager.getCurrentUser() : null;

  // 1. Unauthenticated Guard: Redirect any unauthorized attempt to login screen
  if (!currentUser) {
    viewName = "login";
  } else if (viewName === "login") {
    // If authenticated user attempts to visit login screen, route to their default view
    const role = (currentUser.role || "student").toLowerCase();
    viewName = (role === "faculty" || role === "instructor" || role === "examiner" || role === "teacher")
      ? "examiner"
      : "student-lobby";
  } else {
    // 2. Role-based Access Guards (mirrors desktop application)
    const role = (currentUser.role || "student").toLowerCase();
    if (role === "student" || role === "learner") {
      if (viewName === "examiner" || viewName === "builder") {
        if (typeof window.showToast === "function") {
          window.showToast("Access Restricted: Examiner Studio is reserved for faculty and admin accounts.", "danger");
        }
        viewName = "student-lobby";
      }
    } else if (role === "faculty" || role === "instructor" || role === "examiner" || role === "teacher") {
      if (viewName === "student-lobby" || viewName === "exam-arena") {
        if (typeof window.showToast === "function") {
          window.showToast("Faculty Mode: Candidate Arena is disabled for examiner accounts.", "info");
        }
        viewName = "examiner";
      }
    }
  }

  window.currentView = viewName;
  document.querySelectorAll(".view-section").forEach(sec => {
    sec.classList.remove("active");
  });

  const target = document.getElementById(`view-${viewName}`);
  if (target) {
    target.classList.add("active");
  }

  // Update navbar role tabs
  const studentBtn = document.getElementById("tabBtnStudent");
  const examinerBtn = document.getElementById("tabBtnExaminer");

  if (viewName === "student-lobby" || viewName === "exam-arena" || viewName === "result") {
    studentBtn?.classList.add("active");
    examinerBtn?.classList.remove("active");
  } else if (viewName === "examiner" || viewName === "builder") {
    examinerBtn?.classList.add("active");
    studentBtn?.classList.remove("active");
    if (viewName === "examiner" && window.examinerStudio) {
      window.examinerStudio.renderQuizCatalog();
      window.examinerStudio.loadSubmissionsRoster();
    }
  } else if (viewName === "login") {
    studentBtn?.classList.remove("active");
    examinerBtn?.classList.remove("active");
  }

  window.scrollTo({ top: 0, behavior: "smooth" });
};

// -------------------------------------------------------------
// Authentication Portal Handlers (Web Mirror of Desktop App)
// -------------------------------------------------------------

window.switchAuthTab = function(tab) {
  const tabSignIn = document.getElementById("authTabSignIn");
  const tabRegister = document.getElementById("authTabRegister");
  const formSignIn = document.getElementById("authFormSignIn");
  const formRegister = document.getElementById("authFormRegister");
  const loginStatus = document.getElementById("loginStatusMsg");
  const regStatus = document.getElementById("regStatusMsg");

  if (loginStatus) loginStatus.textContent = "";
  if (regStatus) regStatus.textContent = "";

  if (tab === "signin") {
    tabSignIn?.classList.add("active");
    tabRegister?.classList.remove("active");
    if (formSignIn) formSignIn.style.display = "block";
    if (formRegister) formRegister.style.display = "none";
  } else {
    tabRegister?.classList.add("active");
    tabSignIn?.classList.remove("active");
    if (formSignIn) formSignIn.style.display = "none";
    if (formRegister) formRegister.style.display = "block";
  }
};

window.togglePasswordVisibility = function(inputId, btnId) {
  const input = document.getElementById(inputId);
  const btn = document.getElementById(btnId);
  if (!input) return;

  if (input.type === "password") {
    input.type = "text";
    if (btn) btn.textContent = "🙈";
  } else {
    input.type = "password";
    if (btn) btn.textContent = "👁️";
  }
};

window.quickLoginDemo = async function(username, password) {
  const usernameInput = document.getElementById("loginUsername");
  const passwordInput = document.getElementById("loginPassword");
  if (usernameInput) usernameInput.value = username;
  if (passwordInput) passwordInput.value = password;

  const statusMsg = document.getElementById("loginStatusMsg");
  if (statusMsg) {
    statusMsg.style.color = "var(--accent-cyan)";
    statusMsg.textContent = `⚡ Authenticating ${username}...`;
  }

  try {
    const user = await window.authManager.login(username, password);
    if (statusMsg) statusMsg.textContent = "";
    const role = (user.role || "student").toLowerCase();
    if (role === "faculty" || role === "instructor" || role === "examiner" || role === "teacher") {
      window.switchView("examiner");
    } else {
      window.switchView("student-lobby");
    }
    window.showToast?.(`Welcome back, ${user.full_name} (${user.role.toUpperCase()})!`, "success");
  } catch (err) {
    if (statusMsg) {
      statusMsg.style.color = "#ef4444";
      statusMsg.textContent = err.message || "Failed to authenticate.";
    }
  }
};

window.handleWebSignInSubmit = async function(e) {
  if (e && e.preventDefault) e.preventDefault();
  const username = document.getElementById("loginUsername")?.value.trim();
  const password = document.getElementById("loginPassword")?.value.trim();
  const statusMsg = document.getElementById("loginStatusMsg");
  const submitBtn = document.getElementById("signInSubmitBtn");

  if (statusMsg) {
    statusMsg.style.color = "var(--accent-cyan)";
    statusMsg.textContent = "Authenticating credentials...";
  }
  if (submitBtn) submitBtn.disabled = true;

  try {
    const user = await window.authManager.login(username, password);
    if (statusMsg) statusMsg.textContent = "";
    const role = (user.role || "student").toLowerCase();
    if (role === "faculty" || role === "instructor" || role === "examiner" || role === "teacher") {
      window.switchView("examiner");
    } else {
      window.switchView("student-lobby");
    }
    window.showToast?.(`Welcome back, ${user.full_name}!`, "success");
  } catch (err) {
    if (statusMsg) {
      statusMsg.style.color = "#ef4444";
      statusMsg.textContent = err.message || "Invalid credentials.";
    }
  } finally {
    if (submitBtn) submitBtn.disabled = false;
  }
};

window.handleWebRegisterSubmit = async function(e) {
  if (e && e.preventDefault) e.preventDefault();
  const fullName = document.getElementById("regFullName")?.value.trim();
  const username = document.getElementById("regUsername")?.value.trim();
  const password = document.getElementById("regPassword")?.value.trim();
  const role = document.getElementById("regRole")?.value || "student";
  const dept = document.getElementById("regDept")?.value.trim() || "Computer Science";
  const statusMsg = document.getElementById("regStatusMsg");
  const submitBtn = document.getElementById("regSubmitBtn");

  if (statusMsg) {
    statusMsg.style.color = "var(--accent-cyan)";
    statusMsg.textContent = "Creating account...";
  }
  if (submitBtn) submitBtn.disabled = true;

  try {
    const user = await window.authManager.register(username, password, role, fullName, dept);
    if (statusMsg) statusMsg.textContent = "";
    const userRole = (user.role || "student").toLowerCase();
    if (userRole === "faculty" || userRole === "instructor" || userRole === "examiner" || userRole === "teacher") {
      window.switchView("examiner");
    } else {
      window.switchView("student-lobby");
    }
    window.showToast?.(`Account registered successfully! Welcome, ${user.full_name}.`, "success");
  } catch (err) {
    if (statusMsg) {
      statusMsg.style.color = "#ef4444";
      statusMsg.textContent = err.message || "Registration failed.";
    }
  } finally {
    if (submitBtn) submitBtn.disabled = false;
  }
};

window.showToast = function(message, type = "info") {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✅' : (type === 'danger' ? '⚠️' : 'ℹ️')}</span>
    <span>${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(50px)";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
};

// Render Student Quiz Cards
function renderStudentCatalog() {
  const container = document.getElementById("studentQuizCatalog");
  if (!container) return;

  const quizzes = quizStorage.getQuizzes();
  container.innerHTML = "";

  quizzes.forEach(quiz => {
    const card = document.createElement("div");
    card.className = "card card-interactive quiz-card";
    card.innerHTML = `
      <div>
        <div class="quiz-card-tags">
          <span class="badge badge-cyan">${quiz.category || 'Engineering'}</span>
          ${(quiz.tags || []).slice(0, 2).map(t => `<span class="badge badge-indigo">${t}</span>`).join('')}
        </div>
        <h3 class="quiz-card-title">${quiz.title}</h3>
        <p class="quiz-card-desc">${quiz.description || 'Test your proficiency with challenging questions.'}</p>
        <div class="quiz-info-chips">
          <div class="info-chip"><span>❓</span> ${quiz.questions.length} Questions</div>
          <div class="info-chip"><span>⏱️</span> ${quiz.durationMinutes} Minutes</div>
          <div class="info-chip"><span>🎯</span> Pass: ${quiz.passingScore}%</div>
        </div>
      </div>
      <button class="btn btn-cyan" onclick="openStartExamModal('${quiz.id}')">Start Assessment ⚡</button>
    `;
    container.appendChild(card);
  });
}

// Start Exam Modal
let pendingExamQuizId = null;

window.openStartExamModal = function(quizId) {
  pendingExamQuizId = quizId;
  const quizzes = quizStorage.getQuizzes();
  const quiz = quizzes.find(q => q.id === quizId);
  if (!quiz) return;

  document.getElementById("startModalQuizTitle").textContent = quiz.title;
  document.getElementById("startModalDuration").textContent = `${quiz.durationMinutes} mins`;
  document.getElementById("startModalQuestions").textContent = `${quiz.questions.length}`;

  const modal = document.getElementById("startExamModal");
  if (modal) modal.classList.add("open");
};

window.closeStartExamModal = function() {
  const modal = document.getElementById("startExamModal");
  if (modal) modal.classList.remove("open");
};

window.confirmAndBeginExam = function() {
  const nameInput = document.getElementById("candidateNameInput");
  const name = nameInput.value.trim() || "Candidate";
  const fullscreenCheck = document.getElementById("fullscreenCheckbox");

  if (fullscreenCheck && fullscreenCheck.checked) {
    if (document.documentElement.requestFullscreen) {
      document.documentElement.requestFullscreen().catch(() => {});
    }
  }

  const quizzes = quizStorage.getQuizzes();
  const quiz = quizzes.find(q => q.id === pendingExamQuizId);
  if (!quiz) return;

  closeStartExamModal();
  document.getElementById("examHeaderQuizTitle").textContent = quiz.title;
  quizEngine.startQuiz(quiz, name);
  window.switchView("exam-arena");
  window.showToast(`Welcome ${name}! Assessment started.`, "success");
};

// Cloud Settings Modal
window.openCloudSettingsModal = function() {
  const modal = document.getElementById("cloudSettingsModal");
  const config = quizStorage.getCloudConfig();
  if (config) {
    document.getElementById("cloudProjectId").value = config.projectId || "";
    document.getElementById("cloudApiKey").value = config.apiKey || "";
  }
  if (modal) modal.classList.add("open");
};

window.closeCloudSettingsModal = function() {
  const modal = document.getElementById("cloudSettingsModal");
  if (modal) modal.classList.remove("open");
};

window.saveCloudConfig = function() {
  const projectId = document.getElementById("cloudProjectId").value.trim();
  const apiKey = document.getElementById("cloudApiKey").value.trim();
  quizStorage.setCloudConfig({ projectId, apiKey, connectedAt: new Date().toISOString() });
  window.showToast("Cloud configuration saved successfully!", "success");
  closeCloudSettingsModal();
};

// Join By Code (Mobile & Desktop Web)
window.joinByCodeWeb = async function() {
  const code = (document.getElementById("joinCodeInputWeb")?.value || "").trim().toUpperCase();
  if (!code) {
    window.showToast("Please enter a 6-character Quiz Code (e.g. QZ-1001)", "warning");
    return;
  }
  const quizzes = quizStorage.getQuizzes();
  let found = quizzes.find(q => (q.joinCode && q.joinCode.toUpperCase() === code) || q.id.toUpperCase() === code);

  if (!found) {
    try {
      const res = await fetch(`/api/quizzes/code/${encodeURIComponent(code)}`);
      if (res.ok) {
        const remoteQuiz = await res.json();
        quizStorage.saveQuiz(remoteQuiz);
        found = remoteQuiz;
      }
    } catch (e) {
      /* network lookup fallback */
    }
  }

  if (found) {
    window.showToast(`Found Assessment: "${found.title}"`, "success");
    openStartExamModal(found.id);
  } else {
    window.showToast(`Quiz with code '${code}' not found. Check code with your teacher.`, "danger");
  }
};

// AI Quiz Generator Modals & Handlers
window.openAIGeneratorModal = function() {
  const modal = document.getElementById("aiGeneratorModal");
  if (modal) modal.classList.add("open");
};

window.closeAIGeneratorModal = function() {
  const modal = document.getElementById("aiGeneratorModal");
  if (modal) modal.classList.remove("open");
};

window.confirmGenerateWithAI = async function() {
  const topic = (document.getElementById("aiTopicInput")?.value || "General Science").trim();
  const count = parseInt(document.getElementById("aiCountSelect")?.value || "5", 10);
  const diff = document.getElementById("aiDiffSelect")?.value || "Medium";

  window.showToast(`🤖 Generating ${count} questions for "${topic}"...`, "info");
  closeAIGeneratorModal();

  try {
    const res = await fetch("/api/ai-generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic, numQuestions: count, difficulty: diff })
    });
    if (res.ok) {
      const data = await res.json();
      const newQuiz = {
        id: "quiz-ai-" + Date.now(),
        joinCode: "QZ-" + Math.floor(1000 + Math.random() * 9000),
        title: `${topic} (${diff})`,
        category: "AI Generated",
        description: `Curriculum assessment for ${topic} at ${diff} difficulty level.`,
        durationMinutes: 10,
        passingScore: 70,
        tags: [topic.split(" ")[0], diff, "AI"],
        questions: data.questions
      };
      quizStorage.saveQuiz(newQuiz);
      window.showToast(`Quiz created with Join Code: ${newQuiz.joinCode}!`, "success");
      examinerStudio.init();
      renderStudentCatalog();
    } else {
      throw new Error("API error");
    }
  } catch (err) {
    // Local offline generation fallback
    const newQuiz = {
      id: "quiz-ai-" + Date.now(),
      joinCode: "QZ-" + Math.floor(1000 + Math.random() * 9000),
      title: `${topic} (${diff})`,
      category: "AI Generated",
      description: `Comprehensive evaluation for ${topic}.`,
      durationMinutes: 10,
      passingScore: 70,
      tags: [topic.split(" ")[0], diff],
      questions: [
        {
          id: "q-1",
          text: `In ${topic}, which principle is fundamental to ensure high performance and maintainability?`,
          code: null,
          options: [
            `Standard design patterns, decoupling, and proper validation in ${topic}`,
            "Hardcoding all state directly into global variables",
            "Disabling error handling routines",
            "Bypassing network security protocols"
          ],
          correct: 0,
          explanation: `Systematic decoupling, design patterns, and validation ensure stability in ${topic}.`
        }
      ]
    };
    quizStorage.saveQuiz(newQuiz);
    window.showToast(`Quiz created with Join Code: ${newQuiz.joinCode}!`, "success");
    examinerStudio.init();
    renderStudentCatalog();
  }
};

// Accessibility & Theme Controls: Professional Light (Default), Dark, High Contrast, Font Resize, Minimalist Mode
window.webFontScale = 1.0;

function updateThemeButtonUI(isDark) {
  const icon = document.getElementById("themeToggleIcon");
  const text = document.getElementById("themeToggleText");
  if (icon && text) {
    if (isDark) {
      icon.textContent = "🌙";
      text.textContent = "Dark";
    } else {
      icon.textContent = "☀️";
      text.textContent = "Light";
    }
  }
}

window.toggleWebTheme = function() {
  document.body.classList.toggle("dark-theme");
  const isDark = document.body.classList.contains("dark-theme");
  localStorage.setItem("quiz_theme", isDark ? "dark" : "light");
  updateThemeButtonUI(isDark);
  window.showToast?.(isDark ? "Dark Theme Activated" : "Professional Light Theme (Default)", "info");
};

window.toggleWebHighContrast = function() {
  document.body.classList.toggle("high-contrast");
  const isHighContrast = document.body.classList.contains("high-contrast");
  localStorage.setItem("quiz_high_contrast", isHighContrast ? "1" : "0");
  window.showToast?.(isHighContrast ? "High Contrast Mode: Enabled (WCAG AAA)" : "High Contrast Mode: Disabled", "info");
};

window.adjustWebFontSize = function(delta) {
  window.webFontScale = Math.min(1.4, Math.max(0.85, (window.webFontScale || 1.0) + delta * 0.1));
  document.documentElement.style.fontSize = `${window.webFontScale * 16}px`;
  localStorage.setItem("quiz_font_scale", window.webFontScale.toString());
  window.showToast?.(`Font Scale: ${Math.round(window.webFontScale * 100)}%`, "info");
};

window.toggleWebMinimalistLayout = function() {
  document.body.classList.toggle("minimalist-mode");
  const isMinimal = document.body.classList.contains("minimalist-mode");
  localStorage.setItem("quiz_minimalist_mode", isMinimal ? "1" : "0");
  window.showToast?.(isMinimal ? "Minimalist Focus Mode: ON" : "Standard Layout Restored", "info");
};

// App Initialization
document.addEventListener("DOMContentLoaded", () => {
  // Theme initialization: Default is Light Theme for all
  const savedTheme = localStorage.getItem("quiz_theme") || "light";
  if (savedTheme === "dark") {
    document.body.classList.add("dark-theme");
    updateThemeButtonUI(true);
  } else {
    document.body.classList.remove("dark-theme");
    updateThemeButtonUI(false);
  }

  // Restore accessibility preferences
  if (localStorage.getItem("quiz_high_contrast") === "1") {
    document.body.classList.add("high-contrast");
  }
  const savedScale = parseFloat(localStorage.getItem("quiz_font_scale"));
  if (savedScale && savedScale >= 0.85 && savedScale <= 1.4) {
    window.webFontScale = savedScale;
    document.documentElement.style.fontSize = `${savedScale * 16}px`;
  }
  if (localStorage.getItem("quiz_minimalist_mode") === "1") {
    document.body.classList.add("minimalist-mode");
  }

  renderStudentCatalog();
  examinerStudio.init();

  // Search in student catalog
  const searchInput = document.getElementById("quizSearchInput");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase();
      document.querySelectorAll("#studentQuizCatalog .quiz-card").forEach(card => {
        const title = card.querySelector(".quiz-card-title")?.textContent.toLowerCase() || "";
        const desc = card.querySelector(".quiz-card-desc")?.textContent.toLowerCase() || "";
        if (title.includes(q) || desc.includes(q)) {
          card.style.display = "flex";
        } else {
          card.style.display = "none";
        }
      });
    });
  }

  // Initialize Authentication State & View Session
  if (window.authManager) {
    window.authManager.updateNavSessionState();
    const user = window.authManager.getCurrentUser();
    if (!user) {
      window.switchView("login");
    } else {
      const role = (user.role || "student").toLowerCase();
      if (role === "faculty" || role === "instructor" || role === "examiner" || role === "teacher") {
        window.switchView("examiner");
      } else {
        window.switchView("student-lobby");
      }
    }
  } else {
    window.switchView("login");
  }

  // Register Service Worker for PWA
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('./sw.js').catch(() => {});
  }
});
