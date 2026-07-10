import { useEffect, useState } from "react";
import AdminLayout from "../layouts/AdminLayout";
import "../styles/adminDashboard.css";

import { getCategories } from "../services/categoryService";
import { getQuizzes } from "../services/quizService";
import { getQuestions } from "../services/questionService";

import {
  FaFolderOpen,
  FaClipboardList,
  FaQuestionCircle,
  FaChartBar,
} from "react-icons/fa";

import StatCard from "../components/common/StatCard";

function AdminDashboard() {
  const [categoryCount, setCategoryCount] = useState(0);
  const [quizCount, setQuizCount] = useState(0);
  const [questionCount, setQuestionCount] = useState(0);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const [categories, quizzes, questions] = await Promise.all([
          getCategories(),
          getQuizzes(),
          getQuestions(),
        ]);

        setCategoryCount(categories.length);
        setQuizCount(quizzes.length);
        setQuestionCount(questions.length);
      } catch (error) {
        console.error("Dashboard Error:", error);
      }
    };

    fetchDashboard();
  }, []);

  return (
    <AdminLayout>
      <div className="dashboard">
        <h1>Dashboard</h1>

        <div className="cards">
          <StatCard
            title="Categories"
            value={categoryCount}
            icon={<FaFolderOpen />}
          />

          <StatCard
            title="Quizzes"
            value={quizCount}
            icon={<FaClipboardList />}
          />

          <StatCard
            title="Questions"
            value={questionCount}
            icon={<FaQuestionCircle />}
          />

          <StatCard
            title="Results"
            value={0}
            icon={<FaChartBar />}
          />
        </div>
      </div>
    </AdminLayout>
  );
}

export default AdminDashboard;