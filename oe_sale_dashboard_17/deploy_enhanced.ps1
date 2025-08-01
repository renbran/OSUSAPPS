# Enhanced Sales Dashboard CloudPepper Deployment Script (PowerShell)
# Use this script to deploy the module to CloudPepper Odoo instance

Write-Host "=== Enhanced Sales Dashboard CloudPepper Deployment ===" -ForegroundColor Green
Write-Host "Module: oe_sale_dashboard_17" -ForegroundColor Cyan
Write-Host "CloudPepper Location: /var/odoo/coatest/extra-addons/odoo17_final.git-6880b7fcd4844/oe_sale_dashboard_17" -ForegroundColor Cyan
Write-Host "Local Location: $(Get-Location)" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (!(Test-Path "__manifest__.py")) {
    Write-Host "Error: Not in module directory. Please run from oe_sale_dashboard_17 folder." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Module directory confirmed" -ForegroundColor Green

# Check for merged best practices files
$RequiredFiles = @(
    "models/sale_dashboard.py",
    "static/src/js/dashboard_merged.js",
    "static/src/js/dashboard.js", 
    "static/src/css/dashboard_merged.css",
    "static/src/css/dashboard.css",
    "static/src/xml/dashboard_merged_template.xml",
    "static/src/xml/dashboard_template.xml",
    "views/dashboard_views.xml"
)

Write-Host "🔍 Checking required files..." -ForegroundColor Yellow
foreach ($file in $RequiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file (missing)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📋 Enhanced Features Implemented:" -ForegroundColor Magenta
Write-Host "  ✅ Merged Best Practices from Version 1 & 2" -ForegroundColor Green
Write-Host "  ✅ Defensive field checking (booking_date/create_date)" -ForegroundColor Green
Write-Host "  ✅ Auto-refresh capability with configurable intervals" -ForegroundColor Green
Write-Host "  ✅ Enhanced KPIs (conversion rate, pipeline velocity)" -ForegroundColor Green
Write-Host "  ✅ Revenue growth calculation vs previous period" -ForegroundColor Green
Write-Host "  ✅ Performance tracking and load time monitoring" -ForegroundColor Green
Write-Host "  ✅ Data quality indicators" -ForegroundColor Green
Write-Host "  ✅ CSV export functionality" -ForegroundColor Green
Write-Host "  ✅ Responsive design with mobile-first approach" -ForegroundColor Green
Write-Host "  ✅ Registry error fixes for CloudPepper deployment" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 CloudPepper Deployment Instructions:" -ForegroundColor Cyan
Write-Host "1. Connect to your CloudPepper server via SSH" -ForegroundColor White
Write-Host "2. Navigate to: cd /var/odoo/coatest/extra-addons/odoo17_final.git-6880b7fcd4844/" -ForegroundColor White
Write-Host "3. Pull latest changes: git pull origin main" -ForegroundColor White
Write-Host "4. Update the module: python3 odoo-bin -u oe_sale_dashboard_17 -d your_database_name --stop-after-init" -ForegroundColor White
Write-Host "5. Restart Odoo service: sudo systemctl restart odoo" -ForegroundColor White
Write-Host "6. Clear browser cache and access the dashboard" -ForegroundColor White
Write-Host ""

Write-Host "🔧 CloudPepper Troubleshooting:" -ForegroundColor Yellow
Write-Host "- Ensure you have SSH access to your CloudPepper server" -ForegroundColor White
Write-Host "- Check Odoo service status: sudo systemctl status odoo" -ForegroundColor White
Write-Host "- View Odoo logs: sudo journalctl -u odoo -f" -ForegroundColor White
Write-Host "- Verify dependencies are installed: sale_management, osus_invoice_report, le_sale_type" -ForegroundColor White
Write-Host "- Check module path: /var/odoo/coatest/extra-addons/odoo17_final.git-6880b7fcd4844/oe_sale_dashboard_17" -ForegroundColor White
Write-Host "- Clear browser cache if visualizations don't appear" -ForegroundColor White
Write-Host "- Ensure Chart.js CDN is accessible from your server" -ForegroundColor White
Write-Host ""

Write-Host "📊 Enhanced Dashboard Features:" -ForegroundColor Magenta
Write-Host "- Smart date field detection (booking_date/create_date)" -ForegroundColor White
Write-Host "- Auto-refresh dashboard data every 30 seconds" -ForegroundColor White
Write-Host "- Enhanced KPIs: Conversion Rate, Pipeline Velocity, Revenue Growth" -ForegroundColor White
Write-Host "- Performance tracking with load time indicators" -ForegroundColor White
Write-Host "- Export dashboard data to CSV" -ForegroundColor White
Write-Host "- Responsive design that works on mobile devices" -ForegroundColor White
Write-Host "- Error recovery with graceful degradation" -ForegroundColor White
Write-Host ""

Write-Host "🌐 CloudPepper Access:" -ForegroundColor Cyan
Write-Host "After deployment, access your dashboard at:" -ForegroundColor White
Write-Host "https://your-cloudpepper-domain.com/web#action=oe_sale_dashboard_17_tag" -ForegroundColor Yellow
Write-Host ""

Write-Host "✨ Enhancement deployment ready!" -ForegroundColor Green
Write-Host "=== End of Deployment Script ===" -ForegroundColor Green
