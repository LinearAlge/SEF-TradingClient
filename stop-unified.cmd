@echo off
setlocal

powershell -NoProfile -Command "& { $ports = 8000,5173; $pids = Get-NetTCPConnection -State Listen -LocalPort $ports -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; foreach ($pid in $pids) { Write-Host ('Stopping PID {0}' -f $pid); Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue } }"

echo Unified backend + frontend stopped.
endlocal