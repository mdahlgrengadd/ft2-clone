#!/usr/bin/env powershell
# FastTracker II Clone - Web Server Startup Script
# This script starts the improved web server for testing the WebAssembly build

Write-Host "FastTracker II Clone - Web Server Startup" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Python found: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "Python not found!" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if build directory exists
if (!(Test-Path "build_emscripten\web")) {
    Write-Host "WebAssembly build not found!" -ForegroundColor Red
    Write-Host "Please run 'make-emscripten.ps1' first to build the project." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Starting web server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Web server will serve from: $(Get-Location)" -ForegroundColor Cyan
Write-Host ""
Write-Host "URLs:" -ForegroundColor Cyan
Write-Host "  Main App:    http://localhost:8000/build_emscripten/web/ft2-clone.html" -ForegroundColor White
Write-Host "  Index Page:  http://localhost:8000/" -ForegroundColor White
Write-Host "  Test Page:   http://localhost:8000/test-fix.html" -ForegroundColor White
Write-Host ""
Write-Host "Features:" -ForegroundColor Cyan
Write-Host "  Fixed caching issues (no more Shift+R needed)" -ForegroundColor Green
Write-Host "  Fixed mouse coordinate offset" -ForegroundColor Green
Write-Host "  Fixed threading issues" -ForegroundColor Green
Write-Host "  Proper WASM MIME types" -ForegroundColor Green
Write-Host "  Debug mode (press 'D' in the app)" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
try {
    python serve-web.py
} catch {
    Write-Host "Error starting server: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
} 