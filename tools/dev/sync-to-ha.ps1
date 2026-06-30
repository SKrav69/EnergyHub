$Source = "$PSScriptRoot\..\..\addon"
$Target = "\\homeassistant\addons\local\energy_hub"

$Source = (Resolve-Path $Source).Path

Write-Host "Source: $Source"
Write-Host "Target: $Target"

robocopy "$Source" "$Target" /MIR /XD __pycache__ .git .pytest_cache /XF *.pyc