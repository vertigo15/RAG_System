# Quick Start Testing Script for Documents Page
# PowerShell Script

Write-Host "=" * 70
Write-Host "RAG System - Documents Page Testing" -ForegroundColor Cyan
Write-Host "=" * 70

# Check if Python is available
Write-Host "`n🔍 Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>$null
if ($pythonVersion) {
    Write-Host "✅ $pythonVersion found" -ForegroundColor Green
} else {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check if test dependencies are installed
Write-Host "`n📦 Checking test dependencies..." -ForegroundColor Yellow
$deps = @("selenium", "webdriver_manager")
$missingDeps = @()

foreach ($dep in $deps) {
    $installed = python -c "import $dep" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ $dep" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $dep (missing)" -ForegroundColor Red
        $missingDeps += $dep
    }
}

if ($missingDeps.Count -gt 0) {
    Write-Host "`n📥 Installing missing dependencies..." -ForegroundColor Yellow
    pip install -r test_requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
}

# Check if app is running
Write-Host "`n🌐 Checking if Documents page is accessible..." -ForegroundColor Yellow
$testUrl = "http://localhost:3000/documents"
try {
    $response = Invoke-WebRequest -Uri $testUrl -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Documents page is accessible at $testUrl" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Documents page may not be accessible" -ForegroundColor Yellow
    Write-Host "   Make sure to run: docker-compose up" -ForegroundColor Yellow
}

# Check PDF file
Write-Host "`n📄 Checking PDF file for upload test..." -ForegroundColor Yellow
$pdfPath = "C:\Users\user\Downloads\Docker_80bd9fd_Security_Export (003).pdf"
if (Test-Path $pdfPath) {
    $pdfSize = (Get-Item $pdfPath).Length / 1MB
    Write-Host "✅ Found PDF: Docker_80bd9fd_Security_Export (003).pdf ($([Math]::Round($pdfSize, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "⚠️  PDF file not found: $pdfPath" -ForegroundColor Yellow
    Write-Host "   The upload test will be skipped" -ForegroundColor Yellow
}

# Run tests
Write-Host "`n" 
Write-Host "=" * 70
Write-Host "Starting Test Suite..." -ForegroundColor Cyan
Write-Host "=" * 70
Write-Host "`n"

python test_documents_page.py

$testExitCode = $LASTEXITCODE

# Print summary
Write-Host "`n" 
Write-Host "=" * 70
if ($testExitCode -eq 0) {
    Write-Host "✅ Tests completed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Tests failed with exit code: $testExitCode" -ForegroundColor Red
}
Write-Host "=" * 70

exit $testExitCode
