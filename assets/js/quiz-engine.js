// Core Examination Execution Engine & Anti-Cheat Monitor

class QuizEngine {
  constructor() {
    this.currentQuiz = null;
    this.currentIndex = 0;
    this.answers = {}; // questionId: selectedOptionIndex
    this.reviewFlags = {}; // questionId: boolean
    this.timeLeftSeconds = 0;
    this.timerInterval = null;
    this.cheatViolations = 0;
    this.startTime = null;
    this.candidateName = "Candidate";
    this.isExamActive = false;

    this.bindAntiCheatListeners();
  }

  bindAntiCheatListeners() {
    // Detect window blur / tab switching
    window.addEventListener("blur", () => {
      if (this.isExamActive) {
        this.recordCheatViolation("Window focus lost (switched apps/tabs)");
      }
    });

    // Detect Page Visibility changes
    document.addEventListener("visibilitychange", () => {
      if (this.isExamActive && document.visibilityState === "hidden") {
        this.recordCheatViolation("Tab hidden or browser minimized");
      }
    });
  }

  recordCheatViolation(reason) {
    this.cheatViolations++;
    const banner = document.getElementById("cheatAlertBanner");
    const countSpan = document.getElementById("cheatViolationCount");
    if (banner && countSpan) {
      countSpan.textContent = this.cheatViolations;
      banner.style.display = "flex";
    }
    window.showToast?.(`Proctor Warning: ${reason} (Violation #${this.cheatViolations})`, "danger");
  }

  startQuiz(quiz, candidateName = "Candidate") {
    this.currentQuiz = quiz;
    this.candidateName = candidateName;
    this.currentIndex = 0;
    this.answers = {};
    this.reviewFlags = {};
    this.cheatViolations = 0;
    this.timeLeftSeconds = quiz.durationMinutes * 60;
    this.startTime = new Date().toISOString();
    this.isExamActive = true;

    // Reset cheat alert UI
    const banner = document.getElementById("cheatAlertBanner");
    if (banner) banner.style.display = "none";

    this.startTimer();
    this.renderCurrentQuestion();
    this.renderPalette();
  }

  startTimer() {
    if (this.timerInterval) clearInterval(this.timerInterval);

    const updateTimerDisplay = () => {
      const minutes = Math.floor(this.timeLeftSeconds / 60);
      const seconds = this.timeLeftSeconds % 60;
      const formatted = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;

      const timerElem = document.getElementById("examTimerText");
      const timerBox = document.getElementById("examTimerBox");

      if (timerElem) timerElem.textContent = formatted;

      if (timerBox) {
        if (this.timeLeftSeconds <= 60) {
          timerBox.classList.add("urgent");
        } else {
          timerBox.classList.remove("urgent");
        }
      }

      if (this.timeLeftSeconds <= 0) {
        clearInterval(this.timerInterval);
        this.autoSubmitDueToTime();
      } else {
        this.timeLeftSeconds--;
      }
    };

    updateTimerDisplay();
    this.timerInterval = setInterval(updateTimerDisplay, 1000);
  }

