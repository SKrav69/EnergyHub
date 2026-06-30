Write-Host "Deploying EnergyHub to Home Assistant..."

& "$PSScriptRoot\sync-to-ha.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Deployment failed during sync."
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Sync completed."
Write-Host "Now restart the Energy Hub add-on manually in Home Assistant."
Write-Host "Then check the add-on logs."