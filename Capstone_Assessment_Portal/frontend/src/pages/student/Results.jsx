import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

import StudentLayout from "../../layouts/StudentLayout";
import { getAttemptResult } from "../../services/resultService";

import "../../styles/results.css";

function Results() {
  const { attemptId } = useParams();
  const navigate = useNavigate();

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadResult() {
      try {
        const response = await getAttemptResult(attemptId);
        setResult(response);
      } catch (error) {
        console.error("Failed to load result:", error);
      } finally {
        setLoading(false);
      }
    }

    loadResult();
  }, [attemptId]);

  if (loading) {
    return (
      <StudentLayout>
        <div className="result-page">
          <h2>Loading Result...</h2>
        </div>
      </StudentLayout>
    );
  }

  if (!result) {
    return (
      <StudentLayout>
        <div className="result-page">
          <h2>Result not found.</h2>
        </div>
      </StudentLayout>
    );
  }

  return (
    <StudentLayout>
      <div className="result-page">
        <div className="result-header">
          <h1>Assessment Result</h1>
          <p>Your assessment has been submitted successfully.</p>
        </div>

        <div className="result-summary">
          <div className="summary-card">
            <h3>Score</h3>
            <span>
              {result.correct_answers} / {result.total_questions}
            </span>
          </div>

          <div className="summary-card">
            <h3>Percentage</h3>
            <span>{result.percentage}%</span>
          </div>

          <div className="summary-card">
            <h3>Status</h3>
            <span
              className={
                result.passed ? "status-pass" : "status-fail"
              }
            >
              {result.passed ? "Passed" : "Failed"}
            </span>
          </div>
        </div>

        <div className="answer-review">
          <h2>Answer Review</h2>

          {result.answer_breakdown.map((answer, index) => {
            const yourAnswer =
              answer.selected_answer_index !== null &&
              answer.selected_answer_index !== undefined &&
              answer.options
                ? answer.options[answer.selected_answer_index]
                : "Not Answered";

            const correctAnswer =
              answer.options
                ? answer.options[answer.correct_answer_index]
                : answer.correct_answer_index;

            return (
              <div
                key={answer.question_id}
                className="answer-card"
              >
                <h3>Question {index + 1}</h3>

                <p className="question-text">
                  {answer.question_text}
                </p>

                <p>
                  <strong>Your Answer:</strong>{" "}
                  {yourAnswer}
                </p>

                <p>
                  <strong>Correct Answer:</strong>{" "}
                  {correctAnswer}
                </p>

                <p
                  className={
                    answer.is_correct
                      ? "correct"
                      : "incorrect"
                  }
                >
                  {answer.is_correct
                    ? "✅ Correct"
                    : "❌ Incorrect"}
                </p>
              </div>
            );
          })}
        </div>

        <div className="result-footer">
          <button
            className="dashboard-redirect-btn"
            onClick={() => navigate("/student")}
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>
    </StudentLayout>
  );
}

export default Results;