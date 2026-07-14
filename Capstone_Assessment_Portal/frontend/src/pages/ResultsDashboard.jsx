import { useEffect, useState } from "react";
import AdminLayout from "../layouts/AdminLayout";
import { getAdminDashboardResults } from "../services/attemptService";
import "../styles/results.css";

function ResultsDashboard() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const data = await getAdminDashboardResults();
        setResults(data);
      } catch (err) {
        console.error(err);
        setError(err.response?.data?.detail || "Failed to load assessment results.");
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, []);

  return (
    <AdminLayout>
      <div className="results-page">
        <div className="results-header">
          <h1>Candidate Results Dashboard</h1>
          <p>Monitor global student attempt submissions, compliance metrics, and scores.</p>
        </div>

        {loading ? (
          <h3>Loading candidate grading data...</h3>
        ) : error ? (
          <h3 className="error-message">{error}</h3>
        ) : (
          <div className="table-container">
            <table className="results-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Student ID</th>
                  <th>Quiz ID</th>
                  <th>Attempt No.</th>
                  <th>Score Breakdown</th>
                  <th>Percentage</th>
                  <th>Submitted At</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {results.length === 0 ? (
                  <tr>
                    <td colSpan="8" style={{ textAlign: "center", padding: "24px" }}>
                      No assessment submissions found in the system yet.
                    </td>
                  </tr>
                ) : (
                  results.map((item, index) => (
                    <tr key={item.id}>
                      <td>{index + 1}</td>
                      <td className="font-semibold">{item.student_id}</td>
                      <td>{item.quiz_id}</td>
                      <td style={{ textAlign: "center" }}>{item.attempt_number}</td>
                      <td>
                        <strong>{item.correct_answers}</strong> / {item.total_questions}
                      </td>
                      <td className="font-semibold">{item.percentage.toFixed(1)}%</td>
                      <td>{new Date(item.submitted_at).toLocaleString()}</td>
                      <td>
                        <span className={`status-badge ${item.passed ? "pass" : "fail"}`}>
                          {item.passed ? "PASSED" : "FAILED"}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}

export default ResultsDashboard;