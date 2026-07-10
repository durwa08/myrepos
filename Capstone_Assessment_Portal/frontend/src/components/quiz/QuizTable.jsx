import { FaEdit, FaTrash } from "react-icons/fa";

function QuizTable({
  quizzes,
  categories,
  onEdit,
  onDelete,
}) {
  if (quizzes.length === 0) {
    return (
      <div className="empty-state">
        <h3>No Quizzes Found</h3>
      </div>
    );
  }

  return (
    <table className="quiz-table">
      <thead>
        <tr>
          <th>#</th>
          <th>Title</th>
          <th>Category</th>
          <th>Duration</th>
          <th>Pass %</th>
          <th>Created By</th>
          <th>Actions</th>
        </tr>
      </thead>

      <tbody>
        {quizzes.map((quiz, index) => (
          <tr key={quiz.id}>
            <td>{index + 1}</td>

            <td>{quiz.title}</td>

            <td>
  {categories.find(
    (category) => category.id === quiz.category_id
  )?.name || "-"}
</td>

            <td>{quiz.time_limit_minutes}</td>

            <td>{quiz.pass_percentage}%</td>

            <td>Admin</td>

            <td>
              <div className="action-buttons">
                <button
                  className="edit-btn"
                  onClick={() => onEdit(quiz)}
                >
                  <FaEdit />
                  Edit
                </button>

                <button
                  className="delete-btn"
                  onClick={() => onDelete(quiz)}
                >
                  <FaTrash />
                  Delete
                </button>
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default QuizTable;