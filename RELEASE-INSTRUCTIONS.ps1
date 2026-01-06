# Instructions to create a GitHub release

Write-Host "C64 Game Organizer - GitHub Release Setup" -ForegroundColor Cyan
Write-Host "=" * 60

Write-Host ""
Write-Host "To create a GitHub release, you need a Personal Access Token:" -ForegroundColor Yellow

Write-Host ""
Write-Host "1. Go to: https://github.com/settings/tokens/new" -ForegroundColor White
Write-Host "2. Give it a name like 'C64 Release'"
Write-Host "3. Select scopes: 'repo' (full control of private repositories)"
Write-Host "4. Click 'Generate token'"
Write-Host "5. Copy the token (save it safely)"

Write-Host ""
Write-Host "Once you have your token, run:" -ForegroundColor Green
Write-Host "   .\create-release.ps1 -GitHubToken YOUR_TOKEN_HERE" -ForegroundColor Cyan

Write-Host ""
Write-Host "Keep your token secret! Never commit it to git." -ForegroundColor Red

Write-Host ""
