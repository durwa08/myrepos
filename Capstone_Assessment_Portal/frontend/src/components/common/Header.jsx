import { FaSignOutAlt } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import { clearAuthData } from "../../utils/storage";
import "../../styles/header.css";

function Header() {
  const navigate = useNavigate();

  const today = new Date().toLocaleDateString("en-IN", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  const handleLogout = () => {
    clearAuthData();
    navigate("/");
  };

  return (
    <header className="header">

      <div className="header-left">
        <h2>Assessment Portal</h2>
        <p>Admin Dashboard</p>
      </div>

      <div className="header-right">

        <div className="date">
          {today}
        </div>

        <button
          className="logout-btn"
          onClick={handleLogout}
        >
          <FaSignOutAlt />
          Logout
        </button>

      </div>

    </header>
  );
}

export default Header;