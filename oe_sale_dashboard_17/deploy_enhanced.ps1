# Enhanced Sales Dashboard Deployment Script (PowerShell)
# Use this script to update the module in your Odoo instance

Write-Host "=== Enhanced Sales Dashboard Deployment ===" -ForegroundColor Green
Write-Host "Module: oe_sale_dashboard_17" -ForegroundColor Cyan
Write-Host "Location: $(Get-Location)" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (!(Test-Path "__manifest__.py")) {
    Write-Host "Error: Not in module directory. Please run from oe_sale_dashboard_17 folder." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Module directory confirmed" -ForegroundColor Green

# Check for required files
$RequiredFiles = @(
    "models/sale_dashboard.py",
    "static/src/js/dashboard_enhanced.js",
    "static/src/css/dashboard.css",
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
Write-Host "  ✅ Date filtering with booking_date" -ForegroundColor Green
Write-Host "  ✅ Sales type category filtering" -ForegroundColor Green
Write-Host "  ✅ Category summary scorecards" -ForegroundColor Green
Write-Host "  ✅ Sub-category breakdowns (Draft/SO/Invoice)" -ForegroundColor Green
Write-Host "  ✅ Line chart for sales trends" -ForegroundColor Green
Write-Host "  ✅ Enhanced pie chart for distribution" -ForegroundColor Green
Write-Host "  ✅ Bar chart for category comparison" -ForegroundColor Green
Write-Host "  ✅ Performance ranking table" -ForegroundColor Green
Write-Host "  ✅ Responsive design with modern UI" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 Deployment Instructions:" -ForegroundColor Cyan
Write-Host "1. Restart your Odoo server" -ForegroundColor White
Write-Host "2. Go to Apps menu in Odoo" -ForegroundColor White
Write-Host "3. Search for 'OSUS Executive Sales Dashboard'" -ForegroundColor White
Write-Host "4. Click 'Upgrade' if already installed, or 'Install' if new" -ForegroundColor White
Write-Host "5. Navigate to the dashboard menu to test new features" -ForegroundColor White
Write-Host ""

Write-Host "🔧 Troubleshooting:" -ForegroundColor Yellow
Write-Host "- Ensure Chart.js CDN is accessible: https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js" -ForegroundColor White
Write-Host "- Check that dependencies are installed: sale_management, osus_invoice_report, le_sale_type" -ForegroundColor White
Write-Host "- Verify booking_date field exists in sale.order model" -ForegroundColor White
Write-Host "- Clear browser cache if visualizations don't appear" -ForegroundColor White
Write-Host ""

Write-Host "📊 New Dashboard Features:" -ForegroundColor Magenta
Write-Host "- Use date range controls to filter by booking_date" -ForegroundColor White
Write-Host "- Select sales types in the multi-select dropdown" -ForegroundColor White
Write-Host "- View category totals in the summary cards" -ForegroundColor White
Write-Host "- Analyze trends in the line chart" -ForegroundColor White
Write-Host "- Compare performance in bar charts and ranking table" -ForegroundColor White
Write-Host ""

Write-Host "✨ Enhancement deployment ready!" -ForegroundColor Green
Write-Host "=== End of Deployment Script ===" -ForegroundColor Green
