from datetime import datetime


class TrackingError(Exception):
    pass


# function to return the current date and time as text
def current_time_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# function to convert a database row into a normal dictionary
def row_to_dict(row):
    if row is None:
        return None
    return dict(row)


# function to simulate a GPS/GNSS provider API response
# in a real implementation, this function would call the provider cloud API
def get_latest_tracker_location(tracker_code):
    simulated_locations = {
        "GPS-001": (-33.8688, 151.2093),
        "GPS-002": (-33.8727, 151.2057),
        "GPS-003": (-33.8568, 151.2153),
    }

    if tracker_code in simulated_locations:
        latitude, longitude = simulated_locations[tracker_code]
    else:
        # creates a stable simulated location for tracker codes not listed above
        code_total = sum(ord(character) for character in tracker_code)
        latitude = -33.8688 + ((code_total % 20) / 1000)
        longitude = 151.2093 + ((code_total % 15) / 1000)

    return {
        "tracker_code": tracker_code,
        "latitude": latitude,
        "longitude": longitude,
        "battery_level": 82,
        "last_location_time": current_time_text(),
        "status": "active",
    }


class TrackingService:
    # class that controls tracker records and tracking logs
    # this service is backend-only and can be called by a future frontend
    def __init__(self, connection):
        self.connection = connection

    # function to create a GPS/GNSS asset tracker record
    def create_tracker(self, tracker_code, tracker_type, provider_name, status="active", notes=""):
        if self.get_tracker_status(tracker_code) is not None:
            raise TrackingError("Tracker code already exists.")

        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO trackers (
                tracker_code,
                tracker_type,
                provider_name,
                assigned_tool_id,
                status,
                battery_level,
                last_latitude,
                last_longitude,
                last_location_time,
                last_sync_time,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tracker_code,
                tracker_type,
                provider_name,
                None,
                status,
                None,
                None,
                None,
                None,
                None,
                notes,
            ),
        )
        self.connection.commit()
        return "Tracker created successfully."

    # function to get tracker details using the tracker code
    def get_tracker_status(self, tracker_code):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT
                tracker_id,
                tracker_code,
                tracker_type,
                provider_name,
                assigned_tool_id,
                status,
                battery_level,
                last_latitude,
                last_longitude,
                last_location_time,
                last_sync_time,
                notes
            FROM trackers
            WHERE tracker_code = ?
            """,
            (tracker_code,),
        )
        return row_to_dict(cursor.fetchone())

    # function to get tracker details using the tracker ID
    def get_tracker_by_id(self, tracker_id):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT
                tracker_id,
                tracker_code,
                tracker_type,
                provider_name,
                assigned_tool_id,
                status,
                battery_level,
                last_latitude,
                last_longitude,
                last_location_time,
                last_sync_time,
                notes
            FROM trackers
            WHERE tracker_id = ?
            """,
            (tracker_id,),
        )
        return row_to_dict(cursor.fetchone())

    # function to assign a tracker to a tool
    def assign_tracker_to_tool(self, tool_id, tracker_code):
        tracker = self.get_tracker_status(tracker_code)

        if tracker is None:
            raise TrackingError("Tracker code not found.")

        cursor = self.connection.cursor()
        cursor.execute("SELECT tool_id FROM tools WHERE tool_id = ?", (tool_id,))
        tool = cursor.fetchone()

        if tool is None:
            raise TrackingError("Tool ID not found.")

        if tracker["assigned_tool_id"] not in [None, tool_id]:
            raise TrackingError("Tracker is already assigned to another tool.")

        cursor.execute(
            """
            UPDATE trackers
            SET assigned_tool_id = ?
            WHERE tracker_code = ?
            """,
            (tool_id, tracker_code),
        )
        cursor.execute(
            """
            UPDATE tools
            SET assigned_tracker_id = ?
            WHERE tool_id = ?
            """,
            (tracker["tracker_id"], tool_id),
        )
        self.connection.commit()
        return "Tracker assigned successfully."

    # function to remove the tracker assignment from a tool
    def unassign_tracker_from_tool(self, tool_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT assigned_tracker_id FROM tools WHERE tool_id = ?", (tool_id,))
        row = cursor.fetchone()

        if row is None:
            raise TrackingError("Tool ID not found.")

        assigned_tracker_id = row["assigned_tracker_id"]

        if assigned_tracker_id is None:
            raise TrackingError("Tool has no assigned tracker.")

        cursor.execute(
            "UPDATE trackers SET assigned_tool_id = NULL WHERE tracker_id = ?",
            (assigned_tracker_id,),
        )
        cursor.execute(
            "UPDATE tools SET assigned_tracker_id = NULL WHERE tool_id = ?",
            (tool_id,),
        )
        self.connection.commit()
        return "Tracker unassigned successfully."

    # function to save one tracking event in the database
    def record_tracking_log(
        self,
        tracker_id,
        tool_id,
        latitude,
        longitude,
        battery_level,
        event_type,
        recorded_at,
        notes,
    ):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO tracking_logs (
                tracker_id,
                tool_id,
                latitude,
                longitude,
                battery_level,
                event_type,
                recorded_at,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (tracker_id, tool_id, latitude, longitude, battery_level, event_type, recorded_at, notes),
        )
        self.connection.commit()

    # function to sync a tracker with the simulated provider API
    # every sync updates tracker status and saves a tracking log
    def sync_tracker_location(self, tracker_code, event_type="manual_sync", notes=""):
        tracker = self.get_tracker_status(tracker_code)

        if tracker is None:
            raise TrackingError("Tracker code not found.")

        if tracker["assigned_tool_id"] is None:
            raise TrackingError("Tracker must be assigned to a tool before tracking logs can be saved.")

        provider_data = get_latest_tracker_location(tracker_code)
        sync_time = current_time_text()

        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE trackers
            SET
                status = ?,
                battery_level = ?,
                last_latitude = ?,
                last_longitude = ?,
                last_location_time = ?,
                last_sync_time = ?
            WHERE tracker_code = ?
            """,
            (
                provider_data["status"],
                provider_data["battery_level"],
                provider_data["latitude"],
                provider_data["longitude"],
                provider_data["last_location_time"],
                sync_time,
                tracker_code,
            ),
        )
        self.connection.commit()

        self.record_tracking_log(
            tracker["tracker_id"],
            tracker["assigned_tool_id"],
            provider_data["latitude"],
            provider_data["longitude"],
            provider_data["battery_level"],
            event_type,
            sync_time,
            notes,
        )

        provider_data["tracker_id"] = tracker["tracker_id"]
        provider_data["tool_id"] = tracker["assigned_tool_id"]
        provider_data["last_sync_time"] = sync_time
        return provider_data

    # function to get the tracking status for a tool
    def get_tool_tracking_status(self, tool_id):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT
                tools.tool_id,
                tools.tool_name,
                tools.is_high_value,
                tools.requires_tracking,
                tools.assigned_tracker_id,
                trackers.tracker_code,
                trackers.tracker_type,
                trackers.provider_name,
                trackers.status,
                trackers.battery_level,
                trackers.last_latitude,
                trackers.last_longitude,
                trackers.last_location_time,
                trackers.last_sync_time,
                trackers.notes
            FROM tools
            LEFT JOIN trackers
                ON tools.assigned_tracker_id = trackers.tracker_id
            WHERE tools.tool_id = ?
            """,
            (tool_id,),
        )
        return row_to_dict(cursor.fetchone())

    # function to sync the assigned tracker for a tool
    def sync_tool_location(self, tool_id, event_type="manual_sync", notes=""):
        status = self.get_tool_tracking_status(tool_id)

        if status is None:
            raise TrackingError("Tool ID not found.")

        if status["tracker_code"] is None:
            raise TrackingError("Tool has no assigned tracker.")

        return self.sync_tracker_location(status["tracker_code"], event_type, notes)

    # function to get all tracking logs for a tool
    def get_tracking_history(self, tool_id):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT
                tracking_logs.log_id,
                trackers.tracker_code,
                tracking_logs.tool_id,
                tracking_logs.latitude,
                tracking_logs.longitude,
                tracking_logs.battery_level,
                tracking_logs.event_type,
                tracking_logs.recorded_at,
                tracking_logs.notes
            FROM tracking_logs
            INNER JOIN trackers
                ON tracking_logs.tracker_id = trackers.tracker_id
            WHERE tracking_logs.tool_id = ?
            ORDER BY tracking_logs.log_id
            """,
            (tool_id,),
        )
        rows = cursor.fetchall()
        return [row_to_dict(row) for row in rows]
