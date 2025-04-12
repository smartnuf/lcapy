param (
    [switch]$Force
)

. "$PSScriptRoot\lcapy-w64-dev-env.psm1"
$config = Import-PowerShellDataFile "$PSScriptRoot\lcapy-w64-dev-env-config.psd1"

$apps = Get-InstalledApps
foreach ($app in $apps) {
    Write-Host "Uninstalling $app..."
    scoop uninstall $app -ErrorAction SilentlyContinue
}

if ($Force -or ($apps -contains "gtk3_gvsbuild")) {
    Write-Host "Removing GTK files..."
    Remove-Item -Path "C:\gtk" -Recurse -Force -ErrorAction SilentlyContinue
}

foreach ($pkg in $config.PipxPackages) {
    if ($Force -or ($apps -contains $pkg)) {
        pipx uninstall $pkg -ErrorAction SilentlyContinue
        Write-Host "Uninstalled pipx package: $pkg"
    }
}

# Remove environment variables that were tracked
$envVars = Get-TrackedEnvVars
foreach ($var in $envVars) {
    try {
        Remove-ItemProperty -Path "HKCU:\Environment" -Name $var -ErrorAction SilentlyContinue
        Write-Host "Removed environment variable: $var"
    } catch {
        Write-Host "Could not remove environment variable: $var"
    }
}

if (Test-Path "HKCU:\Software\lcapy-w64-dev-env") {
    Remove-Item -Path "HKCU:\Software\lcapy-w64-dev-env" -Recurse -Force
    Write-Host "Cleaned up registry entries."
}

Notify-EnvVarChange
Write-Host "Teardown complete."
