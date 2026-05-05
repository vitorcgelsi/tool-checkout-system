import { useEffect, useState } from "react";
import { api } from "../services/api";
import StatusBadge from "../components/StatusBadge";

export default function CheckoutPage() {
  const [toolInput, setToolInput] = useState("");
  const [tool, setTool] = useState(null);
  const [availableTools, setAvailableTools] = useState([]);
  const [location, setLocation] = useState("");
  const [managerId, setManagerId] = useState("");
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api.getTools()
      .then((data) => setAvailableTools(data.tools.filter((item) => item.tool_status === "Available").slice(0, 6)))
      .catch(() => {});
  }, [msg]);

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

  const handleCheckout = async (event) => {
    event.preventDefault();
    setError("");
    setMsg("");
    try {
      const data = await api.checkoutTool(tool.tool_id, location, managerId);
      setMsg(`${data.message} ${tool.tool_name} is now assigned for ${location}.`);
      setTool(null);
      setToolInput("");
      setLocation("");
      setManagerId("");
    } catch (err) {
      setError(err.message);
    }
  };

  const trackingRequired = tool && (tool.is_high_value === 1 || tool.value_level === "High Value") && tool.requires_tracking === 1;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2>Check Out Tool</h2>
          <p className="subtitle">Select an available asset, confirm site location, and capture approvals where required</p>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {msg && <div className="alert alert-success">{msg}</div>}

      <div className="workflow-grid">
        <section className="card">
          <div className="step-heading"><span>1</span><h3>Find Asset</h3></div>
          <label>Tool ID</label>
          <div className="input-group">
            <input
              placeholder="Example: T102"
              value={toolInput}
              onChange={(e) => setToolInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            />
            <button className="btn btn-primary" onClick={handleSearch}>Search</button>
          </div>

          <div className="quick-picks">
            {availableTools.map((item) => (
              <button key={item.tool_id} type="button" onClick={() => { setToolInput(item.tool_id); setTool(item); }}>
                <strong>{item.tool_name}</strong>
                <small>{item.tool_id}</small>
              </button>
            ))}
          </div>
        </section>

        <section className="card">
          <div className="step-heading"><span>2</span><h3>Review Details</h3></div>
          {tool ? (
            <div className="detail-panel">
              <div className="detail-title">
                <div>
                  <strong>{tool.tool_name}</strong>
                  <small>{tool.tool_id} - {tool.category}</small>
                </div>
                <StatusBadge status={tool.tool_status} />
              </div>
              <dl>
                <div><dt>Location</dt><dd>{tool.tool_location}</dd></div>
                <div><dt>Condition</dt><dd>{tool.tool_condition}</dd></div>
                <div><dt>High value</dt><dd>{tool.is_high_value ? "Yes" : "No"}</dd></div>
                <div><dt>Tracking required</dt><dd>{tool.requires_tracking ? "Yes" : "No"}</dd></div>
              </dl>
              {trackingRequired && (
                <div className={tool.assigned_tracker_id ? "notice notice-ok" : "notice notice-warn"}>
                  {tool.assigned_tracker_id ? "GPS/GNSS tracker assigned for asset tracking." : "Tracker assignment is required before checkout."}
                </div>
              )}
            </div>
          ) : (
            <div className="empty-state">Selected tool details will appear here.</div>
          )}
        </section>

        <section className="card">
          <div className="step-heading"><span>3</span><h3>Confirm Checkout</h3></div>
          {tool?.tool_status === "Available" ? (
            <form onSubmit={handleCheckout} className="stacked-form">
              <label>Checkout Location<input placeholder="Event site or room" value={location} onChange={(e) => setLocation(e.target.value)} required /></label>
              {(tool.value_level === "High Value" || tool.is_high_value === 1) && (
                <label>Manager Approval ID<input placeholder="U002 or U004" value={managerId} onChange={(e) => setManagerId(e.target.value)} required /></label>
              )}
              <button type="submit" className="btn btn-primary btn-full">Confirm Checkout</button>
            </form>
          ) : (
            <div className="empty-state">{tool ? "This asset is not available for checkout." : "Find an available tool to start checkout."}</div>
          )}
        </section>
      </div>
    </div>
  );
}
