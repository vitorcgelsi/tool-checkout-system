import { useEffect, useState } from "react";
import { api } from "../services/api";
import StatusBadge from "../components/StatusBadge";

export default function ReturnPage() {
  const [toolInput, setToolInput] = useState("");
  const [tool, setTool] = useState(null);
  const [condition, setCondition] = useState("Good");
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");
  const [checkedOut, setCheckedOut] = useState([]);

  const refreshCheckedOut = () => api.getCheckedOutTools().then((data) => setCheckedOut(data.tools)).catch(() => {});
  useEffect(() => { refreshCheckedOut(); }, [msg]);

  const handleSearch = async () => {
    setError("");
    setMsg("");
    setTool(null);
    if (!toolInput.trim()) {
      setError("Enter a tool ID before searching.");
      return;
    }
    try {
      const data = await api.getTool(toolInput.trim());
      setTool(data.tool);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleReturn = async (event) => {
    event.preventDefault();
    setError("");
    setMsg("");
    try {
      const data = await api.returnTool(tool.tool_id, condition);
      setMsg(`${data.message} ${condition === "Damaged" ? "The tool has been flagged for review." : "The tool is available again."}`);
      setTool(null);
      setToolInput("");
      setCondition("Good");
      refreshCheckedOut();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2>Return Tool</h2>
          <p className="subtitle">Process returns, record condition, and flag damaged equipment for review</p>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {msg && <div className="alert alert-success">{msg}</div>}

      <div className="workflow-grid two-column">
        <section className="card">
          <div className="step-heading"><span>1</span><h3>Find Checked-Out Tool</h3></div>
          <label>Tool ID</label>
          <div className="input-group">
            <input placeholder="Example: T104" value={toolInput} onChange={(e) => setToolInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleSearch()} />
            <button className="btn btn-primary" onClick={handleSearch}>Search</button>
          </div>
          <div className="return-list">
            {checkedOut.map((item) => (
              <button key={item.tool_id} onClick={() => { setToolInput(item.tool_id); api.getTool(item.tool_id).then((data) => setTool(data.tool)); }}>
                <span><strong>{item.tool_name}</strong><small>{item.tool_id} - {item.borrowed_by}</small></span>
                <small>{item.tool_location}</small>
              </button>
            ))}
            {checkedOut.length === 0 && <div className="empty-state">No tools are currently checked out.</div>}
          </div>
        </section>

        <section className="card">
          <div className="step-heading"><span>2</span><h3>Condition Review</h3></div>
          {tool ? (
            <>
              <div className="detail-panel">
                <div className="detail-title">
                  <div><strong>{tool.tool_name}</strong><small>{tool.tool_id} - {tool.category}</small></div>
                  <StatusBadge status={tool.tool_status} />
                </div>
                <dl>
                  <div><dt>Borrowed by</dt><dd>{tool.borrowed_by}</dd></div>
                  <div><dt>Current location</dt><dd>{tool.tool_location}</dd></div>
                  <div><dt>Recorded condition</dt><dd>{tool.tool_condition}</dd></div>
                </dl>
              </div>

              {tool.tool_status === "Checked Out" ? (
                <form onSubmit={handleReturn} className="stacked-form">
                  <label>Return Condition
                    <select value={condition} onChange={(e) => setCondition(e.target.value)}>
                      <option value="Good">Good - ready for storage</option>
                      <option value="Damaged">Damaged - flag for maintenance</option>
                    </select>
                  </label>
                  {condition === "Damaged" && <div className="notice notice-warn">Damaged returns become flagged tools in the registry.</div>}
                  <button type="submit" className="btn btn-primary btn-full">Confirm Return</button>
                </form>
              ) : (
                <div className="empty-state">This tool is not currently checked out.</div>
              )}
            </>
          ) : (
            <div className="empty-state">Select a checked-out tool to complete the return workflow.</div>
          )}
        </section>
      </div>
    </div>
  );
}
