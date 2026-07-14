import { Navigate } from "react-router-dom";
import { getAccessToken, getRole } from "../utils/storage";

function ProtectedRoute({ children, role }) {
  const token = getAccessToken();
  const userRole = getRole();

  if (!token) {
    return <Navigate to="/" replace />;
  }

  if (role && userRole !== role) {
    return <Navigate to="/" replace />;
  }

  return children;
}

export default ProtectedRoute;