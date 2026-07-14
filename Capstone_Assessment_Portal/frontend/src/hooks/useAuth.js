import { useNavigate } from "react-router-dom";
import {
  loginUser,
  registerUser,
} from "../services/authService";
import { saveAuthData } from "../utils/storage";

export default function useAuth() {
  const navigate = useNavigate();

  const login = async (values) => {
    const data = await loginUser(values);

    saveAuthData(data);

    if (data.role === "admin") {
      navigate("/admin");
    } else {
      navigate("/student");
    }
  };

  const register = async (values) => {
    return await registerUser(values);
  };

  return {
    login,
    register,
  };
}