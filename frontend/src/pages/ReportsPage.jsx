import { useState, useEffect } from "react";
import { api } from "../services/api";
import StatusBadge from "../components/StatusBadge";

export default function ReportsPage() {
  const [tab, setTab] = useState("overview");
  const [tools, setTools] = useState([]);
  const [history, setHistory] = useState([]);
  const [flagged, setFlagged] = useState([]);
  const [statusFilter, setStatusFilter] = useState("All");
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [searchFilter, setSearchFilter] = useState("");

  useEffect(() => {
    api.getTools().then((d) => setTools(d.tools));
    api.getHistory().then((d) => setHistory(d.history)).catch(() => {});
    api.getFlaggedTools().then((d) => setFlagged(d.tools)).catch(() => {});
  }, []);

  const stats = {
    total: tools.length,
    available: tools.filter((t) => t.tool_status === "Available").length,
    checked_out: tools.filter((t) => t.tool_status === "Checked Out").length,
    flagged: tools.filter((t) => t.tool_status === "Flagged").length,
    maintenance: tools.filter((t) => t.tool_status === "Under Maintenance").length,
  };

  const categories = ["All", ...new Set(tools.map((t) => t.category))];

  const filteredTools = tools.filter((t) => {
    if (statusFilter !== "All" && t.tool_status !== statusFilter) return false;
    if (categoryFilter !== "All" && t.category !== categoryFilter) return false;
    if (searchFilter && !t.tool_name.toLowerCase().includes(searchFilter.toLowerCase()) && !t.tool_id.toLowerCase().includes(searchFilter.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="page">
      <h2>Reports</h2>
      <p className="subtitle">View and analyze tool usage and history</p>

      <div className="tabs">
        {["overview", "history", "flagged"].map((t) => (
          <button
            key={t}
            className={`tab ${tab === t ? "tab-active" : ""}`}
            onClick={() => setTab(t)}
          >
            {t === "overview" ? "Overview" : t === "history" ? "Checkout History" : "Flagged Items"}
          </button>
        ))}
      </div>

      {tab === "overview" && (
        <>
          <div className="filters-row">
            <input placeholder="Search..." value={searchFilter} onChange={(e) => setSearchFilter(e.target.value)} />
            <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
              {categories.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="All">All Statuses</option>
              <option value="Available">Available</option>
              <option value="Checked Out">Checked Out</option>
              <option value="Flagged">Flagged</option>
              <option value="Under Maintenance">Under Maintenance</option>
            </select>
          </div>

          <div className="stats-grid">
            <div className="stat-card"><div className="stat-label">Total Tools</div><div className="stat-value">{stats.total}</div></div>
            <div className="stat-card stat-green"><div className="stat-label">Available</div><div className="stat-value">{stats.available}</div></div>
            <div className="stat-card stat-blue"><div className="stat-label">Checked Out</div><div className="stat-value">{stats.checked_out}</div></div>
            <div className="stat-card stat-orange"><div className="stat-label">Flagged</div><div className="stat-value">{stats.flagged}</div></div>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr><th>Tool ID</th><th>Name</th><th>Category</th><th>Value</th><th>Status</th><th>Borrowed By</th><th>Location</th></tr>
              </thead>
              <tbody>
                {filteredTools.map((t) => (
                  <tr key={t.tool_id}>
                    <td>{t.tool_id}</td><td>{t.tool_name}</td><td>{t.category}</td>
                    <td>{t.value_level}</td><td><StatusBadge status={t.tool_status} /></td>
                    <td>{t.borrowed_by !== "None" ? t.borrowed_by : "-"}</td><td>{t.tool_location}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {tab === "history" && (
        <div className="card">
          <h3>System History</h3>
          <div className="table-container">
            <table>
              <thead><tr><th>ID</th><th>Action</th><th>Date</th></tr></thead>
              <tbody>
                {history.map((h) => (
                  <tr key={h.history_id}>
                    <td>{h.history_id}</td><td>{h.action_text}</td><td>{h.action_date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === "flagged" && (
        <div className="card">
          <h3>Flagged & Maintenance Tools</h3>
          {flagged.length === 0 ? (
            <p>No flagged or maintenance tools found.</p>
          ) : (
            <div className="table-container">
              <table>
                <thead><tr><th>Tool ID</th><th>Name</th><th>Status</th><th>Condition</th></tr></thead>
                <tbody>
                  {flagged.map((t) => (
                    <tr key={t.tool_id}>
                      <td>{t.tool_id}</td><td>{t.tool_name}</td>
                      <td><StatusBadge status={t.tool_status} /></td><td>{t.tool_condition}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