  renderCurrentQuestion() {
    if (!this.currentQuiz) return;
    const q = this.currentQuiz.questions[this.currentIndex];
    if (!q) return;

    // Update Question Meta
    const metaIndex = document.getElementById("questionIndexLabel");
    if (metaIndex) {
      metaIndex.textContent = `Question ${this.currentIndex + 1} of ${this.currentQuiz.questions.length}`;
    }

    // Update Text & Code
    const promptElem = document.getElementById("questionPrompt");
    if (promptElem) promptElem.textContent = q.text;

    const codeContainer = document.getElementById("questionCodeContainer");
    if (codeContainer) {
      if (q.code) {
        codeContainer.style.display = "block";
        codeContainer.textContent = q.code;
      } else {
        codeContainer.style.display = "none";
      }
    }

    // Render Options
    const optionsList = document.getElementById("optionsList");
    if (optionsList) {
      optionsList.innerHTML = "";
      const letters = ["A", "B", "C", "D", "E", "F"];
      const currentAnswer = this.answers[q.id];

      q.options.forEach((optText, optIndex) => {
        const item = document.createElement("div");
        item.className = `option-item ${currentAnswer === optIndex ? "selected" : ""}`;
        item.onclick = () => this.selectOption(optIndex);

        item.innerHTML = `
          <div class="option-marker">${letters[optIndex] || optIndex + 1}</div>
          <div class="option-text">${optText}</div>
        `;
        optionsList.appendChild(item);
      });
    }

    // Update review button state
    const reviewBtn = document.getElementById("markReviewBtn");
    if (reviewBtn) {
      const isMarked = !!this.reviewFlags[q.id];
      reviewBtn.textContent = isMarked ? "★ Marked for Review" : "☆ Mark for Review";
      reviewBtn.className = isMarked ? "btn btn-warning btn-sm" : "btn btn-secondary btn-sm";
    }

    // Update Prev / Next buttons
    const prevBtn = document.getElementById("prevQuestionBtn");
    const nextBtn = document.getElementById("nextQuestionBtn");
    if (prevBtn) prevBtn.disabled = this.currentIndex === 0;
    if (nextBtn) {
      if (this.currentIndex === this.currentQuiz.questions.length - 1) {
        nextBtn.textContent = "Finish & Review";
      } else {
        nextBtn.textContent = "Next Question →";
      }
    }

    this.renderPalette();
  }

  selectOption(optIndex) {
    if (!this.currentQuiz) return;
    const q = this.currentQuiz.questions[this.currentIndex];
    this.answers[q.id] = optIndex;
    this.renderCurrentQuestion();
    this.renderPalette();
  }

  toggleReviewFlag() {
    if (!this.currentQuiz) return;
    const q = this.currentQuiz.questions[this.currentIndex];
    this.reviewFlags[q.id] = !this.reviewFlags[q.id];
    this.renderCurrentQuestion();
    this.renderPalette();
  }

  navigate(direction) {
    if (!this.currentQuiz) return;
    const target = this.currentIndex + direction;
    if (target >= 0 && target < this.currentQuiz.questions.length) {
      this.currentIndex = target;
      this.renderCurrentQuestion();
    } else if (target >= this.currentQuiz.questions.length) {
      this.openSubmitConfirmModal();
    }
  }

  jumpTo(index) {
    if (this.currentQuiz && index >= 0 && index < this.currentQuiz.questions.length) {
      this.currentIndex = index;
      this.renderCurrentQuestion();
    }
  }

  renderPalette() {
    const paletteGrid = document.getElementById("paletteGrid");
    if (!paletteGrid || !this.currentQuiz) return;

    paletteGrid.innerHTML = "";
    this.currentQuiz.questions.forEach((q, idx) => {
      const btn = document.createElement("button");
      btn.className = "palette-btn";
      btn.textContent = idx + 1;

      if (idx === this.currentIndex) {
        btn.classList.add("current");
      }
      if (this.answers[q.id] !== undefined) {
        btn.classList.add("answered");
      }
      if (this.reviewFlags[q.id]) {
        btn.classList.add("review");
      }

      btn.onclick = () => this.jumpTo(idx);
      paletteGrid.appendChild(btn);
    });
  }

  openSubmitConfirmModal() {
    const modal = document.getElementById("submitConfirmModal");
    const answeredCount = Object.keys(this.answers).length;
    const totalCount = this.currentQuiz.questions.length;
    const unattemptedCount = totalCount - answeredCount;

    document.getElementById("modalAnsweredCount").textContent = answeredCount;
    document.getElementById("modalUnattemptedCount").textContent = unattemptedCount;
    document.getElementById("modalViolationsCount").textContent = this.cheatViolations;

    if (modal) modal.classList.add("open");
  }

  closeSubmitConfirmModal() {
    const modal = document.getElementById("submitConfirmModal");
    if (modal) modal.classList.remove("open");
  }

  autoSubmitDueToTime() {
    window.showToast?.("Time has expired! Submitting test automatically...", "warning");
    this.closeSubmitConfirmModal();
    this.finalizeSubmission();
  }

