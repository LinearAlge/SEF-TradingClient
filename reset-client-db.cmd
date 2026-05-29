@echo off
setlocal

set "DB_FILE=%~dp0backend\client\client.sqlite"

if exist "%DB_FILE%" (
  echo Removing client SQLite database...
  del /F /Q "%DB_FILE%"
  echo Done. Please restart the gateway.
) else (
  echo client.sqlite not found. Nothing to reset.
)

endlocal
