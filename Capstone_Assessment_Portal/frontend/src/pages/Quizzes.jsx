import { useEffect, useState } from "react";
import AdminLayout from "../layouts/AdminLayout";
import QuizTable from "../components/quiz/QuizTable";

import {
  getQuizzes,
  createQuiz,
  updateQuiz,
  deleteQuiz,
} from "../services/quizService";

import { getCategories, createCategory } from "../services/categoryService";
import { toast } from "react-toastify";

import "../styles/quiz.css";

/** @type {string[]} */
const DURATION_PRESETS = ["10", "15", "20", "30", "45", "60", "90", "120"];
/** @type {string[]} */
const PASS_PRESETS = ["20", "30", "35", "40", "50", "60", "70", "80"];

/**
 * @typedef {Object} QuizForm
 * @property {string} title
 * @property {string} description
 * @property {string} category_id
 * @property {string|number} time_limit_minutes
 * @property {number} pass_percentage
 */

/** @type {QuizForm} */
const EMPTY_FORM = {
  title: "",
  description: "",
  category_id: "",
  time_limit_minutes: "",
  pass_percentage: 40,
};

/**
 * Quizzes Management Component.
 * Handles CRUD operations, category linking, and paginated display.
 * 
 * @component
 * @returns {React.JSX.Element}
 */
