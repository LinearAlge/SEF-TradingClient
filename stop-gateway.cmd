@echo off
setlocal

set "ROOT=%~dp0"
powershell -NoProfile -Command "& { $root = '%ROOT%'.TrimEnd('\\'); $pidFile = Join-Path $root '.gateway-pids.txt'; if (Test-Path $pidFile) { $lines = Get-Content $pidFile; foreach ($line in $lines) { if ($line -match '^(\d+)') { $procId = [int]$Matches[1]; Write-Host ('Stopping PID {0}' -f $procId); Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue } }; Remove-Item $pidFile -Force } else { $ports = 3010,3021,3022,3023,3024; $pids = Get-NetTCPConnection -State Listen -LocalPort $ports -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; foreach ($procId in $pids) { Write-Host ('Stopping PID {0}' -f $procId); Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue } } }"

echo All gateway + mock services stopped.
endlocal
