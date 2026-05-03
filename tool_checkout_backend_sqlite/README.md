# Tool Checkout and Control System Backend

This project is the backend/core-logic version of the Tool Checkout and Control System.
The frontend has been removed from the active code so another developer can build a new interface later.

The backend uses SQLite through Python's built-in `sqlite3` module. It does not require Microsoft Access, Access Runtime, ODBC, `pyodbc`, or GPS hardware.

## Project Structure

```text
.
|-- main.py
|-- requirements.txt
|-- README.md
`-- tool_checkout/
    |-- __init__.py
    |-- database.py
    |-- services.py
    `-- tracking_service.py
```

## Main Files

- `tool_checkout/database.py` creates the SQLite connection, creates tables, loads sample data, and closes the connection safely.
- `tool_checkout/services.py` contains the main business rules for login, tools, checkout, return, kits, reports, tracking assignment, and tracking checks.
- `tool_checkout/tracking_service.py` contains the simulated GPS/GNSS provider logic and tracking log functions.
- `main.py` is a simple command-line demo that proves the backend works without a frontend.
- `requirements.txt` does not include SQLite because `sqlite3` is built into Python.

## How To Run

Run the project from the project folder:

```bash
python main.py
```

When the program starts, choose:

```text
1. Run automatic backend demo
2. Run interactive CLI demo
```

Sample login details:

```text
U001 / 1234 = Worker
U002 / 1234 = Manager
U003 / 1234 = Warehouse Staff
U004 / 1234 = Administrator
```

## SQLite Database

The SQLite database file is called:

```text
app_database.db
```

The database is created automatically when `main.py` runs.
If the database file does not exist, SQLite creates it and `database.py` creates the required tables.

Tables created by the backend:

- `app_users`
- `tools`
- `kits`
- `kit_tools`
- `transactions`
- `history`
- `trackers`
- `tracking_logs`

The local database file is ignored by Git through `.gitignore`, so each developer can create their own database locally.

## High-Value Tool Tracking

The tracking feature is designed for high-value equipment only. It is for equipment recovery, loss prevention, and investigation of missing or overdue assets. It is not designed for employee monitoring.

High-value tools can be marked as requiring a GPS/GNSS asset tracker before checkout. The intended tracker type is a GPS/GNSS asset tracker with cellular connectivity, not a Bluetooth-only tag or Apple AirTag-style solution.

In a real implementation, the tracker would send location data to a provider cloud platform. The backend would then call the provider API to retrieve the latest location. In this prototype, `tracking_service.py` simulates the provider API response so the system can be tested without hardware.

Tracking checks should be limited to authorised managers or administrators. The backend enforces this rule in the tracking-related service methods.

## Tracking Database Records

The `trackers` table stores the current tracker state, including:

- tracker code
- tracker type
- provider name
- assigned tool
- status
- battery level
- last latitude and longitude
- last location time
- last sync time
- notes

The `tracking_logs` table stores every tracking check, including:

- tracker ID
- tool ID
- latitude and longitude
- battery level
- event type
- recorded time
- notes

Every location sync creates a log entry so tracking checks are auditable.

## Connecting A Future Frontend

A future frontend should import and use the backend services instead of writing business rules directly.

Example:

```python
from tool_checkout.database import initialize_database
from tool_checkout.services import ToolCheckoutService

connection = initialize_database()
service = ToolCheckoutService(connection)

manager = service.authenticate_user("U002", "1234")
worker = service.authenticate_user("U001", "1234")

service.create_tracker(
    manager,
    "GPS-001",
    "GPS/GNSS Cellular Asset Tracker",
    "Simulated GNSS Provider",
)

service.mark_tool_as_high_value(manager, "T003", requires_tracking=True)
service.assign_tracker_to_tool(manager, "T003", "GPS-001")
service.checkout_tool(worker, "T003", "Event Site A", manager["user_id"])
location = service.sync_tool_location(manager, "T003")
```

Useful backend functions for a frontend:

- `create_tracker(...)`
- `assign_tracker_to_tool(...)`
- `unassign_tracker_from_tool(...)`
- `mark_tool_as_high_value(...)`
- `get_tool_tracking_status(...)`
- `sync_tool_location(...)`
- `get_tracking_history(...)`

This keeps the frontend separate from the database and business rules.
