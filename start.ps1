# ============================================================
# Lottery Stats System - One-click Start Script
# Usage: .\start.ps1  or double-click start.bat
# ============================================================

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "Lottery Stats System"

Clear-Host
Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "       Lottery Stats & Visual System v1.2.0" -ForegroundColor Yellow
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# ---------- Step 1: Stop old processes ----------
Write-Host "[1/4] Stopping old service..." -ForegroundColor Green
Get-Process -Name "python" -ErrorAction SilentlyContinue | 
    Where-Object { $_.CommandLine -like "*uvicorn*app.main*" } |
    Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# Release port 8000
$portInUse = netstat -ano 2>$null | Select-String ":8000 " | Select-String "LISTENING"
if ($portInUse) {
    $pidMatch = [regex]::Match($portInUse, '\s+(\d+)\s*$')
    if ($pidMatch.Success) {
        Stop-Process -Id $pidMatch.Groups[1].Value -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }
}
Write-Host "  Done" -ForegroundColor Gray

# ---------- Step 2: Start service ----------
Write-Host ""
Write-Host "[2/4] Starting service..." -ForegroundColor Green
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Get-Location }

$cmd = "cd '$scriptDir'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd

# Wait for service ready
Write-Host "  Waiting for service..." -ForegroundColor Gray
$ready = $false
for ($i = 1; $i -le 20; $i++) {
    Start-Sleep -Seconds 1
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        $ready = $true
        Write-Host "  Service ready!" -ForegroundColor Green
        break
    } catch { }
}
if (-not $ready) {
    Write-Host "  [WARN] Service start timeout, check the service window" -ForegroundColor Yellow
}

# ---------- Step 3: Open browser ----------
Write-Host ""
Write-Host "[3/4] Opening browser..." -ForegroundColor Green
Start-Process "http://localhost:8000/frontend/index.html"
Write-Host "  Done" -ForegroundColor Gray

# ---------- Step 4: Done ----------
Write-Host ""
Write-Host "[4/4] Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  Frontend : http://localhost:8000/frontend/index.html" -ForegroundColor White
Write-Host "  API Docs : http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Close the service window to stop" -ForegroundColor Gray
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to close this window"
