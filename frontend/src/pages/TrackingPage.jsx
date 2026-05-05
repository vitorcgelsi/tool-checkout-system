import { useEffect, useMemo, useState } from "react";
import { api } from "../services/api";
import StatusBadge from "../components/StatusBadge";

const formatLocation = (item) => {
  if (!item?.last_latitude || !item?.last_longitude) return "Awaiting first sync";
  return `${Number(item.last_latitude).toFixed(4)}, ${Number(item.last_longitude).toFixed(4)}`;
};

export default function TrackingPage() {
  const [tools, setTools] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [status, setStatus] = useState(null);
  const [history, setHistory] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const trackedTools = useMemo(
    () => tools.filter((tool) => tool.is_high_value === 1 && tool.requires_tracking === 1),
    [tools]
  );

  useEffect(() => {
    api.getTools()
      .then((data) => {
        setTools(data.tools);
        const firstTracked = data.tools.find((tool) => tool.is_high_value === 1 && tool.requires_tracking === 1);
        if (firstTracked) setSelectedId(firstTracked.tool_id);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    Promise.all([api.getTrackingStatus(selectedId), api.getTrackingHistory(selectedId)])
      .then(([statusData, historyData]) => {
        setError("");
        setMessage("");
        setStatus(statusData.status);
        setHistory(historyData.history.slice().reverse());
      })
      .catch((err) => setError(err.message));
  }, [selectedId]);

  const handleSync = async () => {
    setError("");
    setMessage("");
    try {
      await api.syncTracking(selectedId);
      const [statusData, historyData] = await Promise.all([
        api.getTrackingStatus(selectedId),
        api.getTrackingHistory(selectedId),
      ]);
      setStatus(statusData.status);
      setHistory(historyData.history.slice().reverse());
      setMessage("Tracker synced with the simulated GPS/GNSS asset provider.");
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div className="page"><div className="loading-state">Loading tracking dashboard...</div></div>;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2>High-Value Asset Tracking</h2>
          <p className="subtitle">Simulated GPS/GNSS tracking for high-value equipment only</p>
        </div>
        <button className="btn btn-primary" onClick={handleSync} disabled={!selectedId}>
          Sync Tracker
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {message && <div className="alert alert-success">{message}</div>}

      <div className="tracking-layout">
        <aside className="card tracking-list">
          <h3>Tracked Assets</h3>
          {trackedTools.map((tool) => (
            <button
              key={tool.tool_id}
              className={`asset-row ${selectedId === tool.tool_id ? "asset-row-active" : ""}`}
              onClick={() => setSelectedId(tool.tool_id)}
            >
              <span>
                <strong>{tool.tool_name}</strong>
                <small>{tool.tool_id} - {tool.category}</small>
              </span>
              <StatusBadge status={tool.tool_status} />
            </button>
          ))}
          {trackedTools.length === 0 && <div className="empty-state">No high-value tracked assets found.</div>}
        </aside>

        <section>
          <div className="card tracking-hero">
            <div>
              <p className="eyebrow">Asset tracking, not employee tracking</p>
              <h3>{status?.tool_name || "Select a tracked asset"}</h3>
              <p className="muted">{status?.tool_id} - {status?.tracker_code || "No tracker assigned"}</p>
            </div>
            <div className="tracking-status-grid">
              <div><span>Last known location</span><strong>{formatLocation(status)}</strong></div>
              <div><span>Battery</span><strong>{status?.battery_level ? `${status.battery_level}%` : "Pending"}</strong></div>
              <div><span>Last sync</span><strong>{status?.last_sync_time || "Pending"}</strong></div>
              <div><span>Status</span><strong>{status?.status || "Not assigned"}</strong></div>
            </div>
          </div>

          <div className="map-card">
            <div className="map-grid">
              <div className="map-pin" />
            </div>
            <div className="map-overlay">
              <strong>{status?.tool_location || "Warehouse"}</strong>
              <span>{formatLocation(status)}</span>
            </div>
          </div>

          <div className="card">
            <h3>Tracking History</h3>
            <div className="table-container flush-table">
              <table>
                <thead>
                  <tr><th>Time</th><th>Event</th><th>Location</th><th>Battery</th><th>Notes</th></tr>
                </thead>
                <tbody>
                  {history.map((item) => (
                    <tr key={item.log_id}>
                      <td>{item.recorded_at}</td>
                      <td>{item.event_type.replace("_", " ")}</td>
                      <td>{Number(item.latitude).toFixed(4)}, {Number(item.longitude).toFixed(4)}</td>
                      <td>{item.battery_level}%</td>
                      <td>{item.notes || "Simulated provider sync"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {history.length === 0 && <div className="empty-state">No tracking sync events recorded yet.</div>}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
