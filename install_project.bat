@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ===============================================
echo U RESCUE - install dependencies and prepare data
echo ===============================================

where py >nul 2>&1
if errorlevel 1 (
    where python >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python 3.10 or newer was not found. Install Python and add it to PATH.
        pause
        exit /b 1
    )
    set "PYTHON_CMD=python"
) else (
    set "PYTHON_CMD=py -3"
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 goto :failed
)

set "VENV_PY=%CD%\.venv\Scripts\python.exe"
echo Installing Python packages...
"%VENV_PY%" -m pip install --upgrade pip
if errorlevel 1 goto :failed
"%VENV_PY%" -m pip install -r requirements.txt
if errorlevel 1 goto :failed

if not defined URESCUE_DATA_DIR if exist "%USERPROFILE%\OneDrive\Desktop\DIGITALTWIN_U_RESCUE\U_RESCUE\Datasets" (
    set "URESCUE_DATA_DIR=%USERPROFILE%\OneDrive\Desktop\DIGITALTWIN_U_RESCUE\U_RESCUE\Datasets"
)
if not defined URESCUE_DATA_DIR (
    echo ERROR: Could not find the dataset at the expected OneDrive Desktop path.
    echo Set URESCUE_DATA_DIR to the folder containing 01_Terrain and run this file again.
    pause
    exit /b 1
)
echo Dataset folder: "%URESCUE_DATA_DIR%"

echo Processing terrain tiles...
"%VENV_PY%" scripts\process_terrain.py
if errorlevel 1 goto :failed

if exist "data\osm_roads.json" (
    echo Cached road extract found; skipping road download.
) else (
    echo Trying to download the OpenStreetMap road extract.
    echo The public service may be busy; the installer will continue if it fails.
    "%VENV_PY%" scripts\fetch_roads.py
    if errorlevel 1 echo WARNING: Road download failed. Retry later with this command: .venv\Scripts\python.exe scripts\fetch_roads.py
)

echo.
echo Installation and local terrain preparation are complete.
echo Start the application with start_project.bat
echo If road retrieval failed, routes will remain unavailable until it succeeds.
pause
exit /b 0

:failed
echo.
echo ERROR: Installation or terrain processing failed. Review the message above.
pause
exit /b 1
