import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import StudentLayout from "../layouts/StudentLayout";
import {
  getCategories,
  getQuizzes,
  getQuizzesQuestionCounts,
  getActiveAttempt,
  startAttempt,
} from "../services/quizService";
import "../styles/browseQuizzes.css";

/**
 * BrowseQuizzes Component
 * Allows students to view available quizzes, see current progression,
 * and either start a new attempt or resume an active session.
 */
function BrowseQuizzes() {
  const navigate = useNavigate();
  const [quizzes, setQuizzes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [questionCounts, setQuestionCounts] = useState({});
  const [loading, setLoading] = useState(true);
  const [activeAttempts, setActiveAttempts] = useState({});

  useEffect(() => {
    /**
     * Fetches initialization data for the page including categories,
     * available quizzes, question quantities, and active student attempts.
     */
    const loadQuizzesData = async () => {
      try {
        const [quizData, categoryData] = await Promise.all([
          getQuizzes(),
          getCategories(),
        ]);

        setQuizzes(quizData || []);
        setCategories(categoryData || []);

        if (quizData && quizData.length > 0) {
          const quizIds = quizData.map((quiz) => quiz.id);
          const counts = await getQuizzesQuestionCounts(quizIds);
          setQuestionCounts(counts);

          const activeChecks = {};
          await Promise.all(
            quizData.map(async (quiz) => {
              const active = await getActiveAttempt(quiz.id);
              if (active) {
                activeChecks[quiz.id] = active;
              }
            })
          );
          setActiveAttempts(activeChecks);
        }
      } catch (error) {
        console.error("Failed to load quizzes:", error);
        setQuizzes([]);
        setCategories([]);
      } finally {
        setLoading(false);
      }
    };

    loadQuizzesData();
  }, []);

  /**
   * Resolves a category ID to its corresponding display name.
   * @param {string|number} categoryId - The unique identifier of the category.
   * @returns {string} The matching category name, or "General" as a fallback.
   */
  const getCategoryName = (categoryId) => {
    const category = categories.find((cat) => cat.id === categoryId);
    return category ? category.name : "General";
  };

  /**
   * Retrieves the question quantity for a specific quiz tracking key.
   * @param {string|number} quizId - The unique identifier of the target quiz.
   * @returns {number} Number of assigned questions.
   */
  const getQuestionCount = (quizId) => {
    return questionCounts[quizId] || 0;
  };

  /**
   * Initiates or resumes a quiz attempt sequence.
   * @param {Object} quiz - The configuration record of the selected quiz.
   */
  const handleStartQuiz = async (quiz) => {
    try {
      const attempt = await startAttempt(quiz.id);
      navigate(`/student/attempt/${attempt.id}`);
    } catch (error) {
      console.error("Failed to start/resume quiz:", error);
    }
  };

  return (
    <StudentLayout>
      <div className="browse-quizzes-page">
        <div className="page-header">
          <h1>📚 Browse Quizzes</h1>
          <p>Select a quiz and start your assessment.</p>
        </div>

        {loading && (
          <div className="loading-container">
            <p>Loading quizzes...</p>
          </div>
        )}

        {!loading && quizzes.length === 0 && (
          <div className="empty-state">
            <h3>No Quizzes Available</h3>
            <p>Please check back later.</p>
          </div>
        )}

        {!loading && quizzes.length > 0 && (
          <div className="quizzes-container">
            {quizzes.map((quiz) => (
              <div key={quiz.id} className="quiz-card">
                <div className="quiz-card-header">
                  <div className="quiz-card-category">
                    {getCategoryName(quiz.category_id)}
                  </div>
                  <h3>{quiz.title}</h3>
                </div>

                <p className="quiz-card-description">
                  {quiz.description || "No description available."}
                </p>

                <div className="quiz-card-meta">
                  <div className="meta-item">
                    <div className="meta-item-label">Time Limit</div>
                    <div className="meta-item-value">
                      {quiz.time_limit_minutes} mins
                    </div>
                  </div>

                  <div className="meta-item">
                    <div className="meta-item-label">Questions</div>
                    <div className="meta-item-value">
                      {getQuestionCount(quiz.id)}
                    </div>
                  </div>
                </div>

                <button 
                  className="start-quiz-btn"
                  onClick={() => handleStartQuiz(quiz)}
                >
                  {activeAttempts[quiz.id] ? "Continue Quiz" : "Start Quiz"}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </StudentLayout>
  );
}

export default BrowseQuizzes;