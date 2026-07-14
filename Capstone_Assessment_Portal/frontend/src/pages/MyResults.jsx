import { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";

import StudentLayout from "../layouts/StudentLayout";
import { getStudentResultHistory } from "../services/resultService";
import { getQuizzes } from "../services/quizService";
import { getCategories } from "../services/categoryService";

import "../styles/myResults.css";

function MyResults() {
  const navigate = useNavigate();

  const [results, setResults] = useState([]);
  const [quizMap, setQuizMap] = useState({});
  const [categoryMap, setCategoryMap] = useState({});
  const [summary, setSummary] = useState({});
  const [loading, setLoading] = useState(true);

  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(5);

  useEffect(() => {
    async function loadResults() {
      try {
        const [history, quizzes, categories] = await Promise.all([
          getStudentResultHistory(),
          getQuizzes(),
          getCategories(),
        ]);

        setResults(history);

        const quizLookup = {};
        quizzes.forEach((quiz) => {
          quizLookup[quiz.id] = quiz;
        });
        setQuizMap(quizLookup);

        const categoryLookup = {};
        categories.forEach((category) => {
          categoryLookup[category.id] = category.name;
        });
        setCategoryMap(categoryLookup);

        const categorySummary = {};

        history.forEach((result) => {
          const quiz = quizLookup[result.quiz_id];

          if (!quiz) return;

          const category =
            categoryLookup[quiz.category_id] || "Unknown";

          if (!categorySummary[category]) {
            categorySummary[category] = {
              passed: 0,
              failed: 0,
            };
          }

          if (result.passed) {
            categorySummary[category].passed++;
          } else {
            categorySummary[category].failed++;
          }
        });

        setSummary(categorySummary);
      } catch (error) {
        console.error("Failed to load results:", error);
      } finally {
        setLoading(false);
      }
    }

    loadResults();
  }, []);

  const totalPages = Math.ceil(results.length / itemsPerPage);
  const indexOfFirstItem = (currentPage - 1) * itemsPerPage;

  const paginatedResults = useMemo(() => {
    const indexOfLastItem = currentPage * itemsPerPage;
    return results.slice(indexOfFirstItem, indexOfLastItem);
  }, [results, currentPage, itemsPerPage, indexOfFirstItem]);

  const handlePageChange = (pageNumber) => {
    if (pageNumber >= 1 && pageNumber <= totalPages) {
      setCurrentPage(pageNumber);
    }
  };

  return (
    <StudentLayout>
      <div className="my-results">
        <div className="page-header">
          <div className="page-header-top">
            <div>
              <h1>My Results</h1>
              <p>View all your completed assessments.</p>
            </div>

            <button
              className="dashboard-redirect-btn"
              onClick={() => navigate("/student")}
            >
              ← Back to Dashboard
            </button>
          </div>
        </div>

        {Object.keys(summary).length > 0 && (
          <div className="performance-summary">
            <h2>Category Performance</h2>

            <div className="summary-grid">
              {Object.entries(summary).map(
                ([category, value]) => (
                  <div
                    key={category}
                    className="summary-card"
                  >
                    <h3>{category}</h3>

                    <p>
                      ✅ Passed :
                      <strong> {value.passed}</strong>
                    </p>

                    <p>
                      ❌ Failed :
                      <strong> {value.failed}</strong>
                    </p>
                  </div>
                )
              )}
            </div>
          </div>
        )}

        {loading ? (
          <h3>Loading...</h3>
        ) : results.length === 0 ? (
          <h3>No assessment attempts found.</h3>
        ) : (
          <>
            <div className="results-list">
              {paginatedResults.map((result) => (
                <div
                  key={result.id}
                  className="result-card"
                >
                  <div>
                    <h3>
                      {quizMap[result.quiz_id]?.title ||
                        "Unknown Quiz"}
                    </h3>

                    <p>
                      <strong>Category :</strong>{" "}
                      {categoryMap[
                        quizMap[result.quiz_id]
                          ?.category_id
                      ] || "Unknown"}
                    </p>

                    <p>
                      <strong>Attempt :</strong> #
                      {result.attempt_number}
                    </p>

                    <p>
                      <strong>Score :</strong>{" "}
                      {result.correct_answers}/
                      {result.total_questions}
                    </p>

                    <p>
                      <strong>Percentage :</strong>{" "}
                      {result.percentage}%
                    </p>

                    <p>
                      <strong>Status :</strong>{" "}
                      <span
                        className={
                          result.passed
                            ? "passed"
                            : "failed"
                        }
                      >
                        {result.passed
                          ? "Passed"
                          : "Failed"}
                      </span>
                    </p>

                    <p>
                      <strong>Submitted :</strong>{" "}
                      {new Date(
                        result.submitted_at
                      ).toLocaleString()}
                    </p>
                  </div>

                  <button
                    onClick={() =>
                      navigate(
                        `/student/results/${result.id}`
                      )
                    }
                  >
                    View Result
                  </button>
                </div>
              ))}
            </div>

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
    </StudentLayout>
  );
}

export default MyResults;