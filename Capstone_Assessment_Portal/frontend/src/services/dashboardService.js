import api from "./api";

export const getStudentProfile = async () => {
  const response = await api.get("/auth/me");
  return response.data;
};

export const getQuizzes = async () => {
  const response = await api.get("/quizzes");
  return response.data;
};

export const getCategories = async () => {
  const response = await api.get("/categories");
  return response.data;
};

export const getResultHistory = async () => {
  const response = await api.get("/results/history/me");
  return response.data;
};