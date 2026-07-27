@echo off
cd /d "%~dp0"
title Metrix AI - one request

echo.
echo Metrix AI - one text request
echo.

REM Only launch Python. All questions are asked INSIDE Python
REM (batch breaks on quotes, Russian text, and special characters).

where py >nul 2>&1
if %ERRORLEVEL%==0 (
  py -3 scripts\one_request.py
  goto finish
)

if exist "%LOCALAPPDATA%\Python\bin\python.exe" (
  "%LOCALAPPDATA%\Python\bin\python.exe" scripts\one_request.py
  goto finish
)

if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
  "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" scripts\one_request.py
  goto finish
)

if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
  "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" scripts\one_request.py
  goto finish
)

echo ERROR: Python not found.
echo Open PowerShell and run:
echo   cd Desktop\metrix-ai
echo   py -3 scripts\one_request.py
echo.
pause
exit /b 1

:finish
echo.
echo Done. Press any key to close.
pause >nul
