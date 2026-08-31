$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

$BackendDirectory = Join-Path $ProjectRoot "backend"
$FrontendDirectory = Join-Path $ProjectRoot "frontend"

$PythonExecutable = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $PythonExecutable)) {
    Write-Host ""
    Write-Host "Sentinal AI startup failed." -ForegroundColor Red
    Write-Host ""
    Write-Host "Python virtual environment was not found:" -ForegroundColor Yellow
    Write-Host $PythonExecutable
    Write-Host ""
    Write-Host "Create the virtual environment and install requirements first."
    exit 1
}

if (-not (Test-Path $BackendDirectory)) {
    Write-Host ""
    Write-Host "Sentinal AI startup failed." -ForegroundColor Red
    Write-Host ""
    Write-Host "Backend directory was not found:"
    Write-Host $BackendDirectory
    exit 1
}

if (-not (Test-Path $FrontendDirectory)) {
    Write-Host ""
    Write-Host "Sentinal AI startup failed." -ForegroundColor Red
    Write-Host ""
    Write-Host "Frontend directory was not found:"
    Write-Host $FrontendDirectory
    exit 1
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "           SENTINAL AI STARTUP" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Starting backend..." -ForegroundColor Green

Start-Process powershell.exe -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location -LiteralPath '$BackendDirectory'; & '$PythonExecutable' -m uvicorn app.main:app --reload"
)

Start-Sleep -Seconds 2

Write-Host "Starting frontend..." -ForegroundColor Green

Start-Process powershell.exe -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location -LiteralPath '$FrontendDirectory'; npm run dev"
)

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "          SENTINAL AI IS STARTING" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend : http://127.0.0.1:8000" -ForegroundColor White
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "Two terminal windows have been opened." -ForegroundColor Yellow
Write-Host "Keep both running while using the application."
Write-Host ""