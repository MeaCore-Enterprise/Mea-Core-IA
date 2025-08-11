@echo off
echo 🚀 Installing MEA-Core AI System...

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✅ Python is installed

:: Install dependencies
echo 📦 Installing dependencies...
if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo ⚠️  requirements.txt not found, installing basic dependencies...
    pip install flask pdfminer-six numpy psutil gunicorn
)

:: Create data directories
mkdir data\logs 2>nul
mkdir data\cache 2>nul

echo ✅ MEA-Core installation completed!
echo 🌟 Start the system with: python main.py
echo 🌐 Then open: http://localhost:5000
pause
