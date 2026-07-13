import { useState } from "react";
import { Navigate } from "react-router-dom";

import useAuth from "../hooks/useAuth";
import { checkEmail } from "../services/authService";
import { getAccessToken, getRole } from "../utils/storage";
import { toast } from "react-toastify";
import {
  validateLogin,
  validateRegister,
} from "../utils/validation";

import "../styles/login.css";

function Login() {
  const [isLogin, setIsLogin] = useState(true);

  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
  });

  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState("");
  const [loading, setLoading] = useState(false);

  const { login, register } = useAuth();

  const token = getAccessToken();
  const role = getRole();

  if (token) {
    return (
      <Navigate
        to={role === "admin" ? "/admin" : "/student"}
        replace
      />
    );
  }

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));

    setErrors((prev) => ({
      ...prev,
      [e.target.name]: "",
    }));

    setApiError("");
  };

  const resetForm = () => {
    setFormData({
      username: "",
      email: "",
      password: "",
    });

    setErrors({});
    setApiError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const validationErrors = isLogin
      ? validateLogin(formData)
      : validateRegister(formData);

    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setErrors({});
    setApiError("");
    setLoading(true);

    try {
      if (isLogin) {
        const emailExists = await checkEmail(formData.email);

        if (!emailExists.exists) {
          setErrors({
            email: "Email not registered. Please register first.",
          });
          return;
        }

        try {
          await login({
            email: formData.email,
            password: formData.password,
          });
        } catch {
          setErrors({
            password: "Incorrect password.",
          });
        }
      } else {
        await register({
          username: formData.username,
          email: formData.email,
          password: formData.password,
        });

        toast.success("Registration successful. Please login.");

        setIsLogin(true);
        resetForm();
      }
    } catch (error) {
    const message =
    error.response?.data?.detail || "Something went wrong.";

    setApiError(message);
    toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      {/* Left Panel */}
      <div className="left-panel">
        <div className="overlay">
          <h1>Assessment Portal</h1>

          <p className="subtitle">
            A secure and efficient platform for conducting online
            assessments.
          </p>

          <div className="features">
            <p>✔ Secure JWT Authentication</p>
            <p>✔ Quiz & Question Management</p>
            <p>✔ Instant Result Generation</p>
            <p>✔ Role Based Access Control</p>
          </div>

          <div className="quote">
            "Learn. Attempt. Achieve."
          </div>
        </div>
      </div>

      {/* Right Panel */}
      <div className="right-panel">
        <div className="form-card">
          <div className="toggle-buttons">
            <button
              type="button"
              className={isLogin ? "active" : ""}
              onClick={() => {
                setIsLogin(true);
                resetForm();
              }}
            >
              Login
            </button>

            <button
              type="button"
              className={!isLogin ? "active" : ""}
              onClick={() => {
                setIsLogin(false);
                resetForm();
              }}
            >
              Register
            </button>
          </div>

          <h2>
            {isLogin ? "Welcome Back" : "Create Account"}
          </h2>

          <form onSubmit={handleSubmit}>
            {!isLogin && (
              <div className="input-group">
                <label>Username</label>

                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  placeholder="Enter username"
                />

                {errors.username && (
                  <small className="error">
                    {errors.username}
                  </small>
                )}
              </div>
            )}

            <div className="input-group">
              <label>Email</label>

              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="Enter email"
              />

              {errors.email && (
                <small className="error">
                  {errors.email}
                </small>
              )}
            </div>

            <div className="input-group">
              <label>Password</label>

              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Enter password"
              />

              {errors.password && (
                <small className="error">
                  {errors.password}
                </small>
              )}
            </div>

            {!isLogin && (
              <p className="password-info">
                Password must contain at least 8 characters,
                one uppercase letter, one number and one special
                character.
              </p>
            )}

            {apiError && (
              <p className="api-error">
                {apiError}
              </p>
            )}

            <button
              type="submit"
              className="submit-btn"
              disabled={loading}
            >
              {loading
                ? isLogin
                  ? "Logging In..."
                  : "Registering..."
                : isLogin
                ? "Login"
                : "Register"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Login;