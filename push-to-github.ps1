# Run this AFTER installing Git for Windows and restarting Cursor.
# Repo: https://github.com/chakrinani/coding-rl-environment

Set-Location $PSScriptRoot

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Git is not installed. Install from https://git-scm.com/download/win then restart Cursor." -ForegroundColor Red
    exit 1
}

Write-Host "Initializing git repo..." -ForegroundColor Cyan
if (-not (Test-Path .git)) {
    git init -b main
}

Write-Host "Staging files..." -ForegroundColor Cyan
git add .

Write-Host "Creating commit..." -ForegroundColor Cyan
git status --short
git commit -m "Initial commit: PayStream webhook RL environment" 2>$null
if ($LASTEXITCODE -ne 0) {
    git commit -m "Initial commit: PayStream webhook RL environment"
}

Write-Host "Setting remote..." -ForegroundColor Cyan
$remoteUrl = "https://github.com/chakrinani/coding-rl-environment.git"
if (git remote get-url origin 2>$null) {
    git remote set-url origin $remoteUrl
} else {
    git remote add origin $remoteUrl
}

Write-Host "Pushing to GitHub (sign in if prompted)..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nDone! Repo: https://github.com/chakrinani/coding-rl-environment" -ForegroundColor Green
} else {
    Write-Host "`nPush failed. Make sure you are signed into GitHub." -ForegroundColor Red
}
