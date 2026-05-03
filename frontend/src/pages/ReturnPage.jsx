import { useState, useEffect } from "react";
import { api } from "../services/api";
import StatusBadge from "../components/StatusBadge";

export default function ReturnPage() {
  const [toolInput, setToolInput] = useState("");
  const [tool, setTool] = useState(null);
  const [condition, setCondition] = useState("Good");
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");
  const [checkedOut, setCheckedOut] = useState([]);

  useEffect(() => {
    api.getCheckedOutTools().then((d) => setCheckedOut(d.tools)).catch(() => {});
  }, [msg]);

  const handleSearch = async () => {
    setError("");
    setMsg("");
    setTool(null);
    if (!toolInput.trim()) return;
    try {
      const data = await api.getTool(toolInput.trim());
      setTool(data.tool);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleReturn = async (e) => {
    e.preventDefault();
    setError("");
    setMsg("");
    try {
      const data = await api.returnTool(tool.tool_id, condition);
      setMsg(data.message);
      setTool(null);
      setToolInput("");
      setCondition("Good");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="page">
      <h2>Return Tool</h2>
      <p className="subtitle">Scan or search for a tool to return</p>

      <div className="card">
        <label>Scan QR Code / Barcode or Search</label>
        <div className="input-group">
          <input
            placeholder="Scan barcode or enter tool ID..."
            value={toolInput}
            onChange={(e) => setToolInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <button className="btn btn-primary" onClick={handleSearch}>Search</button>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {msg && <div className="alert alert-success">{msg}</div>}

      {tool && (
        <div className="card">
          <h3>Tool Found</h3>
          <div className="tool-detail">
            <p><strong>{tool.tool_name}</strong> ({tool.tool_id})</p>
            <p>Status: <StatusBadge status={tool.tool_status} /></p>
            <p>Borrowed By: {tool.borrowed_by} | Location: {tool.tool_location}</p>
          </div>

          {tool.tool_status === "Checked Out" ? (
            <form onSubmit={handleReturn} className="checkout-form">
              <label>Condition Check</label>
              <select value={condition} onChange={(e) => setCondition(e.target.value)}>
                <option value="Good">Good - No issues</option>
                <option value="Damaged">Damaged - Needs attention</option>
              </select>
              <button type="submit" className="btn btn-primary">Confirm Return</button>
            </form>
          ) : (
            <p className="error-msg">This tool is not currently checked out.</p>
          )}
        </div>
      )}

      {checkedOut.length > 0 && (
        <div className="card">
          <h3>Currently Checked Out</h3>
          {checkedOut.map((t) => (
            <div
              key={t.tool_id}
              className="list-item clickable"
              onClick={() => { setToolInput(t.tool_id); }}
            >
              <div>
                <strong>{t.tool_name}</strong>
                <small> {t.tool_id} - By {t.borrowed_by}</small>
              </div>
              <small>Location: {t.tool_location}</small>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
