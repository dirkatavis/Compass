@echo off
REM Compass Automation Quick Setup (Windows)
REM
REM This is the simplest way to set up the Compass automation environment.
REM It runs the Python setup script with basic error handling.

echo.
echo ========================================
echo Compass Automation Quick Setup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8+ and add it to your PATH.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python found. Running setup script...
echo.

REM Run the Python setup script
python setup.py
if errorlevel 1 (
    echo.
    echo ERROR: Setup script failed. See errors above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed! 
echo ========================================
echo.
echo Next step: Activate your virtual environment with:
echo    .\venv\Scripts\Activate.ps1
echo.
echo Then update your credentials in config\config.json
echo.
pause