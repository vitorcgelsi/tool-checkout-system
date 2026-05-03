@echo off
echo ================================================
echo  Tool Checkout System - Starting...
echo ================================================
echo.

:: Start Flask API server
echo Starting API server on http://localhost:5000 ...
start /B cmd /c "cd /d %~dp0 && venv\Scripts\activate && python api_server.py"

:: Wait for API to start
timeout /t 3 /nobreak >nul

:: Start React dev server
echo Starting frontend on http://localhost:5173 ...
cd /d %~dp0frontend
start /B cmd /c "npm run dev"

echo.
echo ================================================
echo  System is starting up!
echo  API:      http://localhost:5000
echo  Frontend: http://localhost:5173
echo ================================================
echo.
echo Demo Credentials:
echo   Worker:    U001 / 1234
echo   Manager:   U002 / 1234
echo   Warehouse: U003 / 1234
echo   Admin:     U004 / 1234
echo.
pause
