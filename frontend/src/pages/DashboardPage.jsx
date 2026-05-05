import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import StatusBadge from "../components/StatusBadge";

const statCards = [
  { key: "total", label: "Total tools", tone: "stat-navy" },
  { key: "available", label: "Available tools", tone: "stat-green" },
  { key: "checked_out", label: "Checked out", tone: "stat-blue" },
  { key: "maintenance", label: "Maintenance", tone: "stat-yellow" },
  { key: "flagged", label: "Flagged tools", tone: "stat-orange" },
  { key: "high_value_tracked", label: "Tracked assets", tone: "stat-slate" },
];

const eventType = (text) => {
  const lower = text.toLowerCase();
  if (lower.includes("checkout") || lower.includes("checked out")) return "Checkout";
  if (lower.includes("returned")) return "Return";
  if (lower.includes("maintenance") || lower.includes("flagged")) return "Maintenance";
  if (lower.includes("tracker") || lower.includes("sync")) return "Tracking";
  if (lower.includes("verified")) return "Kit";
  return "System";
};

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [myCheckouts, setMyCheckouts] = useState([]);
  const [history, setHistory] = useState([]);
  const [tools, setTools] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      api.getDashboardStats(),
      api.getTools(),
      ["Manager", "Administrator"].includes(user.user_role) ? api.getHistory() : Promise.resolve({ history: [] }),
    ])
      .then(([dashboardData, toolsData, historyData]) => {
        setStats(dashboardData.stats);
        setMyCheckouts(dashboardData.my_checkouts);
        setTools(toolsData.tools);
        setHistory(historyData.history.slice(-8).reverse());
      })
      .catch((err) => setError(err.message));
  }, [user]);

  if (!stats) return <div className="page"><div className="loading-state">Loading dashboard...</div></div>;

  const attentionTools = tools.filter((tool) =>
    ["Checked Out", "Flagged", "Under Maintenance"].includes(tool.tool_status)
  ).slice(0, 6);

  return (
    <div className="page">
      <div className="page-header dashboard-header">
        <div>
          <p className="eyebrow">Event production inventory</p>
          <h2>Operations Dashboard</h2>
          <p className="subtitle">Welcome back, {user.user_name}. Current asset availability and recent system activity are below.</p>
        </div>
        <div className="header-pill">{user.user_role}</div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="stats-grid stats-grid-six">
        {statCards.map((item) => (
          <div key={item.key} className={`stat-card ${item.tone}`}>
            <div className="stat-label">{item.label}</div>
            <div className="stat-value">{stats[item.key] ?? 0}</div>
          </div>
        ))}
      </div>

      <div className="dashboard-grid">
        <section className="card">
          <div className="section-heading">
            <h3>Recent Activity</h3>
            <span>{history.length} events</span>
          </div>
          {history.map((item) => (
            <div key={item.history_id} className="activity-item">
              <span className={`activity-dot activity-${eventType(item.action_text).toLowerCase()}`} />
              <div>
                <strong>{eventType(item.action_text)}</strong>
                <p>{item.action_text}</p>
              </div>
              <small>{item.action_date}</small>
            </div>
          ))}
          {history.length === 0 && <div className="empty-state">Recent activity appears here for managers and administrators.</div>}
        </section>

        <section className="card">
          <div className="section-heading">
            <h3>Assets Needing Attention</h3>
            <span>{attentionTools.length} visible</span>
          </div>
          {attentionTools.map((tool) => (
            <div key={tool.tool_id} className="list-item">
              <div>
                <strong>{tool.tool_name}</strong>
                <small>{tool.tool_id} - {tool.tool_location}</small>
              </div>
              <StatusBadge status={tool.tool_status} />
            </div>
          ))}
          {attentionTools.length === 0 && <div className="empty-state">No checked-out, flagged, or maintenance tools right now.</div>}
        </section>
      </div>

      {myCheckouts.length > 0 && (
        <section className="card">
          <div className="section-heading">
            <h3>My Current Checkouts</h3>
            <span>{myCheckouts.length} assigned</span>
          </div>
          <div className="tool-card-grid">
            {myCheckouts.map((tool) => (
              <article key={tool.tool_id} className="tool-card compact-tool-card">
                <div className="tool-card-top">
                  <span className="tool-id">{tool.tool_id}</span>
                  <StatusBadge status={tool.tool_status} />
                </div>
                <h3>{tool.tool_name}</h3>
                <p>{tool.tool_location}</p>
              </article>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
