@echo off
setlocal

set "BASE_DIR=%~dp0backend_fastapi\mock_modules\data"
set "FUNDS_FILE=%BASE_DIR%\mock-funds-db.json"
set "SEC_FILE=%BASE_DIR%\mock-securities-db.json"
set "TRADE_FILE=%BASE_DIR%\mock-exchange-db.json"

echo Resetting mock trade data...

(
  echo {
  echo   "accounts": {
  echo     "admin": {
  echo       "fundAccountId": "FUND000001",
  echo       "currency": "CNY",
  echo       "phone": "13800000000",
  echo       "idNumber": "110101199001011234",
  echo       "balances": {
  echo         "available": 200000,
  echo         "frozen": 0
  echo       },
  echo       "positions": []
  echo     }
  echo   },
  echo   "cashFlows": [],
  echo   "passwords": {
  echo     "admin": {
  echo       "trade": "123456",
  echo       "withdraw": "654321"
  echo     }
  echo   }
  echo }
) > "%FUNDS_FILE%"

(
  echo {
  echo   "accounts": {
  echo     "admin": {
  echo       "securitiesAccountId": "SEC000001",
  echo       "positions": []
  echo     }
  echo   },
  echo   "stockFlows": []
  echo }
) > "%SEC_FILE%"

(
  echo {
  echo   "accounts": {
  echo     "admin": {
  echo       "account": "admin"
  echo     }
  echo   },
  echo   "orders": [],
  echo   "fills": []
  echo }
) > "%TRADE_FILE%"

echo Done. Please restart the backend.

endlocal