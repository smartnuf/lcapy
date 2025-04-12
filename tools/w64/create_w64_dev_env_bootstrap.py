from pathlib import Path
import zipfile

# Create a project folder
project_root = Path("lcapy-w64-dev-env-bootstrap")
project_root.mkdir(exist_ok=True)

# lcapy-w64-dev-env-config.psd1: Declarative configuration for the environment.
config_text = """@{
    ScoopPackages = @(
        @{ Name = "main/ghostscript"; Command = "gs" },
        @{ Name = "main/miktex"; Command = "miktex" },
        @{ Name = "main/imagemagick"; Command = "magick" },
        @{ Name = "main/python"; Command = "python" },
        @{ Name = "main/pipx"; Command = "pipx" },
        @{ Name = "main/git"; Command = "git" }
    )

    PipxPackages = @(
        "jupyterlab",
        "spyder"
    )

    GTK = @{
        Version = "2025.4.0"
        URL     = "https://github.com/wingtk/gvsbuild/releases/download/2025.4.0/GTK3_Gvsbuild_2025.4.0_x64.zip"
        Paths   = @{
            BIN              = "C:\\gtk\\bin"
            LIB              = "C:\\gtk\\lib"
            GI_TYPELIB_PATH  = "C:\\gtk\\lib\\girepository-1.0"
            INCLUDE          = @(
                "C:\\gtk\\include",
                "C:\\gtk\\include\\cairo",
                "C:\\gtk\\include\\glib-2.0",
                "C:\\gtk\\include\\gobject-introspection-1.0",
                "C:\\gtk\\lib\\glib-2.0\\include"
            )
        }
    }
}
"""
config_file = project_root / "lcapy-w64-dev-env-config.psd1"
config_file.write_text(config_text)

# lcapy-w64-dev-env-setup.ps1: Installs the environment, updates registry/env vars, etc.
setup_text = """\
. "$PSScriptRoot\\lcapy-w64-dev-env.psm1"
$config = Import-PowerShellDataFile "$PSScriptRoot\\lcapy-w64-dev-env-config.psd1"

Ensure-Scoop

foreach ($pkg in $config.ScoopPackages) {
    Ensure-Installed -CommandName $pkg.Command -ScoopPackageName "main/$pkg.Name"
}

foreach ($pkg in $config.PipxPackages) {
    if (-not (Get-Command $pkg -ErrorAction SilentlyContinue)) {
        pipx install $pkg
        Register-InstalledApp -AppName $pkg
    }
}

if (-not (Get-Command gtk-query-settings -ErrorAction SilentlyContinue)) {
    $gtk = $config.GTK
    Write-Host "Installing GTK..."
    Invoke-WebRequest -Uri $gtk.URL -OutFile "GTK3_Gvsbuild.zip"
    Expand-Archive -Path "GTK3_Gvsbuild.zip" -DestinationPath "C:\\gtk"
    Set-PersistentEnvVar -Name "Path" -Value $gtk.Paths.BIN -Prepend
    Set-PersistentEnvVar -Name "LIB" -Value $gtk.Paths.LIB -Prepend
    Set-PersistentEnvVar -Name "GI_TYPELIB_PATH" -Value $gtk.Paths.GI_TYPELIB_PATH -Prepend
    Set-PersistentEnvVar -Name "INCLUDE" -Value ($gtk.Paths.INCLUDE -join ";") -Prepend
    Register-InstalledApp -AppName "gtk3_gvsbuild"
}

# Register each environment variable change so that teardown can remove them later
Register-EnvVarAdded -Name Path
Register-EnvVarAdded -Name LIB
Register-EnvVarAdded -Name GI_TYPELIB_PATH
Register-EnvVarAdded -Name INCLUDE

Notify-EnvVarChange
"""
setup_script = project_root / "lcapy-w64-dev-env-setup.ps1"
setup_script.write_text(setup_text)

