import "../../styles/questionNavigator.css";

function QuestionNavigator({
  totalQuestions,
  currentQuestion,
  onQuestionChange,
}) {
  return (
    <div className="question-navigator">
      <h3>Questions</h3>

      <div className="question-grid">
        {Array.from({ length: totalQuestions }, (_, index) => (
          <button
            key={index}
            className={
              currentQuestion === index
                ? "question-number active"
                : "question-number"
            }
            onClick={() => onQuestionChange(index)}
          >
            {index + 1}
          </button>
        ))}
      </div>
    </div>
  );
}

export default QuestionNavigator;