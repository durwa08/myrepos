import {
  FaChartPie,
  FaFolderOpen,
  FaClipboardList,
  FaQuestionCircle,
  FaChartBar,
  FaUserGraduate,
  FaPlayCircle,
  FaUser,
} from "react-icons/fa";

import { NavLink } from "react-router-dom";
import "../../styles/sidebar.css";

function Sidebar({ role = "admin" }) {
  const adminMenu = [
    {
      label: "Dashboard",
      path: "/admin",
      icon: <FaChartPie />,
    },
    {
      label: "Categories",
      path: "/admin/categories",
      icon: <FaFolderOpen />,
    },
    {
      label: "Quizzes",
      path: "/admin/quizzes",
      icon: <FaClipboardList />,
    },
    {
      label: "Questions",
      path: "/admin/questions",
      icon: <FaQuestionCircle />,
    },
    {
      label: "Results",
      path: "/admin/results",
      icon: <FaChartBar />,
    },
  ];

  const studentMenu = [
    {
      label: "Dashboard",
      path: "/student",
      icon: <FaUserGraduate />,
    },
    {
      label: "Browse Quizzes",
      path: "/student/quizzes",
      icon: <FaPlayCircle />,
    },
    {
      label: "My Results",
      path: "/student/results",
      icon: <FaChartBar />,
    },
    {
      label: "Profile",
      path: "/student/profile",
      icon: <FaUser />,
    },
  ];

  const menuItems = role === "admin" ? adminMenu : studentMenu;

  return (
    <aside className="sidebar">
      <div>
        <div className="sidebar-logo">
          <div className="logo-circle">
            AP
          </div>

          <div>
            <h2>Assessment</h2>
            <span>
              {role === "admin" ? "Admin Portal" : "Student Portal"}
            </span>
          </div>
        </div>

        <div className="menu-title">
          MAIN MENU
        </div>

        <nav>
          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/admin" || item.path === "/student"}
              className={({ isActive }) =>
                isActive ? "menu-item active" : "menu-item"
              }
            >
              <span className="menu-icon">
                {item.icon}
              </span>

              {item.label}
            </NavLink>
          ))}
        </nav>
      </div>

      <div className="sidebar-footer">
        Version 1.0
      </div>
    </aside>
  );
}

export default Sidebar;