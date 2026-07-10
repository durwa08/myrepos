import { useEffect, useState } from "react";
import AdminLayout from "../layouts/AdminLayout";

import {
  getQuestionsByQuiz,
  createQuestion,
  updateQuestion,
  deleteQuestion,
} from "../services/questionService";

import { getQuizzes } from "../services/quizService";

import QuestionTable from "../components/question/QuestionTable";

import "../styles/question.css";

function Questions() {
  const [questions, setQuestions] = useState([]);
  const [quizzes, setQuizzes] = useState([]);

  const [selectedQuiz, setSelectedQuiz] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [showModal, setShowModal] = useState(false);
  const [deleteModal, setDeleteModal] = useState(false);

  const [editingQuestion, setEditingQuestion] = useState(null);
  const [selectedQuestion, setSelectedQuestion] = useState(null);

  const [formData, setFormData] = useState({
    question_text: "",
    question_type: "mcq",
    options: ["", "", "", ""],
    correct_answer_index: 0,
    difficulty: "easy",
    tags: "",
  });

  // 1. Single source of truth for loading initial quizzes
  useEffect(() => {
    let isMounted = true;

    const fetchInitialData = async () => {
      try {
        const data = await getQuizzes();
        
        if (!isMounted) return;
        setQuizzes(data);

        if (data.length > 0) {
          setSelectedQuiz(data[0].id);
        } else {
          setLoading(false);
        }
        setError("");
      } catch (error) {
        if (!isMounted) return;
        console.error(error);
        setError(error.response?.data?.detail || "Unable to load quizzes.");
        setLoading(false);
      }
    };

    fetchInitialData();
    return () => { isMounted = false; };
  }, []);

  // 2. Fetch questions whenever selectedQuiz changes
  useEffect(() => {
    if (!selectedQuiz) return;
    
    let isMounted = true;

    const fetchQuestions = async () => {
      try {
        setLoading(true);
        const data = await getQuestionsByQuiz(selectedQuiz);
        
        if (!isMounted) return;
        setQuestions(data);
        setError("");
      } catch (error) {
        if (!isMounted) return;
        console.error(error);
        setQuestions([]);
        setError(error.response?.data?.detail || "Unable to load questions.");
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchQuestions();
    return () => { isMounted = false; };
  }, [selectedQuiz]);

  const forceRefreshQuestions = async (quizId) => {
    if (!quizId) return;
    try {
      setLoading(true);
      const data = await getQuestionsByQuiz(quizId);
      setQuestions(data);
      setError("");
    } catch (error) {
      console.error(error);
      setQuestions([]);
      setError(error.response?.data?.detail || "Unable to load questions.");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleOptionChange = (index, value) => {
    const updatedOptions = [...formData.options];
    updatedOptions[index] = value;
    setFormData({
      ...formData,
      options: updatedOptions,
    });
  };

  const resetForm = () => {
    setFormData({
      question_text: "",
      question_type: "mcq",
      options: ["", "", "", ""],
      correct_answer_index: 0,
      difficulty: "easy",
      tags: "",
    });
    setEditingQuestion(null);
  };

  const handleEditClick = (question) => {
    setEditingQuestion(question);
    setFormData({
      question_text: question.question_text,
      question_type: question.question_type,
      options: question.options || ["", "", "", ""],
      correct_answer_index: 0, 
      difficulty: question.difficulty,
      tags: question.tags?.join(", ") || "",
    });
    setShowModal(true);
  };

  const handleDeleteClick = (question) => {
    setSelectedQuestion(question);
    setDeleteModal(true);
  };

  const handleSaveQuestion = async () => {
    if (!formData.question_text.trim()) {
      setError("Question is required.");
      return;
    }

    try {
      const payload = {
        ...formData,
        quiz_id: selectedQuiz,
        tags: formData.tags
          ? formData.tags
              .split(",")
              .map((tag) => tag.trim())
              .filter(Boolean)
          : [],
      };

      if (editingQuestion) {
        await updateQuestion(editingQuestion.id, payload);
      } else {
        await createQuestion(payload);
      }

      setShowModal(false);
      resetForm();
      setError("");

      await forceRefreshQuestions(selectedQuiz);
    } catch (error) {
      setError(error.response?.data?.detail || "Unable to save question.");
    }
  };

  const handleDeleteQuestion = async () => {
    try {
      await deleteQuestion(selectedQuestion.id);

      setDeleteModal(false);
      setSelectedQuestion(null);

      await forceRefreshQuestions(selectedQuiz);
    } catch (error) {
      setError(error.response?.data?.detail || "Unable to delete question.");
    }
  };

  return (
    <AdminLayout>
      <div className="question-page">
        <div className="question-header">
          <h1>Questions</h1>

          <div className="question-actions">
            <div className="header-filter-group">
              <label>Select Category</label>
              <select
                value={selectedQuiz}
                onChange={(e) => setSelectedQuiz(e.target.value)}
              >
                {quizzes.map((quiz) => (
                  <option key={quiz.id} value={quiz.id}>
                    {quiz.title}
                  </option>
                ))}
              </select>
            </div>

            <button
              className="add-category-btn"
              onClick={() => {
                resetForm();
                setError("");
                setShowModal(true);
              }}
            >
              + Add Question
            </button>
          </div>
        </div>

        {showModal && (
          <div className="modal-overlay">
            <div className="category-modal">
              <h2>{editingQuestion ? "Edit Question" : "Add Question"}</h2>

              <label className="field-label">Question Text</label>
              <textarea
                name="question_text"
                rows="3"
                placeholder="Enter question prompt..."
                value={formData.question_text}
                onChange={handleInputChange}
              />

              <label className="field-label">Question Type</label>
              <select
                name="question_type"
                value={formData.question_type}
                onChange={handleInputChange}
              >
                <option value="mcq">MCQ</option>
                <option value="true_false">True / False</option>
              </select>

              {formData.question_type === "mcq" ? (
                <>
                  <label className="field-label">Options (Select radio for correct answer)</label>
                  <div className="options-container">
                    {formData.options.map((option, index) => {
                      const isCorrect = formData.correct_answer_index === index;
                      return (
                        <div key={index} className={`option-row ${isCorrect ? "is-correct" : ""}`}>
                          <input
                            type="radio"
                            name="correct_answer"
                            title="Mark as correct answer"
                            checked={isCorrect}
                            onChange={() =>
                              setFormData({
                                ...formData,
                                correct_answer_index: index,
                              })
                            }
                          />
                          <input
                            type="text"
                            value={option}
                            placeholder={`Option ${index + 1}`}
                            onChange={(e) => handleOptionChange(index, e.target.value)}
                          />
                        </div>
                      );
                    })}
                  </div>
                </>
              ) : (
                <>
                  <label className="field-label">Correct Answer</label>
                  <select
                    value={formData.correct_answer_index}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        correct_answer_index: Number(e.target.value),
                      })
                    }
                  >
                    <option value={0}>True</option>
                    <option value={1}>False</option>
                  </select>
                </>
              )}

              <label className="field-label">Difficulty</label>
              <select
                name="difficulty"
                value={formData.difficulty}
                onChange={handleInputChange}
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>

              <label className="field-label">Tags</label>
              <input
                type="text"
                name="tags"
                placeholder="e.g., java, oops, arrays"
                value={formData.tags}
                onChange={handleInputChange}
              />

              {error && <p className="error-message">{error}</p>}

              <div className="modal-buttons">
                <button className="save-btn" onClick={handleSaveQuestion}>
                  {editingQuestion ? "Update" : "Save"}
                </button>
                <button
                  className="cancel-btn"
                  onClick={() => {
                    setShowModal(false);
                    resetForm();
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
              <h2>Delete Question</h2>
              <p>Are you sure you want to delete this question?</p>
              <p>
                <strong>{selectedQuestion?.question_text}</strong>
              </p>
              <div className="modal-buttons">
                <button className="delete-btn" onClick={handleDeleteQuestion}>
                  Delete
                </button>
                <button
                  className="cancel-btn"
                  onClick={() => {
                    setDeleteModal(false);
                    setSelectedQuestion(null);
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {loading ? (
          <h3>Loading questions...</h3>
        ) : error && !showModal && !deleteModal ? (
          <h3>{error}</h3>
        ) : (
          <QuestionTable
            questions={questions}
            onEdit={handleEditClick}
            onDelete={handleDeleteClick}
          />
        )}
      </div>
    </AdminLayout>
  );
}

export default Questions;