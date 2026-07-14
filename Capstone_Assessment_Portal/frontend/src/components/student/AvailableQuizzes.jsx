import QuizCard from "./QuizCard";
import "../../styles/availableQuizzes.css";

function AvailableQuizzes({
  quizzes,
  categories,
  onStartQuiz,
}) {
  if (!quizzes.length) {
    return (
      <div className="available-quizzes">
        <h2>Available Quizzes</h2>
        <p>No quizzes available.</p>
      </div>
    );
  }

  return (
    <div className="available-quizzes">
      <h2>Available Quizzes</h2>

      <div className="quiz-grid">
        {quizzes.map((quiz) => {
          const category = categories.find(
            (item) => item.id === quiz.category_id
          );

          return (
            <QuizCard
              key={quiz.id}
              quiz={quiz}
              categoryName={category?.name || "Unknown"}
              onStart={onStartQuiz}
            />
          );
        })}
      </div>
    </div>
  );
}

export default AvailableQuizzes;