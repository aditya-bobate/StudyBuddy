@echo off
echo ==========================================
echo StudyBuddy Windows Setup Script (CMD)
echo ==========================================

REM Ensure Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python 3.10+.
    exit /b 1
)

REM Setup E: directories if possible
IF EXIST "E:\" (
    echo Setting up project directories on E:...
    if not exist "E:\StudyBuddy\.ollama" mkdir "E:\StudyBuddy\.ollama"
    if not exist "E:\StudyBuddy\.pip-cache" mkdir "E:\StudyBuddy\.pip-cache"
    if not exist "E:\StudyBuddy\.tmp" mkdir "E:\StudyBuddy\.tmp"
    if not exist "E:\StudyBuddy\.cache\huggingface" mkdir "E:\StudyBuddy\.cache\huggingface"
    
    setx OLLAMA_MODELS "E:\StudyBuddy\.ollama"
    setx PIP_CACHE_DIR "E:\StudyBuddy\.pip-cache"
    setx HF_HOME "E:\StudyBuddy\.cache\huggingface"
)

echo Creating virtual environment...
python -m venv .venv
call .venv\Scripts\activate.bat

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Verifying Ollama...
ollama --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Ollama is not running or not installed. Please install Ollama.
) ELSE (
    echo Pulling required models...
    ollama pull gemma3:4b
    ollama pull nomic-embed-text
)

echo Setup Complete!
echo Run '.\.venv\Scripts\activate.bat' to activate the environment.
