function Set-PersistentEnvVar {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Value,
        [switch]$Append, [switch]$Prepend, [switch]$Force
    )
    $envKey = "HKCU:\Environment"
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
    $regPath = "HKCU:\Software\lcapy-w64-dev-env\InstalledApps"
    if (-not (Test-Path $regPath)) {
        New-Item -Path $regPath -Force | Out-Null
    }
    New-ItemProperty -Path $regPath -Name $AppName -Value 1 -PropertyType DWord -Force | Out-Null
}

function Get-InstalledApps {
    $regPath = "HKCU:\Software\lcapy-w64-dev-env\InstalledApps"
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
$LcapyEnvRegistry = "HKCU:\Software\lcapy-w64-dev-env\EnvironmentVars"

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
