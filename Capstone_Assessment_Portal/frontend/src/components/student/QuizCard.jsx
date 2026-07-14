import "../../styles/quizCard.css";

function QuizCard({ quiz, categoryName, onStart }) {
  return (
    <div className="quiz-card">
      <div className="quiz-card-header">
        <h3>{quiz.title}</h3>

        <span className="quiz-category">
          {categoryName}
        </span>
      </div>

      <p className="quiz-description">
        {quiz.description || "No description available."}
      </p>

      <div className="quiz-details">
        <div>
          <strong>Time</strong>
          <span>{quiz.time_limit_minutes} mins</span>
        </div>

        <div>
          <strong>Pass</strong>
          <span>{quiz.pass_percentage}%</span>
        </div>
      </div>

      <button
        className="start-quiz-btn"
        onClick={() => onStart(quiz)}
      >
        Start Quiz
      </button>
    </div>
  );
}

export default QuizCard;