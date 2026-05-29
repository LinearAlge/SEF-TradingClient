@echo off
setlocal

set "ROOT=%~dp0"
pushd "%ROOT%"

echo Starting Auth server...
start "Auth" /B node "TestScripts\auth\mock-auth-server.cjs"
echo Starting Market server...
start "Market" /B node "TestScripts\market\market-server.cjs"
echo Starting Funds server...
start "Funds" /B node "TestScripts\funds\funds-server.cjs"
echo Starting Holdings server...
start "Holdings" /B node "TestScripts\holding\holdings-server.cjs"
echo Starting Trading server...
start "Trading" /B node "TestScripts\data\trading-server.cjs"

echo All backend services started.
popd
endlocal
