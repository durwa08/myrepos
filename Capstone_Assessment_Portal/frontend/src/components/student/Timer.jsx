import { useEffect, useState } from "react";

function Timer({ expiresAt, onExpire }) {
  const [timeLeft, setTimeLeft] = useState({
    hours: 0,
    minutes: 0,
    seconds: 0,
  });

  useEffect(() => {
    function updateTimer() {
      const difference =
        new Date(expiresAt).getTime() - Date.now();

      if (difference <= 0) {
        setTimeLeft({
          hours: 0,
          minutes: 0,
          seconds: 0,
        });

        if (onExpire) {
          onExpire();
        }

        return true;
      }

      setTimeLeft({
        hours: Math.floor(difference / 3600000),
        minutes: Math.floor(
          (difference % 3600000) / 60000
        ),
        seconds: Math.floor(
          (difference % 60000) / 1000
        ),
      });

      return false;
    }

    updateTimer();

    const interval = setInterval(() => {
      const expired = updateTimer();

      if (expired) {
        clearInterval(interval);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [expiresAt, onExpire]);

  return (
    <div className="timer">
      <h3>Time Remaining</h3>

      <span>
        {String(timeLeft.hours).padStart(2, "0")}:
        {String(timeLeft.minutes).padStart(2, "0")}:
        {String(timeLeft.seconds).padStart(2, "0")}
      </span>
    </div>
  );
}

export default Timer;