function Quizzes() {
  const [quizzes, setQuizzes] = useState([]);
  const [categories, setCategories] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [showModal, setShowModal] = useState(false);

  const [editingQuiz, setEditingQuiz] = useState(null);

  const [deleteModal, setDeleteModal] = useState(false);
  const [selectedQuiz, setSelectedQuiz] = useState(null);

  const [showNewCategoryInput, setShowNewCategoryInput] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState("");

  const [showCustomDuration, setShowCustomDuration] = useState(false);
  const [showCustomPass, setShowCustomPass] = useState(false);

  const [formData, setFormData] = useState(EMPTY_FORM);

  const [fieldErrors, setFieldErrors] = useState({ title: "", duration: "" });

  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(5);

  /**
   * Resets the form properties and conditional dropdown states back to defaults.
   * 
   * @function
   * @returns {void}
   */
  const resetFormState = () => {
    setFormData(EMPTY_FORM);
    setShowNewCategoryInput(false);
    setNewCategoryName("");
    setShowCustomDuration(false);
    setShowCustomPass(false);
    setFieldErrors({ title: "", duration: "" });
  };

  /**
   * Fetches the root array of quizzes from the API endpoint.
   * 
   * @async
   * @function
   * @returns {Promise<void>}
   */
  const fetchQuizzes = async () => {
    try {
      setLoading(true);
      const data = await getQuizzes();
      setQuizzes(data);
      setError("");
    } catch (error) {
      const message =
        error.response?.data?.detail ||
        "Unable to load quizzes.";

      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Fetches available category profiles for selection matching.
   * 
   * @async
   * @function
   * @returns {Promise<void>}
   */
  const fetchCategories = async () => {
    try {
      const data = await getCategories();
      setCategories(data);
    } catch (error) {
      console.error(error);
    }
  };

  /**
   * Updates fields inside the state controller object. Handles configuration
   * toggles for tracking customized string insertions.
   * 
   * @function
   * @param {React.ChangeEvent<HTMLInputElement|HTMLSelectElement|HTMLTextAreaElement>} e
   * @returns {void}
   */
  const handleInputChange = (e) => {
    const { name, value } = e.target;

    if (name === "title" && fieldErrors.title) {
      setFieldErrors({ ...fieldErrors, title: "" });
    }

    if (name === "time_limit_minutes" && fieldErrors.duration) {
      setFieldErrors({ ...fieldErrors, duration: "" });
    }

    if (name === "category_id" && value === "__new__") {
      setShowNewCategoryInput(true);
      setFormData({
        ...formData,
        category_id: "",
      });
      return;
    }

    if (name === "time_limit_minutes" && value === "__custom__") {
      setShowCustomDuration(true);
      setFormData({
        ...formData,
        time_limit_minutes: "",
      });
      return;
    }

    if (name === "pass_percentage" && value === "__custom__") {
      setShowCustomPass(true);
      setFormData({
        ...formData,
        pass_percentage: "",
      });
      return;
    }

    setFormData({
      ...formData,
      [name]: value,
    });
  };

  /**
   * Commits a nested category submission workflow contextually inside the open dialog.
   * 
   * @async
   * @function
   * @returns {Promise<void>}
   */
  const handleAddNewCategory = async () => {
    if (!newCategoryName.trim()) {
      setError("Category name is required.");
      return;
    }

    try {
      const created = await createCategory({
        name: newCategoryName,
      });

      toast.success("Category created successfully.");

      await fetchCategories();

      setFormData({
        ...formData,
        category_id: created?.id ?? "",
      });

      setNewCategoryName("");
      setShowNewCategoryInput(false);
      setError("");
    } catch (error) {
      const message =
        error.response?.data?.detail ||
        "Unable to add category.";

      setError(message);
      toast.error(message);
    }
  };

  /**
   * Initializes target parameters within active modal layouts for patch mapping.
   * 
   * @function
   * @param {Object} quiz 
   * @returns {void}
   */
  const handleEditClick = (quiz) => {
    setEditingQuiz(quiz);

    setFormData({
      title: quiz.title,
      description: quiz.description || "",
      category_id: quiz.category_id,
      time_limit_minutes: quiz.time_limit_minutes,
      pass_percentage: quiz.pass_percentage,
    });

    setShowNewCategoryInput(false);
    setNewCategoryName("");

    setShowCustomDuration(
      !DURATION_PRESETS.includes(String(quiz.time_limit_minutes))
    );
    setShowCustomPass(
      !PASS_PRESETS.includes(String(quiz.pass_percentage))
    );

    setFieldErrors({ title: "", duration: "" });
    setShowModal(true);
    setError("");
  };

  /**
   * Places targeted data payload objects onto local removal buffers.
   * 
   * @function
   * @param {Object} quiz 
   * @returns {void}
   */
  const handleDeleteClick = (quiz) => {
    setSelectedQuiz(quiz);
    setDeleteModal(true);
  };

  /**
   * Validates form integrity checks before committing updates or new records.
   * 
   * @async
   * @function
   * @returns {Promise<void>}
   */
  const handleSaveQuiz = async () => {
    const newFieldErrors = { title: "", duration: "" };
    let hasFieldError = false;

    if (!formData.title || !formData.title.trim()) {
      newFieldErrors.title = "You have to add a valid name for the quiz.";
      hasFieldError = true;
    }

    const duration = Number(formData.time_limit_minutes);
    if (!formData.time_limit_minutes || !duration || duration <= 0) {
      newFieldErrors.duration = "Please set the time.";
      hasFieldError = true;
    }

    if (hasFieldError) {
      setFieldErrors(newFieldErrors);
      return;
    }

    setFieldErrors({ title: "", duration: "" });

    if (!formData.category_id) {
      setError("Please select a category.");
      return;
    }

    const passPercentage = Number(formData.pass_percentage);
    if (
      formData.pass_percentage === "" ||
      Number.isNaN(passPercentage) ||
      passPercentage < 1 ||
      passPercentage > 100
    ) {
      setError("Pass percentage must be between 1 and 100.");
      return;
    }

    try {
      const payload = {
        ...formData,
        title: formData.title.trim(),
        time_limit_minutes: duration,
        pass_percentage: passPercentage,
      };

      if (editingQuiz) {
        await updateQuiz(editingQuiz.id, payload);
        toast.success("Quiz updated successfully.");
      } else {
        await createQuiz(payload);
        toast.success("Quiz created successfully.");
      }

      setShowModal(false);
      setEditingQuiz(null);
      resetFormState();
      await fetchQuizzes();
    } catch (error) {
      const message =
        error.response?.data?.detail ||
        "Unable to save quiz.";

      setError(message);
      toast.error(message);
    }
  };

  /**
   * Clears specific instances from system parameters through database queries.
   * 
   * @async
   * @function
   * @returns {Promise<void>}
   */
  const handleDeleteQuiz = async () => {
    try {
      await deleteQuiz(selectedQuiz.id);
      toast.success("Quiz deleted successfully.");

      setDeleteModal(false);
      setSelectedQuiz(null);

      if (paginatedQuizzes.length === 1 && currentPage > 1) {
        setCurrentPage((prev) => prev - 1);
      }

      await fetchQuizzes();
    } catch (error) {
      const message =
        error.response?.data?.detail ||
        "Unable to delete quiz.";

      setError(message);
      toast.error(message);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      await Promise.all([
        fetchQuizzes(),
        fetchCategories(),
      ]);
    };

    loadData();
  }, []);

  /** @type {number} */
  const totalPages = Math.ceil(quizzes.length / itemsPerPage);
  /** @type {number} */
  const indexOfFirstItem = (currentPage - 1) * itemsPerPage;
  /** @type {number} */
  const indexOfLastItem = currentPage * itemsPerPage;
  /** @type {Object[]} */
  const paginatedQuizzes = quizzes.slice(indexOfFirstItem, indexOfLastItem);

  /**
   * Modifies page state view index ranges.
   * 
   * @function
   * @param {number} pageNumber 
   * @returns {void}
   */
  const handlePageChange = (pageNumber) => {
    if (pageNumber >= 1 && pageNumber <= totalPages) {
      setCurrentPage(pageNumber);
    }
  };

  return (
    <AdminLayout>
      <div className="quiz-page">
        <div className="quiz-header">
          <h1>Quizzes</h1>

          <button
            className="add-category-btn"
            onClick={() => {
              setEditingQuiz(null);
              resetFormState();
              setError("");
              setShowModal(true);
            }}
          >
            + Add Quiz
          </button>
        </div>

        {showModal && (
          <div className="modal-overlay">
            <div className="category-modal">
              <h2>
                {editingQuiz ? "Edit Quiz" : "Add Quiz"}
              </h2>

              <label className="field-label">Quiz Title</label>
              {fieldErrors.title && (
                <p className="error-message">{fieldErrors.title}</p>
              )}
              <input
                type="text"
                name="title"
                placeholder="Quiz Title"
                value={formData.title}
                onChange={handleInputChange}
              />

              <label className="field-label">Description</label>
              <textarea
                name="description"
                placeholder="Description"
                rows="3"
                value={formData.description}
                onChange={handleInputChange}
              />

              <label className="field-label">Category</label>
              <select
                name="category_id"
                value={formData.category_id}
                onChange={handleInputChange}
              >
                <option value="">Select Category</option>

                {categories.map((category) => (
                  <option
                    key={category.id}
                    value={category.id}
                  >
                    {category.name}
                  </option>
                ))}

                <option value="__new__">+ Add New Category</option>
              </select>

              {showNewCategoryInput && (
                <div className="new-category-box">
                  <input
                    type="text"
                    placeholder="Enter new category name"
                    value={newCategoryName}
                    onChange={(e) => setNewCategoryName(e.target.value)}
                  />

                  <button
                    type="button"
                    className="save-btn"
                    onClick={handleAddNewCategory}
                  >
                    Add
                  </button>

                  <button
                    type="button"
                    className="cancel-btn"
                    onClick={() => {
                      setShowNewCategoryInput(false);
                      setNewCategoryName("");
                    }}
                  >
                    Cancel
                  </button>
                </div>
              )}

              <label className="field-label">Duration (Minutes)</label>
              {showCustomDuration ? (
                <div className="new-category-box">
                  <input
                    type="number"
                    min="1"
                    placeholder="Enter duration in minutes"
                    value={formData.time_limit_minutes}
                    onChange={(e) => {
                      setFormData({
                        ...formData,
                        time_limit_minutes: e.target.value,
                      });
                      if (fieldErrors.duration) {
                        setFieldErrors({ ...fieldErrors, duration: "" });
                      }
                    }}
                  />

                  <button
                    type="button"
                    className="cancel-btn"
                    onClick={() => {
                      setShowCustomDuration(false);
                      setFormData({ ...formData, time_limit_minutes: "" });
                    }}
                  >
                    Use preset
                  </button>
                </div>
              ) : (
                <select
                  name="time_limit_minutes"
                  value={formData.time_limit_minutes}
                  onChange={handleInputChange}
                >
                  <option value="">Select Duration</option>
                  <option value="10">10 minutes</option>
                  <option value="15">15 minutes</option>
                  <option value="20">20 minutes</option>
                  <option value="30">30 minutes</option>
                  <option value="45">45 minutes</option>
                  <option value="60">60 minutes</option>
                  <option value="90">90 minutes</option>
                  <option value="120">120 minutes</option>
                  <option value="__custom__">+ Custom duration</option>
                </select>
              )}
              {fieldErrors.duration && (
                <p className="error-message">{fieldErrors.duration}</p>
              )}

              <label className="field-label">Pass Percentage (%)</label>
              {showCustomPass ? (
                <div className="new-category-box">
                  <input
                    type="number"
                    min="1"
                    max="100"
                    placeholder="Enter pass percentage"
                    value={formData.pass_percentage}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        pass_percentage: e.target.value,
                      })
                    }
                  />

                  <button
                    type="button"
                    className="cancel-btn"
                    onClick={() => {
                      setShowCustomPass(false);
                      setFormData({ ...formData, pass_percentage: "" });
                    }}
                  >
                    Use preset
                  </button>
                </div>
              ) : (
                <select
                  name="pass_percentage"
                  value={formData.pass_percentage}
                  onChange={handleInputChange}
                >
                  <option value="">Select Pass %</option>
                  <option value="20">20%</option>
                  <option value="30">30%</option>
                  <option value="35">35%</option>
                  <option value="40">40%</option>
                  <option value="50">50%</option>
                  <option value="60">60%</option>
                  <option value="70">70%</option>
                  <option value="80">80%</option>
                  <option value="__custom__">+ Custom %</option>
                </select>
              )}

              {error && (
                <p className="error-message">
                  {error}
                </p>
              )}

              <div className="modal-buttons">
                <button
                  className="save-btn"
                  onClick={handleSaveQuiz}
                >
                  {editingQuiz ? "Update" : "Save"}
                </button>

                <button
                  className="cancel-btn"
                  onClick={() => {
                    setShowModal(false);
                    setEditingQuiz(null);
                    setError("");
                    resetFormState();
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
              <h2>Delete Quiz</h2>

              <p>
                Are you sure you want to delete
                <strong> {selectedQuiz?.title}</strong>?
              </p>

              <div className="modal-buttons">
                <button
                  className="delete-btn"
                  onClick={handleDeleteQuiz}
                >
                  Delete
                </button>

                <button
                  className="cancel-btn"
                  onClick={() => {
                    setDeleteModal(false);
                    setSelectedQuiz(null);
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {loading ? (
          <h3>Loading quizzes...</h3>
        ) : error && !showModal ? (
          <h3>{error}</h3>
        ) : (
          <>
            <QuizTable
              quizzes={paginatedQuizzes}
              startIndex={indexOfFirstItem}
              categories={categories}
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
                        className={`pagination-page-number ${
                          currentPage === pageNum ? "active" : ""
                        }`}
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

export default Quizzes;