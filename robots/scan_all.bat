@echo off
cd /d "%~dp0\.."
py -3 -m robots scan all
pause
