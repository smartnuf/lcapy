param (
    [string]$ReportPath = "$PSScriptRoot\lcapy-w64-dev-env-test-report.json"
)

Write-Host "Running Dev Environment Validation..."

function Test-Command {
    param ([string]$Name)
    return [PSCustomObject]@{
        Name = $Name
        Present = [bool](Get-Command $Name -ErrorAction SilentlyContinue)
    }
}

function Test-EnvVar {
    param ([string]$Name)
    return [PSCustomObject]@{
        Name = $Name
        Set = [bool]$env:$Name
    }
}

$results = [ordered]@{
    Timestamp = (Get-Date).ToString("s")
    Commands = @()
    EnvVars  = @()
    PythonVersion = ""
    JupyterVersion = ""
    GTKSettings = ""
}

$commandList = @("gs", "miktex", "magick", "python", "pipx", "git", "jupyter-lab", "spyder", "gtk-query-settings")
$envVars = @("Path", "LIB", "INCLUDE", "GI_TYPELIB_PATH")
foreach ($cmd in $commandList) {
    $results.Commands += Test-Command -Name $cmd
}
foreach ($env in $envVars) {
    $results.EnvVars += Test-EnvVar -Name $env
}
$results.PythonVersion = (python --version 2>&1).Trim()
$results.JupyterVersion = (jupyter-lab --version 2>&1).Trim()
$results.GTKSettings = (gtk-query-settings 2>&1 | Out-String).Trim()

$results | ConvertTo-Json -Depth 5 | Out-File -Encoding UTF8 $ReportPath
Write-Host "Report written to $ReportPath"
