// Examiner & Question Bank Management

class ExaminerStudio {
  constructor() {
    this.currentEditingQuiz = null;
    this.currentQuestionIndex = 0;
    this.allSubmissions = [];
  }

  init() {
    this.renderStats();
    this.renderQuizCatalog();
    this.loadSubmissionsRoster();
  }

  renderStats() {
    const quizzes = quizStorage.getQuizzes();
    const attempts = quizStorage.getAttempts();

    const totalQuestions = quizzes.reduce((sum, q) => sum + (q.questions?.length || 0), 0);
    const passCount = attempts.filter(a => a.passed).length;
    const passRate = attempts.length > 0 ? Math.round((passCount / attempts.length) * 100) : 0;

    const elQuizzes = document.getElementById("statTotalQuizzes");
    const elQuestions = document.getElementById("statTotalQuestions");
    const elAttempts = document.getElementById("statTotalAttempts");
    const elPassRate = document.getElementById("statPassRate");

    if (elQuizzes) elQuizzes.textContent = quizzes.length;
    if (elQuestions) elQuestions.textContent = totalQuestions;
    if (elAttempts) elAttempts.textContent = attempts.length;
    if (elPassRate) elPassRate.textContent = `${passRate}%`;
  }

  renderQuizCatalog() {
    const container = document.getElementById("examinerQuizList");
    if (!container) return;

    const quizzes = quizStorage.getQuizzes();
    container.innerHTML = "";

    if (quizzes.length === 0) {
      container.innerHTML = `
        <div class="card" style="text-align:center; padding:3rem 1rem; grid-column:1/-1;">
          <p style="color:var(--text-muted); margin-bottom:1rem;">No quizzes created yet.</p>
          <button class="btn btn-primary" onclick="examinerStudio.openCreateQuizModal()">+ Create Your First Quiz</button>
        </div>
      `;
      return;
    }

    quizzes.forEach(quiz => {
      const card = document.createElement("div");
      card.className = "card quiz-admin-card";
      const code = quiz.joinCode || "QZ-1001";
      card.innerHTML = `
        <div>
          <div class="quiz-card-head">
            <span class="badge badge-cyan">${quiz.category || 'General'}</span>
            <span class="badge badge-indigo" style="cursor:pointer;" onclick="navigator.clipboard.writeText('${code}'); window.showToast('Copied Code: ${code} to clipboard!', 'success')" title="Click to Copy Join Code">🔑 CODE: ${code} 📋</span>
          </div>
          <h3 style="font-size:1.15rem; margin-bottom:0.4rem; color:var(--text-main);">${quiz.title}</h3>
          <p style="font-size:0.85rem; color:var(--text-muted); line-height:1.4;">${quiz.description || 'No description provided.'}</p>
          <div class="quiz-meta-row">
            <span>⏱️ ${quiz.durationMinutes} mins</span>
            <span>❓ ${quiz.questions.length} Questions</span>
            <span>🎯 Pass: ${quiz.passingScore}%</span>
          </div>
        </div>
        <div class="quiz-card-actions">
          <button class="btn btn-secondary btn-sm" onclick="navigator.clipboard.writeText('${code}'); window.showToast('Copied Join Code: ${code} for students!', 'success')">📋 Copy Code</button>
          <button class="btn btn-secondary btn-sm" onclick="examinerStudio.editQuiz('${quiz.id}')">✏️ Edit</button>
          <button class="btn btn-secondary btn-sm" onclick="examinerStudio.exportQuiz('${quiz.id}')">💾 Export</button>
          <button class="btn btn-danger btn-sm" onclick="examinerStudio.deleteQuiz('${quiz.id}')">🗑️ Delete</button>
        </div>
      `;
      container.appendChild(card);
    });
  }

  generateNewJoinCode() {
    const code = "QZ-" + Math.floor(1000 + Math.random() * 9000);
    const input = document.getElementById("builderJoinCode");
    if (input) {
      input.value = code;
      window.showToast?.(`Generated new Join Code: ${code}`, "info");
    }
  }

  openCreateQuizModal() {
    const randomCode = "QZ-" + Math.floor(1000 + Math.random() * 9000);
    this.currentEditingQuiz = {
      id: "quiz-" + Date.now(),
      joinCode: randomCode,
      teacherName: "Prof. Alan Turing",
      title: "",
      category: "Computer Science",
      description: "",
      durationMinutes: 15,
      passingScore: 70,
      tags: [],
      questions: [
        {
          id: "q-1",
          text: "Sample Question 1",
          code: null,
          options: ["Option A", "Option B", "Option C", "Option D"],
          correct: 0,
          explanation: "Explanation for why Option A is correct."
        }
      ]
    };
    this.currentQuestionIndex = 0;
    this.loadQuizIntoBuilder(this.currentEditingQuiz);
    window.switchView("builder");
  }

