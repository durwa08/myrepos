import axios from "axios";

const API_URL = "http://localhost:8000/attempts"; // Adjust based on your backend address

// Add JWT access token to requests from localStorage
const getAuthHeaders = () => {
  const token = localStorage.getItem("token");
  return { headers: { Authorization: `Bearer ${token}` } };
};

/**
 * Fetches all submitted results across all candidates for the admin dashboard
 */
export const getAdminDashboardResults = async () => {
  const response = await axios.get(`${API_URL}/admin/dashboard`, getAuthHeaders());
  return response.data;
};