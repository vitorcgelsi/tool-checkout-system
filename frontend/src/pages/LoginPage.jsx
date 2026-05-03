import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
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
      <div className="login-card">
        <div className="login-icon">🔐</div>
        <h1>Tool Checkout System</h1>
        <p className="login-subtitle">Event Production Management</p>

        <form onSubmit={handleSubmit}>
          <label>Staff ID</label>
          <input
            type="text"
            placeholder="Enter your staff ID"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            required
          />

          <label>Password</label>
          <input
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {error && <div className="error-msg">{error}</div>}

          <button type="submit" className="btn btn-primary btn-full">
            Sign In
          </button>
        </form>

        <div className="demo-credentials">
          <p><strong>Demo Credentials:</strong></p>
          <p>Worker: U001 / 1234</p>
          <p>Manager: U002 / 1234</p>
          <p>Warehouse: U003 / 1234</p>
          <p>Admin: U004 / 1234</p>
        </div>
      </div>
    </div>
  );
}
