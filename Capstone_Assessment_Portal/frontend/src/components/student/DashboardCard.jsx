import "../../styles/dashboardCard.css";

function DashboardCard({ title, value }) {
  return (
    <div className="dashboard-card">
      <h3>{title}</h3>
      <span>{value}</span>
    </div>
  );
}

export default DashboardCard;