@echo off
echo ========================================
echo  Juriscope - Starting...
echo ========================================
echo.
echo [1/2] Starting FastAPI backend on http://localhost:8000
start "Juriscope Backend" cmd /k "cd /d c:\Users\mspb2\legalRAG && uvicorn src.app:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul
echo [2/2] Starting React frontend on http://localhost:3000
start "Juriscope Frontend" cmd /k "cd /d c:\Users\mspb2\legalRAG\frontend && npm run dev"
echo.
echo Both servers starting in separate windows.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
pause
