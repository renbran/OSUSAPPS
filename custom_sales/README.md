# Custom Sales Dashboard Pro

An advanced, branded sales dashboard for Odoo 17 featuring comprehensive analytics, KPI tracking, and business intelligence tools.

## 🎨 Design Theme

- **Primary Color**: Burgundy (#8B0000)
- **Secondary Color**: Gold (#FFD700) 
- **Accent Color**: Light Gold (#F5DEB3)
- **Professional, modern UI with smooth animations**

## ✨ Features

### 📊 Advanced Dashboard
- Real-time sales analytics and KPIs
- Interactive charts and graphs with Chart.js
- Multi-period comparison and forecasting
- Mobile-responsive design
- Auto-refresh capabilities

### 📈 Custom Sales Management
- Extended sales order model with additional fields
- Custom workflow states and approval processes
- Priority management and customer categorization
- Profit margin tracking and analysis

### 🎯 KPI Tracking
- Configurable KPI widgets
- Target setting and achievement tracking
- Period-over-period comparisons
- Visual status indicators (good/warning/critical)

### 📋 Business Intelligence
- Sales performance metrics
- Customer lifetime value analysis
- Product performance analytics
- Geographic sales distribution
- Sales team leaderboards

### 📊 Reporting & Export
- PDF dashboard reports
- Excel data exports
- CSV data downloads
- Scheduled report generation

### 🔐 Security & Access Control
- Role-based access control
- User and group-specific dashboards
- Multi-company support
- Comprehensive audit trails

## 🚀 Installation

### Prerequisites
- Odoo 17.0+
- Python packages: `xlsxwriter`, `pandas`, `numpy`
- Chart.js (included in assets)

### Installation Steps

1. **Copy Module**
   ```bash
   cp -r custom_sales /path/to/odoo/addons/
   ```

2. **Install Dependencies**
   ```bash
   pip3 install xlsxwriter pandas numpy
   ```

3. **Update Odoo**
   ```bash
   # Restart Odoo server
   # Update apps list in Odoo
   # Install "Custom Sales Dashboard Pro" module
   ```

4. **Configure Dashboard**
   - Go to Custom Sales Pro → Configuration → Dashboard Config
   - Create your first dashboard configuration
   - Set up KPIs and charts as needed

## 🛠️ Configuration

### Dashboard Setup

1. **Create Dashboard Configuration**
   ```
   Navigation: Custom Sales Pro → Configuration → Dashboard Config
   ```
   - Set dashboard name and preferences
   - Configure colors and theme
   - Set refresh intervals
   - Assign users/groups

2. **Configure KPIs**
   ```
   Navigation: Custom Sales Pro → Configuration → KPI Configuration
   ```
   - Define KPI calculations
   - Set targets and thresholds
   - Configure display options
   - Enable period comparisons

3. **Setup Charts**
   ```
   Navigation: Custom Sales Pro → Configuration → Chart Configuration
   ```
   - Create chart configurations
   - Define data sources
   - Set chart types and options
   - Configure filters and grouping

### User Access

1. **Assign Groups**
   - `Sales Dashboard User`: View dashboard and orders
   - `Sales Dashboard Manager`: Configure dashboards
   - `Sales Dashboard Administrator`: Full system access

2. **Dashboard Access**
   ```
   Navigation: Custom Sales Pro → Dashboard
   ```

## 📊 Usage

### Creating Custom Sales Orders

1. Navigate to `Custom Sales Pro → Sales Orders → All Orders`
2. Click "Create" to add a new custom sales order
3. Fill in required fields:
   - Customer information
   - Sales team and salesperson
   - Custom fields for business data
   - Estimated revenue and priority

### Using the Dashboard

1. **Main Dashboard**
   - Access via `Custom Sales Pro → Dashboard`
   - View real-time KPIs and charts
   - Use date filters for period analysis
   - Export reports as needed

2. **Date Filtering**
   - Use date range selectors
   - Quick filters (Today, This Week, etc.)
   - Real-time data updates

3. **Exporting Data**
   - PDF reports for presentations
   - Excel exports for analysis
   - CSV downloads for data processing

### Analytics and Reporting

1. **Sales Overview**
   ```
   Navigation: Custom Sales Pro → Analytics → Sales Overview
   ```

2. **KPI Analysis**
   ```
   Navigation: Custom Sales Pro → Analytics → KPI Analysis
   ```

3. **Custom Reports**
   ```
   Navigation: Custom Sales Pro → Reports
   ```

## 🔧 Customization

### Adding Custom KPIs

1. Create new KPI configuration
2. Define calculation method:
   ```python
   # Example custom calculation
   def custom_kpi_calculation(self):
       # Your custom logic here
       return calculated_value
   ```

3. Set display formatting and thresholds

### Custom Chart Types

1. Extend chart configuration model
2. Add new chart types in generator:
   ```python
   def _generate_custom_chart_data(self, records, chart_config):
       # Custom chart data generation
       return chart_data
   ```

### Theme Customization

1. Modify CSS variables in `branded_theme.css`:
   ```css
   :root {
       --osus-burgundy: #YourColor;
       --osus-gold: #YourColor;
       --osus-light-gold: #YourColor;
   }
   ```

## 🧪 Testing

### Running Tests

```bash
# Run all module tests
odoo-bin -i custom_sales --test-enable --stop-after-init

# Run specific test class
odoo-bin --test-tags custom_sales.TestCustomSalesOrder
```

### Test Coverage

- Unit tests for all models
- Integration tests for controllers
- UI tests for dashboard functionality
- Performance tests for large datasets

## 🚀 API Documentation

### REST Endpoints

#### Dashboard Data
```
GET/POST /custom_sales/api/dashboard_data
Parameters: dashboard_id, date_from, date_to
Response: Complete dashboard data
```

#### KPI Data
```
POST /custom_sales/api/kpis
Parameters: dashboard_id, date_from, date_to
Response: KPI values and comparisons
```

#### Chart Data
```
POST /custom_sales/api/charts
Parameters: dashboard_id, date_from, date_to
Response: Chart configurations and data
```

#### Sales Overview
```
POST /custom_sales/api/sales_overview
Parameters: date_from, date_to
Response: Sales summary and breakdowns
```

### Model API

#### Custom Sales Order
```python
# Create custom sales order
order = env['custom.sales.order'].create({
    'name': 'SO001',
    'custom_field_1': 'Value',
    'custom_field_2': 100,
    'custom_field_3': partner_id,
})

# Calculate KPI
kpi_value = env['sales.kpi.calculator'].calculate_kpi(kpi_config)

# Generate chart data
chart_data = env['sales.chart.generator'].generate_chart_data(chart_config)
```

## 📱 Mobile Support

- Responsive dashboard design
- Touch-friendly controls
- Optimized charts for mobile
- Progressive web app capabilities

## 🔄 Updates and Maintenance

### Regular Updates
- Keep dependencies updated
- Monitor performance metrics
- Review security configurations
- Update dashboard configurations as needed

### Backup Recommendations
- Regular database backups
- Configuration export/import
- Dashboard settings backup

## 🆘 Troubleshooting

### Common Issues

1. **Dashboard Not Loading**
   - Check user permissions
   - Verify dashboard configuration
   - Review server logs

2. **Charts Not Displaying**
   - Ensure Chart.js is loaded
   - Check data source configurations
   - Verify model access rights

3. **KPI Calculation Errors**
   - Validate KPI domain filters
   - Check field names and types
   - Review calculation logic

4. **Export Issues**
   - Verify xlsxwriter installation
   - Check file permissions
   - Review export configurations

### Log Files
```bash
# Check Odoo logs
tail -f /var/log/odoo/odoo.log

# Check dashboard-specific logs
grep "custom_sales" /var/log/odoo/odoo.log
```

## 🤝 Support

- **Documentation**: This README and inline code comments
- **Issues**: Report bugs via your support channel
- **Feature Requests**: Submit enhancement requests
- **Training**: Available for advanced configurations

## 📝 License

LGPL-3 - See LICENSE file for details

## 👥 Credits

- **Developer**: OSUS Business Solutions
- **Designer**: Custom Sales Dashboard Pro Team
- **Contributors**: Odoo Community

---

**Custom Sales Dashboard Pro** - Transforming sales data into actionable insights with style and intelligence.
