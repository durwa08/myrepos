import { useEffect, useState } from "react";
import StudentLayout from "../../layouts/StudentLayout";
import api from "../../services/api";
import { getStudentResultHistory } from "../../services/resultService";
import { getQuizzes } from "../../services/quizService";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import "../../styles/profile.css";

function Profile() {
  const [profile, setProfile] = useState(null);

  const [stats, setStats] = useState({
    totalAttempts: 0,
    passed: 0,
    failed: 0,
    averageScore: 0,
  });

  const [history, setHistory] = useState([]);
  const [quizMap, setQuizMap] = useState({});

  useEffect(() => {
    async function loadProfile() {
      try {
        const [response, resultHistory, quizzes] = await Promise.all([
          api.get("/auth/me"),
          getStudentResultHistory(),
          getQuizzes(),
        ]);

        const email = response.data.your_data.sub;

        const username = email
          .split("@")[0]
          .replace(/[._-]/g, " ")
          .replace(/\b\w/g, (char) => char.toUpperCase());

        setProfile({
          username,
          email,
          role: response.data.your_data.role,
        });

        const lookup = {};

        quizzes.forEach((quiz) => {
          lookup[quiz.id] = quiz.title;
        });

        setQuizMap(lookup);

        // Exclude results whose quiz has since been deleted, so they
        // don't show up as "Unknown Quiz" or skew the stats below.
        const activeHistory = resultHistory.filter((item) =>
          Boolean(lookup[item.quiz_id])
        );

        const totalAttempts = activeHistory.length;

        const passed = activeHistory.filter(
          (item) => item.passed
        ).length;

        const failed = totalAttempts - passed;

        const averageScore =
          totalAttempts > 0
            ? (
                activeHistory.reduce(
                  (sum, item) => sum + item.percentage,
                  0
                ) / totalAttempts
              ).toFixed(1)
            : 0;

        setStats({
          totalAttempts,
          passed,
          failed,
          averageScore,
        });

        setHistory(activeHistory);
      } catch (error) {
        console.error("Failed to load profile:", error);
      }
    }

    loadProfile();
  }, []);

  if (!profile) {
    return (
      <StudentLayout>
        <h2>Loading profile...</h2>
      </StudentLayout>
    );
  }

  const pieData = [
    { name: "Passed", value: stats.passed, fill: "#10b981" },
    { name: "Failed", value: stats.failed, fill: "#ef4444" },
  ];

  return (
    <StudentLayout>
      <div className="profile-page">
        <div className="profile-card">
          <div className="avatar">
            {profile.username.charAt(0)}
          </div>

          <h2>{profile.username}</h2>

          <span className="role">
            {profile.role.charAt(0).toUpperCase() +
              profile.role.slice(1)}
          </span>

          <div className="profile-info">
            <div className="info-row">
              <span>Username</span>
              <strong>{profile.username}</strong>
            </div>

            <div className="info-row">
              <span>Email</span>
              <strong>{profile.email}</strong>
            </div>

            <div className="info-row">
              <span>Role</span>
              <strong>
                {profile.role.charAt(0).toUpperCase() +
                  profile.role.slice(1)}
              </strong>
            </div>
          </div>

          <div className="stats-section">
            <h3>Assessment Statistics</h3>

            <div className="stats-layout">
              <div className="stats-grid">
                <div className="stat-box">
                  <h2>{stats.totalAttempts}</h2>
                  <span>Total Attempts</span>
                </div>

                <div className="stat-box">
                  <h2>{stats.averageScore}%</h2>
                  <span>Average Score</span>
                </div>

                <div className="stat-box stat-box-pass">
                  <h2>{stats.passed}</h2>
                  <span>Passed</span>
                </div>

                <div className="stat-box stat-box-fail">
                  <h2>{stats.failed}</h2>
                  <span>Failed</span>
                </div>
              </div>

              {stats.totalAttempts > 0 && (
                <div className="stats-chart">
                  <ResponsiveContainer width="100%" height={180}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={45}
                        outerRadius={70}
                        paddingAngle={3}
                        dataKey="value"
                      >
                        {pieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="stats-chart-legend">
                    <span className="legend-dot legend-pass"></span> Passed
                    <span className="legend-dot legend-fail"></span> Failed
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="history-section">
            <h3>Recent Assessments</h3>

            {history.length === 0 ? (
              <p className="empty-history">
                You haven't attempted any assessments yet.
              </p>
            ) : (
              <div className="history-table-container">
                <table className="history-table">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Quiz</th>
                      <th>Score</th>
                      <th>Status</th>
                      <th>Date</th>
                    </tr>
                  </thead>

                  <tbody>
                    {history.map((item, index) => (
                      <tr key={item.id}>
                        <td>{index + 1}</td>

                        <td>
                          {quizMap[item.quiz_id] ||
                            "Unknown Quiz"}
                        </td>

                        <td>{item.percentage}%</td>

                        <td>
                          <span
                            className={`result-badge ${
                              item.passed
                                ? "passed"
                                : "failed"
                            }`}
                          >
                            {item.passed
                              ? "Passed"
                              : "Failed"}
                          </span>
                        </td>

                        <td>
                          {item.submitted_at
                            ? new Date(
                                item.submitted_at
                              ).toLocaleDateString()
                            : "-"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </StudentLayout>
  );
}

export default Profile;