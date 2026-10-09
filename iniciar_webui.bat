@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
call webui.bat
pause
