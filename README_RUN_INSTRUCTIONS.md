# Tool Checkout System - Run Instructions

These instructions are for running the project locally on Windows for assessment/demo use.

## Required Software

- Python 3.12+ or 3.13+
- Node.js LTS
- npm, included with Node.js

The project uses the existing stack:

- React/Vite frontend
- Python backend
- Flask REST API
- SQLite database

## Run With `start.bat`

1. Open the project root folder in File Explorer.
2. Double-click `start.bat`.
3. Wait while it checks Python, creates `venv` if needed, installs backend requirements, checks Node/npm, and installs frontend dependencies if needed.
4. Two terminal windows will open:
   - Flask backend at `http://localhost:5000`
   - React/Vite frontend at `http://localhost:5173`
5. The browser should open automatically at `http://localhost:5173`.

Keep both backend and frontend terminal windows open while using the system.

## Manual Run If `start.bat` Fails

From the project root folder, run:

```bat
python -m venv venv
venv\Scripts\activate
python -m pip install -r tool_checkout_backend_sqlite\requirements.txt
python api_server.py
```

Leave that backend terminal open. Then open a second terminal and run:

```bat
cd frontend
npm install
npm run dev
```

Open the frontend in your browser:

```text
http://localhost:5173
```

## Local URLs

- Backend: `http://localhost:5000`
- Frontend: `http://localhost:5173`

## Demo Credentials

- Worker: `U001 / 1234`
- Manager: `U002 / 1234`
- Warehouse: `U003 / 1234`
- Admin: `U004 / 1234`
