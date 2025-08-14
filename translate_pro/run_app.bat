@echo off
echo ========================================
echo      TranslatePro - Quick Run
echo ========================================

:: Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo Please run setup_and_run.bat first to create the environment.
    pause
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Check if optimized version exists, otherwise run original
if exist "app_main_optimized.py" (
    echo Running optimized version...
    python app_main_optimized.py
) else if exist "app_main.py" (
    echo Running original version...
    python app_main.py
) else (
    echo ERROR: No Python application file found!
    echo Looking for: app_main_optimized.py or app_main.py
    pause
    exit /b 1
)

echo.
echo Application closed.
pause
