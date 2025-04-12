. "$PSScriptRoot\lcapy-w64-dev-env.psm1"
$config = Import-PowerShellDataFile "$PSScriptRoot\lcapy-w64-dev-env-config.psd1"

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
    Expand-Archive -Path "GTK3_Gvsbuild.zip" -DestinationPath "C:\gtk"
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
