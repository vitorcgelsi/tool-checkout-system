from datetime import datetime

from tool_checkout.tracking_service import TrackingService


ROLE_WORKER = "Worker"
ROLE_MANAGER = "Manager"
ROLE_WAREHOUSE = "Warehouse Staff"
ROLE_ADMIN = "Administrator"

STATUS_AVAILABLE = "Available"
STATUS_CHECKED_OUT = "Checked Out"
STATUS_FLAGGED = "Flagged"
STATUS_MAINTENANCE = "Under Maintenance"
STATUS_MISSING = "Missing"
STATUS_UNDER_INVESTIGATION = "Under Investigation"

VALUE_STANDARD = "Standard"
VALUE_HIGH = "High Value"


class BusinessRuleError(Exception):
    pass


class AuthorizationError(Exception):
    pass


class NotFoundError(Exception):
    pass


# function to return the current date and time as text
def current_time_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# function to check if a role is allowed to complete an action
def role_allowed(role, allowed_roles):
    return role in allowed_roles


# function to convert a database row into a normal dictionary
def row_to_dict(row):
    if row is None:
        return None
    return dict(row)


class ToolCheckoutService:
    # class that stores the business logic for the system
    # a future frontend can call these methods instead of writing business rules again
    def __init__(self, connection):
        self.connection = connection
        self.tracking_service = TrackingService(connection)

    # function to find a user by user ID
    def get_user(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT user_id, user_name, user_role, user_password
            FROM app_users
            WHERE user_id = ?
            """,
            (user_id,),
        )
        return row_to_dict(cursor.fetchone())

    # function to check user login details
    def authenticate_user(self, user_id, password):
        user = self.get_user(user_id)

        if user is None:
            raise NotFoundError("User ID not found.")

        if user["user_password"] != password:
            raise BusinessRuleError("Incorrect password.")

        self.add_history(user["user_name"] + " logged in")
        return {
            "user_id": user["user_id"],
            "user_name": user["user_name"],
            "user_role": user["user_role"],
        }

    # function to record logout in the history table
    def logout_user(self, current_user):
        self.add_history(current_user["user_name"] + " logged out")

    # function to find a tool by tool ID
    def get_tool(self, tool_id):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT
                tool_id,
                tool_name,
                category,
                value_level,
                tool_status,
                borrowed_by,
                tool_location,
                tool_condition,
                is_high_value,
                requires_tracking,
                assigned_tracker_id
            FROM tools
            WHERE tool_id = ?
            """,
            (tool_id,),
        )
        return row_to_dict(cursor.fetchone())

    # function to return all tools
    def get_all_tools(self):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT
                tool_id,
                tool_name,
                category,
                value_level,
                tool_status,
                borrowed_by,
                tool_location,
                tool_condition,
                is_high_value,
                requires_tracking,
                assigned_tracker_id
            FROM tools
            ORDER BY tool_id
            """
        )
        rows = cursor.fetchall()
        return [row_to_dict(row) for row in rows]

    # function to add a new tool
    def add_tool(self, current_user, tool_id, tool_name, category, value_level, requires_tracking=False):
        if not role_allowed(current_user["user_role"], [ROLE_MANAGER, ROLE_ADMIN]):
            raise AuthorizationError("Only managers and administrators can add tools.")

        if value_level not in [VALUE_STANDARD, VALUE_HIGH]:
            raise BusinessRuleError("Value level must be Standard or High Value.")

        if self.get_tool(tool_id) is not None:
            raise BusinessRuleError("Tool ID already exists.")

        if value_level == VALUE_HIGH:
            is_high_value = 1
        else:
            is_high_value = 0
            requires_tracking = False

        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO tools (
                tool_id,
                tool_name,
                category,
                value_level,
                tool_status,
                borrowed_by,
                tool_location,
                tool_condition,
                is_high_value,
                requires_tracking,
                assigned_tracker_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tool_id,
                tool_name,
                category,
                value_level,
                STATUS_AVAILABLE,
                "None",
                "Warehouse",
                "Good",
                is_high_value,
                int(bool(requires_tracking)),
                None,
            ),
        )
        self.connection.commit()
        self.add_history(current_user["user_name"] + " added tool " + tool_name)
        return "Tool added successfully."

    # function to update the status fields for a tool
    def update_tool_status(self, tool_id, status, borrowed_by, location, condition):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE tools
            SET
                tool_status = ?,
                borrowed_by = ?,
                tool_location = ?,
                tool_condition = ?
            WHERE tool_id = ?
            """,
            (status, borrowed_by, location, condition, tool_id),
        )
        self.connection.commit()

    # function to checkout a tool
    def checkout_tool(self, current_user, tool_id, location, manager_id=None):
        if not role_allowed(current_user["user_role"], [ROLE_WORKER, ROLE_MANAGER, ROLE_ADMIN]):
            raise AuthorizationError("This user cannot checkout tools.")

        tool = self.get_tool(tool_id)

        if tool is None:
            raise NotFoundError("Tool ID not found.")

        if tool["tool_status"] != STATUS_AVAILABLE:
            raise BusinessRuleError("Tool is not available for checkout.")

        approved_by = "None"

        if tool["is_high_value"] == 1 and tool["requires_tracking"] == 1 and tool["assigned_tracker_id"] is None:
            raise BusinessRuleError("High value tool requires an assigned GPS/GNSS tracker before checkout.")

        if tool["value_level"] == VALUE_HIGH or tool["is_high_value"] == 1:
            if manager_id is None or manager_id.strip() == "":
                raise BusinessRuleError("High value tools require manager approval.")

            manager = self.get_user(manager_id)

            if manager is None:
                raise NotFoundError("Manager ID not found.")

            if not role_allowed(manager["user_role"], [ROLE_MANAGER, ROLE_ADMIN]):
                raise AuthorizationError("Approval must come from a manager or administrator.")

            approved_by = manager_id
            self.add_history(manager["user_name"] + " approved checkout for " + tool["tool_name"])

        self.update_tool_status(
            tool_id,
            STATUS_CHECKED_OUT,
            current_user["user_id"],
            location,
            tool["tool_condition"],
        )
        self.add_transaction(
            tool_id,
            current_user["user_id"],
            "Checkout",
            location,
            tool["tool_condition"],
            approved_by,
        )
        self.add_history(current_user["user_name"] + " checked out " + tool["tool_name"])
        return "Tool checked out successfully."

    # function to return a tool
    def return_tool(self, current_user, tool_id, condition):
        if not role_allowed(current_user["user_role"], [ROLE_WORKER, ROLE_MANAGER, ROLE_WAREHOUSE, ROLE_ADMIN]):
            raise AuthorizationError("This user cannot return tools.")

        if condition not in ["Good", "Damaged"]:
            raise BusinessRuleError("Condition must be Good or Damaged.")

        tool = self.get_tool(tool_id)

        if tool is None:
            raise NotFoundError("Tool ID not found.")

        if tool["tool_status"] != STATUS_CHECKED_OUT:
            raise BusinessRuleError("Tool is not currently checked out.")

        if condition == "Damaged":
            new_status = STATUS_FLAGGED
        else:
            new_status = STATUS_AVAILABLE

        self.update_tool_status(tool_id, new_status, "None", "Warehouse", condition)
        self.add_transaction(tool_id, current_user["user_id"], "Return", "Warehouse", condition, "None")
        self.add_history(current_user["user_name"] + " returned " + tool["tool_name"] + " as " + condition)
        return "Tool returned successfully."

    # function to flag a tool as damaged
    def flag_tool(self, current_user, tool_id):
        if not role_allowed(current_user["user_role"], [ROLE_WORKER, ROLE_MANAGER, ROLE_WAREHOUSE, ROLE_ADMIN]):
            raise AuthorizationError("This user cannot flag tools.")

        tool = self.get_tool(tool_id)

        if tool is None:
            raise NotFoundError("Tool ID not found.")

        self.update_tool_status(
            tool_id,
            STATUS_FLAGGED,
            tool["borrowed_by"],
            tool["tool_location"],
            "Damaged",
        )
        self.add_history(current_user["user_name"] + " flagged tool " + tool["tool_name"])
        return "Tool flagged successfully."

    # function to send a flagged tool to maintenance
    def send_to_maintenance(self, current_user, tool_id):
        if not role_allowed(current_user["user_role"], [ROLE_MANAGER, ROLE_ADMIN]):
            raise AuthorizationError("Only managers and administrators can send tools to maintenance.")

        tool = self.get_tool(tool_id)

        if tool is None:
            raise NotFoundError("Tool ID not found.")

        if tool["tool_status"] != STATUS_FLAGGED:
            raise BusinessRuleError("Only flagged tools can be sent to maintenance.")

        self.update_tool_status(tool_id, STATUS_MAINTENANCE, "None", "Maintenance", tool["tool_condition"])
        self.add_history(current_user["user_name"] + " sent tool " + tool["tool_name"] + " to maintenance")
        return "Tool sent to maintenance successfully."

    # function to mark a tool as high value and set its tracking requirement
    def mark_tool_as_high_value(self, current_user, tool_id, requires_tracking=True):
        if not role_allowed(current_user["user_role"], [ROLE_MANAGER, ROLE_ADMIN]):
            raise AuthorizationError("Only managers and administrators can classify high value tools.")

        tool = self.get_tool(tool_id)

        if tool is None:
            raise NotFoundError("Tool ID not found.")

        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE tools
            SET
                value_level = ?,
                is_high_value = 1,
                requires_tracking = ?
            WHERE tool_id = ?
            """,
            (VALUE_HIGH, int(bool(requires_tracking)), tool_id),
        )
        self.connection.commit()
        self.add_history(current_user["user_name"] + " marked " + tool["tool_name"] + " as high value")
        return "Tool marked as high value successfully."

    # function to create a GPS/GNSS asset tracker
    def create_tracker(self, current_user, tracker_code, tracker_type, provider_name, status="active", notes=""):
        if not role_allowed(current_user["user_role"], [ROLE_MANAGER, ROLE_ADMIN]):
            raise AuthorizationError("Only managers and administrators can create trackers.")

        message = self.tracking_service.create_tracker(tracker_code, tracker_type, provider_name, status, notes)
        self.add_history(current_user["user_name"] + " created tracker " + tracker_code)
        return message

    # function to assign a tracker to a tool
    def assign_tracker_to_tool(self, current_user, tool_id, tracker_code):
        if not role_allowed(current_user["user_role"], [ROLE_MANAGER, ROLE_ADMIN]):
            raise AuthorizationError("Only managers and administrators can assign trackers.")

        tool = self.get_tool(tool_id)

        if tool is None:
            raise NotFoundError("Tool ID not found.")

        message = self.tracking_service.assign_tracker_to_tool(tool_id, tracker_code)
        self.add_history(current_user["user_name"] + " assigned tracker " + tracker_code + " to " + tool["tool_name"])
        return message

    # function to remove the tracker assignment from a tool
    def unassign_tracker_from_tool(self, current_user, tool_id):
        if not role_allowed(current_user["user_role"], [ROLE_MANAGER, ROLE_ADMIN]):
            raise AuthorizationError("Only managers and administrators can unassign trackers.")

        tool = self.get_tool(tool_id)

        if tool is None:
            raise NotFoundError("Tool ID not found.")

        message = self.tracking_service.unassign_tracker_from_tool(tool_id)
        self.add_history(current_user["user_name"] + " unassigned tracker from " + tool["tool_name"])
        return message

    # function to get tracker status for a tracker code
    def get_tracker_status(self, current_user, tracker_code):
        if not role_allowed(current_user["user_role"], [ROLE_MANAGER, ROLE_ADMIN]):
            raise AuthorizationError("Only managers and administrators can view tracker status.")

        return self.tracking_service.get_tracker_status(tracker_code)

    # function to get the tracking status for a tool
    def get_tool_tracking_status(self, current_user, tool_id):
        if not role_allowed(current_user["user_role"], [ROLE_MANAGER, ROLE_ADMIN]):
            raise AuthorizationError("Only managers and administrators can view tracking status.")

        status = self.tracking_service.get_tool_tracking_status(tool_id)

        if status is None:
            raise NotFoundError("Tool ID not found.")

        return status

    # function to sync the latest location for a tool
    # this is intended for high-value equipment recovery and loss prevention only
    def sync_tool_location(self, current_user, tool_id, event_type="manual_sync", notes=""):
        if not role_allowed(current_user["user_role"], [ROLE_MANAGER, ROLE_ADMIN]):
            raise AuthorizationError("Only managers and administrators can sync tracker location.")

        tool = self.get_tool(tool_id)

        if tool is None:
            raise NotFoundError("Tool ID not found.")

        if tool["assigned_tracker_id"] is None:
            raise BusinessRuleError("Tool has no assigned GPS/GNSS tracker.")

        sync_result = self.tracking_service.sync_tool_location(tool_id, event_type, notes)
        self.add_history(current_user["user_name"] + " synced tracker location for " + tool["tool_name"])
        return sync_result

    # function to get tracking history for a tool
    def get_tracking_history(self, current_user, tool_id):
        if not role_allowed(current_user["user_role"], [ROLE_MANAGER, ROLE_ADMIN]):
            raise AuthorizationError("Only managers and administrators can view tracking history.")

        tool = self.get_tool(tool_id)

        if tool is None:
            raise NotFoundError("Tool ID not found.")

        return self.tracking_service.get_tracking_history(tool_id)

    # function to return all kits
    def get_all_kits(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT kit_id, kit_name FROM kits ORDER BY kit_id")
        rows = cursor.fetchall()
        return [row_to_dict(row) for row in rows]

    # function to create a kit with a list of tool IDs
    def create_kit(self, current_user, kit_id, kit_name, tool_ids):
        if not role_allowed(current_user["user_role"], [ROLE_MANAGER, ROLE_WAREHOUSE, ROLE_ADMIN]):
            raise AuthorizationError("This user cannot create kits.")

        if len(tool_ids) == 0:
            raise BusinessRuleError("Kit must contain at least one tool.")

        cursor = self.connection.cursor()
        cursor.execute("SELECT kit_id FROM kits WHERE kit_id = ?", (kit_id,))

        if cursor.fetchone() is not None:
            raise BusinessRuleError("Kit ID already exists.")

        for tool_id in tool_ids:
            if self.get_tool(tool_id) is None:
                raise NotFoundError("Tool ID not found: " + tool_id)

        cursor.execute("INSERT INTO kits (kit_id, kit_name) VALUES (?, ?)", (kit_id, kit_name))

        for tool_id in tool_ids:
            cursor.execute(
                "INSERT INTO kit_tools (kit_id, tool_id) VALUES (?, ?)",
                (kit_id, tool_id),
            )

        self.connection.commit()
        self.add_history(current_user["user_name"] + " created kit " + kit_name)
        return "Kit created successfully."

    # function to get all tool IDs inside a kit
    def get_kit_tool_ids(self, kit_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT tool_id FROM kit_tools WHERE kit_id = ? ORDER BY tool_id", (kit_id,))
        rows = cursor.fetchall()
        return [row["tool_id"] for row in rows]

    # function to verify whether all tools inside a kit are available
    def verify_kit(self, current_user, kit_id):
        if not role_allowed(current_user["user_role"], [ROLE_MANAGER, ROLE_WAREHOUSE, ROLE_ADMIN]):
            raise AuthorizationError("This user cannot verify kits.")

        cursor = self.connection.cursor()
        cursor.execute("SELECT kit_id, kit_name FROM kits WHERE kit_id = ?", (kit_id,))
        kit = row_to_dict(cursor.fetchone())

        if kit is None:
            raise NotFoundError("Kit ID not found.")

        tool_ids = self.get_kit_tool_ids(kit_id)
        results = []
        all_available = True

        for tool_id in tool_ids:
            tool = self.get_tool(tool_id)

            if tool is None:
                results.append({"tool_id": tool_id, "tool_name": "Unknown", "status": "Missing"})
                all_available = False
            else:
                results.append(
                    {
                        "tool_id": tool["tool_id"],
                        "tool_name": tool["tool_name"],
                        "status": tool["tool_status"],
                    }
                )

                if tool["tool_status"] != STATUS_AVAILABLE:
                    all_available = False

        self.add_history(current_user["user_name"] + " verified kit " + kit["kit_name"])
        return {
            "kit_id": kit["kit_id"],
            "kit_name": kit["kit_name"],
            "all_available": all_available,
            "tools": results,
        }

    # function to return checked out tools for reporting
    def get_checked_out_tools(self):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT tool_id, tool_name, borrowed_by, tool_location
            FROM tools
            WHERE tool_status = ?
            ORDER BY tool_id
            """,
            (STATUS_CHECKED_OUT,),
        )
        rows = cursor.fetchall()
        return [row_to_dict(row) for row in rows]

    # function to return flagged and maintenance tools for reporting
    def get_flagged_and_maintenance_tools(self):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT tool_id, tool_name, tool_status, tool_condition
            FROM tools
            WHERE tool_status IN (?, ?)
            ORDER BY tool_id
            """,
            (STATUS_FLAGGED, STATUS_MAINTENANCE),
        )
        rows = cursor.fetchall()
        return [row_to_dict(row) for row in rows]

    # function to return system history for reporting
    def get_history(self, current_user):
        if not role_allowed(current_user["user_role"], [ROLE_MANAGER, ROLE_ADMIN]):
            raise AuthorizationError("Only managers and administrators can view system history.")

        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT history_id, action_text, action_date
            FROM history
            ORDER BY history_id
            """
        )
        rows = cursor.fetchall()
        return [row_to_dict(row) for row in rows]

    # function to add a transaction record
    def add_transaction(self, tool_id, user_id, action_type, location, condition, approved_by):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO transactions (
                tool_id,
                user_id,
                action_type,
                action_date,
                tool_location,
                condition_text,
                approved_by
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (tool_id, user_id, action_type, current_time_text(), location, condition, approved_by),
        )
        self.connection.commit()

    # function to add a history record
    def add_history(self, action_text):
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO history (action_text, action_date) VALUES (?, ?)",
            (action_text, current_time_text()),
        )
        self.connection.commit()