  editQuiz(quizId) {
    const quizzes = quizStorage.getQuizzes();
    const quiz = quizzes.find(q => q.id === quizId);
    if (!quiz) return;

    this.currentEditingQuiz = JSON.parse(JSON.stringify(quiz));
    this.currentQuestionIndex = 0;
    this.loadQuizIntoBuilder(this.currentEditingQuiz);
    window.switchView("builder");
  }

  loadQuizIntoBuilder(quiz) {
    document.getElementById("builderQuizTitle").value = quiz.title || "";
    const joinCodeInput = document.getElementById("builderJoinCode");
    if (joinCodeInput) {
      joinCodeInput.value = quiz.joinCode || ("QZ-" + Math.floor(1000 + Math.random() * 9000));
    }
    document.getElementById("builderCategory").value = quiz.category || "";
    document.getElementById("builderDuration").value = quiz.durationMinutes || 15;
    document.getElementById("builderPassing").value = quiz.passingScore || 70;
    document.getElementById("builderDescription").value = quiz.description || "";

    this.renderBuilderQuestionList();
    this.renderCurrentBuilderQuestion();
  }

  renderBuilderQuestionList() {
    const list = document.getElementById("builderQuestionList");
    if (!list || !this.currentEditingQuiz) return;

    list.innerHTML = "";
    this.currentEditingQuiz.questions.forEach((q, idx) => {
      const item = document.createElement("div");
      item.className = `question-nav-item ${idx === this.currentQuestionIndex ? "active" : ""}`;
      item.onclick = () => {
        this.saveCurrentQuestionForm();
        this.currentQuestionIndex = idx;
        this.renderBuilderQuestionList();
        this.renderCurrentBuilderQuestion();
      };

      item.innerHTML = `
        <span style="font-weight:600; font-size:0.875rem;">Q${idx + 1}: ${(q.text || "Untitled").substring(0, 22)}...</span>
        ${this.currentEditingQuiz.questions.length > 1 ? `
          <button class="btn btn-danger btn-sm btn-icon" style="height:26px; width:26px;" onclick="event.stopPropagation(); examinerStudio.removeQuestion(${idx})">✕</button>
        ` : ''}
      `;
      list.appendChild(item);
    });
  }

  renderCurrentBuilderQuestion() {
    if (!this.currentEditingQuiz) return;
    const q = this.currentEditingQuiz.questions[this.currentQuestionIndex];
    if (!q) return;

    document.getElementById("builderCurrentQNum").textContent = this.currentQuestionIndex + 1;
    document.getElementById("builderQuestionPrompt").value = q.text || "";
    document.getElementById("builderQuestionCode").value = q.code || "";
    document.getElementById("builderExplanation").value = q.explanation || "";

    const optionsContainer = document.getElementById("builderOptionsContainer");
    optionsContainer.innerHTML = "";

    q.options.forEach((optText, optIdx) => {
      const row = document.createElement("div");
      row.className = "option-input-row";
      row.innerHTML = `
        <input type="radio" name="builderCorrectOption" class="option-radio" value="${optIdx}" ${q.correct === optIdx ? "checked" : ""}>
        <input type="text" class="form-input builder-opt-input" data-index="${optIdx}" value="${optText}" placeholder="Option ${optIdx + 1}">
      `;
      optionsContainer.appendChild(row);
    });
  }

  saveCurrentQuestionForm() {
    if (!this.currentEditingQuiz) return;
    const q = this.currentEditingQuiz.questions[this.currentQuestionIndex];
    if (!q) return;

    q.text = document.getElementById("builderQuestionPrompt").value || "Untitled Question";
    q.code = document.getElementById("builderQuestionCode").value.trim() || null;
    q.explanation = document.getElementById("builderExplanation").value.trim() || "";

    const optionInputs = document.querySelectorAll(".builder-opt-input");
    q.options = Array.from(optionInputs).map(inp => inp.value || "Option");

    const selectedRadio = document.querySelector('input[name="builderCorrectOption"]:checked');
    if (selectedRadio) {
      q.correct = parseInt(selectedRadio.value, 10);
    }
  }

  addNewQuestion() {
    if (!this.currentEditingQuiz) return;
    this.saveCurrentQuestionForm();

    const newQ = {
      id: "q-" + Date.now(),
      text: "New Question",
      code: null,
      options: ["Option A", "Option B", "Option C", "Option D"],
      correct: 0,
      explanation: ""
    };

    this.currentEditingQuiz.questions.push(newQ);
    this.currentQuestionIndex = this.currentEditingQuiz.questions.length - 1;
    this.renderBuilderQuestionList();
    this.renderCurrentBuilderQuestion();
  }

