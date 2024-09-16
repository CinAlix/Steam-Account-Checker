@echo off
echo Setting up the Python environment...

python --version
IF ERRORLEVEL 1 (
    echo Python is not installed. Please install Python first.
    pause
    exit /b
)

pip install -r requirements.txt

IF ERRORLEVEL 1 (
    echo Failed to install the required packages. Check the errors above.
    pause
    exit /b
)

echo Environment setup completed successfully!
pause
