@echo off
setlocal

set "ROOT=%~dp0"
cd /d "%ROOT%"

echo ============================================================
echo  Tool Checkout System - Windows Starter
echo ============================================================
echo.
echo Project folder:
echo   %ROOT%
echo.

echo Checking Python...
set "PYTHON_CMD="
where py >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
) else (
    where python >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
    echo ERROR: Python was not found.
    echo Install Python 3.12+ or 3.13+ from https://www.python.org/downloads/
    echo Make sure "Add Python to PATH" is selected during installation.
    echo.
    pause
    exit /b 1
)

%PYTHON_CMD% --version
if errorlevel 1 (
    echo ERROR: Python is installed but could not be started.
    echo.
    pause
    exit /b 1
)

if not exist "%ROOT%venv\Scripts\activate.bat" (
    echo.
    echo Creating Python virtual environment in venv...
    %PYTHON_CMD% -m venv "%ROOT%venv"
    if errorlevel 1 (
        echo ERROR: Could not create the Python virtual environment.
        echo.
        pause
        exit /b 1
    )
) else (
    echo Python virtual environment already exists.
)

echo.
echo Activating Python virtual environment...
call "%ROOT%venv\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: Could not activate the Python virtual environment.
    echo.
    pause
    exit /b 1
)

echo.
echo Installing backend requirements...
if exist "%ROOT%tool_checkout_backend_sqlite\requirements.txt" (
    python -m pip install -r "%ROOT%tool_checkout_backend_sqlite\requirements.txt"
) else (
    python -m pip install Flask flask-cors
)
if errorlevel 1 (
    echo ERROR: Backend dependency installation failed.
    echo.
    pause
    exit /b 1
)

echo.
echo Checking Node.js and npm...
where node >nul 2>nul
if errorlevel 1 (
    echo ERROR: Node.js was not found.
    echo Install Node.js LTS from https://nodejs.org/
    echo.
    pause
    exit /b 1
)
node --version

where npm >nul 2>nul
if errorlevel 1 (
    echo ERROR: npm was not found.
    echo Install Node.js LTS, which includes npm.
    echo.
    pause
    exit /b 1
)
npm --version

if not exist "%ROOT%frontend\node_modules" (
    echo.
    echo Installing frontend dependencies...
    pushd "%ROOT%frontend"
    npm install
    if errorlevel 1 (
        popd
        echo ERROR: Frontend dependency installation failed.
        echo.
        pause
        exit /b 1
    )
    popd
) else (
    echo Frontend dependencies already installed.
)

echo.
echo ============================================================
echo  Demo Login Credentials
echo ============================================================
echo   Worker:    U001 / 1234
echo   Manager:   U002 / 1234
echo   Warehouse: U003 / 1234
echo   Admin:     U004 / 1234
echo.
echo Local URLs:
echo   Backend:  http://localhost:5000
echo   Frontend: http://localhost:5173
echo.
echo Starting backend and frontend in separate terminal windows...
echo Keep both terminal windows open while using the system.
echo.

start "Tool Checkout Backend - Flask API" cmd /k "cd /d ^"%ROOT%^" && call ^"%ROOT%venv\Scripts\activate.bat^" && python api_server.py"

timeout /t 3 /nobreak >nul

start "Tool Checkout Frontend - React Vite" cmd /k "cd /d ^"%ROOT%frontend^" && npm run dev"

timeout /t 3 /nobreak >nul

echo Opening frontend in browser...
start "" "http://localhost:5173"

echo.
echo Setup complete. This window can be closed after the browser opens.
echo Backend and frontend terminals must remain open.
echo.
pause
