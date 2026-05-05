const API_BASE = "http://localhost:5000/api";

function getToken() {
  return localStorage.getItem("token");
}

function headers() {
  const h = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) h["Authorization"] = `Bearer ${token}`;
  return h;
}

async function handleResponse(res) {
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error || "Request failed");
  }
  return data;
}

export const api = {
  // Auth
  async login(user_id, password) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id, password }),
    });
    return handleResponse(res);
  },
  async logout() {
    const res = await fetch(`${API_BASE}/auth/logout`, { method: "POST", headers: headers() });
    return handleResponse(res);
  },

  // Dashboard
  async getDashboardStats() {
    const res = await fetch(`${API_BASE}/dashboard/stats`, { headers: headers() });
    return handleResponse(res);
  },

  // Tools
  async getTools() {
    const res = await fetch(`${API_BASE}/tools`, { headers: headers() });
    return handleResponse(res);
  },
  async getTool(toolId) {
    const res = await fetch(`${API_BASE}/tools/${toolId}`, { headers: headers() });
    return handleResponse(res);
  },
  async addTool(data) {
    const res = await fetch(`${API_BASE}/tools`, { method: "POST", headers: headers(), body: JSON.stringify(data) });
    return handleResponse(res);
  },
  async flagTool(toolId) {
    const res = await fetch(`${API_BASE}/tools/${toolId}/flag`, { method: "PUT", headers: headers() });
    return handleResponse(res);
  },
  async sendToMaintenance(toolId) {
    const res = await fetch(`${API_BASE}/tools/${toolId}/maintenance`, { method: "PUT", headers: headers() });
    return handleResponse(res);
  },
  async getCheckedOutTools() {
    const res = await fetch(`${API_BASE}/tools/checked-out`, { headers: headers() });
    return handleResponse(res);
  },
  async getFlaggedTools() {
    const res = await fetch(`${API_BASE}/tools/flagged`, { headers: headers() });
    return handleResponse(res);
  },

  // Checkout / Return
  async checkoutTool(tool_id, location, manager_id) {
    const res = await fetch(`${API_BASE}/checkout`, {
      method: "POST", headers: headers(),
      body: JSON.stringify({ tool_id, location, manager_id }),
    });
    return handleResponse(res);
  },
  async returnTool(tool_id, condition) {
    const res = await fetch(`${API_BASE}/return`, {
      method: "POST", headers: headers(),
      body: JSON.stringify({ tool_id, condition }),
    });
    return handleResponse(res);
  },

  // Tracking
  async getTrackingStatus(toolId) {
    const res = await fetch(`${API_BASE}/tools/${toolId}/tracking-status`, { headers: headers() });
    return handleResponse(res);
  },
  async syncTracking(toolId) {
    const res = await fetch(`${API_BASE}/tools/${toolId}/tracker/sync`, { method: "POST", headers: headers() });
    return handleResponse(res);
  },
  async getTrackingHistory(toolId) {
    const res = await fetch(`${API_BASE}/tools/${toolId}/tracking-history`, { headers: headers() });
    return handleResponse(res);
  },

  // Kits
  async getKits() {
    const res = await fetch(`${API_BASE}/kits`, { headers: headers() });
    return handleResponse(res);
  },
  async createKit(data) {
    const res = await fetch(`${API_BASE}/kits`, { method: "POST", headers: headers(), body: JSON.stringify(data) });
    return handleResponse(res);
  },
  async verifyKit(kitId) {
    const res = await fetch(`${API_BASE}/kits/${kitId}/verify`, { method: "POST", headers: headers() });
    return handleResponse(res);
  },

  // History
  async getHistory() {
    const res = await fetch(`${API_BASE}/history`, { headers: headers() });
    return handleResponse(res);
  },

  // Users
  async getUsers() {
    const res = await fetch(`${API_BASE}/users`, { headers: headers() });
    return handleResponse(res);
  },
  async addUser(data) {
    const res = await fetch(`${API_BASE}/users`, { method: "POST", headers: headers(), body: JSON.stringify(data) });
    return handleResponse(res);
  },
};
