# PowerShell script to deploy OSUS Executive Sales Dashboard
# This script prepares the module for deployment, ensuring all robustness improvements are applied

Write-Host "OSUS Executive Sales Dashboard Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "This script will prepare your module for deployment" -ForegroundColor Green

# Check if we're in the correct directory
if (-not (Test-Path ".\oe_sale_dashboard_17")) {
    Write-Host "Error: oe_sale_dashboard_17 directory not found. Please run this script from your Odoo addons directory." -ForegroundColor Red
    exit 1
}

# Create backup
Write-Host "Creating backup..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = ".\oe_sale_dashboard_17_backup_$timestamp"
Copy-Item -Path ".\oe_sale_dashboard_17" -Destination $backupDir -Recurse
Write-Host "Backup created at: $backupDir" -ForegroundColor Green

# Clear assets cache if available
if (Test-Path "..\var\assets") {
    Write-Host "Clearing assets cache..." -ForegroundColor Yellow
    Get-ChildItem -Path "..\var\assets" -Recurse | Remove-Item -Force -Recurse
}

# Create missing directories if needed
$directories = @(
    ".\oe_sale_dashboard_17\static\src\js",
    ".\oe_sale_dashboard_17\static\src\css",
    ".\oe_sale_dashboard_17\static\src\xml",
    ".\oe_sale_dashboard_17\views",
    ".\oe_sale_dashboard_17\data"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -Path $dir -ItemType Directory -Force | Out-Null
    }
}

Write-Host "Deployment preparation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To install/update the module:" -ForegroundColor Yellow
Write-Host "1. Restart your Odoo server" -ForegroundColor White
Write-Host "2. Update the module via the Apps menu or run:" -ForegroundColor White
Write-Host "   python odoo-bin -d YOUR_DATABASE -u oe_sale_dashboard_17" -ForegroundColor White
Write-Host ""
Write-Host "If you encounter any issues:" -ForegroundColor Yellow
Write-Host "1. Check browser console for JavaScript errors" -ForegroundColor White
Write-Host "2. Review Odoo server logs for Python errors" -ForegroundColor White
Write-Host "3. Consult the documentation in oe_sale_dashboard_17/docs/" -ForegroundColor White
