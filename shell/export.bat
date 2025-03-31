@echo off
setlocal enabledelayedexpansion

:: Initialize variables
set "ledger_file="
set "start_date="
set "depth_level="

:: Parse command-line arguments
:parse_args
if "%1"=="" goto done

if "%1"=="-f" (
    set "ledger_file=%2"
    shift
    shift
    goto parse_args
)

if "%1"=="-b" (
    set "start_date=%2"
    shift
    shift
    goto parse_args
)

if "%1"=="-d" (
    set "depth_level=%2"
    shift
    shift
    goto parse_args
)

:: If an unrecognized argument is found, exit
echo Invalid argument %1
goto done

:done

:: Check if Python3 is installed
python --version
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in the PATH.
    exit /b 1
)

:: Create virtual environment
python -m venv venv

:: Activate virtual environment (Windows style)
call venv\Scripts\activate.bat

:: Install required Python packages
pip install -r python\requirements.txt

:: Run the Python script with provided arguments
python python\full_import.py -f "%ledger_file%" -b "%start_date%" -d "%depth_level%"

:: Deactivate virtual environment
deactivate

endlocal
