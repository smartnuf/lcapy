function Set-PersistentEnvVar {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [string]$Value,
        [switch]$Append,
        [switch]$Prepend,
        [switch]$Force
    )

    $envKey = "HKCU:\Environment"
    $existing = (Get-ItemProperty -Path $envKey -Name $Name -ErrorAction SilentlyContinue).$Name

    if ($Force -or -not $existing) {
        $newValue = $Value
    }
    else {
        $separator = ";"
        $entries = $existing -split $separator
        $alreadyPresent = $entries -contains $Value

        if ($alreadyPresent -and -not $Force) {
            Write-Host "ℹ️ $Name already contains: $Value"
            return
        }

        if ($Append) {
            $newValue = "$existing$separator$Value"
        } elseif ($Prepend) {
            $newValue = "$Value$separator$existing"
        } else {
            $newValue = $Value
        }
    }

    Set-ItemProperty -Path $envKey -Name $Name -Value $newValue
    Write-Host "✅ Updated $Name with value: $newValue"
}

function Notify-EnvVarChange {
    $signature = @"
[DllImport("user32.dll", SetLastError=true)]
public static extern int SendMessageTimeout(
    int hWnd, int Msg, int wParam, int lParam, int fuFlags, int uTimeout, out int lpdwResult);
"@
    Add-Type -Namespace Win32 -Name NativeMethods -MemberDefinition $signature -ErrorAction SilentlyContinue | Out-Null
    $HWND_BROADCAST = 0xffff
    $WM_SETTINGCHANGE = 0x1A
    $result = 0
    [Win32.NativeMethods]::SendMessageTimeout($HWND_BROADCAST, $WM_SETTINGCHANGE, 0, [IntPtr]::Zero, 2, 5000, [ref]$result) | Out-Null
    Write-Host "🔁 Notified system of environment variable changes."
}

function Ensure-Installed {
    param (
        [string]$CommandName,
        [string]$ScoopPackageName
    )
    if (Get-Command $CommandName -ErrorAction SilentlyContinue) {
        Write-Host "✅ $CommandName is already installed."
    } else {
        Write-Host "📦 Installing $CommandName..."
        scoop install $ScoopPackageName
    }
}

function Ensure-Scoop {
    if (Get-Command scoop -ErrorAction SilentlyContinue) {
        Write-Host "✅ Scoop is installed."
    } else {
        Write-Host "📦 Installing Scoop..."
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
    }

    scoop bucket add main
    scoop bucket add extras
}
