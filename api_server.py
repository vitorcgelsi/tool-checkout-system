"""
Flask REST API server for the Tool Checkout System.
Wraps the existing Python backend (ToolCheckoutService) with HTTP endpoints.
"""

import sys
import os

# Add the backend module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tool_checkout_backend_sqlite"))

import sqlite3
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from tool_checkout.database import get_database_path, create_tables, seed_sample_data
from tool_checkout.services import (
    ToolCheckoutService,
    AuthorizationError,
    BusinessRuleError,
    NotFoundError,
)
from tool_checkout.tracking_service import TrackingError

app = Flask(__name__)
app.secret_key = "tool-checkout-secret-key-dev"
CORS(app, supports_credentials=True)

# Initialize DB on first run to create tables/seed data
_init_conn = sqlite3.connect(get_database_path())
_init_conn.row_factory = sqlite3.Row
_init_conn.execute("PRAGMA foreign_keys = ON")
create_tables(_init_conn)
seed_sample_data(_init_conn)
_init_conn.close()


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(get_database_path())
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def get_service():
    return ToolCheckoutService(get_db())


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


logged_in_users = {}


def get_current_user():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token or token not in logged_in_users:
        return None
    return logged_in_users[token]


def require_auth():
    return get_current_user()


def error_response(message, status_code=400):
    return jsonify({"error": message}), status_code


# ─── Authentication ───────────────────────────────────────────────────────────

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    user_id = data.get("user_id", "")
    password = data.get("password", "")
    try:
        user = get_service().authenticate_user(user_id, password)
        token = user["user_id"]
        logged_in_users[token] = user
        return jsonify({"token": token, "user": user})
    except (NotFoundError, BusinessRuleError) as e:
        return error_response(str(e), 401)


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    user = get_current_user()
    if user:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        get_service().logout_user(user)
        logged_in_users.pop(token, None)
    return jsonify({"message": "Logged out"})


@app.route("/api/auth/me", methods=["GET"])
def get_me():
    user = get_current_user()
    if not user:
        return error_response("Not authenticated", 401)
    return jsonify({"user": user})


# ─── Tools ────────────────────────────────────────────────────────────────────

@app.route("/api/tools", methods=["GET"])
def get_all_tools():
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    tools = get_service().get_all_tools()
    return jsonify({"tools": tools})


@app.route("/api/tools/<tool_id>", methods=["GET"])
def get_tool(tool_id):
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    tool = get_service().get_tool(tool_id)
    if tool is None:
        return error_response("Tool not found", 404)
    return jsonify({"tool": tool})


@app.route("/api/tools", methods=["POST"])
def add_tool():
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    data = request.get_json()
    try:
        message = get_service().add_tool(
            user,
            data.get("tool_id", ""),
            data.get("tool_name", ""),
            data.get("category", ""),
            data.get("value_level", "Standard"),
            data.get("requires_tracking", False),
        )
        return jsonify({"message": message})
    except (AuthorizationError, BusinessRuleError, NotFoundError) as e:
        return error_response(str(e))


@app.route("/api/tools/<tool_id>/high-value", methods=["PUT"])
def mark_high_value(tool_id):
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    data = request.get_json()
    try:
        message = get_service().mark_tool_as_high_value(
            user, tool_id, data.get("requires_tracking", True)
        )
        return jsonify({"message": message})
    except (AuthorizationError, BusinessRuleError, NotFoundError) as e:
        return error_response(str(e))


@app.route("/api/tools/<tool_id>/flag", methods=["PUT"])
def flag_tool(tool_id):
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    try:
        message = get_service().flag_tool(user, tool_id)
        return jsonify({"message": message})
    except (AuthorizationError, BusinessRuleError, NotFoundError) as e:
        return error_response(str(e))


@app.route("/api/tools/<tool_id>/maintenance", methods=["PUT"])
def send_to_maintenance(tool_id):
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    try:
        message = get_service().send_to_maintenance(user, tool_id)
        return jsonify({"message": message})
    except (AuthorizationError, BusinessRuleError, NotFoundError) as e:
        return error_response(str(e))


