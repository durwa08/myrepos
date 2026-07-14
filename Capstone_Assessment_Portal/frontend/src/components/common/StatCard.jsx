import "./../../styles/statCard.css";

function StatCard({ title, value, icon, color }) {
  return (
    <div className="stat-card">

      <div
        className="stat-icon"
        style={{ background: color }}
      >
        {icon}
      </div>

      <div className="stat-info">
        <h3>{title}</h3>

        <h2>{value}</h2>
      </div>

    </div>
  );
}

export default StatCard;