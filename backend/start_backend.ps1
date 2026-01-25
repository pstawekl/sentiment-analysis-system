# PowerShell script to start the backend server
Write-Host "Starting Backend Server..." -ForegroundColor Green
Write-Host ""
Write-Host "Make sure you have:" -ForegroundColor Yellow
Write-Host "1. Activated virtual environment (venv\Scripts\Activate.ps1)" -ForegroundColor Yellow
Write-Host "2. Installed dependencies (pip install -r requirements.txt)" -ForegroundColor Yellow
Write-Host "3. Ollama is running (optional, will use TextBlob as fallback)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Starting uvicorn server on http://localhost:8000" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Start uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
