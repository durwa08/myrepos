import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "react-toastify";
import StudentLayout from "../layouts/StudentLayout";
import {
  getQuizById,
  getCategories,
  startAttempt,
  getActiveAttempt,
} from "../services/quizService";

import "../styles/quizInstructions.css";

/**
 * QuizInstructions Component
 * Displays instructions and metadata for a specific quiz, allowing students 
 * to either start a brand new attempt or resume an active session.
 */
function QuizInstructions() {
  const { quizId } = useParams();
  const navigate = useNavigate();

  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [hasActiveAttempt, setHasActiveAttempt] = useState(false);

  useEffect(() => {
    /**
     * Fetches initialization data for the target quiz including its metadata,
     * category assignment, and active completion statuses.
     */
    async function loadQuiz() {
      try {
        const [quizData, categories] = await Promise.all([
          getQuizById(quizId),
          getCategories(),
        ]);

        const active = await getActiveAttempt(quizId);
        setHasActiveAttempt(Boolean(active));

        const category = categories.find(
          (item) => item.id === quizData.category_id
        );

        setQuiz({
          ...quizData,
          categoryName: category?.name || "N/A",
        });
      } catch (error) {
        console.error("Failed to load quiz:", error);
      } finally {
        setLoading(false);
      }
    }

    loadQuiz();
  }, [quizId]);

  /**
   * Initiates or resumes a quiz attempt sequence.
   * Leverages built-in backend auto-resume mechanisms if an attempt exists.
   */
  const handleStartAssessment = async () => {
    try {
      setStarting(true);

      const attempt = await startAttempt(quizId);
      const isResuming = Object.keys(attempt.answers || {}).length > 0;

      toast.success(
        isResuming
          ? "Resuming your previous attempt."
          : "Assessment started successfully."
      );

      navigate(`/student/attempt/${attempt.id}`);
    } catch (error) {
      console.error(error.response?.data);

      toast.error(
        error.response?.data?.detail ||
        "Unable to start assessment."
      );
    } finally {
      setStarting(false);
    }
  };

  if (loading) {
    return (
      <StudentLayout>
        <div className="quiz-instructions-loading">
          <div className="spinner"></div>
          <p>Loading quiz...</p>
        </div>
      </StudentLayout>
    );
  }

  if (!quiz) {
    return (
      <StudentLayout>
        <div className="quiz-instructions-loading">
          <p>Quiz not found.</p>
        </div>
      </StudentLayout>
    );
  }

  return (
    <StudentLayout>
      <div className="quiz-instructions">
        <div className="instructions-card">
          <div className="instructions-hero">
            <span className="instructions-category">{quiz.categoryName}</span>
            <h1>{quiz.title}</h1>
            <p className="description">
              {quiz.description || "No description available."}
            </p>
          </div>

          <div className="quiz-info">
            <div className="info-item">
              <span className="info-icon">⏱️</span>
              <div>
                <span className="info-label">Time Limit</span>
                <strong>{quiz.time_limit_minutes} Minutes</strong>
              </div>
            </div>

            <div className="info-item">
              <span className="info-icon">🎯</span>
              <div>
                <span className="info-label">Pass Percentage</span>
                <strong>{quiz.pass_percentage}%</strong>
              </div>
            </div>
          </div>

          <div className="instructions-box">
            <h3>Instructions</h3>

            <ul>
              <li>Read every question carefully before answering.</li>
              <li>The timer starts immediately after you begin the assessment.</li>
              <li>Your answers are automatically saved as you attempt the quiz.</li>
              <li>You may navigate between questions before submitting.</li>
              <li>Submit the assessment before the allotted time expires.</li>
              <li>Once submitted, your answers cannot be modified.</li>
            </ul>
          </div>

          <button
            className="start-btn"
            onClick={handleStartAssessment}
            disabled={starting}
          >
            {starting
              ? "Starting Assessment..."
              : hasActiveAttempt
              ? "Continue Assessment"
              : "Start Assessment"}
          </button>
        </div>
      </div>
    </StudentLayout>
  );
}

export default QuizInstructions;