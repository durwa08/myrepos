import Sidebar from "../components/common/Sidebar";
import Header from "../components/common/Header";
import "../styles/studentLayout.css";

function StudentLayout({ children }) {
  return (
    <div className="student-layout">
      <Sidebar role="student" />

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