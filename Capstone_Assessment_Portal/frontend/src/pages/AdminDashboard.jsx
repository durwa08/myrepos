import { useEffect, useState } from "react";
import AdminLayout from "../layouts/AdminLayout";
import "../styles/adminDashboard.css";

import { getCategories } from "../services/categoryService";

import {
  FaFolderOpen,
  FaClipboardList,
  FaQuestionCircle,
  FaChartBar,
} from "react-icons/fa";

import StatCard from "../components/common/StatCard";

function AdminDashboard() {
  const [categoryCount, setCategoryCount] = useState(0);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const categories = await getCategories();
        setCategoryCount(categories.length);
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
            value={0}
            icon={<FaClipboardList />}
          />

          <StatCard
            title="Questions"
            value={0}
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