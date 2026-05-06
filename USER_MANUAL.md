# Tool Checkout System - User Manual

## 1. System Overview

The Tool Checkout System is a prototype inventory management application designed for event production environments. Its purpose is to support the checkout, return, tracking, and reporting of tools and equipment used by staff in operational workflows.

The system includes:

- a React/Vite frontend for user interaction
- a Python backend exposing a Flask REST API
- a SQLite database for local data storage
- simulated GPS/GNSS asset tracking for high-value tools only

This prototype is intended for local demonstration and academic assessment use.

## 2. Required Software Summary

The following software is required to run the system on Windows:

- Python 3.12+ or 3.13+
- Node.js LTS
- npm, included with Node.js

## 3. Starting the System With `start.bat`

1. Open the project root folder.
2. Double-click `start.bat`.
3. The script will:
   - check that Python is available
   - create a `venv` virtual environment if it does not already exist
   - activate the virtual environment
   - install backend requirements
   - check that Node.js and npm are available
   - install frontend dependencies if needed
   - start the backend and frontend in separate terminal windows
   - open the frontend in the default browser
4. Wait for the browser to open `http://localhost:5173`.

Important:
- The backend terminal and frontend terminal must remain open while using the system.
- If the frontend does not open automatically, open it manually at `http://localhost:5173`.

