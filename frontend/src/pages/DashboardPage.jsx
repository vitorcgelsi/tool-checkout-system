import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import StatusBadge from "../components/StatusBadge";

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [myCheckouts, setMyCheckouts] = useState([]);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    api.getDashboardStats().then((data) => {
      setStats(data.stats);
      setMyCheckouts(data.my_checkouts);
    });
    if (["Manager", "Administrator"].includes(user.user_role)) {
      api.getHistory().then((data) => setHistory(data.history.slice(-10).reverse())).catch(() => {});
    }
  }, [user]);

  if (!stats) return <div className="page"><p>Loading...</p></div>;

  return (
    <div className="page">
      <h2>Dashboard</h2>
      <p className="subtitle">Welcome back, {user.user_name}</p>

      <div className="stats-grid">
        <div className="stat-card stat-green">
          <div className="stat-label">Available</div>
          <div className="stat-value">{stats.available}</div>
        </div>
        <div className="stat-card stat-blue">
          <div className="stat-label">Checked Out</div>
          <div className="stat-value">{stats.checked_out}</div>
        </div>
        <div className="stat-card stat-orange">
          <div className="stat-label">Flagged</div>
          <div className="stat-value">{stats.flagged}</div>
        </div>
        <div className="stat-card stat-yellow">
          <div className="stat-label">Under Maintenance</div>
          <div className="stat-value">{stats.maintenance}</div>
        </div>
      </div>

      {myCheckouts.length > 0 && (
        <div className="card">
          <h3>My Current Checkouts</h3>
          {myCheckouts.map((t) => (
            <div key={t.tool_id} className="list-item">
              <div>
                <strong>{t.tool_name}</strong>
                <small> ID: {t.tool_id}</small>
              </div>
              <StatusBadge status={t.tool_status} />
            </div>
          ))}
        </div>
      )}

      {history.length > 0 && (
        <div className="card">
          <h3>Recent Activity</h3>
          {history.map((h) => (
            <div key={h.history_id} className="list-item">
              <span>{h.action_text}</span>
              <small>{h.action_date}</small>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
