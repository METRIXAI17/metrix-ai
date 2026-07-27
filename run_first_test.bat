@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo === Metrix AI — first test (6 directions) ===
echo.

REM 1) Prefer "py -3" launcher (most reliable on Windows)
where py >nul 2>&1
if %ERRORLEVEL%==0 (
  echo Using: py -3
  py -3 scripts\first_test_all_industries.py
  goto :end
)

REM 2) Real Python installs (NOT the WindowsApps Store stub)
if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
  echo Using: %LOCALAPPDATA%\Python\bin\python.exe
  "%LOCALAPPDATA%\Python\bin\python.exe" scripts\first_test_all_industries.py
  goto :end
)

if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
  echo Using: %LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe
  "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" scripts\first_test_all_industries.py
  goto :end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
  echo Using: Python314
  "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" scripts\first_test_all_industries.py
  goto :end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
  echo Using: Python313
  "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" scripts\first_test_all_industries.py
  goto :end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
  echo Using: Python312
  "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" scripts\first_test_all_industries.py
  goto :end
)

echo.
echo [ERROR] Real Python not found.
echo.
echo The command "python" often opens a Microsoft Store stub and prints nothing useful.
echo.
echo Fix options:
echo   A) Run:  py -3 scripts\first_test_all_industries.py
echo   B) Install Python from https://www.python.org/downloads/
echo      and CHECK "Add python.exe to PATH"
echo   C) Windows Settings -^> Apps -^> Advanced app settings -^> App execution aliases
echo      - turn OFF "python.exe" and "python3.exe" aliases
echo.
pause
exit /b 1

:end
echo.
if %ERRORLEVEL%==0 (
  echo === OK ===
) else (
  echo === FAILED exit code %ERRORLEVEL% ===
)
echo.
pause
