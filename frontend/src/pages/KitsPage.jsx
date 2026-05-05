import { useEffect, useState } from "react";
import { api } from "../services/api";
import StatusBadge from "../components/StatusBadge";

export default function KitsPage() {
  const [kits, setKits] = useState([]);
  const [selectedResult, setSelectedResult] = useState(null);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  const loadKits = () => api.getKits().then((data) => setKits(data.kits)).catch((err) => setError(err.message));
  useEffect(() => { loadKits(); }, []);

  const handleVerify = async (kitId) => {
    setMsg("");
    setError("");
    try {
      const data = await api.verifyKit(kitId);
      setSelectedResult(data.result);
      setMsg(data.result.all_available
        ? `${data.result.kit_name} is ready for dispatch.`
        : `${data.result.kit_name} has missing or unavailable items.`);
      loadKits();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2>Kit Verification</h2>
          <p className="subtitle">Confirm required equipment is present before dispatch to an event site</p>
        </div>
      </div>

      {msg && <div className={selectedResult?.all_available ? "alert alert-success" : "alert alert-error"}>{msg}</div>}
      {error && <div className="alert alert-error">{error}</div>}

      <div className="kits-grid">
        {kits.map((kit) => (
          <article key={kit.kit_id} className={`card kit-card ${kit.all_available ? "kit-ready" : "kit-warning"}`}>
            <div className="kit-header">
              <div>
                <h3>{kit.kit_name}</h3>
                <p className="kit-id">{kit.kit_id} - {kit.tools.length} required items</p>
              </div>
              <span className={`badge ${kit.all_available ? "badge-green" : "badge-orange"}`}>
                {kit.all_available ? "Ready" : "Issue"}
              </span>
            </div>

            <div className="kit-contents">
              {kit.tools.map((tool) => (
                <div key={tool.tool_id} className="kit-tool-item">
                  <div>
                    <strong>{tool.tool_name}</strong>
                    <small>{tool.tool_id}</small>
                  </div>
                  <div className="kit-present">
                    <span className={tool.tool_status === "Available" ? "presence-dot present" : "presence-dot missing"} />
                    <StatusBadge status={tool.tool_status} />
                  </div>
                </div>
              ))}
            </div>

            <div className="verification-note">
              {kit.all_available ? "All required items are present and available." : "One or more items need review before dispatch."}
            </div>
            <button className="btn btn-full btn-outline" onClick={() => handleVerify(kit.kit_id)}>
              Verify Kit
            </button>
          </article>
        ))}
      </div>

      {selectedResult && (
        <section className="card verification-result">
          <div className="section-heading">
            <h3>Verification Result</h3>
            <span>{selectedResult.all_available ? "Ready" : "Issue flagged"}</span>
          </div>
          <div className="table-container flush-table">
            <table>
              <thead><tr><th>Tool ID</th><th>Required Item</th><th>Present Status</th><th>Notes</th></tr></thead>
              <tbody>
                {selectedResult.tools.map((tool) => (
                  <tr key={tool.tool_id}>
                    <td>{tool.tool_id}</td>
                    <td>{tool.tool_name}</td>
                    <td><StatusBadge status={tool.status} /></td>
                    <td>{tool.status === "Available" ? "Ready for kit dispatch" : "Issue flag required"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {kits.length === 0 && <div className="empty-state">No kits found.</div>}
    </div>
  );
}
