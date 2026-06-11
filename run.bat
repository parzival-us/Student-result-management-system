@echo off
echo Checking Student Result Management System setup...
python check_setup.py
if %errorlevel% neq 0 (
    echo.
    echo Setup check failed. Please install dependencies manually:
    echo pip install -r requirements.txt
    pause
    exit /b 1
)
echo.
echo Starting application...
python main.py
