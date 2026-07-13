import api from "./api";

export const getQuizzes = async () => {
  const response = await api.get("/quizzes");
  return response.data;
};

export const getQuizById = async (quizId) => {
  const response = await api.get(`/quizzes/${quizId}`);
  return response.data;
};

export const getQuizQuestionCount = async (quizId) => {
  try {
    const response = await api.get(`/quizzes/${quizId}/question-count`);
    return response.data.question_count || 0;
  } catch (error) {
    console.error(`Failed to fetch question count for quiz ${quizId}:`, error);
    return 0;
  }
};

export const getQuizzesQuestionCounts = async (quizIds) => {
  try {
    const counts = {};
    await Promise.all(
      quizIds.map(async (quizId) => {
        counts[quizId] = await getQuizQuestionCount(quizId);
      })
    );
    return counts;
  } catch (error) {
    console.error("Failed to fetch question counts:", error);
    return {};
  }
};

export const createQuiz = async (quizData) => {
  const response = await api.post("/quizzes", quizData);
  return response.data;
};

export const updateQuiz = async (quizId, quizData) => {
  const response = await api.put(`/quizzes/${quizId}`, quizData);
  return response.data;
};

export const deleteQuiz = async (quizId) => {
  const response = await api.delete(`/quizzes/${quizId}`);
  return response.data;
};

export const startAttempt = async (quizId) => {
  const response = await api.post(`/attempts/start/${quizId}`);
  return response.data;
};

export const getCategories = async () => {
  const response = await api.get("/categories");
  return response.data;
};
export const getActiveAttempt = async (quizId) => {
  const response = await api.get(`/attempts/active/${quizId}`);
  return response.data;
};