import api from "./api";

export const getQuizzes = async () => {
  const response = await api.get("/quizzes");
  return response.data;
};

export const createQuiz = async (quiz) => {
  const response = await api.post("/quizzes", quiz);
  return response.data;
};

export const updateQuiz = async (id, quiz) => {
  const response = await api.put(`/quizzes/${id}`, quiz);
  return response.data;
};

export const deleteQuiz = async (id) => {
  const response = await api.delete(`/quizzes/${id}`);
  return response.data;
};