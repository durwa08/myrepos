import {
  FaChartPie,
  FaFolderOpen,
  FaClipboardList,
  FaQuestionCircle,
  FaChartBar,
} from "react-icons/fa";


import { NavLink } from "react-router-dom";
import "../../styles/sidebar.css";

function Sidebar() {
  return (
    <aside className="sidebar">
      <div>
        <div className="sidebar-logo">
          <div className="logo-circle">
            AP
          </div>

          <div>
            <h2>Assessment</h2>
            <span>Admin Portal</span>
          </div>
        </div>

        <div className="menu-title">
          MAIN MENU
        </div>

        <nav>

          <NavLink
            to="/admin"
            end
            className={({ isActive }) =>
              isActive ? "menu-item active" : "menu-item"
            }
          >
            <span className="menu-icon">
              <FaChartPie />
            </span>
            Dashboard
          </NavLink>

          <NavLink
            to="/admin/categories"
            className={({ isActive }) =>
              isActive ? "menu-item active" : "menu-item"
            }
          >
            <span className="menu-icon">
              <FaFolderOpen />
            </span>
            Categories
          </NavLink>

          <NavLink
            to="/admin/quizzes"
            className={({ isActive }) =>
              isActive ? "menu-item active" : "menu-item"
            }
          >
            <span className="menu-icon">
              <FaClipboardList />
            </span>
            Quizzes
          </NavLink>

          <NavLink
            to="/admin/questions"
            className={({ isActive }) =>
              isActive ? "menu-item active" : "menu-item"
            }
          >
            <span className="menu-icon">
              <FaQuestionCircle />
            </span>
            Questions
          </NavLink>

          <NavLink
            to="/admin/results"
            className={({ isActive }) =>
              isActive ? "menu-item active" : "menu-item"
            }
          >
            <span className="menu-icon">
              <FaChartBar />
            </span>
            Results
          </NavLink>

        </nav>
      </div>

      <div className="sidebar-footer">
        Version 1.0
      </div>
    </aside>
  );
}

export default Sidebar;