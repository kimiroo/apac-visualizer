@echo off

:: Check if the virtual environment directory exists
if not exist "%~dp0.venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating a new one...
    python -m venv .venv
    if not exist "%~dp0.venv\Scripts\activate.bat" (
        echo Error: Failed to create virtual environment.
        goto :EOF
    )
    echo Virtual environment created successfully.
)

:: activate venv
call "%~dp0.venv\Scripts\activate.bat"

:: Check dependency
echo Checking dependency...
python "%~dp0check_dependency.py" >nul 2>&1

:: Install dependency if not installed
if ERRORLEVEL 1 (
    echo Installing dependency...
    pip install -r "%~dp0requirements.txt"
)

:: Launch Streamlit
echo Starting main application...
streamlit run "%~dp0main.py"