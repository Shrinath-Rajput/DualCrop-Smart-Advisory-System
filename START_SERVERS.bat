@echo off
REM DualCrop Smart Advisory System - Quick Start Script
REM This script starts both Flask and Node.js servers

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║   DualCrop Smart Advisory System - Quick Start            ║
echo ║   This will open 2 terminal windows                       ║
echo ║   Terminal 1: Flask Server (Port 5000)                   ║
echo ║   Terminal 2: Node.js Server (Port 3000)                 ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Get the project root directory
set PROJECT_DIR=%~dp0

echo 📁 Project Directory: %PROJECT_DIR%
echo.

REM Check if Python exists
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.10+
    pause
    exit /b 1
)

REM Check if Node.js exists
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found! Please install Node.js 16+
    pause
    exit /b 1
)

REM Check if MySQL is running
REM netstat -ano | findstr :3306 >nul 2>&1
REM if %errorlevel% neq 0 (
REM     echo ⚠️  MySQL might not be running. Please start MySQL Server.
REM     echo.
REM )

echo ✅ All prerequisites found!
echo.
echo Starting servers...
echo.

REM Start Flask Server in a new window
echo 🚀 Terminal 1: Starting Flask Server...
start cmd /k "cd /d %PROJECT_DIR% && venv310\Scripts\activate && python app.py"

REM Wait 3 seconds for Flask to start
timeout /t 3 /nobreak

REM Start Node.js Server in a new window
echo 🚀 Terminal 2: Starting Node.js Server...
start cmd /k "cd /d %PROJECT_DIR%Backend && npm start"

REM Wait for Node.js to start
timeout /t 3 /nobreak

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║  ✅ Both servers are starting...                          ║
echo ║                                                           ║
echo ║  📌 Flask Server: http://localhost:5000                  ║
echo ║  📌 Web Interface: http://localhost:3000                 ║
echo ║                                                           ║
echo ║  🎯 Check both terminal windows for any errors           ║
echo ║  ⏳ Wait 10-15 seconds for servers to fully load         ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Open the web browser
timeout /t 5 /nobreak
echo Opening web browser...
start http://localhost:3000

echo.
echo 💡 To stop the servers, close both terminal windows
echo.
pause
