import { useState } from "react";
import StudentSidebar from "../components/common/StudentSidebar";
import Header from "../components/common/Header";
import "../styles/studentLayout.css";

function StudentLayout({ children }) {
  const [activeMenu, setActiveMenu] = useState("dashboard");

  return (
    <div className="student-layout">
      <StudentSidebar
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

export default StudentLayout;