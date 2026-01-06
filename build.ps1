# C64 Game Organizer - Build Script
# Builds an executable using PyInstaller

Write-Host "C64 Game Organizer - Build Script" -ForegroundColor Cyan
Write-Host "=" * 50

# Check if PyInstaller is installed
Write-Host "`nChecking for PyInstaller..." -ForegroundColor Yellow
$pyinstaller = python -m pip show pyinstaller 2>$null
if ($null -eq $pyinstaller) {
    Write-Host "PyInstaller not installed" -ForegroundColor Red
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    python -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install PyInstaller" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "PyInstaller found" -ForegroundColor Green
}

# Build the executable
Write-Host "`nBuilding executable..." -ForegroundColor Yellow
python -m PyInstaller --onefile --name C64GameOrganizer gb64_reorganizer.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n" -ForegroundColor Green
    Write-Host "Build successful!" -ForegroundColor Green
    Write-Host "Executable location: .\dist\C64GameOrganizer.exe" -ForegroundColor Cyan
} else {
    Write-Host "`nBuild failed" -ForegroundColor Red
    exit 1
}
