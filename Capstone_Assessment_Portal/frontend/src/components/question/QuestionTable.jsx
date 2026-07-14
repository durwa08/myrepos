function QuestionTable({
  questions,
  onEdit,
  onDelete,
}) {
  if (questions.length === 0) {
    return (
      <div className="empty-state">
        <h3>No Questions Found</h3>
      </div>
    );
  }

  return (
    <table className="question-table">
      <thead>
        <tr>
          <th>#</th>
          <th>Question</th>
          <th>Type</th>
          <th>Difficulty</th>
          <th>Tags</th>
          <th>Actions</th>
        </tr>
      </thead>

      <tbody>
        {questions.map((question, index) => (
          <tr key={question.id}>
            <td>{index + 1}</td>

            <td>{question.question_text}</td>

            <td>{question.question_type}</td>

            <td>{question.difficulty}</td>

            <td>
              {question.tags?.length
                ? question.tags.join(", ")
                : "-"}
            </td>

            <td>
              <button
                className="edit-btn"
                onClick={() => onEdit(question)}
              >
                Edit
              </button>

              <button
                className="delete-btn"
                onClick={() => onDelete(question)}
              >
                Delete
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default QuestionTable;