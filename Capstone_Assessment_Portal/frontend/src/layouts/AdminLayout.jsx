import { useState } from "react";
import Sidebar from "../components/common/Sidebar";
import Header from "../components/common/Header";
import "../styles/adminLayout.css";

function AdminLayout({ children }) {
  const [activeMenu, setActiveMenu] = useState("dashboard");

  return (
    <div className="admin-layout">
      <Sidebar
        activeMenu={activeMenu}
        setActiveMenu={setActiveMenu}
      />

      <div className="main-content">
        <Header />

        <div className="page-content">
          {children}
        </div>
      </div>
    </div>
  );
}

export default AdminLayout;