import { useEffect, useState } from "react";
import StudentLayout from "../layouts/StudentLayout";
import WelcomeBanner from "../components/student/WelcomeBanner";
import {
  getStudentProfile,
  getQuizzes,
  getResultHistory,
} from "../services/dashboardService";
import "../styles/studentDashboard.css";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

function StudentDashboard() {
  const [profile, setProfile] = useState(null);
  const [quizzes, setQuizzes] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const profileData = await getStudentProfile();
        const quizzesData = await getQuizzes();
        const resultsData = await getResultHistory();

        setProfile(profileData);
        setQuizzes(quizzesData);
        setResults(resultsData);
      } catch (error) {
        console.error("Failed to load dashboard:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  
  const getDashboardData = () => {
    const passedCount = results.filter(result => result.passed).length;
    const avgScore = results.length > 0 
      ? (results.reduce((sum, r) => sum + r.percentage, 0) / results.length).toFixed(1)
      : 0;

    return {
      quizzes: quizzes.length,
      attempts: results.length,
      passed: passedCount,
      failed: results.length - passedCount,
      avgScore: avgScore,
    };
  };

  
  const getPerformanceData = () => {
    const categoryMap = {};
    
    results.forEach(result => {
      
      const category = result.quiz_title || result.quiz?.title || result.quiz_name || "Quiz Evaluation";
      if (!categoryMap[category]) {
        categoryMap[category] = { attempts: 0, passed: 0 };
      }
      categoryMap[category].attempts++;
      if (result.passed) {
        categoryMap[category].passed++;
      }
    });

    return Object.keys(categoryMap)
      .slice(0, 5)
      .map(category => ({
        category: category.length > 12 ? category.substring(0, 12) + "..." : category,
        attempts: categoryMap[category].attempts,
        passRate: Math.round((categoryMap[category].passed / categoryMap[category].attempts) * 100),
      }));
  };

  const dashboardData = getDashboardData();
  const performanceData = getPerformanceData();

  const passRateValue = dashboardData.attempts > 0 ? Math.round((dashboardData.passed / dashboardData.attempts) * 100) : 0;
  const failRateValue = dashboardData.attempts > 0 ? Math.round((dashboardData.failed / dashboardData.attempts) * 100) : 0;

  const pieChartData = [
    { name: "Pass Rate", value: passRateValue, color: "#10b981" },
    { name: "Fail Rate", value: failRateValue, color: "#ef4444" }
  ];

  const cards = [
    {
      title: "Available Quizzes",
      value: loading ? "-" : dashboardData.quizzes,
      icon: "📚",
    },
    {
      title: "Completed Attempts",
      value: loading ? "-" : dashboardData.attempts,
      icon: "✅",
    },
    {
      title: "Passed",
      value: loading ? "-" : dashboardData.passed,
      icon: "🏆",
    },
    {
      title: "Failed",
      value: loading ? "-" : dashboardData.failed,
      icon: "📉",
    },
  ];

  return (
    <StudentLayout>
      <div className="student-dashboard">
        <WelcomeBanner username={profile ? profile.username : "Student"} />

        {/* Dashboard Cards */}
        <div className="dashboard-cards">
          {cards.map((card, index) => (
            <div key={index} className="dashboard-card">
              <span className="dashboard-card-icon">{card.icon}</span>
              <h3>{card.title}</h3>
              <span>{card.value}</span>
            </div>
          ))}
        </div>

        {/* Performance Section */}
        {!loading && results.length > 0 && (
          <div className="performance-section">
            {/* Performance Chart */}
            <div className="performance-card">
              <h3>📊 Performance by Quiz</h3>
              <div className="performance-wrapper">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={performanceData} barGap={4}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="category" stroke="#999" />
                    <YAxis stroke="#999" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#fff",
                        border: "1px solid #ddd",
                        borderRadius: "8px",
                      }}
                    />
                    <Legend />
                    {/* Fixed barSize to 24 for a perfectly balanced professional view */}
                    <Bar dataKey="attempts" fill="#667eea" name="Attempts" barSize={24} radius={[4, 4, 0, 0]} />
                    <Bar dataKey="passRate" fill="#10b981" name="Pass Rate %" barSize={24} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Stats Pie Chart Card */}
            <div className="performance-card">
              <h3>📈 Your Stats</h3>
              <div className="performance-wrapper" style={{ height: "220px" }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieChartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={85}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {pieChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `${value}%`} />
                    <Legend verticalAlign="bottom" height={36} />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* Numerical Metrics Grid */}
              <div className="stats-bottom-row" style={{ display: "flex", gap: "12px", marginTop: "15px" }}>
                <div className="stat-item average" style={{ flex: 1, textAlign: "center", padding: "10px", background: "#f8fafc", borderRadius: "8px", borderLeft: "4px solid #3b82f6" }}>
                  <h4 style={{ fontSize: "12px", color: "#64748b", margin: "0 0 4px 0", textTransform: "uppercase" }}>Avg Score</h4>
                  <span style={{ fontSize: "18px", fontWeight: "700", color: "#1e293b" }}>{dashboardData.avgScore}%</span>
                </div>
                <div className="stat-item total" style={{ flex: 1, textAlign: "center", padding: "10px", background: "#f8fafc", borderRadius: "8px", borderLeft: "4px solid #6366f1" }}>
                  <h4 style={{ fontSize: "12px", color: "#64748b", margin: "0 0 4px 0", textTransform: "uppercase" }}>Total Score</h4>
                  <span style={{ fontSize: "18px", fontWeight: "700", color: "#1e293b" }}>{Math.round(results.reduce((sum, r) => sum + r.percentage, 0))}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && results.length === 0 && (
          <div className="empty-state">
            <div className="empty-state-icon">🎯</div>
            <h3>Get Started!</h3>
            <p>No attempts yet. Browse available quizzes from the sidebar to begin your learning journey.</p>
          </div>
        )}
      </div>
    </StudentLayout>
  );
}

export default StudentDashboard;