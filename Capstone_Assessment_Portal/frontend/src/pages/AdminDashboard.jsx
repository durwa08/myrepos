import AdminLayout from "../layouts/AdminLayout";
import "../styles/adminDashboard.css";

import {
  FaFolderOpen,
  FaClipboardList,
  FaQuestionCircle,
  FaChartBar,
} from "react-icons/fa";

import StatCard from "../components/common/StatCard";

function AdminDashboard() {
  return (
    <AdminLayout>
      <div className="dashboard">
        <h1>Dashboard</h1>

        <div className="cards">

          <StatCard
            title="Categories"
            value={0}
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