  removeQuestion(index) {
    if (!this.currentEditingQuiz || this.currentEditingQuiz.questions.length <= 1) return;
    this.currentEditingQuiz.questions.splice(index, 1);
    if (this.currentQuestionIndex >= this.currentEditingQuiz.questions.length) {
      this.currentQuestionIndex = this.currentEditingQuiz.questions.length - 1;
    }
    this.renderBuilderQuestionList();
    this.renderCurrentBuilderQuestion();
  }

  saveFullQuiz() {
    if (!this.currentEditingQuiz) return;
    this.saveCurrentQuestionForm();

    const title = document.getElementById("builderQuizTitle").value.trim() || "Untitled Quiz";
    const joinCodeInput = document.getElementById("builderJoinCode");
    const joinCode = (joinCodeInput?.value.trim() || ("QZ-" + Math.floor(1000 + Math.random() * 9000))).toUpperCase();

    this.currentEditingQuiz.title = title;
    this.currentEditingQuiz.joinCode = joinCode;
    this.currentEditingQuiz.teacherName = "Prof. Alan Turing";
    this.currentEditingQuiz.category = document.getElementById("builderCategory").value.trim() || "General";
    this.currentEditingQuiz.durationMinutes = parseInt(document.getElementById("builderDuration").value, 10) || 10;
    this.currentEditingQuiz.passingScore = parseInt(document.getElementById("builderPassing").value, 10) || 60;
    this.currentEditingQuiz.description = document.getElementById("builderDescription").value.trim();

    quizStorage.saveQuiz(this.currentEditingQuiz);

    // Sync to backend SQLite
    fetch("/api/quizzes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(this.currentEditingQuiz)
    }).catch(() => {});

