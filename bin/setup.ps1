# Agentic SDLC - Windows Setup Script
# Usage: .\bin\setup.ps1

Write-Host "🚀 Starting Agentic SDLC Setup..." -ForegroundColor Cyan

# 1. Check for Python
if (Get-Command "python" -ErrorAction SilentlyContinue) {
    Write-Host "✅ Python found." -ForegroundColor Green
} else {
    Write-Host "❌ Python is not installed. Please install Python 3.10+." -ForegroundColor Red
    exit 1
}

# 2. Check for Package Manager (Bun or NPM)
$PackageManager = ""
if (Get-Command "bun" -ErrorAction SilentlyContinue) {
    Write-Host "✅ Bun found." -ForegroundColor Green
    $PackageManager = "bun"
} elseif (Get-Command "npm" -ErrorAction SilentlyContinue) {
    Write-Host "✅ NPM found." -ForegroundColor Green
    $PackageManager = "npm"
} else {
    Write-Host "❌ Neither Bun nor NPM found. Please install Node.js or Bun." -ForegroundColor Red
    exit 1
}

# 3. Setup Virtual Environment
if (-not (Test-Path ".venv")) {
    Write-Host "📦 Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
}
Write-Host "📦 Activating virtual environment..." -ForegroundColor Cyan
& ".\.venv\Scripts\Activate.ps1"

# 4. Install Python Dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Cyan
pip install -e .[dev]

# 5. Install Node/Bun Dependencies
Write-Host "📦 Installing JS dependencies using $PackageManager..." -ForegroundColor Cyan
if ($PackageManager -eq "bun") {
    bun install
} else {
    npm install
}

# 6. Final Check
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "👉 Run 'python asdlc.py dashboard' to start the UI." -ForegroundColor Yellow
Write-Host "👉 Run 'python asdlc.py brain status' to check state." -ForegroundColor Yellow
Write-Host "👉 Run '.\bin\asdlc.ps1 --help' to see all commands." -ForegroundColor Yellow
