@echo off
echo ========================================
echo AI Learning Game - Build Executable
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Building executable...
python -m PyInstaller --onefile --windowed --name "AI_Learning_Game" --add-data "TSU.png;." ai_learning_app.py

echo.
echo ========================================
echo Build complete!
echo Executable is in: dist\AI_Learning_Game.exe
echo ========================================
pause
