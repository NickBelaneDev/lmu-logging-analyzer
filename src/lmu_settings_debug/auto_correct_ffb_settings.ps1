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

# 7. Game Options: optionally disable replay & telemetry recording (Settings.JSON)
$gameSettingsPath = Join-Path $gameRoot "UserData\player\Settings.JSON"

if (-not (Test-Path $gameSettingsPath)) {
    Write-Warning "Settings.JSON not found at: $gameSettingsPath. Skipping Game Options step."
} else {
    Write-Host "`n--- Game Options ---" -ForegroundColor Cyan
    $gameSettings = Get-Content $gameSettingsPath -Raw | ConvertFrom-Json

    $disableReplay = (Read-Host "Disable replay recording? It often causes stutters. (y/n)") -eq "y"
    $disableTelemetry = (Read-Host "Disable automatic telemetry recording? (y/n)") -eq "y"

    if ($disableReplay -or $disableTelemetry) {
        # Backup before modification
        $gsTimestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        Copy-Item $gameSettingsPath "$gameSettingsPath.bak_$gsTimestamp"
        Write-Host "Backup created: Settings.JSON.bak_$gsTimestamp"

        $gameOptions = $gameSettings.'Game Options'
        if ($null -eq $gameOptions) {
            Write-Warning "Section 'Game Options' not found in Settings.JSON. Skipping."
        } else {
            if ($disableReplay) {
                if ($gameOptions.PSObject.Properties.Name -contains "Record Replays") {
                    $gameOptions.'Record Replays' = $false
                    Write-Host "Disabled replay recording."
                } else {
                    Write-Warning "Option 'Record Replays' not found. Skipping."
                }
            }
            if ($disableTelemetry) {
                if ($gameOptions.PSObject.Properties.Name -contains "Automatically Record Telemetry") {
                    $gameOptions.'Automatically Record Telemetry' = $false
                    Write-Host "Disabled automatic telemetry recording."
                } else {
                    Write-Warning "Option 'Automatically Record Telemetry' not found. Skipping."
                }
            }

            # Settings.JSON is deeply nested; use a high depth so nothing is truncated.
            $gameSettings | ConvertTo-Json -Depth 50 | Set-Content $gameSettingsPath
            Write-Host "Game Options saved." -ForegroundColor Green
        }
    } else {
        Write-Host "Leaving Game Options unchanged."
    }
}

Pause