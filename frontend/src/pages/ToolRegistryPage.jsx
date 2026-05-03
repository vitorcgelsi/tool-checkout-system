import { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import StatusBadge from "../components/StatusBadge";

export default function ToolRegistryPage() {
  const { user } = useAuth();
  const [tools, setTools] = useState([]);
  const [search, setSearch] = useState("");
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ tool_id: "", tool_name: "", category: "", value_level: "Standard" });
  const [msg, setMsg] = useState("");

  const loadTools = () => api.getTools().then((d) => setTools(d.tools));
  useEffect(() => { loadTools(); }, []);

  const filtered = tools.filter(
    (t) =>
      t.tool_id.toLowerCase().includes(search.toLowerCase()) ||
      t.tool_name.toLowerCase().includes(search.toLowerCase()) ||
      t.category.toLowerCase().includes(search.toLowerCase())
  );

  const handleAdd = async (e) => {
    e.preventDefault();
    setMsg("");
    try {
      const res = await api.addTool(form);
      setMsg(res.message);
      setForm({ tool_id: "", tool_name: "", category: "", value_level: "Standard" });
      setShowAdd(false);
      loadTools();
    } catch (err) {
      setMsg(err.message);
    }
  };

  const handleFlag = async (toolId) => {
    try {
      await api.flagTool(toolId);
      loadTools();
    } catch (err) {
      setMsg(err.message);
    }
  };

  const handleMaintenance = async (toolId) => {
    try {
      await api.sendToMaintenance(toolId);
      loadTools();
    } catch (err) {
      setMsg(err.message);
    }
  };

  const canManage = ["Manager", "Administrator"].includes(user.user_role);

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2>Tool Registry</h2>
          <p className="subtitle">Manage and track all tools</p>
        </div>
        {canManage && (
          <button className="btn btn-primary" onClick={() => setShowAdd(!showAdd)}>
            Register New Tool
          </button>
        )}
      </div>

      {msg && <div className="alert">{msg}</div>}

      {showAdd && (
        <div className="card">
          <h3>Register New Tool</h3>
          <form onSubmit={handleAdd} className="form-row">
            <input placeholder="Tool ID" value={form.tool_id} onChange={(e) => setForm({ ...form, tool_id: e.target.value })} required />
            <input placeholder="Tool Name" value={form.tool_name} onChange={(e) => setForm({ ...form, tool_name: e.target.value })} required />
            <input placeholder="Category" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} required />
            <select value={form.value_level} onChange={(e) => setForm({ ...form, value_level: e.target.value })}>
              <option value="Standard">Standard</option>
              <option value="High Value">High Value</option>
            </select>
            <button type="submit" className="btn btn-primary">Add Tool</button>
          </form>
        </div>
      )}

      <input
        className="search-input"
        placeholder="Search by tool name, ID, or category..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Tool ID</th>
              <th>Name</th>
              <th>Category</th>
              <th>Value Level</th>
              <th>Status</th>
              <th>Location</th>
              {canManage && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {filtered.map((t) => (
              <tr key={t.tool_id}>
                <td>{t.tool_id}</td>
                <td>{t.tool_name}</td>
                <td>{t.category}</td>
                <td>{t.value_level}</td>
                <td><StatusBadge status={t.tool_status} /></td>
                <td>{t.tool_location}</td>
                {canManage && (
                  <td className="action-btns">
                    {t.tool_status === "Available" && (
                      <button className="btn btn-small btn-outline" onClick={() => handleFlag(t.tool_id)}>Flag</button>
                    )}
                    {t.tool_status === "Flagged" && (
                      <button className="btn btn-small btn-outline" onClick={() => handleMaintenance(t.tool_id)}>Maintenance</button>
                    )}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