# ─── Checkout / Return ────────────────────────────────────────────────────────

@app.route("/api/checkout", methods=["POST"])
def checkout_tool():
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    data = request.get_json()
    try:
        message = get_service().checkout_tool(
            user,
            data.get("tool_id", ""),
            data.get("location", ""),
            data.get("manager_id", ""),
        )
        return jsonify({"message": message})
    except (AuthorizationError, BusinessRuleError, NotFoundError, TrackingError) as e:
        return error_response(str(e))


@app.route("/api/return", methods=["POST"])
def return_tool():
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    data = request.get_json()
    try:
        message = get_service().return_tool(
            user,
            data.get("tool_id", ""),
            data.get("condition", "Good"),
        )
        return jsonify({"message": message})
    except (AuthorizationError, BusinessRuleError, NotFoundError) as e:
        return error_response(str(e))


@app.route("/api/tools/checked-out", methods=["GET"])
def get_checked_out_tools():
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    tools = get_service().get_checked_out_tools()
    return jsonify({"tools": tools})


@app.route("/api/tools/flagged", methods=["GET"])
def get_flagged_tools():
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    tools = get_service().get_flagged_and_maintenance_tools()
    return jsonify({"tools": tools})


# ─── Kits ─────────────────────────────────────────────────────────────────────

@app.route("/api/kits", methods=["GET"])
def get_all_kits():
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    svc = get_service()
    kits = svc.get_all_kits()
    enriched = []
    for kit in kits:
        tool_ids = svc.get_kit_tool_ids(kit["kit_id"])
        tools = []
        for tid in tool_ids:
            tool = svc.get_tool(tid)
            if tool:
                tools.append({"tool_id": tool["tool_id"], "tool_name": tool["tool_name"], "tool_status": tool["tool_status"]})
            else:
                tools.append({"tool_id": tid, "tool_name": "Unknown", "tool_status": "Missing"})
        all_available = all(t["tool_status"] == "Available" for t in tools)
        enriched.append({**kit, "tools": tools, "all_available": all_available})
    return jsonify({"kits": enriched})


@app.route("/api/kits", methods=["POST"])
def create_kit():
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    data = request.get_json()
    try:
        message = get_service().create_kit(user, data.get("kit_id", ""), data.get("kit_name", ""), data.get("tool_ids", []))
        return jsonify({"message": message})
    except (AuthorizationError, BusinessRuleError, NotFoundError) as e:
        return error_response(str(e))


@app.route("/api/kits/<kit_id>/verify", methods=["POST"])
def verify_kit(kit_id):
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    try:
        result = get_service().verify_kit(user, kit_id)
        return jsonify({"result": result})
    except (AuthorizationError, BusinessRuleError, NotFoundError) as e:
        return error_response(str(e))


# ─── Reports / History ────────────────────────────────────────────────────────

@app.route("/api/history", methods=["GET"])
def get_history():
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    try:
        history = get_service().get_history(user)
        return jsonify({"history": history})
    except (AuthorizationError, BusinessRuleError) as e:
        return error_response(str(e))


# ─── Tracking ─────────────────────────────────────────────────────────────────

@app.route("/api/trackers", methods=["POST"])
def create_tracker():
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    data = request.get_json()
    try:
        message = get_service().create_tracker(
            user, data.get("tracker_code", ""), data.get("tracker_type", "GPS/GNSS Cellular Asset Tracker"),
            data.get("provider_name", ""), data.get("status", "active"), data.get("notes", ""),
        )
        return jsonify({"message": message})
    except (AuthorizationError, TrackingError) as e:
        return error_response(str(e))


@app.route("/api/tools/<tool_id>/tracker/assign", methods=["POST"])
def assign_tracker(tool_id):
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    data = request.get_json()
    try:
        message = get_service().assign_tracker_to_tool(user, tool_id, data.get("tracker_code", ""))
        return jsonify({"message": message})
    except (AuthorizationError, NotFoundError, TrackingError) as e:
        return error_response(str(e))


