@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo === Metrix AI backend server ===
echo.

where py >nul 2>&1
if %ERRORLEVEL%==0 (
  echo Using: py -3
  py -3 -m backend.main
  goto :end
)

if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
  "%LOCALAPPDATA%\Python\bin\python.exe" -m backend.main
  goto :end
)

if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
  "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" -m backend.main
  goto :end
)

echo [ERROR] Real Python not found. Use: py -3 -m backend.main
pause
exit /b 1

:end
pause
