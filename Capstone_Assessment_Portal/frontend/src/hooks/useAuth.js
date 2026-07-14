import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

import {
  loginUser,
  registerUser,
} from "../services/authService";

import { saveAuthData } from "../utils/storage";

/**
 * Custom hook for handling authentication.
 *
 * Provides login and registration functionality,
 * stores authentication details, and redirects users
 * based on their role after successful login.
 */
export default function useAuth() {
  const navigate = useNavigate();

  /**
   * Authenticate the user and redirect to the
   * appropriate dashboard.
   *
   * @param {Object} values Login credentials.
   */
  const login = async (values) => {
    const data = await loginUser(values);

    saveAuthData(data);

    toast.success("Login successful.");

    if (data.role === "admin") {
      navigate("/admin");
    } else {
      navigate("/student");
    }
  };

  /**
   * Register a new user.
   *
   * @param {Object} values Registration details.
   * @returns {Promise<Object>} Registered user.
   */
  const register = async (values) => {
    return await registerUser(values);
  };

  return {
    login,
    register,
  };
}