@echo off
SETLOCAL

:: --- CONFIGURATION ---
:: Replace this with your actual Conda environment name
SET CONDA_ENV_NAME=ai-cover-letter-generator

:: Get the directory where this script is located
SET "SCRIPT_DIR=%~dp0"
CD /D "%SCRIPT_DIR%"

echo ==================================================
echo   Starting Smart Cover Letter Generator...
echo ==================================================
echo.

:: 1. Activate Conda Environment
:: We use 'call' to ensure the script continues after activation
echo [1/3] Activating Conda environment: %CONDA_ENV_NAME%...
call conda activate %CONDA_ENV_NAME%
IF %ERRORLEVEL% NEQ 0 (
    echo Error: Could not activate Conda environment '%CONDA_ENV_NAME%'.
    echo Make sure Conda is in your PATH and the environment exists.
    pause
    exit /b
)

:: 2. Start Backend (in a separate window)
echo [2/3] Launching FastAPI Backend...
start "FastAPI Backend" cmd /k "conda activate %CONDA_ENV_NAME% && uvicorn backend.main:app --reload --port 8000"

:: Wait a few seconds for the backend to initialize
timeout /t 3 /nobreak >nul

:: 3. Start Frontend (in the current window)
echo [3/3] Launching Streamlit Frontend...
streamlit run frontend/app.py

:: If Streamlit closes, the script ends
echo.
echo Application closed.
pause