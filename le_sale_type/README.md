# Sale Order Type with Dynamic Filters

## Overview

This enhanced module provides comprehensive sale order type management with dynamic search filters that automatically update when new order types are created.

## Features

### 🔍 Dynamic Search Filters
- **Automatic Filter Generation**: When you create a new sale order type, a corresponding search filter is automatically created in the sale orders view
- **Real-time Updates**: Filters are updated immediately when sale order types are modified or deleted
- **Enhanced Search**: Quick search by sale type name, description, or prefix

### 📊 Analytics & Statistics
- **Order Count**: See how many orders are associated with each sale type
- **Total Amount**: View the total monetary value for each sale type
- **Visual Dashboard**: Kanban view with color-coded cards showing statistics

### 🎨 Enhanced Views
- **Kanban View**: Visual cards with statistics and color coding
- **Enhanced Tree View**: Sortable columns with statistics
- **Smart Buttons**: Quick access to view orders by type
- **Form View**: Comprehensive editing with statistics display

### ⚡ Advanced Features
- **Sequence Management**: Drag-and-drop ordering of sale types
- **Color Coding**: Assign colors to different sale types for visual identification
- **Automatic Prefixes**: Sale order numbers automatically use the type's prefix
- **Quick Actions**: One-click access to view all orders of a specific type

## Technical Implementation

### Dynamic Filter System
The module uses a combination of:
1. **JavaScript Components**: Dynamic injection of filters into the search view
2. **Controller Endpoints**: RESTful API for fetching filter data
3. **Model Enhancements**: Computed fields for real-time statistics
4. **Event Triggers**: Automatic filter updates on type creation/modification

### API Endpoints
- `/sale_order_type/get_dynamic_filters`: Returns JSON array of dynamic filters
- `/sale_order_type/get_sale_orders_by_type`: Returns filtered order data

### Model Extensions
- **sale.order.type**: Enhanced with statistics and filter management
- **sale.order**: Extended with improved search capabilities

## Usage

### Creating Sale Order Types
1. Go to **Sales → Configuration → Sale Order Types**
2. Click **Create** and fill in the required information:
   - Name: Display name for the sale type
   - Sequence: For ordering in lists
   - Prefix: Will be used in sale order numbers
   - Description: Optional description
   - Color: For visual identification

### Using Dynamic Filters
1. Go to **Sales → Orders → Orders by Type** (new menu item)
2. Use the search filters that are automatically generated for each sale type
3. Filters will show the sale type name followed by "Orders"
4. Click any filter to see only orders of that type

### Viewing Statistics
- **Kanban View**: Shows order count and total amount for each type
- **Form View**: Click the "Orders" smart button to see detailed statistics
- **Tree View**: Order count and total amount columns

## Installation

1. Copy the module to your addons directory
2. Update the app list in Odoo
3. Install "Sale Order Type with Dynamic Filters"
4. The module will automatically enhance existing sale order views

## Compatibility

- **Odoo Version**: 17.0+
- **Dependencies**: sale module
- **Browser Support**: Modern browsers with JavaScript ES6+ support

## Configuration

No additional configuration required. The module works out of the box and automatically:
- Creates dynamic filters for existing sale order types
- Updates filters when types are created/modified/deleted
- Maintains filter state across page reloads

## Benefits

1. **Improved User Experience**: Quick access to orders by type
2. **Better Organization**: Visual categorization of sale orders
3. **Real-time Analytics**: Instant statistics for business insights
4. **Automated Workflow**: No manual filter management required
5. **Enhanced Reporting**: Better segmentation for sales analysis

## Support

For technical support or feature requests, please contact the development team.

## License

LGPL-3 - See LICENSE file for details.
