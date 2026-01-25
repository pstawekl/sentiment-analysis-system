@echo off
echo Starting Backend Server...
echo.
echo Make sure you have:
echo 1. Activated virtual environment (venv\Scripts\activate)
echo 2. Installed dependencies (pip install -r requirements.txt)
echo 3. Ollama is running (optional, will use TextBlob as fallback)
echo.
echo Starting uvicorn server on http://localhost:8000
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