@app.route("/api/tools/<tool_id>/tracker/unassign", methods=["POST"])
def unassign_tracker(tool_id):
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    try:
        message = get_service().unassign_tracker_from_tool(user, tool_id)
        return jsonify({"message": message})
    except (AuthorizationError, NotFoundError, TrackingError) as e:
        return error_response(str(e))


@app.route("/api/tools/<tool_id>/tracker/sync", methods=["POST"])
def sync_location(tool_id):
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    try:
        result = get_service().sync_tool_location(user, tool_id)
        return jsonify({"result": result})
    except (AuthorizationError, BusinessRuleError, NotFoundError, TrackingError) as e:
        return error_response(str(e))


@app.route("/api/tools/<tool_id>/tracking-status", methods=["GET"])
def get_tracking_status(tool_id):
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    try:
        status = get_service().get_tool_tracking_status(user, tool_id)
        return jsonify({"status": status})
    except (AuthorizationError, NotFoundError) as e:
        return error_response(str(e))


@app.route("/api/tools/<tool_id>/tracking-history", methods=["GET"])
def get_tracking_history(tool_id):
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    try:
        history = get_service().get_tracking_history(user, tool_id)
        return jsonify({"history": history})
    except (AuthorizationError, NotFoundError) as e:
        return error_response(str(e))


# ─── User Management (Admin) ─────────────────────────────────────────────────

@app.route("/api/users", methods=["GET"])
def get_all_users():
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    if user["user_role"] not in ["Administrator", "Manager"]:
        return error_response("Not authorized", 403)
    cursor = get_db().cursor()
    cursor.execute("SELECT user_id, user_name, user_role FROM app_users ORDER BY user_id")
    rows = cursor.fetchall()
    users = [dict(row) for row in rows]
    return jsonify({"users": users})


@app.route("/api/users", methods=["POST"])
def add_user():
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    if user["user_role"] != "Administrator":
        return error_response("Not authorized", 403)
    data = request.get_json()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT user_id FROM app_users WHERE user_id = ?", (data.get("user_id", ""),))
    if cursor.fetchone():
        return error_response("User ID already exists")
    cursor.execute(
        "INSERT INTO app_users (user_id, user_name, user_role, user_password) VALUES (?, ?, ?, ?)",
        (data.get("user_id", ""), data.get("user_name", ""), data.get("user_role", "Worker"), data.get("password", "1234")),
    )
    db.commit()
    get_service().add_history(user["user_name"] + " added user " + data.get("user_name", ""))
    return jsonify({"message": "User created successfully."})


# ─── Dashboard Stats ──────────────────────────────────────────────────────────

@app.route("/api/dashboard/stats", methods=["GET"])
def get_dashboard_stats():
    user = require_auth()
    if not user:
        return error_response("Not authenticated", 401)
    tools = get_service().get_all_tools()
    available = sum(1 for t in tools if t["tool_status"] == "Available")
    checked_out = sum(1 for t in tools if t["tool_status"] == "Checked Out")
    flagged = sum(1 for t in tools if t["tool_status"] == "Flagged")
    maintenance = sum(1 for t in tools if t["tool_status"] == "Under Maintenance")

    my_checkouts = []
    if user["user_role"] in ["Worker", "Manager", "Administrator"]:
        for t in tools:
            if t["tool_status"] == "Checked Out" and t["borrowed_by"] == user["user_id"]:
                my_checkouts.append(t)

    high_value_tracked = sum(1 for t in tools if t["is_high_value"] == 1 and t["requires_tracking"] == 1)

    return jsonify({
        "stats": {"available": available, "checked_out": checked_out, "flagged": flagged, "maintenance": maintenance, "total": len(tools), "high_value_tracked": high_value_tracked},
        "my_checkouts": my_checkouts,
    })


if __name__ == "__main__":
    print("Starting Tool Checkout API server on http://localhost:5000")
    print("Sample users: U001/1234 (Worker), U002/1234 (Manager), U003/1234 (Warehouse), U004/1234 (Admin)")
    app.run(debug=True, port=5000)
