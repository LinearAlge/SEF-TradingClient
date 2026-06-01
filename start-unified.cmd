@echo off
setlocal

set "ROOT=%~dp0"
pushd "%ROOT%"

echo Starting FastAPI backend...
start "FastAPI" /B cmd /C "python -m uvicorn backend_fastapi.main:app --reload --port 8000"

echo Starting frontend...
start "Vite" /B cmd /C "npm run dev"

echo Unified backend + frontend started.
popd
endlocal