# lcapy-w64-dev-env-teardown.ps1: Uninstalls installed tools and removes tracked env vars.
teardown_text = """\
param (
    [switch]$Force
)

. "$PSScriptRoot\\lcapy-w64-dev-env.psm1"
$config = Import-PowerShellDataFile "$PSScriptRoot\\lcapy-w64-dev-env-config.psd1"

$apps = Get-InstalledApps
foreach ($app in $apps) {
    Write-Host "Uninstalling $app..."
    scoop uninstall $app -ErrorAction SilentlyContinue
}

if ($Force -or ($apps -contains "gtk3_gvsbuild")) {
    Write-Host "Removing GTK files..."
    Remove-Item -Path "C:\\gtk" -Recurse -Force -ErrorAction SilentlyContinue
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
        Remove-ItemProperty -Path "HKCU:\\Environment" -Name $var -ErrorAction SilentlyContinue
        Write-Host "Removed environment variable: $var"
    } catch {
        Write-Host "Could not remove environment variable: $var"
    }
}

if (Test-Path "HKCU:\\Software\\lcapy-w64-dev-env") {
    Remove-Item -Path "HKCU:\\Software\\lcapy-w64-dev-env" -Recurse -Force
    Write-Host "Cleaned up registry entries."
}

Notify-EnvVarChange
Write-Host "Teardown complete."
"""
teardown_script = project_root / "lcapy-w64-dev-env-teardown.ps1"
teardown_script.write_text(teardown_text)

# lcapy-w64-dev-env-test.ps1: Diagnostic test of the setup.
test_text = """\
param (
    [string]$ReportPath = "$PSScriptRoot\\lcapy-w64-dev-env-test-report.json"
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
"""
test_script = project_root / "lcapy-w64-dev-env-test.ps1"
test_script.write_text(test_text)

# lcapy-w64-dev-env-test-teardown.ps1: Unit test for the teardown process.
test_teardown_text = """\
Write-Host "Running teardown test..."

$installReg = "HKCU:\\Software\\lcapy-w64-dev-env\\InstalledApps"
$envVarReg = "HKCU:\\Software\\lcapy-w64-dev-env\\EnvironmentVars"

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
"""
test_teardown_script = project_root / "lcapy-w64-dev-env-test-teardown.ps1"
test_teardown_script.write_text(test_teardown_text)

# lcapy-w64-dev-env.psm1: The PowerShell module with reusable functions.
module_text = """\
function Set-PersistentEnvVar {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Value,
        [switch]$Append, [switch]$Prepend, [switch]$Force
    )
    $envKey = "HKCU:\\Environment"
    $existing = (Get-ItemProperty -Path $envKey -Name $Name -ErrorAction SilentlyContinue).$Name
    if ($Force -or -not $existing) {
        $newValue = $Value
    } else {
        $separator = ";"
        $entries = $existing -split $separator
        $alreadyPresent = $entries -contains $Value
        if ($alreadyPresent -and -not $Force) {
            Write-Host "$Name already contains: $Value"
            return
        }
        $newValue = if ($Append) { "$existing$separator$Value" } elseif ($Prepend) { "$Value$separator$existing" } else { $Value }
    }
    Set-ItemProperty -Path $envKey -Name $Name -Value $newValue
    Write-Host "Updated $Name with value: $newValue"
}

function Notify-EnvVarChange {
    $signature = '[DllImport("user32.dll")] public static extern int SendMessageTimeout(int hWnd, int Msg, int wParam, int lParam, int fuFlags, int uTimeout, out int lpdwResult);'
    Add-Type -Namespace Win32 -Name NativeMethods -MemberDefinition $signature -ErrorAction SilentlyContinue | Out-Null
    [Win32.NativeMethods]::SendMessageTimeout(0xffff, 0x1A, 0, [IntPtr]::Zero, 2, 5000, [ref]0) | Out-Null
    Write-Host "Notified system of environment variable changes."
}

function Register-InstalledApp {
    param ([Parameter(Mandatory)][string]$AppName)
    $regPath = "HKCU:\\Software\\lcapy-w64-dev-env\\InstalledApps"
    if (-not (Test-Path $regPath)) {
        New-Item -Path $regPath -Force | Out-Null
    }
    New-ItemProperty -Path $regPath -Name $AppName -Value 1 -PropertyType DWord -Force | Out-Null
}

function Get-InstalledApps {
    $regPath = "HKCU:\\Software\\lcapy-w64-dev-env\\InstalledApps"
    if (Test-Path $regPath) {
        Get-ItemProperty -Path $regPath | Select-Object -ExcludeProperty PS* | Get-Member -MemberType NoteProperty | ForEach-Object { $_.Name }
    } else {
        return @()
    }
}

function Ensure-Installed {
    param ([string]$CommandName, [string]$ScoopPackageName)
    if (Get-Command $CommandName -ErrorAction SilentlyContinue) {
        Write-Host "$CommandName is already installed."
    } else {
        Write-Host "Installing $CommandName..."
        scoop install $ScoopPackageName
        Register-InstalledApp -AppName $CommandName
    }
}

function Ensure-Scoop {
    if (Get-Command scoop -ErrorAction SilentlyContinue) {
        Write-Host "Scoop is installed."
    } else {
        Write-Host "Installing Scoop..."
        Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
    }
    scoop bucket add main
    scoop bucket add extras
}

# Environment variable tracking
$LcapyEnvRegistry = "HKCU:\\Software\\lcapy-w64-dev-env\\EnvironmentVars"

function Register-EnvVarAdded {
    param ([string]$Name)
    if (-not (Test-Path $LcapyEnvRegistry)) {
        New-Item -Path $LcapyEnvRegistry -Force | Out-Null
    }
    New-ItemProperty -Path $LcapyEnvRegistry -Name $Name -Value 1 -PropertyType DWord -Force | Out-Null
}

function Get-TrackedEnvVars {
    if (Test-Path $LcapyEnvRegistry) {
        Get-ItemProperty -Path $LcapyEnvRegistry | Select-Object -ExcludeProperty PS* | Get-Member -MemberType NoteProperty | ForEach-Object { $_.Name }
    } else {
        return @()
    }
}
"""
module_script = project_root / "lcapy-w64-dev-env.psm1"
module_script.write_text(module_text)

