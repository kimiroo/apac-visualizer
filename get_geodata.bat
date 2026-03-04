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

:: pushd
pushd "%~dp0"

:: Launch Streamlit
python "%~dp0get_geodata.py"

:: popd
popd