## 4. Local URLs

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:5000`

## 5. Demo Login Credentials

Use one of the following demonstration accounts:

- Worker: `U001 / 1234`
- Manager: `U002 / 1234`
- Warehouse: `U003 / 1234`
- Admin: `U004 / 1234`

## 6. User Roles

The system includes four user roles with different access levels.

### Worker

Workers can:

- view the dashboard
- check out tools
- return tools

### Manager

Managers can:

- view the dashboard
- manage the Tool Registry
- approve high-value tool checkouts
- check out and return tools
- verify kits
- access high-value tracking
- view reports and system history

### Warehouse Staff

Warehouse Staff can:

- view the dashboard
- check out tools
- return tools
- verify kits

### Administrator

Administrators can:

- access all Manager functions
- manage users

## 7. Logging In

1. Open the frontend in the browser.
2. Enter a valid staff ID and password.
3. Select the appropriate demonstration account for the workflow you want to view.
4. After login, the system opens the dashboard.

### Forgotten ID or password

If a user forgets their staff ID or password, the login screen provides a `Forgot ID or password?` help option.

In this prototype, recovery is handled through Administrator support rather than a self-service reset feature. The expected process is:

1. Select the help option on the login screen.
2. Contact an Administrator.
3. The Administrator confirms the account details or resets the password as required.

For assessment and demonstration use, the published demo credentials may also be used directly.

## 8. Dashboard Guide

The dashboard provides a summary of current system status.

Typical dashboard content includes:

- total tools
- available tools
- checked-out tools
- tools under maintenance
- flagged tools
- tracked high-value tools
- recent activity history

For some users, the dashboard also shows current assigned checkouts or tools that need attention.

Use the dashboard as the main starting point to understand the current state of the inventory.

## 9. Tool Registry Guide

The Tool Registry is available to Managers and Administrators.

The Tool Registry allows users to:

- view all registered tools
- search by tool ID, name, category, or location
- review status, condition, location, and assignment
- identify high-value tools
- identify whether tracking is required
- register new tools
- flag tools
- send flagged tools to maintenance

Typical fields displayed include:

- tool ID
- tool name
- category
- status
- assigned user
- location
- condition
- high-value status
- tracking requirement

This page is intended for inventory oversight rather than checkout processing.

## 10. Checkout Process Guide

The Checkout screen supports the issue of tools to staff for operational use.

### Standard Checkout Workflow

1. Open the `Check Out` page.
2. Enter the tool ID and search for the asset.
3. Review the tool details shown on screen.
4. Confirm that the tool is available.
5. Enter the checkout location.
6. Select or confirm the checkout action.

### High-Value Checkout Workflow

For high-value tools, the system may require:

- a manager approval ID
- an assigned GPS/GNSS tracker if tracking is required

If a required tracker has not been assigned, checkout will not proceed until that condition is met.

The interface is designed to make this validation visible before final confirmation.

## 11. Return Process Guide

The Return screen is used to process returned tools and record their condition.

### Return Workflow

1. Open the `Return` page.
2. Search for the checked-out tool by tool ID.
3. Review the current borrower and location details.
4. Select the return condition:
   - `Good`
   - `Damaged`
5. Confirm the return.

### Return Outcomes

- If the tool is returned as `Good`, it becomes available again.
- If the tool is returned as `Damaged`, it is flagged for review and may later be sent to maintenance by an authorised user.

## 12. Kit Verification Guide

The Kit Verification area is used to confirm that grouped equipment sets are complete before dispatch.

Each kit screen may show:

- kit name
- kit ID
- required items
- current present or missing status
- availability of each item
- overall verification result

### Kit Verification Workflow

1. Open the `Kits` page.
2. Review the listed kit contents.
3. Select `Verify Kit`.
4. Review the result.

If all items are available, the kit is ready for dispatch. If one or more items are unavailable, the system indicates that the kit is not ready.

## 13. High-Value Tracking Guide

The High-Value Tracking page is available to Managers and Administrators.

This page is used for asset protection and loss prevention. It is important to note that this tracking feature applies to equipment only, not to people or employee movement.

The tracking screen may display:

- tool name and ID
- tracker code
- last known location
- battery level
- last sync time
- tracker status
- location summary or map placeholder
- tracking history events

### Tracking Workflow

1. Open the `Tracking` page.
2. Select a high-value tracked asset from the list.
3. Review current tracker details.
4. Use the sync action to request the latest simulated GPS/GNSS update.
5. Review the tracking history table.

This feature uses a simulated tracking provider for demonstration purposes.

## 14. Reports and History Guide

The Reports area is available to Managers and Administrators.

This section provides report-style views of activity and equipment status.

It may include:

- overall inventory overview
- checkout records
- return records
- maintenance-related records
- tracking sync records
- flagged or maintenance tools

Use this area to review how the system has been used over time and to support demonstration of audit and oversight features.

## 15. Common Issues

### "Failed to fetch"

This usually means the frontend cannot contact the backend API.

Check the following:

1. Confirm that the backend terminal window is still open.
2. Confirm that the backend is running on `http://localhost:5000`.
3. Confirm that the frontend terminal window is still open.
4. If `start.bat` was closed before the service windows opened correctly, restart the system.
5. If necessary, run the backend and frontend manually using the instructions in `README_RUN_INSTRUCTIONS.md`.

### Login does not work

Check that:

- the system is fully loaded
- the correct credentials are being used
- the backend is running

If the user has forgotten their ID or password, use the login screen help option and contact an Administrator.

### Frontend page does not load

Check that:

- the frontend terminal is still open
- Vite is running on `http://localhost:5173`
- Node.js dependencies installed successfully

### Backend does not start

Check that:

- Python is installed
- the virtual environment was created successfully
- backend dependencies were installed successfully

## 16. Prototype Limitations

This project is a prototype intended for assessment and demonstration, so several limitations apply.

Current limitations include:

- the tracking provider is simulated rather than connected to a real hardware service
- the system is intended for local execution rather than production deployment
- the database is local SQLite storage rather than a multi-user enterprise database
- authentication is demonstration-focused and not production-grade security
- forgotten ID and password recovery is handled through Administrator support rather than a full self-service recovery workflow
- browser sessions and service startup depend on both local backend and frontend processes remaining open
- sample data is designed to support demonstration rather than live operational use

## 17. Summary

The Tool Checkout System demonstrates a local prototype for managing event production tools, including role-based workflows, tool checkout and return, kit verification, high-value asset tracking, and reporting. For assessment use, the recommended startup method is `start.bat`, followed by login with one of the provided demonstration accounts.
