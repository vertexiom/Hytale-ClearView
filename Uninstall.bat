@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" -Uninstall %*
set "clearview_exit=%errorlevel%"
echo.
pause
exit /b %clearview_exit%
