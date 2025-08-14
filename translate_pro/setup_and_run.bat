@echo off
echo ========================================
echo   TranslatePro - Setup and Run Script
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

echo Python found. Checking version...
python --version

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
) else (
    echo Virtual environment already exists.
)

:: Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

:: Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install requirements
echo.
echo Installing requirements...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install requirements
        pause
        exit /b 1
    )
) else (
    echo requirements.txt not found, installing PySide6 directly...
    pip install PySide6>=6.4.0
    if errorlevel 1 (
        echo ERROR: Failed to install PySide6
        pause
        exit /b 1
    )
)

echo.
echo Installation completed successfully!
echo.

:: Ask user which version to run
echo Which version would you like to run?
echo 1. Original version (app_main.py)
echo 2. Optimized version (app_main_optimized.py) - 400x300 compact
echo 3. Simple version (app_simple.py) - No recursion issues
echo 4. Mini version (app_mini.py) - Ultra compact 400x300
echo.
set /p choice="Enter your choice (1, 2, 3, or 4): "

if "%choice%"=="1" (
    if exist "app_main.py" (
        echo.
        echo Running original version...
        echo ========================================
        python app_main.py
    ) else (
        echo ERROR: app_main.py not found!
        pause
        exit /b 1
    )
) else if "%choice%"=="2" (
    if exist "app_main_optimized.py" (
        echo.
        echo Running optimized version...
        echo ========================================
        python app_main_optimized.py
        if errorlevel 1 (
            echo.
            echo ERROR: Optimized version failed. Trying original version...
            if exist "app_main.py" (
                python app_main.py
            ) else (
                echo ERROR: Original version not found either!
                pause
                exit /b 1
            )
        )
    ) else (
        echo ERROR: app_main_optimized.py not found!
        pause
        exit /b 1
    )
) else if "%choice%"=="3" (
    if exist "app_simple.py" (
        echo.
        echo Running simple version...
        echo ========================================
        python app_simple.py
    ) else (
        echo ERROR: app_simple.py not found!
        pause
        exit /b 1
    )
) else if "%choice%"=="4" (
    if exist "app_mini.py" (
        echo.
        echo Running mini version...
        echo ========================================
        python app_mini.py
    ) else (
        echo ERROR: app_mini.py not found!
        pause
        exit /b 1
    )
) else (
    echo Invalid choice. Running mini version by default...
    echo.
    echo Running mini version...
    echo ========================================
    python app_mini.py
)

echo.
echo Application closed.
pause
