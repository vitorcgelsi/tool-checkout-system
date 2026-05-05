import { useState, useEffect } from "react";
import { api } from "../services/api";

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ user_id: "", user_name: "", user_role: "Worker", password: "1234" });
  const [msg, setMsg] = useState("");

  const loadUsers = () => api.getUsers().then((d) => setUsers(d.users)).catch(() => {});
  useEffect(() => { loadUsers(); }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    setMsg("");
    try {
      const res = await api.addUser(form);
      setMsg(res.message);
      setForm({ user_id: "", user_name: "", user_role: "Worker", password: "1234" });
      setShowAdd(false);
      loadUsers();
    } catch (err) {
      setMsg(err.message);
    }
  };

  const roleColor = (role) => {
    switch (role) {
      case "Worker": return "badge-blue";
      case "Manager": return "badge-green";
      case "Warehouse Staff": return "badge-orange";
      case "Administrator": return "badge-purple";
      default: return "badge-gray";
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2>User Management</h2>
          <p className="subtitle">Manage system users and access control</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowAdd(!showAdd)}>Add User</button>
      </div>

      {msg && <div className="alert">{msg}</div>}

      {showAdd && (
        <div className="card">
          <h3>Add New User</h3>
          <form onSubmit={handleAdd} className="form-row">
            <input placeholder="User ID" value={form.user_id} onChange={(e) => setForm({ ...form, user_id: e.target.value })} required />
            <input placeholder="Full Name" value={form.user_name} onChange={(e) => setForm({ ...form, user_name: e.target.value })} required />
            <select value={form.user_role} onChange={(e) => setForm({ ...form, user_role: e.target.value })}>
              <option value="Worker">Worker</option>
              <option value="Manager">Manager</option>
              <option value="Warehouse Staff">Warehouse Staff</option>
              <option value="Administrator">Administrator</option>
            </select>
            <input placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
            <button type="submit" className="btn btn-primary">Create User</button>
          </form>
        </div>
      )}

      <div className="table-container">
        <table>
          <thead>
            <tr><th>User ID</th><th>Name</th><th>Role</th></tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.user_id}>
                <td>{u.user_id}</td>
                <td>{u.user_name}</td>
                <td><span className={`badge ${roleColor(u.user_role)}`}>{u.user_role}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card" style={{ marginTop: "1.5rem" }}>
        <h3>Role Permissions</h3>
        <div className="role-info">
          <div><span className="badge badge-purple">Administrator</span> Full system access, manage users, settings, and all features</div>
          <div><span className="badge badge-green">Manager</span> Register tools, approve high-value checkouts, view reports</div>
          <div><span className="badge badge-orange">Warehouse Staff</span> Verify kits, process returns, flag tools</div>
          <div><span className="badge badge-blue">Worker</span> Check out and return tools, view own history</div>
        </div>
      </div>
    </div>
  );
}
