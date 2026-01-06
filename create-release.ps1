# C64 Game Organizer - Create GitHub Release
# This script creates a GitHub release and uploads the executable

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubToken
)

$owner = "jcarr71"
$repo = "gb64-reorganizer"
$tag = "v1.0.0"
$exePath = "dist\GB64GameOrganizer.exe"

Write-Host "Creating GitHub Release for C64 Game Organizer" -ForegroundColor Cyan
Write-Host "=" * 50

# Check if executable exists
if (!(Test-Path $exePath)) {
    Write-Host "Error: Executable not found at $exePath" -ForegroundColor Red
    exit 1
}

$exeSize = (Get-Item $exePath).Length / 1MB
Write-Host "Executable size: $($exeSize.ToString('F2')) MB" -ForegroundColor Green

# Create release
Write-Host "`nCreating release..." -ForegroundColor Yellow

$releaseData = @{
    tag_name = $tag
    name = "GB64 Game Organizer v1.0.0"
    body = "Initial release - Standalone executable for organizing GameBase64 games.`n`nThis release includes a pre-built executable that doesn't require Python installation.`n`nSimply download GB64GameOrganizer.exe and run it to start organizing your GameBase64 collection!`n`n## What's Included`n- Standalone Windows executable (no Python needed)`n- Automatic game organization by Genre/Subgenre/Language`n- VERSION.NFO parsing for metadata extraction`n- Duplicate game handling`n`n## Usage`nJust run the EXE and provide your GameBase64 games folder path!"
    draft = $false
    prerelease = $false
} | ConvertTo-Json

$headers = @{
    Authorization = "token $GitHubToken"
    "Content-Type" = "application/json"
    "Accept" = "application/vnd.github.v3+json"
}

try {
    $releaseResponse = Invoke-WebRequest -Uri "https://api.github.com/repos/$owner/$repo/releases" `
        -Method Post `
        -Headers $headers `
        -Body $releaseData `
        -ErrorAction Stop

    $release = $releaseResponse.Content | ConvertFrom-Json
    Write-Host "✓ Release created successfully!" -ForegroundColor Green
    Write-Host "Release URL: $($release.html_url)" -ForegroundColor Cyan

    # Upload executable
    Write-Host "`nUploading executable..." -ForegroundColor Yellow
    
    $uploadUrl = $release.upload_url -replace '\{.*?\}', ''
    $uploadUrl = "$uploadUrl`?name=GB64GameOrganizer.exe"
    
    $exe = Get-Item $exePath
    $fileBytes = [System.IO.File]::ReadAllBytes($exe.FullName)
    
    $uploadHeaders = @{
        Authorization = "token $GitHubToken"
        "Content-Type" = "application/octet-stream"
    }

    $uploadResponse = Invoke-WebRequest -Uri $uploadUrl `
        -Method Post `
        -Headers $uploadHeaders `
        -Body $fileBytes `
        -ErrorAction Stop

    Write-Host "✓ Executable uploaded successfully!" -ForegroundColor Green
    Write-Host "`nRelease is ready! Visit: $($release.html_url)" -ForegroundColor Cyan

} catch {
    Write-Host "✗ Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
