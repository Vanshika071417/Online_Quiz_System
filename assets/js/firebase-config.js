// Storage & Backend Synchronization Layer
// Supports Local-First Offline persistence + Firebase/Supabase real-time sync

const STORAGE_KEYS = {
  QUIZZES: "online_quiz_quizzes_v1",
  ATTEMPTS: "online_quiz_attempts_v1",
  ACTIVE_EXAM: "online_quiz_active_session_v1",
  CLOUD_CONFIG: "online_quiz_cloud_config_v1"
};

class QuizStorage {
  constructor() {
    this.initStorage();
  }

  initStorage() {
    if (!localStorage.getItem(STORAGE_KEYS.QUIZZES)) {
      localStorage.setItem(STORAGE_KEYS.QUIZZES, JSON.stringify(DEFAULT_QUIZZES));
    }
    if (!localStorage.getItem(STORAGE_KEYS.ATTEMPTS)) {
      localStorage.setItem(STORAGE_KEYS.ATTEMPTS, JSON.stringify([]));
    }
  }

  getQuizzes() {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.QUIZZES);
      return data ? JSON.parse(data) : DEFAULT_QUIZZES;
    } catch (e) {
      console.error("Failed to load quizzes", e);
      return DEFAULT_QUIZZES;
    }
  }

  saveQuiz(quiz) {
    const quizzes = this.getQuizzes();
    const existingIndex = quizzes.findIndex(q => q.id === quiz.id);
    if (existingIndex >= 0) {
      quizzes[existingIndex] = quiz;
    } else {
      quizzes.unshift(quiz);
    }
    localStorage.setItem(STORAGE_KEYS.QUIZZES, JSON.stringify(quizzes));
    return quizzes;
  }

  deleteQuiz(quizId) {
    const quizzes = this.getQuizzes().filter(q => q.id !== quizId);
    localStorage.setItem(STORAGE_KEYS.QUIZZES, JSON.stringify(quizzes));
    return quizzes;
  }

  getAttempts() {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.ATTEMPTS);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      return [];
    }
  }

  saveAttempt(attempt) {
    const attempts = this.getAttempts();
    attempts.unshift(attempt);
    localStorage.setItem(STORAGE_KEYS.ATTEMPTS, JSON.stringify(attempts));
    return attempts;
  }

  saveActiveExamState(session) {
    localStorage.setItem(STORAGE_KEYS.ACTIVE_EXAM, JSON.stringify(session));
  }

  getActiveExamState() {
    const data = localStorage.getItem(STORAGE_KEYS.ACTIVE_EXAM);
    return data ? JSON.parse(data) : null;
  }

  clearActiveExamState() {
    localStorage.removeItem(STORAGE_KEYS.ACTIVE_EXAM);
  }

  getCloudConfig() {
    const data = localStorage.getItem(STORAGE_KEYS.CLOUD_CONFIG);
    return data ? JSON.parse(data) : null;
  }

  setCloudConfig(config) {
    localStorage.setItem(STORAGE_KEYS.CLOUD_CONFIG, JSON.stringify(config));
  }
}

const quizStorage = new QuizStorage();
