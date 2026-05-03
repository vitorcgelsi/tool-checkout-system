import { useState, useEffect } from "react";
import { api } from "../services/api";
import StatusBadge from "../components/StatusBadge";

export default function KitsPage() {
  const [kits, setKits] = useState([]);
  const [msg, setMsg] = useState("");

  const loadKits = () => api.getKits().then((d) => setKits(d.kits)).catch(() => {});
  useEffect(() => { loadKits(); }, []);

  const handleVerify = async (kitId) => {
    try {
      const data = await api.verifyKit(kitId);
      const r = data.result;
      if (r.all_available) {
        setMsg(`Kit "${r.kit_name}" is ready for dispatch. All items available.`);
      } else {
        setMsg(`Kit "${r.kit_name}" is NOT ready. Some tools are unavailable.`);
      }
      loadKits();
    } catch (err) {
      setMsg(err.message);
    }
  };

  return (
    <div className="page">
      <h2>Equipment Kit Management</h2>
      <p className="subtitle">Prepare and verify job-based equipment kits</p>

      {msg && <div className="alert">{msg}</div>}

      <div className="kits-grid">
        {kits.map((kit) => (
          <div key={kit.kit_id} className={`card kit-card ${kit.all_available ? "kit-ready" : "kit-warning"}`}>
            <div className="kit-header">
              <h3>{kit.kit_name}</h3>
              <span className={kit.all_available ? "kit-icon-ok" : "kit-icon-warn"}>
                {kit.all_available ? "✓" : "⚠"}
              </span>
            </div>
            <p className="kit-id">Kit ID: {kit.kit_id}</p>

            <div className="kit-contents">
              <strong>Kit Contents ({kit.tools.length} items)</strong>
              {kit.tools.map((t) => (
                <div key={t.tool_id} className="kit-tool-item">
                  <span>{t.tool_name}</span>
                  <StatusBadge status={t.tool_status} />
                </div>
              ))}
            </div>

            <p className="kit-status">
              {kit.all_available ? "✓ All items available" : "⚠ Some item(s) unavailable"}
            </p>

            <button className="btn btn-full btn-outline" onClick={() => handleVerify(kit.kit_id)}>
              Verify Kit
            </button>
          </div>
        ))}
      </div>

      {kits.length === 0 && <p>No kits found.</p>}
    </div>
  );
}
