#!/bin/bash
echo "=========================================="
echo "StudyBuddy Setup Script (Linux/macOS/Bash)"
echo "=========================================="

if ! command -v python3 &> /dev/null
then
    echo "Python3 could not be found. Please install Python 3.10+"
    exit 1
fi

echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Verifying Ollama..."
if command -v ollama &> /dev/null
then
    echo "Pulling required models..."
    ollama pull gemma3:4b
    ollama pull nomic-embed-text
else
    echo "Ollama is not running or not installed. Please install Ollama."
fi

echo "Setup Complete!"
echo "Run 'source .venv/bin/activate' to activate the environment."
