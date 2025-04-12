Write-Host "Running teardown test..."

$installReg = "HKCU:\Software\lcapy-w64-dev-env\InstalledApps"
$envVarReg = "HKCU:\Software\lcapy-w64-dev-env\EnvironmentVars"

function Test-RegistryCleared($path) {
    if (Test-Path $path) {
        $props = (Get-ItemProperty -Path $path | Select-Object -ExcludeProperty PS*).PSObject.Properties.Name
        if ($props.Count -eq 0) {
            Write-Host "Registry $path is cleared."
        } else {
            Write-Host "Registry $path still contains: $($props -join ', ')"
        }
    } else {
        Write-Host "Registry $path does not exist."
    }
}

Test-RegistryCleared $installReg
Test-RegistryCleared $envVarReg

$expectedVars = @("Path", "LIB", "INCLUDE", "GI_TYPELIB_PATH")
foreach ($var in $expectedVars) {
    if ($env:$var) {
        Write-Host "Env var $var still set."
    } else {
        Write-Host "Env var $var is cleared."
    }
}
