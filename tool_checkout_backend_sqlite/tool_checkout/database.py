from pathlib import Path
import sqlite3


# database file used by the backend
# this file is created automatically when the project runs
DATABASE_NAME = "app_database.db"


# function to return the database path
# the database is stored in the project folder and is not tied to one computer
def get_database_path():
    project_folder = Path(__file__).parent.parent
    return project_folder / DATABASE_NAME


# function to connect to the SQLite database
# sqlite3 creates the database file automatically if it does not exist
def connect_to_database(database_path=None):
    if database_path is None:
        database_path = get_database_path()

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


# function to check if a table has a specific column
def column_exists(connection, table_name, column_name):
    cursor = connection.cursor()
    cursor.execute("PRAGMA table_info(" + table_name + ")")
    columns = cursor.fetchall()

    for column in columns:
        if column["name"] == column_name:
            return True

    return False


# function to add a column only when it does not exist yet
def add_column_if_missing(connection, table_name, column_name, column_definition):
    if not column_exists(connection, table_name, column_name):
        connection.execute(
            "ALTER TABLE " + table_name + " ADD COLUMN " + column_name + " " + column_definition
        )
        connection.commit()


# function to create all required tables
# CREATE TABLE IF NOT EXISTS keeps existing data safe when the app starts again
def create_tables(connection):
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS app_users (
            user_id TEXT PRIMARY KEY,
            user_name TEXT NOT NULL,
            user_role TEXT NOT NULL,
            user_password TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tools (
            tool_id TEXT PRIMARY KEY,
            tool_name TEXT NOT NULL,
            category TEXT NOT NULL,
            value_level TEXT NOT NULL,
            tool_status TEXT NOT NULL,
            borrowed_by TEXT NOT NULL,
            tool_location TEXT NOT NULL,
            tool_condition TEXT NOT NULL,
            is_high_value INTEGER NOT NULL DEFAULT 0,
            requires_tracking INTEGER NOT NULL DEFAULT 0,
            assigned_tracker_id INTEGER
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS kits (
            kit_id TEXT PRIMARY KEY,
            kit_name TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS kit_tools (
            kit_id TEXT NOT NULL,
            tool_id TEXT NOT NULL,
            PRIMARY KEY (kit_id, tool_id),
            FOREIGN KEY (kit_id) REFERENCES kits(kit_id),
            FOREIGN KEY (tool_id) REFERENCES tools(tool_id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            action_date TEXT NOT NULL,
            tool_location TEXT NOT NULL,
            condition_text TEXT NOT NULL,
            approved_by TEXT NOT NULL,
            FOREIGN KEY (tool_id) REFERENCES tools(tool_id),
            FOREIGN KEY (user_id) REFERENCES app_users(user_id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_text TEXT NOT NULL,
            action_date TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trackers (
            tracker_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracker_code TEXT NOT NULL UNIQUE,
            tracker_type TEXT NOT NULL,
            provider_name TEXT NOT NULL,
            assigned_tool_id TEXT,
            status TEXT NOT NULL,
            battery_level INTEGER,
            last_latitude REAL,
            last_longitude REAL,
            last_location_time TEXT,
            last_sync_time TEXT,
            notes TEXT,
            FOREIGN KEY (assigned_tool_id) REFERENCES tools(tool_id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tracking_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracker_id INTEGER NOT NULL,
            tool_id TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            battery_level INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            recorded_at TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (tracker_id) REFERENCES trackers(tracker_id),
            FOREIGN KEY (tool_id) REFERENCES tools(tool_id)
        )
        """
    )

    connection.commit()
    migrate_existing_database(connection)


# function to update older SQLite databases with new tracking columns
def migrate_existing_database(connection):
    add_column_if_missing(connection, "tools", "is_high_value", "INTEGER NOT NULL DEFAULT 0")
    add_column_if_missing(connection, "tools", "requires_tracking", "INTEGER NOT NULL DEFAULT 0")
    add_column_if_missing(connection, "tools", "assigned_tracker_id", "INTEGER")

    cursor = connection.cursor()
    cursor.execute(
        """
        UPDATE tools
        SET is_high_value = 1,
            requires_tracking = 1
        WHERE value_level = 'High Value'
        """
    )
    cursor.execute(
        """
        UPDATE tools
        SET is_high_value = 0,
            requires_tracking = 0
        WHERE value_level <> 'High Value'
        """
    )
    connection.commit()


# function to add sample records only when the database is empty
# this gives the demo users, tools, and one kit to work with
def seed_sample_data(connection):
    cursor = connection.cursor()

    cursor.executemany(
        """
        INSERT INTO app_users (user_id, user_name, user_role, user_password)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            user_name = excluded.user_name,
            user_role = excluded.user_role,
            user_password = excluded.user_password
        """,
        [
            ("U001", "Alice Martin", "Worker", "1234"),
            ("U002", "Bruno Silva", "Manager", "1234"),
            ("U003", "Carla Nguyen", "Warehouse Staff", "1234"),
            ("U004", "Daniel Reed", "Administrator", "1234"),
        ],
    )

    cursor.executemany(
        """
        INSERT OR IGNORE INTO app_users (user_id, user_name, user_role, user_password)
        VALUES (?, ?, ?, ?)
        """,
        [
            ("U005", "Maya Chen", "Worker", "1234"),
            ("U006", "Ethan Brooks", "Worker", "1234"),
            ("U007", "Priya Shah", "Warehouse Staff", "1234"),
        ],
    )

    cursor.executemany(
        """
        INSERT OR IGNORE INTO tools (
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
        [
            ("T101", "Cordless Drill", "Power Tools", "Standard", "Available", "None", "Warehouse Bay A", "Good", 0, 0, None),
            ("T102", "Laser Level", "Surveying", "High Value", "Checked Out", "U001", "ICC Sydney - Hall 3", "Good", 1, 1, None),
            ("T103", "Truss Hammer", "Rigging", "Standard", "Available", "None", "Rigging Cage", "Good", 0, 0, None),
            ("T104", "Lighting Console", "Lighting", "High Value", "Checked Out", "U002", "Grand Ballroom FOH", "Good", 1, 1, None),
            ("T105", "Audio Mixer", "Audio", "High Value", "Under Maintenance", "None", "Maintenance Bench", "Damaged", 1, 1, None),
            ("T106", "Cable Tester", "Electrical", "Standard", "Available", "None", "Warehouse Bay B", "Good", 0, 0, None),
            ("T107", "Impact Driver", "Power Tools", "Standard", "Flagged", "None", "Returns Desk", "Damaged", 0, 0, None),
            ("T108", "Rigging Kit", "Rigging", "Standard", "Available", "None", "Rigging Cage", "Good", 0, 0, None),
            ("T109", "LED Panel", "Lighting", "High Value", "Available", "None", "Lighting Store", "Good", 1, 1, None),
            ("T110", "Safety Harness", "Safety", "Standard", "Available", "None", "Safety Locker", "Good", 0, 0, None),
            ("T111", "Power Distribution Box", "Electrical", "High Value", "Checked Out", "U005", "Loading Dock B", "Good", 1, 1, None),
            ("T112", "Camera Scanner", "Inventory", "Standard", "Available", "None", "Warehouse Office", "Good", 0, 0, None),
        ],
    )

    cursor.executemany(
        """
        INSERT OR IGNORE INTO trackers (
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
        [
            ("GPS-001", "GPS/GNSS Cellular Asset Tracker", "Simulated Asset Provider", "T102", "active", 82, -33.8688, 151.2093, "2026-05-05 08:45:00", "2026-05-05 08:46:00", "Attached to Laser Level case"),
            ("GPS-002", "GPS/GNSS Cellular Asset Tracker", "Simulated Asset Provider", "T104", "active", 76, -33.8727, 151.2057, "2026-05-05 09:15:00", "2026-05-05 09:16:00", "Console road case tracker"),
            ("GPS-003", "GPS/GNSS Cellular Asset Tracker", "Simulated Asset Provider", "T109", "active", 91, -33.8568, 151.2153, "2026-05-05 07:58:00", "2026-05-05 08:00:00", "LED panel flight case"),
            ("GPS-004", "GPS/GNSS Cellular Asset Tracker", "Simulated Asset Provider", "T111", "active", 69, -33.8615, 151.2114, "2026-05-05 10:05:00", "2026-05-05 10:06:00", "Power distro asset tracker"),
        ],
    )

    cursor.execute("SELECT tracker_id, tracker_code, assigned_tool_id FROM trackers WHERE tracker_code IN ('GPS-001', 'GPS-002', 'GPS-003', 'GPS-004')")
    tracker_rows = cursor.fetchall()
    for tracker in tracker_rows:
        cursor.execute(
            "UPDATE tools SET assigned_tracker_id = ? WHERE tool_id = ? AND assigned_tracker_id IS NULL",
            (tracker["tracker_id"], tracker["assigned_tool_id"]),
        )

    cursor.executemany(
        "INSERT OR IGNORE INTO kits (kit_id, kit_name) VALUES (?, ?)",
        [
            ("K001", "Small Event Audio Kit"),
            ("K101", "Corporate AV Checkout Kit"),
            ("K102", "Rigging Safety Inspection Kit"),
            ("K103", "Outdoor Power Distribution Kit"),
        ],
    )
    cursor.executemany(
        "INSERT OR IGNORE INTO kit_tools (kit_id, tool_id) VALUES (?, ?)",
        [
            ("K001", "T002"), ("K001", "T003"),
            ("K101", "T104"), ("K101", "T105"), ("K101", "T106"),
            ("K102", "T103"), ("K102", "T108"), ("K102", "T110"),
            ("K103", "T106"), ("K103", "T111"), ("K103", "T101"),
        ],
    )

    cursor.executemany(
        """
        INSERT INTO transactions (tool_id, user_id, action_type, action_date, tool_location, condition_text, approved_by)
        SELECT ?, ?, ?, ?, ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM transactions WHERE tool_id = ? AND action_type = ? AND action_date = ?
        )
        """,
        [
            ("T102", "U001", "Checkout", "2026-05-04 14:20:00", "ICC Sydney - Hall 3", "Good", "U002", "T102", "Checkout", "2026-05-04 14:20:00"),
            ("T104", "U002", "Checkout", "2026-05-05 08:10:00", "Grand Ballroom FOH", "Good", "U004", "T104", "Checkout", "2026-05-05 08:10:00"),
            ("T111", "U005", "Checkout", "2026-05-05 09:35:00", "Loading Dock B", "Good", "U002", "T111", "Checkout", "2026-05-05 09:35:00"),
            ("T107", "U003", "Return", "2026-05-05 10:40:00", "Warehouse", "Damaged", "None", "T107", "Return", "2026-05-05 10:40:00"),
        ],
    )

    cursor.executemany(
        """
        INSERT INTO tracking_logs (tracker_id, tool_id, latitude, longitude, battery_level, event_type, recorded_at, notes)
        SELECT trackers.tracker_id, ?, ?, ?, ?, ?, ?, ?
        FROM trackers
        WHERE trackers.tracker_code = ?
          AND NOT EXISTS (
              SELECT 1 FROM tracking_logs WHERE tool_id = ? AND event_type = ? AND recorded_at = ?
          )
        """,
        [
            ("T102", -33.8688, 151.2093, 82, "scheduled_sync", "2026-05-05 08:46:00", "Asset case remained at event hall storage.", "GPS-001", "T102", "scheduled_sync", "2026-05-05 08:46:00"),
            ("T104", -33.8727, 151.2057, 76, "manual_sync", "2026-05-05 09:16:00", "Console road case located at FOH.", "GPS-002", "T104", "manual_sync", "2026-05-05 09:16:00"),
            ("T109", -33.8568, 151.2153, 91, "scheduled_sync", "2026-05-05 08:00:00", "LED panel flight case in lighting store.", "GPS-003", "T109", "scheduled_sync", "2026-05-05 08:00:00"),
            ("T111", -33.8615, 151.2114, 69, "checkout_sync", "2026-05-05 10:06:00", "Power distribution box checked at loading dock.", "GPS-004", "T111", "checkout_sync", "2026-05-05 10:06:00"),
        ],
    )

    cursor.executemany(
        """
        INSERT INTO history (action_text, action_date)
        SELECT ?, ?
        WHERE NOT EXISTS (SELECT 1 FROM history WHERE action_text = ? AND action_date = ?)
        """,
        [
            ("Alice Martin checked out Laser Level", "2026-05-04 14:20:00", "Alice Martin checked out Laser Level", "2026-05-04 14:20:00"),
            ("Bruno Silva approved checkout for Lighting Console", "2026-05-05 08:09:00", "Bruno Silva approved checkout for Lighting Console", "2026-05-05 08:09:00"),
            ("Bruno Silva checked out Lighting Console", "2026-05-05 08:10:00", "Bruno Silva checked out Lighting Console", "2026-05-05 08:10:00"),
            ("Carla Nguyen verified kit Rigging Safety Inspection Kit", "2026-05-05 09:00:00", "Carla Nguyen verified kit Rigging Safety Inspection Kit", "2026-05-05 09:00:00"),
            ("Maya Chen checked out Power Distribution Box", "2026-05-05 09:35:00", "Maya Chen checked out Power Distribution Box", "2026-05-05 09:35:00"),
            ("Carla Nguyen returned Impact Driver as Damaged", "2026-05-05 10:40:00", "Carla Nguyen returned Impact Driver as Damaged", "2026-05-05 10:40:00"),
            ("Daniel Reed sent tool Audio Mixer to maintenance", "2026-05-05 11:05:00", "Daniel Reed sent tool Audio Mixer to maintenance", "2026-05-05 11:05:00"),
            ("Bruno Silva synced tracker location for Lighting Console", "2026-05-05 11:30:00", "Bruno Silva synced tracker location for Lighting Console", "2026-05-05 11:30:00"),
        ],
    )

    connection.commit()


# function to prepare the database for use
# it connects to SQLite, creates tables, loads sample data, and returns the connection
def initialize_database(database_path=None):
    connection = connect_to_database(database_path)
    create_tables(connection)
    seed_sample_data(connection)
    return connection


# function to close the database safely
def close_connection(connection):
    if connection is not None:
        connection.close()
