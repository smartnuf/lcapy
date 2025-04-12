@{
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
