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

    cursor.execute("SELECT COUNT(*) FROM app_users")
    user_count = cursor.fetchone()[0]

    if user_count == 0:
        cursor.executemany(
            """
            INSERT INTO app_users (user_id, user_name, user_role, user_password)
            VALUES (?, ?, ?, ?)
            """,
            [
                ("U001", "Alice", "Worker", "1234"),
                ("U002", "Bruno", "Manager", "1234"),
                ("U003", "Carla", "Warehouse Staff", "1234"),
                ("U004", "Daniel", "Administrator", "1234"),
            ],
        )

    cursor.execute("SELECT COUNT(*) FROM tools")
    tool_count = cursor.fetchone()[0]

    if tool_count == 0:
        cursor.executemany(
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
            [
                ("T001", "Lighting Stand", "Lighting", "Standard", "Available", "None", "Warehouse", "Good", 0, 0, None),
                ("T002", "Microphone", "Audio", "Standard", "Available", "None", "Warehouse", "Good", 0, 0, None),
                ("T003", "Digital Mixer", "Audio", "High Value", "Available", "None", "Warehouse", "Good", 1, 1, None),
                ("T004", "Power Cable Reel", "Electrical", "Standard", "Available", "None", "Warehouse", "Good", 0, 0, None),
            ],
        )

    cursor.execute("SELECT COUNT(*) FROM kits")
    kit_count = cursor.fetchone()[0]

    if kit_count == 0:
        cursor.execute(
            "INSERT INTO kits (kit_id, kit_name) VALUES (?, ?)",
            ("K001", "Small Event Audio Kit"),
        )
        cursor.executemany(
            "INSERT INTO kit_tools (kit_id, tool_id) VALUES (?, ?)",
            [("K001", "T002"), ("K001", "T003")],
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