# lcapy-w64-dev-env.psd1: Module manifest.
module_manifest_text = """@{
    RootModule = 'lcapy-w64-dev-env.psm1'
    ModuleVersion = '1.0.0'
    GUID = '12345678-90ab-cdef-1234-567890abcdef'
    Author = 'DevEnvBootstrap'
    Description = 'Helper functions for managing the lcapy-w64-dev-env'
    PowerShellVersion = '5.1'
    FunctionsToExport = @(
        'Set-PersistentEnvVar',
        'Notify-EnvVarChange',
        'Register-InstalledApp',
        'Get-InstalledApps',
        'Ensure-Installed',
        'Ensure-Scoop',
        'Register-EnvVarAdded',
        'Get-TrackedEnvVars'
    )
    PrivateData = @{}
}
"""
module_manifest = project_root / "lcapy-w64-dev-env.psd1"
module_manifest.write_text(module_manifest_text)

# Dockerfile: For testing the environment in a Windows container.
dockerfile_text = """\
# Use Windows Server Core as the base image
FROM mcr.microsoft.com/windows/servercore:ltsc2022

SHELL ["cmd", "/S", "/C"]

# Install PowerShell 7
RUN powershell -Command "Invoke-WebRequest -Uri https://github.com/PowerShell/PowerShell/releases/download/v7.4.0/PowerShell-7.4.0-win-x64.msi -OutFile pwsh.msi"
RUN msiexec /i pwsh.msi /qn

# Set Execution Policy for Scoop
RUN powershell -Command "Set-ExecutionPolicy RemoteSigned -Scope LocalMachine -Force"

# Copy project files into container
COPY . C:\\lcapy-env
WORKDIR C:\\lcapy-env

# Default command runs the test harness
CMD ["pwsh.exe", "-File", "run-all-tests.ps1"]
"""
dockerfile = project_root / "Dockerfile"
dockerfile.write_text(dockerfile_text)

# run-all-tests.ps1: Runs full install, test, teardown, and post-teardown tests.
run_all_tests_text = """\
Write-Host "Running full install + test + teardown + verify sequence..."

.\\lcapy-w64-dev-env-setup.ps1
.\\lcapy-w64-dev-env-test.ps1
.\\lcapy-w64-dev-env-teardown.ps1
.\\lcapy-w64-dev-env-test-teardown.ps1

Write-Host "All phases completed."
"""
run_all_tests = project_root / "run-all-tests.ps1"
run_all_tests.write_text(run_all_tests_text)

# Create the ZIP file
zip_path = Path("w64-dev-env-bootstrap.zip")
with zipfile.ZipFile(zip_path, "w") as zipf:
    for file_path in project_root.rglob("*"):
        zipf.write(file_path, arcname=file_path.relative_to(project_root))

print(f"w64-dev-env-bootstrap.zip created in {zip_path.resolve()}")

