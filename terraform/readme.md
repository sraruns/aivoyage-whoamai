
# Create dev/test/prod environment
.\scripts\deploy.ps1 -Environment test



# Destroy dev environment
.\scripts\destroy.ps1 -Environment dev

# Destroy test environment
.\scripts\destroy.ps1 -Environment test

# Destroy prod environment
.\scripts\destroy.ps1 -Environment prod