import api from "./api";

/**
 * Retrieve the detailed result for a submitted attempt.
 *
 * @param {string} attemptId Attempt identifier.
 * @returns {Promise<Object>} Attempt result.
 */
export const getAttemptResult = async (attemptId) => {
  const response = await api.get(`/results/${attemptId}`);
  return response.data;
};

/**
 * Retrieve the logged-in student's result history.
 *
 * @returns {Promise<Array>} Result history.
 */
export const getStudentResultHistory = async () => {
  const response = await api.get("/results/history/me");
  return response.data;
};

/**
 * Retrieve all submitted assessment results for the administrator
 * dashboard.
 *
 * @returns {Promise<Array>} Assessment results.
 */
export const getAdminDashboardResults = async () => {
  const response = await api.get("/results/admin/dashboard");
  return response.data;
};