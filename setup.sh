#!/bin/bash

# Setup script for AnimeKai Downloader Web Frontend

echo "=================================================="
echo "🎬 AnimeKai Downloader - Setup Script"
echo "=================================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    echo "Try: sudo apt install python3-venv"
    exit 1
fi

echo "✅ Virtual environment created"
echo ""

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

echo "✅ Python dependencies installed"
echo ""

# Check for ffmpeg
echo "🔍 Checking for ffmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  ffmpeg not found!"
    echo "   Install with: sudo apt install ffmpeg"
else
    echo "✅ ffmpeg found: $(ffmpeg -version | head -n1)"
fi
echo ""

# Check for yt-dlp
echo "🔍 Checking for yt-dlp..."
if ! command -v yt-dlp &> /dev/null; then
    echo "⚠️  yt-dlp not found in PATH, but might be in venv"
    echo "   Will be available after activating virtual environment"
else
    echo "✅ yt-dlp found"
fi
echo ""

# Create downloads directory
echo "📁 Creating downloads directory..."
mkdir -p downloads
echo "✅ Downloads directory created"
echo ""

echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "To start the web server:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the server: python app.py"
echo ""
echo "The server will be available at: http://localhost:5000"
echo ""
echo "To deactivate virtual environment later: deactivate"
echo "=================================================="
