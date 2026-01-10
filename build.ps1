# Build script for Gamebase Game Organizer
# Builds an executable using PyInstaller

Write-Host "Gamebase Game Organizer - Build Script" -ForegroundColor Cyan
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

# Build the GUI executable
Write-Host "`nBuilding GUI executable..." -ForegroundColor Yellow
python -m PyInstaller --onefile --windowed --name GamebaseGameOrganizer gb64_gui.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n" -ForegroundColor Green
    Write-Host "Build successful!" -ForegroundColor Green
    Write-Host "Executable location: .\dist\GamebaseGameOrganizer.exe" -ForegroundColor Cyan
    Write-Host "`nNote: Original CLI version still available via 'python gb64_reorganizer.py'" -ForegroundColor Cyan
} else {
    Write-Host "`nBuild failed" -ForegroundColor Red
    exit 1
}
