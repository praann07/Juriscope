@echo off
setlocal
title Juriscope Launcher

REM Double-click this file to run the whole app: it checks the setup,
REM installs anything missing, starts the backend and frontend, and opens
REM the browser once both are responding.

REM Resolve the project root from this script's own location so the
REM launcher keeps working no matter where the repo is cloned.
set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"
cd /d "%ROOT%"

echo ========================================
echo  Juriscope - Starting...
echo ========================================
echo.

REM ---- 1. Tools that must already be installed -----------------------------
where node >nul 2>&1
if errorlevel 1 (
    echo [X] Node.js is not installed or not on PATH.
    echo     Install the LTS version from https://nodejs.org and run this again.
    goto fail
)

REM Use the project venv if one exists, otherwise the system Python.
set "PY=python"
if exist "%ROOT%\.venv\Scripts\python.exe" set "PY=%ROOT%\.venv\Scripts\python.exe"
"%PY%" --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python is not installed or not on PATH.
    echo     Install Python 3.12 from https://www.python.org and tick "Add to PATH", then run this again.
    goto fail
)

REM ---- 2. Configuration -----------------------------------------------------
REM The backend cannot start without its API keys.
if not exist "%ROOT%\.env" (
    echo [X] No .env file found in the project root.
    echo     Create it with GROQ_API_KEY, PINECONE_API_KEY and INDEX_NAME, then run this again.
    goto fail
)

REM ---- 3. Python packages (installed on first run) -------------------------
REM find_spec only looks for the packages, so this check is quick.
"%PY%" -c "import importlib.util as u, sys; sys.exit(0 if all(u.find_spec(m) for m in ['fastapi','uvicorn','dotenv','langchain_pinecone','sentence_transformers','pypdf']) else 1)"
if errorlevel 1 (
    echo [!] Python packages are missing. Installing requirements.txt now.
    echo     The first install can take a while because it includes PyTorch.
    "%PY%" -m pip install -r "%ROOT%\requirements.txt"
    if errorlevel 1 (
        echo [X] pip install failed. See the messages above.
        goto fail
    )
    echo.
)

REM ---- 4. Frontend packages (installed on first run) -----------------------
if not exist "%ROOT%\frontend\node_modules\vite" (
    echo [!] Frontend packages are missing. Running npm install...
    pushd "%ROOT%\frontend"
    call npm install
    if errorlevel 1 (
        popd
        echo [X] npm install failed. See the messages above.
        goto fail
    )
    popd
    echo.
)

REM ---- 5. Start the servers -------------------------------------------------
REM If a server is already listening, reuse it instead of starting a second copy.
set "BACKEND_UP=0"
set "FRONTEND_UP=0"
netstat -ano | findstr /R /C:":8000 .*LISTENING" >nul && set "BACKEND_UP=1"
netstat -ano | findstr /R /C:":3000 .*LISTENING" >nul && set "FRONTEND_UP=1"

if "%BACKEND_UP%"=="1" echo [1/2] Backend is already running on http://localhost:8000
if "%BACKEND_UP%"=="0" echo [1/2] Starting FastAPI backend on http://localhost:8000
if "%BACKEND_UP%"=="0" start "Juriscope Backend" cmd /k "cd /d "%ROOT%" && "%PY%" -m uvicorn src.app:app --reload --host 127.0.0.1 --port 8000"

if "%FRONTEND_UP%"=="1" echo [2/2] Frontend is already running on http://localhost:3000
if "%FRONTEND_UP%"=="0" echo [2/2] Starting React frontend on http://localhost:3000
if "%FRONTEND_UP%"=="0" start "Juriscope Frontend" cmd /k "cd /d "%ROOT%\frontend" && npm run dev"

REM ---- 6. Wait until both respond, then open the browser --------------------
echo.
echo Waiting for the servers to respond...
call :wait_for http://localhost:8000/ 90 "Backend"
call :wait_for http://localhost:3000/ 60 "Frontend"

start "" http://localhost:3000

echo.
echo ========================================
echo  Juriscope is running
echo ========================================
echo   App     : http://localhost:3000   (opened in your browser)
echo   Backend : http://localhost:8000
echo.
echo To stop the app, close the "Juriscope Backend" and "Juriscope Frontend" windows.
echo This launcher window can be closed.
echo.
exit /b 0

REM ---- Helpers --------------------------------------------------------------

REM %1 = URL to poll, %2 = seconds to wait, %3 = display name
:wait_for
set /a TRIES=0
:wait_loop
curl.exe -s -o nul "%~1" >nul 2>&1
if not errorlevel 1 (
    echo [OK] %~3 is responding.
    exit /b 0
)
if %TRIES% GEQ %~2 (
    echo [!] %~3 did not respond after %~2 seconds. Check its window for errors.
    exit /b 1
)
set /a TRIES+=1
ping -n 2 127.0.0.1 >nul
goto wait_loop

:fail
echo.
echo Startup stopped. Fix the problem above, then run start.bat again.
pause
exit /b 1
