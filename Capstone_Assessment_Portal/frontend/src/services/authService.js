import api from "./api";

export const loginUser = async (data) => {
  const response = await api.post("/auth/login", data);
  return response.data;
};

export const registerUser = async (data) => {
  const response = await api.post("/auth/register", data);
  return response.data;
};

export const checkEmail = async (email) => {
  const response = await api.get(`/auth/check-email/${email}`);
  return response.data;
};