    window.showToast?.(`Quiz saved! Student Join Code: ${joinCode}`, "success");
    this.init();
    renderStudentCatalog();
    window.switchView("examiner");
  }

  deleteQuiz(quizId) {
    if (confirm("Are you sure you want to delete this quiz? This action cannot be undone.")) {
      quizStorage.deleteQuiz(quizId);
      window.showToast?.("Quiz deleted.", "warning");
      this.init();
      renderStudentCatalog();
    }
  }

  exportQuiz(quizId) {
    const quizzes = quizStorage.getQuizzes();
    const quiz = quizzes.find(q => q.id === quizId);
    if (!quiz) return;

    const blob = new Blob([JSON.stringify(quiz, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${quiz.title.toLowerCase().replace(/[^a-z0-9]/g, "-")}-quiz.json`;
    a.click();
    URL.revokeObjectURL(url);
    window.showToast?.("Quiz exported as JSON", "success");
  }

  importQuiz(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const quiz = JSON.parse(e.target.result);
        if (!quiz.title || !Array.isArray(quiz.questions)) {
          throw new Error("Invalid quiz schema");
        }
        quiz.id = "quiz-" + Date.now();
        if (!quiz.joinCode) {
          quiz.joinCode = "QZ-" + Math.floor(1000 + Math.random() * 9000);
        }
        quizStorage.saveQuiz(quiz);
        window.showToast?.(`Imported "${quiz.title}" (Code: ${quiz.joinCode}) successfully!`, "success");
        this.init();
        renderStudentCatalog();
      } catch (err) {
        window.showToast?.("Failed to import quiz. Invalid JSON format.", "danger");
      }
    };
    reader.readAsText(file);
  }

  // =========================================================================
  // STUDENT SUBMISSIONS & GRADEBOOK ROSTER MANAGEMENT
  // =========================================================================
  async loadSubmissionsRoster() {
    let localAttempts = quizStorage.getAttempts() || [];

    // Also attempt to fetch server reports if backend is available
    try {
      const res = await fetch("/api/teacher/reports");
      if (res.ok) {
        const serverReports = await res.json();
        // Merge and deduplicate by id
        const map = new Map();
        localAttempts.forEach(a => map.set(a.id, a));
        serverReports.forEach(r => {
          map.set(r.id, {
            id: r.id,
            quizTitle: r.quizTitle,
            joinCode: r.joinCode,
            studentName: r.studentName,
            candidateName: r.studentName,
            score: r.score,
            totalQuestions: r.totalQuestions,
            percentage: r.percentage,
            passed: r.passed,
            cheatViolations: r.cheatViolations,
            submittedAt: r.submittedAt
          });
        });
        localAttempts = Array.from(map.values());
      }
    } catch (e) {
      /* offline fallback */
    }

    // Sort by newest first
    const parseTime = d => {
      if (!d) return 0;
      const t = new Date(typeof d === 'string' ? d.replace(' ', 'T') : d).getTime();
      return isNaN(t) ? 0 : t;
    };
    localAttempts.sort((a, b) => parseTime(b.submittedAt) - parseTime(a.submittedAt));
    this.allSubmissions = localAttempts;

    // Populate filter dropdown
    const filterSelect = document.getElementById("rosterQuizFilter");
    if (filterSelect) {
      const quizzes = quizStorage.getQuizzes();
      const currentVal = filterSelect.value || "ALL";
      filterSelect.innerHTML = `<option value="ALL">All Assessments (${this.allSubmissions.length})</option>`;
      quizzes.forEach(q => {
        const opt = document.createElement("option");
        opt.value = q.joinCode || q.id;
        opt.textContent = `${q.title.substring(0, 24)} (${q.joinCode || 'Code'})`;
        filterSelect.appendChild(opt);
      });
      if (Array.from(filterSelect.options).some(o => o.value === currentVal)) {
        filterSelect.value = currentVal;
      }
    }

    this.filterSubmissions();
    this.renderStats();
  }

  filterSubmissions() {
    const tbody = document.getElementById("studentSubmissionsTableBody");
    if (!tbody) return;

    const quizFilter = document.getElementById("rosterQuizFilter")?.value || "ALL";
    const searchQuery = (document.getElementById("rosterSearchStudent")?.value || "").trim().toLowerCase();

    const filtered = this.allSubmissions.filter(item => {
      const matchesQuiz = quizFilter === "ALL" || (item.joinCode && item.joinCode.toUpperCase() === quizFilter.toUpperCase()) || item.quizId === quizFilter;
      const sName = (item.studentName || item.candidateName || "").toLowerCase();
      const qTitle = (item.quizTitle || "").toLowerCase();
      const matchesSearch = !searchQuery || sName.includes(searchQuery) || qTitle.includes(searchQuery);
      return matchesQuiz && matchesSearch;
    });

    tbody.innerHTML = "";

    if (filtered.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="9" style="text-align:center; padding:2.5rem 1rem; color:var(--text-muted);">
            No student submissions found. Share the <strong>Quiz Join Code</strong> with students to take the test.
          </td>
        </tr>
      `;
      return;
    }

    filtered.forEach(sub => {
      const row = document.createElement("tr");
      const name = sub.studentName || sub.candidateName || "Candidate";
      const title = sub.quizTitle || "Assessment";
      const code = sub.joinCode || "QZ-1001";
      const passed = sub.passed;
      const dateStr = sub.submittedAt ? new Date(sub.submittedAt).toLocaleString() : "Just now";
      const violations = sub.cheatViolations || 0;

      row.innerHTML = `
        <td><strong style="color:var(--text-main); font-size:0.95rem;">👤 ${name}</strong></td>
        <td><span style="color:var(--text-muted);">${title}</span></td>
        <td><span class="badge badge-cyan" style="font-weight:700;">${code}</span></td>
        <td><strong style="color:var(--text-main);">${sub.score} / ${sub.totalQuestions}</strong></td>
        <td><strong style="color:${passed ? '#059669' : '#dc2626'};">${sub.percentage}%</strong></td>
        <td>
          <span class="badge ${passed ? 'badge-success' : 'badge-danger'}">
            ${passed ? 'PASSED 🏆' : 'FAILED'}
          </span>
        </td>
        <td>
          ${violations > 0 ? `<span style="color:#d97706; font-weight:700;">⚠️ ${violations}</span>` : `<span style="color:var(--text-dim);">0</span>`}
        </td>
        <td><span style="color:var(--text-dim); font-size:0.8rem;">${dateStr}</span></td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="generateCertificate('${name.replace(/'/g, "\\'")}', '${title.replace(/'/g, "\\'")}', ${sub.percentage})" title="Download Student Certificate">
            📜 Certificate
          </button>
        </td>
      `;
      tbody.appendChild(row);
    });
  }

  exportSubmissionsCSV() {
    if (!this.allSubmissions || this.allSubmissions.length === 0) {
      window.showToast?.("No student submissions to export.", "warning");
      return;
    }

    const headers = ["Student Name", "Assessment Title", "Join Code", "Score", "Total Questions", "Percentage", "Status", "Violations", "Submitted At"];
    const rows = this.allSubmissions.map(s => [
      `"${(s.studentName || s.candidateName || 'Candidate').replace(/"/g, '""')}"`,
      `"${(s.quizTitle || 'Assessment').replace(/"/g, '""')}"`,
      `"${s.joinCode || 'QZ-1001'}"`,
      s.score,
      s.totalQuestions,
      `${s.percentage}%`,
      s.passed ? "PASSED" : "FAILED",
      s.cheatViolations || 0,
      `"${s.submittedAt || ''}"`
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `student-submissions-gradebook-${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.showToast?.("Class Submissions Gradebook CSV downloaded!", "success");
  }
}

window.examinerStudio = new ExaminerStudio();
var examinerStudio = window.examinerStudio;
