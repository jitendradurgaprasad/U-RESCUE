@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Project dependencies are not installed. Run install_project.bat first.
    pause
    exit /b 1
)

if not defined URESCUE_DATA_DIR if exist "%USERPROFILE%\OneDrive\Desktop\DIGITALTWIN_U_RESCUE\U_RESCUE\Datasets" (
    set "URESCUE_DATA_DIR=%USERPROFILE%\OneDrive\Desktop\DIGITALTWIN_U_RESCUE\U_RESCUE\Datasets"
)
if not defined URESCUE_DATA_DIR (
    echo ERROR: Dataset folder not found. Set URESCUE_DATA_DIR before starting.
    pause
    exit /b 1
)

if not exist "data\processed\terrain_risk_grid.npz" (
    echo Terrain output is missing. Processing the supplied HGT tiles now...
    ".venv\Scripts\python.exe" scripts\process_terrain.py
    if errorlevel 1 goto :failed
)

echo Opening U RESCUE at http://127.0.0.1:8000
start "U RESCUE server" "%CD%\.venv\Scripts\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8000
for /l %%i in (1,1,20) do (
    powershell -NoProfile -Command "try { Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/api/status -TimeoutSec 1 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
    if not errorlevel 1 goto :server_ready
    timeout /t 1 /nobreak >nul
)
echo WARNING: The server did not respond within 20 seconds. Check the U RESCUE server window.
pause
exit /b 1

:server_ready
start "" "http://127.0.0.1:8000"
echo U RESCUE is running in the separate server window. Press Ctrl+C in that window to stop it.
exit /b 0

:failed
echo.
echo ERROR: U RESCUE failed to start. Check the messages above.
pause
exit /b 1
