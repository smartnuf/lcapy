# Use Windows Server Core as the base image
FROM mcr.microsoft.com/windows/servercore:ltsc2022

SHELL ["cmd", "/S", "/C"]

# Install PowerShell 7
RUN powershell -Command "Invoke-WebRequest -Uri https://github.com/PowerShell/PowerShell/releases/download/v7.4.0/PowerShell-7.4.0-win-x64.msi -OutFile pwsh.msi"
RUN msiexec /i pwsh.msi /qn

# Set Execution Policy for Scoop
RUN powershell -Command "Set-ExecutionPolicy RemoteSigned -Scope LocalMachine -Force"

# Copy project files into container
COPY . C:/lcapy-w64-dev-env
WORKDIR C:/lcapy-w64-dev-env

# Default command runs the test harness
CMD ["pwsh.exe", "-File", "run-all-tests.ps1"]
