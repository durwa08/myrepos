import { useEffect, useState, useMemo } from "react";
import AdminLayout from "../../layouts/AdminLayout";
import { FaPlus } from "react-icons/fa";
import {
  getCategories,
  createCategory,
  updateCategory,
  deleteCategory,
} from "../../services/categoryService";
import CategoryTable from "../../components/category/CategoryTable";
import "../../styles/category.css";
import { toast } from "react-toastify";

function Categories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [showModal, setShowModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [categoryName, setCategoryName] = useState("");

  const [deleteModal, setDeleteModal] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null);

  
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(5); 

   const refreshCategoriesList = async () => {
    try {
      setLoading(true);
      const data = await getCategories();
      setCategories(data);
      setError("");
    } catch (err) {
      console.error(err);
      const message = err.response?.data?.detail || "Failed to load categories.";
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  
  useEffect(() => {
    let isMounted = true;

    const loadData = async () => {
      try {
        setLoading(true);
        const data = await getCategories();
        if (isMounted) {
          setCategories(data);
          setError("");
        }
      } catch (err) {
        console.error(err);
        if (isMounted) {
          const message = err.response?.data?.detail || "Failed to load categories.";
          setError(message);
          toast.error(message);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadData();

    return () => {
      isMounted = false;
    };
  }, []); 

  
  const totalPages = Math.ceil(categories.length / itemsPerPage);
  const indexOfFirstItem = (currentPage - 1) * itemsPerPage;

  const paginatedCategories = useMemo(() => {
    const indexOfLastItem = currentPage * itemsPerPage;
    return categories.slice(indexOfFirstItem, indexOfLastItem);
  }, [categories, currentPage, itemsPerPage, indexOfFirstItem]);

  const handlePageChange = (pageNumber) => {
    if (pageNumber >= 1 && pageNumber <= totalPages) {
      setCurrentPage(pageNumber);
    }
  };

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
        await updateCategory(editingCategory.id, { name: categoryName });
        toast.success("Category updated successfully.");
      } else {
        await createCategory({ name: categoryName });
        toast.success("Category created successfully.");
      }

      setShowModal(false);
      setEditingCategory(null);
      setCategoryName("");
      setError("");
      await refreshCategoriesList();
    } catch (err) {
      const message = err.response?.data?.detail || "An error occurred.";
      setError(message);
      toast.error(message);
    }
  };

  const handleDeleteCategory = async () => {
    try {
      await deleteCategory(selectedCategory.id);
      toast.success("Category deleted successfully.");
      setDeleteModal(false);
      setSelectedCategory(null);

      if (paginatedCategories.length === 1 && currentPage > 1) {
        setCurrentPage((prev) => prev - 1);
      }
      await refreshCategoriesList();
    } catch (err) {
      const message = err.response?.data?.detail || "Unable to delete category.";
      setError(message);
      toast.error(message);
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
              <h2>{editingCategory ? "Edit Category" : "Add Category"}</h2>
              <input
                type="text"
                placeholder="Enter category name"
                value={categoryName}
                onChange={(e) => setCategoryName(e.target.value)}
              />
              {error && <p className="error-message">{error}</p>}
              <div className="modal-buttons">
                <button className="save-btn" onClick={handleSaveCategory}>
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
              <p>Are you sure you want to delete <strong>"{selectedCategory?.name}"</strong>?</p>
              <div className="modal-buttons">
                <button className="delete-btn" onClick={handleDeleteCategory}>Delete</button>
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
          <>
            <CategoryTable
              categories={paginatedCategories}
              startIndex={indexOfFirstItem}
              onEdit={handleEditClick}
              onDelete={handleDeleteClick}
            />

            {totalPages > 1 && (
              <div className="pagination-container">
                <button
                  className="pagination-btn"
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  Previous
                </button>

                <div className="pagination-pages-list">
                  {[...Array(totalPages)].map((_, index) => {
                    const pageNum = index + 1;
                    return (
                      <button
                        key={pageNum}
                        className={`pagination-page-number ${currentPage === pageNum ? "active" : ""}`}
                        onClick={() => handlePageChange(pageNum)}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                </div>

                <button
                  className="pagination-btn"
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </AdminLayout>
  );
}

export default Categories;