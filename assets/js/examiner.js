// Examiner & Question Bank Management

class ExaminerStudio {
  constructor() {
    this.currentEditingQuiz = null;
    this.currentQuestionIndex = 0;
  }

  init() {
    this.renderStats();
    this.renderQuizCatalog();
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
      card.innerHTML = `
        <div>
          <div class="quiz-card-head">
            <span class="badge badge-cyan">${quiz.category || 'General'}</span>
            <span class="badge badge-indigo">${quiz.questions.length} Questions</span>
          </div>
          <h3 style="font-size:1.15rem; margin-bottom:0.4rem; color:#fff;">${quiz.title}</h3>
          <p style="font-size:0.85rem; color:var(--text-muted); line-height:1.4;">${quiz.description || 'No description provided.'}</p>
          <div class="quiz-meta-row">
            <span>⏱️ ${quiz.durationMinutes} mins</span>
            <span>🎯 Passing: ${quiz.passingScore}%</span>
          </div>
        </div>
        <div class="quiz-card-actions">
          <button class="btn btn-secondary btn-sm" onclick="examinerStudio.editQuiz('${quiz.id}')">✏️ Edit</button>
          <button class="btn btn-secondary btn-sm" onclick="examinerStudio.exportQuiz('${quiz.id}')">💾 Export</button>
          <button class="btn btn-danger btn-sm" onclick="examinerStudio.deleteQuiz('${quiz.id}')">🗑️ Delete</button>
        </div>
      `;
      container.appendChild(card);
    });
  }

  openCreateQuizModal() {
    this.currentEditingQuiz = {
      id: "quiz-" + Date.now(),
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
    document.getElementById("builderQuizTitle").value = quiz.title;
    document.getElementById("builderCategory").value = quiz.category || "";
    document.getElementById("builderDuration").value = quiz.durationMinutes;
    document.getElementById("builderPassing").value = quiz.passingScore;
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
        <span style="font-weight:600; font-size:0.875rem;">Q${idx + 1}: ${q.text.substring(0, 22)}...</span>
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
    document.getElementById("builderQuestionPrompt").value = q.text;
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

    // Read options
    const optionInputs = document.querySelectorAll(".builder-opt-input");
    q.options = Array.from(optionInputs).map(inp => inp.value || "Option");

    // Read selected radio
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

    this.currentEditingQuiz.title = document.getElementById("builderQuizTitle").value.trim() || "Untitled Quiz";
    this.currentEditingQuiz.category = document.getElementById("builderCategory").value.trim() || "General";
    this.currentEditingQuiz.durationMinutes = parseInt(document.getElementById("builderDuration").value, 10) || 10;
    this.currentEditingQuiz.passingScore = parseInt(document.getElementById("builderPassing").value, 10) || 60;
    this.currentEditingQuiz.description = document.getElementById("builderDescription").value.trim();

    quizStorage.saveQuiz(this.currentEditingQuiz);
    window.showToast?.("Quiz saved successfully!", "success");
    this.init();
    window.switchView("examiner");
  }

  deleteQuiz(quizId) {
    if (confirm("Are you sure you want to delete this quiz? This action cannot be undone.")) {
      quizStorage.deleteQuiz(quizId);
      window.showToast?.("Quiz deleted.", "warning");
      this.init();
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
        quizStorage.saveQuiz(quiz);
        window.showToast?.(`Imported "${quiz.title}" successfully!`, "success");
        this.init();
      } catch (err) {
        window.showToast?.("Failed to import quiz. Invalid JSON format.", "danger");
      }
    };
    reader.readAsText(file);
  }
}

const examinerStudio = new ExaminerStudio();
