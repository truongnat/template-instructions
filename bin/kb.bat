@echo off
REM Knowledge Base CLI - Windows batch entry point
REM Usage: kb.bat [command] [args]

setlocal enabledelayedexpansion

REM Get script directory
set "SCRIPT_DIR=%~dp0"

REM Check for Python
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=python"
    goto :run
)

where python3 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=python3"
    goto :run
)

echo Error: Python not found. Please install Python 3.7+
exit /b 1

:run
REM Run the Python CLI
"%PYTHON_CMD%" "%SCRIPT_DIR%kb_cli.py" %*
