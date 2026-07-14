import {
  useCallback,
  useEffect,
  useState,
} from "react";

import { useNavigate, useParams } from "react-router-dom";

import StudentLayout from "../../layouts/StudentLayout";
import QuestionCard from "../../components/student/QuestionCard";
import QuestionNavigator from "../../components/student/QuestionNavigator";
import Timer from "../../components/student/Timer";
import { toast } from "react-toastify";

import {
  getAttempt,
  saveAnswer,
  submitAttempt,
} from "../../services/attemptService";

import "../../styles/takeQuiz.css";

function TakeQuiz() {
  const { attemptId } = useParams();
  const navigate = useNavigate();

  const [attempt, setAttempt] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    async function loadAttempt() {
      try {
        const response = await getAttempt(attemptId);

        setAttempt(response);
        setAnswers(response.answers || {});
      } catch (error) {
        console.error("Failed to load attempt:", error);
      } finally {
        setLoading(false);
      }
    }

    loadAttempt();
  }, [attemptId]);

  const handleAnswerSelect = async (answerIndex) => {
    const question = attempt.questions[currentQuestion];

    try {
      await saveAnswer(
        attemptId,
        question.question_id,
        answerIndex
      );

      setAnswers((previous) => ({
        ...previous,
        [question.question_id]: answerIndex,
      }));
    } catch (error) {
      console.error("Failed to save answer:", error);
    }
  };

  const handleSubmit = async () => {
  try {
    const result = await submitAttempt(attemptId);

    toast.success("Assessment submitted successfully.");

    navigate(`/student/results/${result.id}`);
  } catch (error) {
    console.error(error);

    toast.error("Unable to submit assessment.");
  }
};

  const handleTimerExpire = useCallback(async () => {
    if (submitting) {
      return;
    }

    try {
      setSubmitting(true);

      const result = await submitAttempt(attemptId);

      navigate(`/student/results/${result.id}`);
    } catch (error) {
      console.error("Failed to auto-submit attempt:", error);
      setSubmitting(false);
    }
  }, [attemptId, navigate, submitting]);

  if (loading) {
    return (
      <StudentLayout>
        <div className="take-quiz-loading">
          <h2>Loading assessment...</h2>
        </div>
      </StudentLayout>
    );
  }

  if (!attempt) {
    return (
      <StudentLayout>
        <div className="take-quiz-loading">
          <h2>Assessment not found.</h2>
        </div>
      </StudentLayout>
    );
  }

  const question = attempt.questions[currentQuestion];

  return (
    <StudentLayout>
      <div className="take-quiz">
        <div className="quiz-header">
          <div>
            <h2>
              Question {currentQuestion + 1} of{" "}
              {attempt.questions.length}
            </h2>
          </div>

          <Timer
            expiresAt={attempt.expires_at}
            onExpire={handleTimerExpire}
          />
        </div>

        <QuestionCard
          question={question}
          selectedAnswer={
            answers[question.question_id]
          }
          onAnswerSelect={handleAnswerSelect}
        />

        <QuestionNavigator
          totalQuestions={attempt.questions.length}
          currentQuestion={currentQuestion}
          onQuestionChange={setCurrentQuestion}
          answers={answers}
          questions={attempt.questions}
        />

        <div className="quiz-actions">
          <button
            disabled={currentQuestion === 0}
            onClick={() =>
              setCurrentQuestion(currentQuestion - 1)
            }
          >
            Previous
          </button>

          {currentQuestion <
          attempt.questions.length - 1 ? (
            <button
              onClick={() =>
                setCurrentQuestion(currentQuestion + 1)
              }
            >
              Next
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={submitting}
            >
              {submitting
                ? "Submitting..."
                : "Submit Assessment"}
            </button>
          )}
        </div>
      </div>
    </StudentLayout>
  );
}

export default TakeQuiz;