import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import AdminDashboard from "./pages/AdminDashboard";
import StudentDashboard from "./pages/StudentDashboard";
import Categories from "./pages/Categories";
import Quizzes from "./pages/Quizzes";
import Questions from "./pages/Questions";
import ResultsDashboard from "./pages/ResultsDashboard";
import ProtectedRoute from "./routes/ProtectedRoute";

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Public Route */}
        <Route path="/" element={<Login />} />

        {/* Admin Dashboard */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute role="admin">
              <AdminDashboard />
            </ProtectedRoute>
          }
        />

        {/* Categories */}
        <Route
          path="/admin/categories"
          element={
            <ProtectedRoute role="admin">
              <Categories />
            </ProtectedRoute>
          }
        />

        {/* Student Dashboard */}
        <Route
          path="/student"
          element={
            <ProtectedRoute role="student">
              <StudentDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/quizzes"
          element={
            <ProtectedRoute role="admin">
              <Quizzes />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/questions"
          element={
            <ProtectedRoute role="admin">
              <Questions />
            </ProtectedRoute>
          }
        />

        {/* Results Dashboard - Added New Protected Route */}
        <Route
          path="/admin/results"
          element={
            <ProtectedRoute role="admin">
              <ResultsDashboard />
            </ProtectedRoute>
          }
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;