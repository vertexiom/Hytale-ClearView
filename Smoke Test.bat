@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0smoke-test.ps1"
set "clearview_exit=%errorlevel%"
echo.
pause
exit /b %clearview_exit%
