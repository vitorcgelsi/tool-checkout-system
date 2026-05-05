import { useEffect, useMemo, useState } from "react";
import { api } from "../services/api";
import StatusBadge from "../components/StatusBadge";

const actionKind = (text) => {
  const lower = text.toLowerCase();
  if (lower.includes("checked out") || lower.includes("checkout")) return "Checkout";
  if (lower.includes("returned")) return "Return";
  if (lower.includes("maintenance") || lower.includes("flagged")) return "Maintenance";
  if (lower.includes("tracker") || lower.includes("sync")) return "Tracking";
  return "System";
};

export default function ReportsPage() {
  const [tab, setTab] = useState("overview");
  const [tools, setTools] = useState([]);
  const [history, setHistory] = useState([]);
  const [flagged, setFlagged] = useState([]);
  const [statusFilter, setStatusFilter] = useState("All");
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [searchFilter, setSearchFilter] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.getTools(), api.getHistory(), api.getFlaggedTools()])
      .then(([toolsData, historyData, flaggedData]) => {
        setTools(toolsData.tools);
        setHistory(historyData.history.slice().reverse());
        setFlagged(flaggedData.tools);
      })
      .catch((err) => setError(err.message));
  }, []);

  const stats = {
    total: tools.length,
    available: tools.filter((tool) => tool.tool_status === "Available").length,
    checked_out: tools.filter((tool) => tool.tool_status === "Checked Out").length,
    flagged: tools.filter((tool) => tool.tool_status === "Flagged").length,
    maintenance: tools.filter((tool) => tool.tool_status === "Under Maintenance").length,
    tracked: tools.filter((tool) => tool.requires_tracking === 1).length,
  };

  const categories = useMemo(() => ["All", ...new Set(tools.map((tool) => tool.category))], [tools]);
  const reportRows = useMemo(() => history.filter((item) => {
    if (tab === "checkout" && actionKind(item.action_text) !== "Checkout") return false;
    if (tab === "returns" && actionKind(item.action_text) !== "Return") return false;
    if (tab === "maintenance" && actionKind(item.action_text) !== "Maintenance") return false;
    if (tab === "tracking" && actionKind(item.action_text) !== "Tracking") return false;
    return true;
  }), [history, tab]);

  const filteredTools = tools.filter((tool) => {
    if (statusFilter !== "All" && tool.tool_status !== statusFilter) return false;
    if (categoryFilter !== "All" && tool.category !== categoryFilter) return false;
    const searchText = `${tool.tool_name} ${tool.tool_id} ${tool.tool_location}`.toLowerCase();
    return searchText.includes(searchFilter.toLowerCase());
  });

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2>Reports & History</h2>
          <p className="subtitle">Checkout, return, maintenance, flagged asset, and tracking sync history</p>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="tabs">
        {[
          ["overview", "Overview"],
          ["checkout", "Checkouts"],
          ["returns", "Returns"],
          ["maintenance", "Maintenance"],
          ["tracking", "Tracking Syncs"],
          ["flagged", "Flagged"],
        ].map(([key, label]) => (
          <button key={key} className={`tab ${tab === key ? "tab-active" : ""}`} onClick={() => setTab(key)}>
            {label}
          </button>
        ))}
      </div>

      {tab === "overview" && (
        <>
          <div className="stats-grid stats-grid-six">
            <div className="stat-card stat-navy"><div className="stat-label">Total</div><div className="stat-value">{stats.total}</div></div>
            <div className="stat-card stat-green"><div className="stat-label">Available</div><div className="stat-value">{stats.available}</div></div>
            <div className="stat-card stat-blue"><div className="stat-label">Checked Out</div><div className="stat-value">{stats.checked_out}</div></div>
            <div className="stat-card stat-orange"><div className="stat-label">Flagged</div><div className="stat-value">{stats.flagged}</div></div>
            <div className="stat-card stat-yellow"><div className="stat-label">Maintenance</div><div className="stat-value">{stats.maintenance}</div></div>
            <div className="stat-card stat-slate"><div className="stat-label">Tracked</div><div className="stat-value">{stats.tracked}</div></div>
          </div>

          <div className="filters-row">
            <input placeholder="Search assets" value={searchFilter} onChange={(e) => setSearchFilter(e.target.value)} />
            <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
              {categories.map((category) => <option key={category} value={category}>{category}</option>)}
            </select>
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="All">All statuses</option>
              <option value="Available">Available</option>
              <option value="Checked Out">Checked Out</option>
              <option value="Flagged">Flagged</option>
              <option value="Under Maintenance">Under Maintenance</option>
            </select>
          </div>

          <div className="table-container">
            <table>
              <thead><tr><th>Tool ID</th><th>Name</th><th>Category</th><th>Status</th><th>Borrowed By</th><th>Location</th><th>Tracking</th></tr></thead>
              <tbody>
                {filteredTools.map((tool) => (
                  <tr key={tool.tool_id}>
                    <td>{tool.tool_id}</td><td>{tool.tool_name}</td><td>{tool.category}</td>
                    <td><StatusBadge status={tool.tool_status} /></td>
                    <td>{tool.borrowed_by !== "None" ? tool.borrowed_by : "-"}</td>
                    <td>{tool.tool_location}</td>
                    <td>{tool.requires_tracking ? "Required" : "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {tab !== "overview" && tab !== "flagged" && (
        <section className="card">
          <div className="section-heading">
            <h3>{tab === "tracking" ? "Tracking Sync Events" : `${tab[0].toUpperCase()}${tab.slice(1)} History`}</h3>
            <span>{reportRows.length} records</span>
          </div>
          <div className="table-container flush-table">
            <table>
              <thead><tr><th>Type</th><th>Action</th><th>Date</th></tr></thead>
              <tbody>
                {reportRows.map((item) => (
                  <tr key={item.history_id}>
                    <td><span className="badge badge-gray">{actionKind(item.action_text)}</span></td>
                    <td>{item.action_text}</td>
                    <td>{item.action_date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {reportRows.length === 0 && <div className="empty-state">No records found for this report.</div>}
          </div>
        </section>
      )}

      {tab === "flagged" && (
        <section className="card">
          <div className="section-heading">
            <h3>Overdue, Flagged & Maintenance Items</h3>
            <span>{flagged.length} records</span>
          </div>
          <div className="table-container flush-table">
            <table>
              <thead><tr><th>Tool ID</th><th>Name</th><th>Status</th><th>Condition</th><th>Action Needed</th></tr></thead>
              <tbody>
                {flagged.map((tool) => (
                  <tr key={tool.tool_id}>
                    <td>{tool.tool_id}</td><td>{tool.tool_name}</td>
                    <td><StatusBadge status={tool.tool_status} /></td><td>{tool.tool_condition}</td>
                    <td>{tool.tool_status === "Flagged" ? "Manager review" : "Repair or inspection"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {flagged.length === 0 && <div className="empty-state">No flagged or maintenance tools found.</div>}
          </div>
        </section>
      )}
    </div>
  );
}
