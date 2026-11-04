@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0diagnostics.ps1" %*
set "clearview_exit=%errorlevel%"
echo.
pause
exit /b %clearview_exit%
