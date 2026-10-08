Write-Host "=========================================="
Write-Host "StudyBuddy Windows Setup Script (PowerShell)"
Write-Host "=========================================="

# Ensure Python is installed
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed or not in PATH. Please install Python 3.10+."
    exit 1
}

# Setup E: directories if possible
if (Test-Path "E:\") {
    Write-Host "Setting up project directories on E:..."
    New-Item -ItemType Directory -Force -Path "E:\StudyBuddy\.ollama" | Out-Null
    New-Item -ItemType Directory -Force -Path "E:\StudyBuddy\.pip-cache" | Out-Null
    New-Item -ItemType Directory -Force -Path "E:\StudyBuddy\.tmp" | Out-Null
    New-Item -ItemType Directory -Force -Path "E:\StudyBuddy\.cache\huggingface" | Out-Null
    
    [System.Environment]::SetEnvironmentVariable("OLLAMA_MODELS", "E:\StudyBuddy\.ollama", "User")
    [System.Environment]::SetEnvironmentVariable("PIP_CACHE_DIR", "E:\StudyBuddy\.pip-cache", "User")
    [System.Environment]::SetEnvironmentVariable("HF_HOME", "E:\StudyBuddy\.cache\huggingface", "User")
}

Write-Host "Creating virtual environment..."
python -m venv .venv
& .\.venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Verifying Ollama..."
if (Get-Command ollama -ErrorAction SilentlyContinue) {
    Write-Host "Pulling required models..."
    ollama pull gemma3:4b
    ollama pull nomic-embed-text
} else {
    Write-Host "Ollama is not running or not installed. Please install Ollama."
}

Write-Host "Setup Complete!"
Write-Host "Run '.\.venv\Scripts\Activate.ps1' to activate the environment."
