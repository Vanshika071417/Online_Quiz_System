// Main Application Controller & View Router

window.currentView = "student-lobby";

window.switchView = function(viewName) {
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
  }

  window.scrollTo({ top: 0, behavior: "smooth" });
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

// App Initialization
document.addEventListener("DOMContentLoaded", () => {
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

  // Register Service Worker for PWA
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('./sw.js').catch(() => {});
  }
});
