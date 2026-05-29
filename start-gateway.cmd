@echo off
setlocal

set "ROOT=%~dp0"
powershell -NoProfile -Command "& { $root = '%ROOT%'.TrimEnd('\\'); $pidFile = Join-Path $root '.gateway-pids.txt'; if (Test-Path $pidFile) { Remove-Item $pidFile -Force }; $services = @(@{ Name = 'Gateway'; Script = 'backend\client\client-gateway-server.cjs' }, @{ Name = 'MockFunds'; Script = 'backend\mocks\mock-funds-service.cjs' }, @{ Name = 'MockSecurities'; Script = 'backend\mocks\mock-securities-service.cjs' }, @{ Name = 'MockExchange'; Script = 'backend\mocks\mock-exchange-service.cjs' }, @{ Name = 'MockMarket'; Script = 'backend\mocks\mock-market-service.cjs' }); foreach ($svc in $services) { $proc = Start-Process -FilePath 'node' -ArgumentList $svc.Script -WorkingDirectory $root -NoNewWindow -PassThru; ('{0} {1}' -f $proc.Id, $svc.Name) | Out-File -FilePath $pidFile -Append -Encoding ascii; Write-Host ('Started {0} (PID {1})' -f $svc.Name, $proc.Id) } }"

echo All gateway + mock services started.
endlocal