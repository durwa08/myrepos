import "../../styles/questionCard.css";

function QuestionCard({
  question,
  selectedAnswer,
  onAnswerSelect,
}) {
  if (!question) {
    return null;
  }

  return (
    <div className="question-card">
      <h2>{question.question_text}</h2>

      <div className="options-list">
        {question.options.map((option, index) => (
          <label
            key={index}
            className="option-item"
          >
            <input
              type="radio"
              name={question.id}
              checked={selectedAnswer === index}
              onChange={() => onAnswerSelect(index)}
            />

            <span>{option}</span>
          </label>
        ))}
      </div>
    </div>
  );
}

export default QuestionCard;