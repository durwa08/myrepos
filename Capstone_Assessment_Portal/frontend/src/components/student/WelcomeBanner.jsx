import "../../styles/welcomeBanner.css";

function WelcomeBanner({ username }) {
  return (
    <div className="welcome-banner">
      <h1>Welcome, {username || "Student"} 👋</h1>

      <p>
        Ready to continue your learning journey?
      </p>
    </div>
  );
}

export default WelcomeBanner;