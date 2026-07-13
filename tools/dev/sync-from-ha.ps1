$ErrorActionPreference = "Stop"

$HaConfig = "\\homeassistant\config"
$RepoRoot = (Resolve-Path "$PSScriptRoot\..\..").Path

$TargetConfig = Join-Path $RepoRoot "homeassistant\live\config"
$TargetStorage = Join-Path $RepoRoot "homeassistant\live\storage"

Write-Host "Syncing Home Assistant configuration to EnergyHub repository..."
Write-Host ""
Write-Host "HA source: $HaConfig"
Write-Host "Repository: $RepoRoot"
Write-Host ""

# ------------------------------------------------------------
# Create destination directories
# ------------------------------------------------------------

New-Item `
    -ItemType Directory `
    -Force `
    -Path $TargetConfig `
    | Out-Null

New-Item `
    -ItemType Directory `
    -Force `
    -Path $TargetStorage `
    | Out-Null


# ------------------------------------------------------------
# Home Assistant YAML configuration files
# ------------------------------------------------------------

$ConfigFiles = @(
    "automations.yaml",
    "scripts.yaml",
    "scenes.yaml",
    "configuration.yaml"
)

Write-Host "Syncing HA configuration files..."

foreach ($File in $ConfigFiles) {

    $Source = Join-Path $HaConfig $File
    $Target = Join-Path $TargetConfig $File

    if (Test-Path $Source) {

        Copy-Item `
            -Path $Source `
            -Destination $Target `
            -Force

        Write-Host "  Copied: $File"

    }
    else {

        Write-Host "  Missing: $File"

    }
}


# ------------------------------------------------------------
# Selected Home Assistant .storage files
# ------------------------------------------------------------

$HaStorage = Join-Path $HaConfig ".storage"

$StorageFiles = @(
    "input_boolean",
    "input_number",
    "timer",
    "lovelace.dashboard_powmr1",
    "lovelace_dashboards",
    "lovelace_resources"
)

Write-Host ""
Write-Host "Syncing selected HA storage files..."

foreach ($File in $StorageFiles) {

    $Source = Join-Path $HaStorage $File
    $Target = Join-Path $TargetStorage $File

    if (Test-Path $Source) {

        Copy-Item `
            -Path $Source `
            -Destination $Target `
            -Force

        Write-Host "  Copied: $File"

    }
    else {

        Write-Host "  Missing: $File"

    }
}


# ------------------------------------------------------------
# Completed
# ------------------------------------------------------------

Write-Host ""
Write-Host "Home Assistant sync completed."
Write-Host ""
Write-Host "Review changes in GitHub Desktop before committing."

exit 0