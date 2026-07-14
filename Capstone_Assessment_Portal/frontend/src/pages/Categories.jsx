import { useEffect, useState } from "react";
import AdminLayout from "../layouts/AdminLayout";
import { FaPlus } from "react-icons/fa";
import {
  getCategories,
  createCategory,
  updateCategory,
  deleteCategory,
} from "../services/categoryService";
import CategoryTable from "../components/category/CategoryTable";
import "../styles/category.css";

function Categories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [showModal, setShowModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [categoryName, setCategoryName] = useState("");

  const [deleteModal, setDeleteModal] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null);

  const fetchCategories = async () => {
    try {
      setLoading(true);

      const data = await getCategories();

      setCategories(data);
      setError("");
    } catch (error) {
      console.error(error);

      setError(
        error.response?.data?.detail ||
          "Failed to load categories."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const loadCategories = async () => {
      await fetchCategories();
    };

    loadCategories();
  }, []);

  const handleEditClick = (category) => {
    setEditingCategory(category);
    setCategoryName(category.name);
    setError("");
    setShowModal(true);
  };

  const handleDeleteClick = (category) => {
    setSelectedCategory(category);
    setDeleteModal(true);
  };

  const handleSaveCategory = async () => {
    if (!categoryName.trim()) {
      setError("Category name is required.");
      return;
    }

    try {
      if (editingCategory) {
        await updateCategory(editingCategory.id, {
          name: categoryName,
        });
      } else {
        await createCategory({
          name: categoryName,
        });
      }

      setShowModal(false);
      setEditingCategory(null);
      setCategoryName("");
      setError("");

      await fetchCategories();
    } catch (error) {
      setError(
        error.response?.data?.detail ||
          (editingCategory
            ? "Unable to update category."
            : "Unable to create category.")
      );
    }
  };

  const handleDeleteCategory = async () => {
    try {
      await deleteCategory(selectedCategory.id);

      setDeleteModal(false);
      setSelectedCategory(null);

      await fetchCategories();
    } catch (error) {
      setError(
        error.response?.data?.detail ||
          "Unable to delete category."
      );
    }
  };

  return (
    <AdminLayout>
      <div className="category-page">
        <div className="category-header">
          <h1>Categories</h1>

          <button
            className="add-category-btn"
            onClick={() => {
                setEditingCategory(null);
                setCategoryName("");
                setError("");
                setShowModal(true);
            }}
>
            <FaPlus />
            <span>Add Category</span>
           </button>
        </div>

        {showModal && (
          <div className="modal-overlay">
            <div className="category-modal">
              <h2>
                {editingCategory
                  ? "Edit Category"
                  : "Add Category"}
              </h2>

              <input
                type="text"
                placeholder="Enter category name"
                value={categoryName}
                onChange={(e) =>
                  setCategoryName(e.target.value)
                }
              />

              {error && (
                <p className="error-message">
                  {error}
                </p>
              )}

              <div className="modal-buttons">
                <button
                  className="save-btn"
                  onClick={handleSaveCategory}
                >
                  {editingCategory ? "Update" : "Save"}
                </button>

                <button
                  className="cancel-btn"
                  onClick={() => {
                    setShowModal(false);
                    setEditingCategory(null);
                    setCategoryName("");
                    setError("");
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {deleteModal && (
          <div className="modal-overlay">
            <div className="delete-modal">
              <h2>Delete Category</h2>

              <p>
                Are you sure you want to delete
                <strong> "{selectedCategory?.name}"</strong>?
              </p>

              <div className="modal-buttons">
                <button
                  className="delete-btn"
                  onClick={handleDeleteCategory}
                >
                  Delete
                </button>

                <button
                  className="cancel-btn"
                  onClick={() => {
                    setDeleteModal(false);
                    setSelectedCategory(null);
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {loading ? (
          <h3>Loading categories...</h3>
        ) : error && !showModal && !deleteModal ? (
          <h3>{error}</h3>
        ) : (
          <CategoryTable
            categories={categories}
            onEdit={handleEditClick}
            onDelete={handleDeleteClick}
          />
        )}
      </div>
    </AdminLayout>
  );
}

export default Categories;