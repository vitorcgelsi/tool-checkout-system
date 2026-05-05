import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const NAV_ITEMS = {
  Worker: [
    { to: "/dashboard", label: "Dashboard" },
    { to: "/checkout", label: "Check Out" },
    { to: "/return", label: "Return" },
  ],
  Manager: [
    { to: "/dashboard", label: "Dashboard" },
    { to: "/tools", label: "Tool Registry" },
    { to: "/checkout", label: "Check Out" },
    { to: "/return", label: "Return" },
    { to: "/kits", label: "Kits" },
    { to: "/tracking", label: "Tracking" },
    { to: "/reports", label: "Reports" },
  ],
  "Warehouse Staff": [
    { to: "/dashboard", label: "Dashboard" },
    { to: "/checkout", label: "Check Out" },
    { to: "/return", label: "Return" },
    { to: "/kits", label: "Kits" },
  ],
  Administrator: [
    { to: "/dashboard", label: "Dashboard" },
    { to: "/tools", label: "Tool Registry" },
    { to: "/checkout", label: "Check Out" },
    { to: "/return", label: "Return" },
    { to: "/kits", label: "Kits" },
    { to: "/tracking", label: "Tracking" },
    { to: "/reports", label: "Reports" },
    { to: "/users", label: "Users" },
  ],
};

export default function Navbar() {
  const { user, logout } = useAuth();
  if (!user) return null;

  const items = NAV_ITEMS[user.user_role] || NAV_ITEMS.Worker;

  return (
    <header className="navbar">
      <div className="navbar-left">
        <span className="navbar-brand">Tool Checkout System</span>
        <span className="navbar-subtitle">Event Production Management</span>
      </div>
      <nav className="navbar-center">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="navbar-right">
        <span className="user-info">
          <strong>{user.user_name}</strong>
          <small>{user.user_role}</small>
        </span>
        <button className="btn btn-outline" onClick={logout}>Sign Out</button>
      </div>
    </header>
  );
}
