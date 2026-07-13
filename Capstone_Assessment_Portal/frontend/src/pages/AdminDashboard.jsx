import { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import AdminLayout from "../layouts/AdminLayout";
import "../styles/adminDashboard.css";

import { getCategories } from "../services/categoryService";
import { getQuizzes } from "../services/quizService";
import { getQuestions } from "../services/questionService";
import { getAdminDashboardResults } from "../services/resultService";

import {
  FaFolderOpen,
  FaClipboardList,
  FaQuestionCircle,
  FaChartBar,
  FaBolt,
  FaPercent,
  FaGraduationCap,
  FaCalendarAlt,
} from "react-icons/fa";

import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

function AdminDashboard() {
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [categoryCount, setCategoryCount] = useState(0);
  const [quizzes, setQuizzes] = useState([]);
  const [quizCount, setQuizCount] = useState(0);
  const [questionCount, setQuestionCount] = useState(0);
  const [resultCount, setResultCount] = useState(0);
  const [allResults, setAllResults] = useState([]); 
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState("1"); // Default: Last 1 Day

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const [categoriesData, quizzesData, questions, resultsData] = await Promise.all([
          getCategories(),
          getQuizzes(),
          getQuestions(),
          getAdminDashboardResults(),
        ]);

        setCategories(categoriesData);
        setCategoryCount(categoriesData.length);
        setQuizzes(quizzesData);
        setQuizCount(quizzesData.length);
        setQuestionCount(questions.length);
        setResultCount(resultsData.length);
        setAllResults(resultsData);
      } catch (error) {
        console.error("Dashboard Error:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  /**
   * 1. Dynamic filtering based on custom micro intervals (1, 3, 5 days)
   */
  const filteredResults = useMemo(() => {
    if (timeRange === "all") return allResults;
    
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - parseInt(timeRange, 10));
    
    return allResults.filter((r) => new Date(r.submitted_at) >= cutoffDate);
  }, [allResults, timeRange]);

  /**
   * 2. Calculate summary block cards metrics
   */
  const metrics = useMemo(() => {
    const resultsSubset = filteredResults;
    const subsetCount = resultsSubset.length;
    const passed = resultsSubset.filter((r) => r.passed).length;
    const failed = subsetCount - passed;
    
    const passRate = subsetCount > 0 ? ((passed / subsetCount) * 100).toFixed(1) : 0;
    const avgScore =
      subsetCount > 0
        ? (resultsSubset.reduce((sum, r) => sum + r.percentage, 0) / subsetCount).toFixed(1)
        : 0;

    const todayDate = new Date();
    const todayActivity = allResults.filter((r) => {
      const submittedDate = new Date(r.submitted_at);
      return submittedDate.toDateString() === todayDate.toDateString();
    }).length;

    return { passRate, avgScore, todayActivity, passed, failed, currentTotal: subsetCount };
  }, [filteredResults, allResults]);

  /**
   * 3. Construct segment metrics for time-variant charts
   */
  const trendData = useMemo(() => {
    if (timeRange === "1") {
      const hours = ["Morning", "Afternoon", "Evening", "Night"];
      return hours.map((label, idx) => {
        const hourlyResults = filteredResults.filter((r) => {
          const hour = new Date(r.submitted_at).getHours();
          if (idx === 0) return hour >= 6 && hour < 12;
          if (idx === 1) return hour >= 12 && hour < 17;
          if (idx === 2) return hour >= 17 && hour < 21;
          return hour >= 21 || hour < 6;
        });
        return {
          day: label,
          attempts: hourlyResults.length,
          passed: hourlyResults.filter((r) => r.passed).length,
        };
      });
    }

    if (timeRange === "3" || timeRange === "5") {
      const limit = parseInt(timeRange, 10);
      const dataPoints = [];
      for (let i = limit - 1; i >= 0; i--) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        const dayLabel = d.toLocaleDateString("en-US", { weekday: "short" });
        
        const targetResults = filteredResults.filter(
          (r) => new Date(r.submitted_at).toDateString() === d.toDateString()
        );

        dataPoints.push({
          day: i === 0 ? "Today" : dayLabel,
          attempts: targetResults.length,
          passed: targetResults.filter((r) => r.passed).length,
        });
      }
      return dataPoints;
    }

    const blocks = ["Prior", "3 mo ago", "2 mo ago", "Last mo", "Current"];
    return blocks.map((label, idx) => {
      const blockResults = filteredResults.filter((r) => {
        const rDate = new Date(r.submitted_at);
        const now = new Date();
        const diffMonths = (now.getFullYear() - rDate.getFullYear()) * 12 + (now.getMonth() - rDate.getMonth());
        if (idx === 4) return diffMonths === 0;
        if (idx === 3) return diffMonths === 1;
        if (idx === 2) return diffMonths === 2;
        if (idx === 1) return diffMonths === 3;
        return diffMonths > 3;
      });
      return {
        day: label,
        attempts: blockResults.length,
        passed: blockResults.filter((r) => r.passed).length,
      };
    });
  }, [filteredResults, timeRange]);

  /**
   * 4. Categorized dynamic data array parser
   */
  const categoryPerformance = useMemo(() => {
    const perfMap = {};

    filteredResults.forEach((result) => {
      const quizId = result.quiz_id;
      if (!quizId) return;

      const matchingQuiz = quizzes.find((q) => String(q.id || q._id) === String(quizId));
      const categoryIdentifier = matchingQuiz?.category_id || matchingQuiz?.category || "Uncategorized";

      let categoryName = "Uncategorized";
      if (categoryIdentifier !== "Uncategorized") {
        const matchingCategory = categories.find((c) => String(c.id || c._id) === String(categoryIdentifier));
        categoryName = matchingCategory ? (matchingCategory.name || matchingCategory.title) : "General";
      }

      if (!perfMap[categoryName]) {
        perfMap[categoryName] = { attempts: 0, passed: 0 };
      }
      
      perfMap[categoryName].attempts++;
      if (result.passed) perfMap[categoryName].passed++;
    });

    return Object.keys(perfMap).slice(0, 5).map((catName) => ({
      category: catName,
      attempts: perfMap[catName].attempts,
      passRate: ((perfMap[catName].passed / perfMap[catName].attempts) * 100).toFixed(0),
    }));
  }, [filteredResults, quizzes, categories]);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good Morning";
    if (hour < 18) return "Good Afternoon";
    return "Good Evening";
  };

  return (
    <AdminLayout>
      <div className="dashboard">
        {/* Header Grid Section */}
        <div className="dashboard-header-container">
          <div>
            <h1>👋 {getGreeting()}, Admin!</h1>
            <p className="dashboard-subtitle">
              Welcome back to the Assessment Portal. Here's your dashboard overview.
            </p>
          </div>
          
          {/* Main Global Time Range Dropdown Selector */}
          <div className="time-filter-dropdown-box">
            <FaCalendarAlt className="calendar-filter-icon" />
            <select 
              value={timeRange} 
              onChange={(e) => setTimeRange(e.target.value)}
              className="dashboard-native-select"
            >
              <option value="1">Last 1 Day</option>
              <option value="3">Last 3 Days</option>
              <option value="5">Last 5 Days</option>
              <option value="all">All Time Records</option>
            </select>
          </div>
        </div>

        {/* Global Inventory Counts Row */}
        <div className="cards">
          {[
            { title: "Categories", count: categoryCount, icon: <FaFolderOpen />, subtext: "Quiz categories" },
            { title: "Quizzes", count: quizCount, icon: <FaClipboardList />, subtext: "Active quizzes" },
            { title: "Questions", count: questionCount, icon: <FaQuestionCircle />, subtext: "Total questions" },
            { title: "Results", count: resultCount, icon: <FaChartBar />, subtext: "Submissions" },
          ].map((item, index) => (
            <div key={index} className="card">
              <div className="card-icon-container">{item.icon}</div>
              <h3>{item.title}</h3>
              <p>{loading ? "-" : item.count}</p>
              <div className="card-subtext">{item.subtext}</div>
            </div>
          ))}

          {/* Sync Dynamic Ratio status bar */}
          {!loading && metrics.currentTotal > 0 && (
            <div className="card trend-inline-card">
              <h3>📌 Activity Status Breakdown</h3>
              <div className="status-breakdown-wrapper">
                <div className="status-split-labels">
                  <div className="status-label passed">
                    <span className="dot"></span>
                    Passed: <strong>{metrics.passed}</strong>
                  </div>
                  <div className="status-label failed">
                    <span className="dot"></span>
                    Failed: <strong>{metrics.failed}</strong>
                  </div>
                </div>
                
                <div className="ratio-bar-container">
                  <div 
                    className="ratio-bar passed-fill" 
                    style={{ width: `${(metrics.passed / metrics.currentTotal) * 100}%` }}
                    title={`Passed: ${((metrics.passed / metrics.currentTotal) * 100).toFixed(0)}%`}
                  ></div>
                  <div 
                    className="ratio-bar failed-fill" 
                    style={{ width: `${(metrics.failed / metrics.currentTotal) * 100}%` }}
                    title={`Failed: ${((metrics.failed / metrics.currentTotal) * 100).toFixed(0)}%`}
                  ></div>
                </div>
                
                <div className="ratio-bar-percentage">
                  <span>{((metrics.passed / metrics.currentTotal) * 100).toFixed(0)}% Pass Ratio</span>
                  <span>Scope Base: {metrics.currentTotal} Items</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Dynamic Multi-radial Momentum Metrics Grid */}
        <div className="dashboard-grid">
          <div className="stats-section">
            <div className="stat-box">
              <div className="stat-box-info">
                <h3>⚡ Today's Activity</h3>
                <div className="stat-box-value">{loading ? "-" : metrics.todayActivity}</div>
                <div className="stat-box-trend">Rolling live metric</div>
              </div>
              <div className="stat-box-graphical" style={{ "--progress-val": Math.min(metrics.todayActivity * 10, 100), "--progress-color": "#667eea" }}>
                <div className="progress-track-bg"></div>
                <div className="progress-track-fill"></div>
                <div className="progress-inner-icon"><FaBolt /></div>
              </div>
            </div>

            <div className="stat-box">
              <div className="stat-box-info">
                <h3>📈 Pass Rate</h3>
                <div className="stat-box-value">{loading ? "-" : `${metrics.passRate}%`}</div>
                <div className="stat-box-trend">Scoped average index</div>
              </div>
              <div className="stat-box-graphical" style={{ "--progress-val": metrics.passRate, "--progress-color": "#10b981" }}>
                <div className="progress-track-bg"></div>
                <div className="progress-track-fill"></div>
                <div className="progress-inner-icon"><FaPercent /></div>
              </div>
            </div>

            <div className="stat-box">
              <div className="stat-box-info">
                <h3>🎓 Average Score</h3>
                <div className="stat-box-value">{loading ? "-" : `${metrics.avgScore}%`}</div>
                <div className="stat-box-trend">Scoped total index</div>
              </div>
              <div className="stat-box-graphical" style={{ "--progress-val": metrics.avgScore, "--progress-color": "#f5576c" }}>
                <div className="progress-track-bg"></div>
                <div className="progress-track-fill"></div>
                <div className="progress-inner-icon"><FaGraduationCap /></div>
              </div>
            </div>
          </div>
        </div>

        {/* Side-by-Side Analytical Plot Elements */}
        <div className="charts-section-two-col">
          {!loading && metrics.currentTotal > 0 && (
            <div className="chart-container">
              <h3>📅 Submission Trends ({timeRange === "all" ? "All Time" : `Last ${timeRange} ${timeRange === "1" ? "Day" : "Days"}` })</h3>
              <div className="chart-wrapper">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trendData}>
                    <defs>
                      <linearGradient id="colorAttempts" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#667eea" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#667eea" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="colorPassed" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="day" stroke="#999" />
                    <YAxis stroke="#999" />
                    <Tooltip
                      contentStyle={{ backgroundColor: "#fff", border: "1px solid #ddd", borderRadius: "8px" }}
                    />
                    <Legend />
                    <Area type="monotone" dataKey="attempts" stroke="#667eea" fillOpacity={1} fill="url(#colorAttempts)" name="Total Attempts" />
                    <Area type="monotone" dataKey="passed" stroke="#10b981" fillOpacity={1} fill="url(#colorPassed)" name="Passed" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {!loading && categoryPerformance.length > 0 && (
            <div className="chart-container">
              <h3>🎯 Performance by Category</h3>
              <div className="chart-wrapper">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={categoryPerformance}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="category" stroke="#999" />
                    <YAxis stroke="#999" />
                    <Tooltip
                      contentStyle={{ backgroundColor: "#fff", border: "1px solid #ddd", borderRadius: "8px" }}
                    />
                    <Legend />
                    <Bar dataKey="attempts" fill="#667eea" name="Attempts" radius={[8, 8, 0, 0]} />
                    <Bar dataKey="passRate" fill="#10b981" name="Pass Rate %" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>

        {/* Global Structural Page-to-Page Navigation Footer Module */}
        <div className="portal-navigation-footer">
          <div className="nav-footer-info">
            <span>Module 1 of 4</span>
            <p>Ready to manage your categories, quizzes, and questions structures?</p>
          </div>
          <button 
            className="portal-next-page-btn"
            onClick={() => navigate("/admin/categories")}
          >
            Go to Categories Page →
          </button>
        </div>

      </div>
    </AdminLayout>
  );
}

export default AdminDashboard;