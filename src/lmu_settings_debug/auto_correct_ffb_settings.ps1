# 1. Resolve paths
$steamPath = (Get-ItemProperty -Path "HKCU:\Software\Valve\Steam").SteamPath
$gameRoot = Join-Path $steamPath "steamapps\common\Le Mans Ultimate"
$settingsPath = Join-Path $gameRoot "UserData\player\direct input.json"

# Pull the config from the script directory
$configPath = Join-Path $PSScriptRoot "direct_input_config.json"

# File validation
if (-not (Test-Path $settingsPath)) {
    Write-Error "Le Mans Ultimate settings not found at: $settingsPath"
    return
}

if (-not (Test-Path $configPath)) {
    Write-Error "Configuration template not found at: $configPath"
    return
}

# 2. Load data
$settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
$config = Get-Content $configPath -Raw | ConvertFrom-Json
$devices = $settings.Devices.PSObject.Properties.Name

# 3. Interactive menu for the user
Write-Host "--- LMU Wheelbase Selector ---" -ForegroundColor Cyan
for ($i = 0; $i -lt $devices.Count; $i++) {
    Write-Host "$($i + 1): $($devices[$i])"
}

$selection = Read-Host "`nSelect the number of your wheelbase"
$wheelbaseIndex = [int]$selection - 1
$chosenWheelbase = $devices[$wheelbaseIndex]

Write-Host "`nYou have selected '$chosenWheelbase' as your wheelbase." -ForegroundColor Green

# 4. Create backup before modification
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item $settingsPath "$settingsPath.bak_$timestamp"
Write-Host "Backup created: direct input.json.bak_$timestamp"

# 5. Apply configuration (Apply Logic)
foreach ($deviceName in $devices) {
    $targetDevice = $settings.Devices.$deviceName

    if ($deviceName -eq $chosenWheelbase) {
        $payload = $config.wheelbase_defaults
        Write-Host "Applying wheelbase settings to: $deviceName"
    } else {
        $payload = $config.periphery_defaults
        Write-Host "Applying periphery settings to: $deviceName"
    }

    # Update categories (options, Force Feedback)
    foreach ($categoryProp in $payload.PSObject.Properties) {
        $catName = $categoryProp.Name
        if ($targetDevice.$catName) {
            foreach ($optionProp in $categoryProp.Value.PSObject.Properties) {
                $key = $optionProp.Name
                $targetDevice.$catName.$key = $optionProp.Value
            }
        }
    }
}

# 6. Save with correct depth
$settings | ConvertTo-Json -Depth 10 | Set-Content $settingsPath
Write-Host "`nSuccessfully saved! You can now start the game." -ForegroundColor Green
Pause