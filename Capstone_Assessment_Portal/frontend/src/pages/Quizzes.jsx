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

import "../styles/quiz.css";

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

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    category_id: "",
    time_limit_minutes: "",
    pass_percentage: 40,
  });

  const fetchQuizzes = async () => {
    try {
      setLoading(true);

      const data = await getQuizzes();

      setQuizzes(data);
      setError("");
    } catch (error) {
      setError(
        error.response?.data?.detail ||
          "Unable to load quizzes."
      );
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const data = await getCategories();
      setCategories(data);
    } catch (error) {
      console.error(error);
    }
  };

  const handleInputChange = (e) => {
    if (e.target.name === "category_id" && e.target.value === "__new__") {
      setShowNewCategoryInput(true);
      setFormData({
        ...formData,
        category_id: "",
      });
      return;
    }

    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleAddNewCategory = async () => {
    if (!newCategoryName.trim()) {
      setError("Category name is required.");
      return;
    }

    try {
      const created = await createCategory({ name: newCategoryName });

      await fetchCategories();

      setFormData({
        ...formData,
        category_id: created?.id ?? "",
      });

      setNewCategoryName("");
      setShowNewCategoryInput(false);
      setError("");
    } catch (error) {
      setError(
        error.response?.data?.detail ||
          "Unable to add category."
      );
    }
  };

  const handleEditClick = (quiz) => {
    setEditingQuiz(quiz);

    setFormData({
      title: quiz.title,
      description: quiz.description || "",
      category_id: quiz.category_id,
      time_limit_minutes: quiz.time_limit_minutes,
      pass_percentage: quiz.pass_percentage,
    });

    setShowModal(true);
    setError("");
  };

  const handleDeleteClick = (quiz) => {
    setSelectedQuiz(quiz);
    setDeleteModal(true);
  };

  const handleSaveQuiz = async () => {
    if (
      !formData.title ||
      !formData.category_id ||
      !formData.time_limit_minutes
    ) {
      setError("Please fill all required fields.");
      return;
    }

    try {
      if (editingQuiz) {
        await updateQuiz(editingQuiz.id, formData);
      } else {
        await createQuiz(formData);
      }

      setShowModal(false);

      setEditingQuiz(null);

      setFormData({
        title: "",
        description: "",
        category_id: "",
        time_limit_minutes: "",
        pass_percentage: 40,
      });

      await fetchQuizzes();
    } catch (error) {
      setError(
        error.response?.data?.detail ||
          "Unable to save quiz."
      );
    }
  };

  const handleDeleteQuiz = async () => {
    try {
      await deleteQuiz(selectedQuiz.id);

      setDeleteModal(false);
      setSelectedQuiz(null);

      await fetchQuizzes();
    } catch (error) {
      setError(
        error.response?.data?.detail ||
          "Unable to delete quiz."
      );
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
    return (
    <AdminLayout>
      <div className="quiz-page">
        <div className="quiz-header">
          <h1>Quizzes</h1>

          <button
            className="add-category-btn"
            onClick={() => {
              setEditingQuiz(null);

              setFormData({
                title: "",
                description: "",
                category_id: "",
                time_limit_minutes: "",
                pass_percentage: 40,
              });

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
                {editingQuiz
                  ? "Edit Quiz"
                  : "Add Quiz"}
              </h2>

              <label className="field-label">Quiz Title</label>
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
                <option value="">
                  Select Category
                </option>

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
              </select>

              <label className="field-label">Pass Percentage (%)</label>
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
              </select>

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
          <QuizTable
            quizzes={quizzes}
            categories={categories}
            onEdit={handleEditClick}
            onDelete={handleDeleteClick}
            />
        )}
      </div>
    </AdminLayout>
  );
}

export default Quizzes;