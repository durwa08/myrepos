import {
  FaChartPie,
  FaFolderOpen,
  FaClipboardList,
  FaQuestionCircle,
  FaChartBar,
} from "react-icons/fa";

import "../../styles/sidebar.css";

function Sidebar({ activeMenu, setActiveMenu }) {
  const menus = [
    {
      id: "dashboard",
      title: "Dashboard",
      icon: <FaChartPie />,
    },
    {
      id: "categories",
      title: "Categories",
      icon: <FaFolderOpen />,
    },
    {
      id: "quizzes",
      title: "Quizzes",
      icon: <FaClipboardList />,
    },
    {
      id: "questions",
      title: "Questions",
      icon: <FaQuestionCircle />,
    },
    {
      id: "results",
      title: "Results",
      icon: <FaChartBar />,
    },
  ];

  return (
    <aside className="sidebar">

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

        {menus.map((menu) => (

          <button
            key={menu.id}
            className={
              activeMenu === menu.id
                ? "menu-item active"
                : "menu-item"
            }
            onClick={() => setActiveMenu(menu.id)}
          >
            <span className="menu-icon">
              {menu.icon}
            </span>

            {menu.title}
          </button>

        ))}

      </nav>

      <div className="sidebar-footer">
        Version 1.0
      </div>

    </aside>
  );
}

export default Sidebar;