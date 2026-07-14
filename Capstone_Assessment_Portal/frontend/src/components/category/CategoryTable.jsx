import { FaEdit, FaTrash } from "react-icons/fa";

function CategoryTable({
  categories,
  startIndex = 0,
  onEdit,
  onDelete,
}) {
  if (categories.length === 0) {
    return (
      <div className="empty-state">
        <h3>No Categories Found</h3>
      </div>
    );
  }

  return (
    <table className="category-table">
      <thead>
        <tr>
          <th>#</th>
          <th>Category Name</th>
          <th>Created By</th>
          <th>Actions</th>
        </tr>
      </thead>

      <tbody>
        {categories.map((category, index) => (
          <tr key={category.id || index}>
            {/* Displays continuous serial numbers across paginated pages */}
            <td>{startIndex + index + 1}</td>
            <td>{category.name}</td>
            <td>{category.created_by}</td>

            <td className="action-buttons">
              <button
                className="edit-btn"
                onClick={() => onEdit(category)}
              >
                <FaEdit />
                <span>Edit</span>
              </button>

              <button
                className="delete-btn"
                onClick={() => onDelete(category)}
              >
                <FaTrash />
                <span>Delete</span>
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default CategoryTable;