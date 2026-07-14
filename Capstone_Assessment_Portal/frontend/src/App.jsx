import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/auth/Login";

import AdminDashboard from "./pages/admin/AdminDashboard";
import Categories from "./pages/admin/Categories";
import Quizzes from "./pages/admin/Quizzes";
import Questions from "./pages/admin/Questions";
import ResultsDashboard from "./pages/admin/ResultsDashboard";

import StudentDashboard from "./pages/student/StudentDashboard";
import BrowseQuizzes from "./pages/student/BrowseQuizzes";
import QuizInstructions from "./pages/student/QuizInstructions";
import TakeQuiz from "./pages/student/TakeQuiz";
import Results from "./pages/student/Results";
import MyResults from "./pages/student/MyResults";
import Profile from "./pages/student/Profile";

import ProtectedRoute from "./routes/ProtectedRoute";

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Public Route */}
        <Route path="/" element={<Login />} />

        {/* Admin Routes */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute role="admin">
              <AdminDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/categories"
          element={
            <ProtectedRoute role="admin">
              <Categories />
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

        <Route
          path="/admin/results"
          element={
            <ProtectedRoute role="admin">
              <ResultsDashboard />
            </ProtectedRoute>
          }
        />

        {/* Student Routes */}
        <Route
          path="/student"
          element={
            <ProtectedRoute role="student">
              <StudentDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/student/quizzes"
          element={
            <ProtectedRoute role="student">
              <BrowseQuizzes />
            </ProtectedRoute>
          }
        />

        <Route
          path="/student/quizzes/:quizId"
          element={
            <ProtectedRoute role="student">
              <QuizInstructions />
            </ProtectedRoute>
          }
        />

        <Route
          path="/student/attempt/:attemptId"
          element={
            <ProtectedRoute role="student">
              <TakeQuiz />
            </ProtectedRoute>
          }
        />

        <Route
          path="/student/results"
          element={
            <ProtectedRoute role="student">
              <MyResults />
            </ProtectedRoute>
          }
        />

        <Route
          path="/student/results/:attemptId"
          element={
            <ProtectedRoute role="student">
              <Results />
            </ProtectedRoute>
          }
        />

        <Route
          path="/student/profile"
          element={
            <ProtectedRoute role="student">
              <Profile />
            </ProtectedRoute>
          }
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;