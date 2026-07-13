import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import StudentLayout from "../layouts/StudentLayout";
import {
  getCategories,
  getQuizzes,
  getQuizzesQuestionCounts,
  startAttempt,
} from "../services/quizService";
import "../styles/browseQuizzes.css";

function BrowseQuizzes() {
  const navigate = useNavigate();
  const [quizzes, setQuizzes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [questionCounts, setQuestionCounts] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
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

  const getCategoryName = (categoryId) => {
    const category = categories.find((cat) => cat.id === categoryId);
    return category ? category.name : "General";
  };

  const getQuestionCount = (quizId) => {
    return questionCounts[quizId] || 0;
  };

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
                  Start Quiz
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