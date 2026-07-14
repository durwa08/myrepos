import { useEffect, useState, useMemo } from "react";
import AdminLayout from "../layouts/AdminLayout";
import { getAdminDashboardResults } from "../services/resultService";
import { getQuizzes } from "../services/quizService";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import "../styles/results.css";

function ResultsDashboard() {
  const [results, setResults] = useState([]);
  const [quizTitleById, setQuizTitleById] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  /**
   * Fetch dashboard data on component mount
   */
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [resultsData, quizzesData] = await Promise.all([
          getAdminDashboardResults(),
          getQuizzes(),
        ]);

        const titleMap = {};
        quizzesData.forEach((quiz) => {
          titleMap[quiz.id] = quiz.title;
        });

        setResults(resultsData);
        setQuizTitleById(titleMap);
        setError("");
      } catch (err) {
        console.error(err);
        setError(
          err.response?.data?.detail ||
            "Failed to load assessment results."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  /**
   * Results whose quiz still exists. Results tied to a deleted quiz
   * (no matching entry in quizTitleById) are excluded from the entire
   * dashboard - table, stats, chart, and insights.
   */
  const activeResults = useMemo(() => {
    return results.filter((item) => Boolean(quizTitleById[item.quiz_id]));
  }, [results, quizTitleById]);

  /**
   * Filter results based on the status filter using useMemo.
   * This avoids cascading renders by computing the filtered list
   * without setState.
   */
  const filteredResults = useMemo(() => {
    if (statusFilter === "all") return activeResults;
    return activeResults.filter((item) =>
      statusFilter === "pass" ? item.passed : !item.passed
    );
  }, [statusFilter, activeResults]);

  /**
   * Calculate statistics using useMemo
   */
  const stats = useMemo(() => {
    const totalAttempts = activeResults.length;
    const passedAttempts = activeResults.filter((r) => r.passed).length;
    const failedAttempts = activeResults.filter((r) => !r.passed).length;
    const passRate = totalAttempts > 0 ? ((passedAttempts / totalAttempts) * 100).toFixed(1) : 0;
    const avgScore =
      totalAttempts > 0
        ? (activeResults.reduce((sum, r) => sum + r.percentage, 0) / totalAttempts).toFixed(1)
        : 0;
    const uniqueStudents = new Set(activeResults.map((r) => r.student_id)).size;

    return {
      totalAttempts,
      passedAttempts,
      failedAttempts,
      passRate,
      avgScore,
      uniqueStudents,
    };
  }, [activeResults]);

  /**
   * Derive quick insights from the existing results and quiz title
   * data, avoiding the need for any additional backend endpoints:
   * how many distinct quizzes have been attempted, which student has
   * submitted the most attempts, and which quiz has the best and
   * worst pass rate. Quizzes that no longer resolve to a title
   * (deleted quizzes) are excluded from the best/worst calculations,
   * since there's nothing meaningful to show for them.
   */
  const insights = useMemo(() => {
    if (activeResults.length === 0) {
      return {
        uniqueQuizzesAttempted: 0,
        mostActiveStudent: null,
        bestQuiz: null,
        worstQuiz: null,
      };
    }

    const uniqueQuizzesAttempted = new Set(activeResults.map((r) => r.quiz_id)).size;

    const attemptsByStudent = {};
    activeResults.forEach((r) => {
      attemptsByStudent[r.student_id] = (attemptsByStudent[r.student_id] || 0) + 1;
    });
    const [mostActiveStudentId, mostActiveCount] = Object.entries(
      attemptsByStudent
    ).sort((a, b) => b[1] - a[1])[0];

    const quizStats = {};
    activeResults.forEach((r) => {
      if (!quizStats[r.quiz_id]) {
        quizStats[r.quiz_id] = { total: 0, passed: 0 };
      }
      quizStats[r.quiz_id].total += 1;
      if (r.passed) {
        quizStats[r.quiz_id].passed += 1;
      }
    });

    const quizPassRates = Object.entries(quizStats)
      .filter(([quizId]) => Boolean(quizTitleById[quizId]))
      .map(([quizId, data]) => ({
        quizId,
        title: quizTitleById[quizId],
        passRate: (data.passed / data.total) * 100,
        attempts: data.total,
      }));

    const sortedByPassRate = [...quizPassRates].sort(
      (a, b) => b.passRate - a.passRate
    );

    return {
      uniqueQuizzesAttempted,
      mostActiveStudent: {
        id: mostActiveStudentId,
        count: mostActiveCount,
      },
      bestQuiz: sortedByPassRate[0] || null,
      worstQuiz:
        sortedByPassRate.length > 1
          ? sortedByPassRate[sortedByPassRate.length - 1]
          : null,
    };
  }, [activeResults, quizTitleById]);

  /**
   * Chart data
   */
  const chartData = [
    { name: "Passed", value: stats.passedAttempts, fill: "#10b981" },
    { name: "Failed", value: stats.failedAttempts, fill: "#ef4444" },
  ];

  return (
    <AdminLayout>
      <div className="results-page">
        {/* Header Section */}
        <div className="results-header">
          <div className="header-content">
            <h1>📊 Candidate Results Dashboard</h1>
            <p>Monitor global student attempt submissions, compliance metrics, and scores.</p>
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        {!loading && !error && (
          <>
            {/* KPI Cards */}
            <div className="kpi-grid">
              <div className="kpi-card">
                <div className="kpi-icon">📝</div>
                <div className="kpi-content">
                  <div className="kpi-label">Total Attempts</div>
                  <div className="kpi-value">{stats.totalAttempts}</div>
                </div>
              </div>

              <div className="kpi-card">
                <div className="kpi-icon">✅</div>
                <div className="kpi-content">
                  <div className="kpi-label">Pass Rate</div>
                  <div className="kpi-value">{stats.passRate}%</div>
                </div>
              </div>

              <div className="kpi-card">
                <div className="kpi-icon">📈</div>
                <div className="kpi-content">
                  <div className="kpi-label">Average Score</div>
                  <div className="kpi-value">{stats.avgScore}%</div>
                </div>
              </div>

              <div className="kpi-card">
                <div className="kpi-icon">👥</div>
                <div className="kpi-content">
                  <div className="kpi-label">Unique Students</div>
                  <div className="kpi-value">{stats.uniqueStudents}</div>
                </div>
              </div>
            </div>

            {/* Chart and Filters Section */}
            <div className="dashboard-content">
              {/* Chart */}
              <div className="chart-container">
                <h2>Performance Distribution</h2>
                {stats.totalAttempts > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={chartData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, value }) => `${name}: ${value}`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {chartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <p style={{ textAlign: "center", padding: "40px", color: "#999" }}>
                    No data to display
                  </p>
                )}
              </div>

              {/* Filters */}
              <div className="filters-section">
                <h2>Filter by Status</h2>
                <div className="filter-inputs">
                  <div className="filter-buttons">
                    <button
                      className={`filter-btn ${statusFilter === "all" ? "active" : ""}`}
                      onClick={() => setStatusFilter("all")}
                    >
                      All ({stats.totalAttempts})
                    </button>
                    <button
                      className={`filter-btn ${statusFilter === "pass" ? "active" : ""}`}
                      onClick={() => setStatusFilter("pass")}
                    >
                      Passed ({stats.passedAttempts})
                    </button>
                    <button
                      className={`filter-btn ${statusFilter === "fail" ? "active" : ""}`}
                      onClick={() => setStatusFilter("fail")}
                    >
                      Failed ({stats.failedAttempts})
                    </button>
                  </div>
                </div>

                <div className="quick-insights">
                  <h3>Quick Insights</h3>
                  <ul className="insights-list">
                    <li>
                      <span className="insight-label">Quizzes attempted</span>
                      <span className="insight-value">{insights.uniqueQuizzesAttempted}</span>
                    </li>
                    {insights.mostActiveStudent && (
                      <li>
                        <span className="insight-label">Most active student</span>
                        <span className="insight-value">
                          {insights.mostActiveStudent.id.split("@")[0]} (
                          {insights.mostActiveStudent.count})
                        </span>
                      </li>
                    )}
                    {insights.bestQuiz && (
                      <li>
                        <span className="insight-label">Best performing quiz</span>
                        <span className="insight-value insight-good">
                          {insights.bestQuiz.title} ({insights.bestQuiz.passRate.toFixed(0)}%)
                        </span>
                      </li>
                    )}
                    {insights.worstQuiz && (
                      <li>
                        <span className="insight-label">Needs attention</span>
                        <span className="insight-value insight-bad">
                          {insights.worstQuiz.title} ({insights.worstQuiz.passRate.toFixed(0)}%)
                        </span>
                      </li>
                    )}
                  </ul>
                </div>
              </div>
            </div>

            {/* Results Table */}
            <div className="table-section">
              <h2>Detailed Results</h2>
              {filteredResults.length === 0 ? (
                <div className="empty-state">
                  <p>📭 No results match your filters</p>
                </div>
              ) : (
                <div className="table-container">
                  <table className="results-table">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Student ID</th>
                        <th>Quiz Title</th>
                        <th>Attempt</th>
                        <th>Score</th>
                        <th>Percentage</th>
                        <th>Submitted</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredResults.map((item, index) => (
                        <tr key={item.id} className={item.passed ? "row-pass" : "row-fail"}>
                          <td className="row-number">{index + 1}</td>
                          <td className="student-id">{item.student_id}</td>
                          <td className="quiz-title">{quizTitleById[item.quiz_id]}</td>
                          <td className="attempt">{item.attempt_number}</td>
                          <td className="score">
                            <strong>{item.correct_answers}</strong> / {item.total_questions}
                          </td>
                          <td className="percentage">{item.percentage.toFixed(1)}%</td>
                          <td className="submitted">
                            {new Date(item.submitted_at).toLocaleDateString()}
                          </td>
                          <td>
                            <span className={`status-badge ${item.passed ? "pass" : "fail"}`}>
                              {item.passed ? "✓ PASSED" : "✗ FAILED"}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </>
        )}

        {loading && (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading candidate data...</p>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}

export default ResultsDashboard;