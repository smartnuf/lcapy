Write-Host "Running full install + test + teardown + verify sequence..."

.\lcapy-w64-dev-env-setup.ps1
.\lcapy-w64-dev-env-test.ps1
.\lcapy-w64-dev-env-teardown.ps1
.\lcapy-w64-dev-env-test-teardown.ps1

Write-Host "All phases completed."
