import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    try {
      await login(userId, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="login-container">
      <section className="login-panel">
        <div className="login-copy">
          <div className="brand-lockup">
            <span className="brand-mark">TCS</span>
            <span>Tool Checkout System</span>
          </div>
          <h1>Event Production Asset Control</h1>
          <p>Manage tool availability, kit readiness, high-value asset tracking, and return condition records from one demo system.</p>
        </div>

        <div className="login-card">
          <div className="login-mark">TCS</div>
          <h2>Sign in</h2>
          <p className="login-subtitle">Use a demo role to view the workflow.</p>

          <form onSubmit={handleSubmit}>
            <label>Staff ID</label>
            <input type="text" placeholder="U001" value={userId} onChange={(e) => setUserId(e.target.value)} required />

            <label>Password</label>
            <input type="password" placeholder="1234" value={password} onChange={(e) => setPassword(e.target.value)} required />

            {error && <div className="error-msg">{error}</div>}

            <button type="submit" className="btn btn-primary btn-full">Sign In</button>
          </form>

          <div className="demo-credentials">
            <p><strong>Demo Credentials</strong></p>
            <p>Worker: U001 / 1234</p>
            <p>Manager: U002 / 1234</p>
            <p>Warehouse: U003 / 1234</p>
            <p>Admin: U004 / 1234</p>
          </div>
        </div>
      </section>
    </div>
  );
}
