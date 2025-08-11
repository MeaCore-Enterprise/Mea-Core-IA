#!/bin/bash
# MEA-Core Installation Script

echo "🚀 Installing MEA-Core AI System..."

# Check Python version
python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2)
if [ -z "$python_version" ]; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python version: $python_version"

# Install dependencies
echo "📦 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
else
    echo "⚠️  requirements.txt not found, installing basic dependencies..."
    pip3 install flask pdfminer-six numpy psutil gunicorn
fi

# Create data directories
mkdir -p data/logs data/cache

# Set permissions
chmod +x main.py

echo "✅ MEA-Core installation completed!"
echo "🌟 Start the system with: python3 main.py"
echo "🌐 Then open: http://localhost:5000"
