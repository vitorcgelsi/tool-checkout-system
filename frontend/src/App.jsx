import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import ToolRegistryPage from "./pages/ToolRegistryPage";
import CheckoutPage from "./pages/CheckoutPage";
import ReturnPage from "./pages/ReturnPage";
import KitsPage from "./pages/KitsPage";
import ReportsPage from "./pages/ReportsPage";
import UsersPage from "./pages/UsersPage";
import TrackingPage from "./pages/TrackingPage";
import "./App.css";

function ProtectedRoute({ children, roles }) {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (!user) return <Navigate to="/login" />;
  if (roles && !roles.includes(user.user_role)) return <Navigate to="/dashboard" />;
  return children;
}

function AppRoutes() {
  const { user, loading } = useAuth();
  if (loading) return null;

  return (
    <>
      <Navbar />
      <main>
        <Routes>
          <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <LoginPage />} />
          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/tools" element={<ProtectedRoute roles={["Manager", "Administrator"]}><ToolRegistryPage /></ProtectedRoute>} />
          <Route path="/checkout" element={<ProtectedRoute><CheckoutPage /></ProtectedRoute>} />
          <Route path="/return" element={<ProtectedRoute><ReturnPage /></ProtectedRoute>} />
          <Route path="/kits" element={<ProtectedRoute roles={["Manager", "Warehouse Staff", "Administrator"]}><KitsPage /></ProtectedRoute>} />
          <Route path="/tracking" element={<ProtectedRoute roles={["Manager", "Administrator"]}><TrackingPage /></ProtectedRoute>} />
          <Route path="/reports" element={<ProtectedRoute roles={["Manager", "Administrator"]}><ReportsPage /></ProtectedRoute>} />
          <Route path="/users" element={<ProtectedRoute roles={["Administrator"]}><UsersPage /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
        </Routes>
      </main>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