  finalizeSubmission() {
    this.isExamActive = false;
    if (this.timerInterval) clearInterval(this.timerInterval);

    // Calculate score
    let correctCount = 0;
    this.currentQuiz.questions.forEach(q => {
      if (this.answers[q.id] === q.correct) {
        correctCount++;
      }
    });

    const totalQuestions = this.currentQuiz.questions.length;
    const scorePercentage = Math.round((correctCount / totalQuestions) * 100);
    const passed = scorePercentage >= this.currentQuiz.passingScore;

    const attemptRecord = {
      id: "attempt-" + Date.now(),
      quizId: this.currentQuiz.id,
      quizTitle: this.currentQuiz.title,
      candidateName: this.candidateName,
      submittedAt: new Date().toISOString(),
      score: correctCount,
      totalQuestions: totalQuestions,
      percentage: scorePercentage,
      passed: passed,
      cheatViolations: this.cheatViolations,
      answers: { ...this.answers }
    };

    quizStorage.saveAttempt(attemptRecord);
    this.renderResultScreen(attemptRecord);
    window.switchView("result");
  }

  renderResultScreen(attempt) {
    document.getElementById("resultCandidateName").textContent = attempt.candidateName;
    document.getElementById("resultQuizTitle").textContent = attempt.quizTitle;
    document.getElementById("resultPercentageNumber").textContent = `${attempt.percentage}%`;
    document.getElementById("resultCorrectQuestions").textContent = `${attempt.score} / ${attempt.totalQuestions}`;
    document.getElementById("resultViolations").textContent = attempt.cheatViolations;

    // Badge status
    const statusBadge = document.getElementById("resultStatusBadge");
    if (statusBadge) {
      if (attempt.passed) {
        statusBadge.textContent = "PASSED";
        statusBadge.className = "badge badge-success";
      } else {
        statusBadge.textContent = "NEEDS IMPROVEMENT";
        statusBadge.className = "badge badge-danger";
      }
    }

    // Animate Circular Gauge
    const gaugeCircle = document.getElementById("resultGaugeCircle");
    if (gaugeCircle) {
      const radius = 64;
      const circumference = 2 * Math.PI * radius;
      gaugeCircle.style.strokeDasharray = `${circumference}`;
      const offset = circumference - (attempt.percentage / 100) * circumference;
      setTimeout(() => {
        gaugeCircle.style.strokeDashoffset = `${offset}`;
      }, 100);
    }

    // Render detailed answer review list
    this.renderAnswerReviewList(attempt);
  }

  renderAnswerReviewList(attempt) {
    const listContainer = document.getElementById("answerReviewList");
    if (!listContainer || !this.currentQuiz) return;

    listContainer.innerHTML = "";
    this.currentQuiz.questions.forEach((q, idx) => {
      const userSelected = attempt.answers[q.id];
      const isCorrect = userSelected === q.correct;
      const isSkipped = userSelected === undefined;

      const card = document.createElement("div");
      card.className = "card";
      card.style.marginBottom = "1rem";
      card.style.borderLeft = isCorrect 
        ? "4px solid var(--accent-success)" 
        : (isSkipped ? "4px solid var(--accent-warning)" : "4px solid var(--accent-danger)");

      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
          <span style="font-weight:700;">Question ${idx + 1}</span>
          <span class="badge ${isCorrect ? 'badge-success' : (isSkipped ? 'badge-warning' : 'badge-danger')}">
            ${isCorrect ? 'Correct' : (isSkipped ? 'Skipped' : 'Incorrect')}
          </span>
        </div>
        <p style="margin-bottom:0.75rem; color:#fff;">${q.text}</p>
        <div style="font-size:0.875rem; margin-bottom:0.5rem;">
          <div style="color:var(--text-muted);">Your Answer: <strong style="color:${isCorrect ? '#10b981' : '#ef4444'}">${userSelected !== undefined ? q.options[userSelected] : 'Not Answered'}</strong></div>
          <div style="color:var(--text-muted);">Correct Answer: <strong style="color:#10b981">${q.options[q.correct]}</strong></div>
        </div>
        <div style="background:rgba(0,0,0,0.25); padding:0.6rem 0.85rem; border-radius:var(--radius-sm); font-size:0.825rem; color:var(--text-muted); border-left:3px solid var(--accent-cyan);">
          💡 <strong>Explanation:</strong> ${q.explanation}
        </div>
      `;
      listContainer.appendChild(card);
    });
  }
}

const quizEngine = new QuizEngine();
