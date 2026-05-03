import { useState, useEffect } from "react";
import { api } from "../services/api";
import StatusBadge from "../components/StatusBadge";

export default function CheckoutPage() {
  const [toolInput, setToolInput] = useState("");
  const [tool, setTool] = useState(null);
  const [location, setLocation] = useState("");
  const [managerId, setManagerId] = useState("");
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

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

  const handleCheckout = async (e) => {
    e.preventDefault();
    setError("");
    setMsg("");
    try {
      const data = await api.checkoutTool(tool.tool_id, location, managerId);
      setMsg(data.message);
      setTool(null);
      setToolInput("");
      setLocation("");
      setManagerId("");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="page">
      <h2>Check Out Tool</h2>
      <p className="subtitle">Scan or search for a tool to check out</p>

      <div className="card">
        <label>Scan QR Code / Barcode or Search</label>
        <div className="input-group">
          <input
            placeholder="Scan barcode or enter tool ID/name..."
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
            <p>Category: {tool.category} | Value: {tool.value_level}</p>
            <p>Status: <StatusBadge status={tool.tool_status} /></p>
          </div>

          {tool.tool_status === "Available" ? (
            <form onSubmit={handleCheckout} className="checkout-form">
              <label>Location</label>
              <input
                placeholder="Enter checkout location (e.g., Event Site A)"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                required
              />
              {(tool.value_level === "High Value" || tool.is_high_value === 1) && (
                <>
                  <label>Manager ID (required for high-value tools)</label>
                  <input
                    placeholder="Enter Manager ID for approval"
                    value={managerId}
                    onChange={(e) => setManagerId(e.target.value)}
                    required
                  />
                </>
              )}
              <button type="submit" className="btn btn-primary">Confirm Checkout</button>
            </form>
          ) : (
            <p className="error-msg">This tool is not available for checkout.</p>
          )}
        </div>
      )}
    </div>
  );
}
