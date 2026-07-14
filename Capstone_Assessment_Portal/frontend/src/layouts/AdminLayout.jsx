import Sidebar from "../components/common/Sidebar";
import Header from "../components/common/Header";
import "../styles/adminLayout.css";

function AdminLayout({ children }) {
  return (
    <div className="admin-layout">
      <Sidebar role="admin" />

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