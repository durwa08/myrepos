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

const DURATION_PRESETS = ["10", "15", "20", "30", "45", "60", "90", "120"];
const PASS_PRESETS = ["20", "30", "35", "40", "50", "60", "70", "80"];

const EMPTY_FORM = {
  title: "",
  description: "",
  category_id: "",
  time_limit_minutes: "",
  pass_percentage: 40,
};

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

  const resetFormState = () => {
    setFormData(EMPTY_FORM);
    setShowNewCategoryInput(false);
    setNewCategoryName("");
    setShowCustomDuration(false);
    setShowCustomPass(false);
    setFieldErrors({ title: "", duration: "" });
  };

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

    setShowNewCategoryInput(false);
    setNewCategoryName("");

    // If the saved value isn't one of the presets, drop straight into
    // custom-input mode so editing doesn't silently blank the value.
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

  const handleDeleteClick = (quiz) => {
    setSelectedQuiz(quiz);
    setDeleteModal(true);
  };

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
      } else {
        await createQuiz(payload);
      }

      setShowModal(false);

      setEditingQuiz(null);

      resetFormState();

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
                {editingQuiz
                  ? "Edit Quiz"
                  : "Add Quiz"}
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
                    setFieldErrors({ title: "", duration: "" });
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