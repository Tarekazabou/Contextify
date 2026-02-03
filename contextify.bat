@echo off
REM Contextify Launcher for Windows
REM This batch file allows you to run Contextify easily on Windows

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Run the Python script with all arguments passed to this batch file
python "%SCRIPT_DIR%contextify.py" %*
