import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import StatusBadge from "../components/StatusBadge";

const flagLabel = (value) => (value === 1 || value === true ? "Yes" : "No");

export default function ToolRegistryPage() {
  const { user } = useAuth();
  const [tools, setTools] = useState([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ tool_id: "", tool_name: "", category: "", value_level: "Standard", requires_tracking: false });
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  const canManage = ["Manager", "Administrator"].includes(user.user_role);
  const loadTools = () => api.getTools().then((data) => setTools(data.tools)).catch((err) => setError(err.message));

  useEffect(() => { loadTools(); }, []);

  const categories = useMemo(() => [...new Set(tools.map((tool) => tool.category))], [tools]);
  const filtered = tools.filter((tool) => {
    const searchText = `${tool.tool_id} ${tool.tool_name} ${tool.category} ${tool.tool_location}`.toLowerCase();
    if (statusFilter !== "All" && tool.tool_status !== statusFilter) return false;
    return searchText.includes(search.toLowerCase());
  });

  const handleAdd = async (event) => {
    event.preventDefault();
    setMsg("");
    setError("");
    try {
      const res = await api.addTool(form);
      setMsg(res.message);
      setForm({ tool_id: "", tool_name: "", category: "", value_level: "Standard", requires_tracking: false });
      setShowAdd(false);
      loadTools();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleFlag = async (toolId) => {
    setMsg("");
    setError("");
    try {
      await api.flagTool(toolId);
      setMsg(`${toolId} has been flagged for review.`);
      loadTools();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleMaintenance = async (toolId) => {
    setMsg("");
    setError("");
    try {
      await api.sendToMaintenance(toolId);
      setMsg(`${toolId} has been moved to maintenance.`);
      loadTools();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2>Tool Registry</h2>
          <p className="subtitle">Inventory status, assignment, condition, and high-value tracking requirements</p>
        </div>
        {canManage && (
          <button className="btn btn-primary" onClick={() => setShowAdd(!showAdd)}>
            Register Tool
          </button>
        )}
      </div>

      {msg && <div className="alert alert-success">{msg}</div>}
      {error && <div className="alert alert-error">{error}</div>}

      {showAdd && (
        <div className="card">
          <h3>Register Tool</h3>
          <form onSubmit={handleAdd} className="form-grid">
            <label>Tool ID<input value={form.tool_id} onChange={(e) => setForm({ ...form, tool_id: e.target.value })} required /></label>
            <label>Tool Name<input value={form.tool_name} onChange={(e) => setForm({ ...form, tool_name: e.target.value })} required /></label>
            <label>Category<input list="tool-categories" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} required /></label>
            <datalist id="tool-categories">{categories.map((category) => <option key={category} value={category} />)}</datalist>
            <label>Value Level<select value={form.value_level} onChange={(e) => setForm({ ...form, value_level: e.target.value, requires_tracking: e.target.value === "High Value" ? form.requires_tracking : false })}>
              <option value="Standard">Standard</option>
              <option value="High Value">High Value</option>
            </select></label>
            <label className="checkbox-field">
              <input type="checkbox" checked={form.requires_tracking} disabled={form.value_level !== "High Value"} onChange={(e) => setForm({ ...form, requires_tracking: e.target.checked })} />
              Tracking required
            </label>
            <button type="submit" className="btn btn-primary">Add Tool</button>
          </form>
        </div>
      )}

      <div className="filters-row">
        <input placeholder="Search tool ID, name, category, or location" value={search} onChange={(e) => setSearch(e.target.value)} />
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
          <thead>
            <tr>
              <th>Tool ID</th><th>Name</th><th>Category</th><th>Status</th><th>Assigned User</th>
              <th>Location</th><th>Condition</th><th>High Value</th><th>Tracking</th>{canManage && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {filtered.map((tool) => (
              <tr key={tool.tool_id}>
                <td><strong>{tool.tool_id}</strong></td>
                <td>{tool.tool_name}</td>
                <td>{tool.category}</td>
                <td><StatusBadge status={tool.tool_status} /></td>
                <td>{tool.borrowed_by !== "None" ? tool.borrowed_by : "-"}</td>
                <td>{tool.tool_location}</td>
                <td>{tool.tool_condition}</td>
                <td><span className={`badge ${tool.is_high_value ? "badge-blue" : "badge-gray"}`}>{flagLabel(tool.is_high_value)}</span></td>
                <td><span className={`badge ${tool.requires_tracking ? "badge-purple" : "badge-gray"}`}>{flagLabel(tool.requires_tracking)}</span></td>
                {canManage && (
                  <td className="action-btns">
                    {tool.tool_status === "Available" && <button className="btn btn-small btn-outline" onClick={() => handleFlag(tool.tool_id)}>Flag</button>}
                    {tool.tool_status === "Flagged" && <button className="btn btn-small btn-outline" onClick={() => handleMaintenance(tool.tool_id)}>Maintenance</button>}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && <div className="empty-state">No tools match the current filters.</div>}
      </div>
    </div>
  );
}
