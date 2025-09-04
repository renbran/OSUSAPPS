# SCHOLARIX Commission Statement System

A comprehensive commission statement reporting system designed specifically for SCHOLARIX that provides consolidated reports for all agents with professional PDF output.

## Overview

The SCHOLARIX Commission Statement System transforms the standard commission reporting into a powerful, multi-agent reporting platform with professional branding and advanced analytics capabilities.

## Key Features

### 🎯 Multi-Agent Consolidated Reports
- Generate comprehensive reports covering all agents in a single document
- Executive summary with overview statistics
- Individual agent breakdowns with detailed order information
- Professional SCHOLARIX branding throughout

### 📊 Commission Calculation Logic
- **Direct Sales**: 5% commission rate on direct sales transactions
- **Referral Bonus**: 2% commission rate on successful referrals
- **Team Override**: 1% commission rate for team management activities
- Automatic categorization and calculation based on existing commission_ax data

### 🔍 Advanced Filtering & Reporting
- **Period Selection**: Current month, last month, quarterly, yearly, or custom date ranges
- **Agent Selection**: All agents, specific agents, or agents with commission only
- **Commission Type Filters**: Filter by direct sales, referrals, or team override
- **Payment Status Filters**: Pending, paid, or cancelled commissions
- **Minimum Threshold**: Filter agents by minimum commission amounts

### 📱 Professional Output Formats
- **PDF Reports**: SCHOLARIX-branded with signature sections and terms
- **Excel Spreadsheets**: Detailed data export for analysis
- **Individual Statements**: Personal commission statements for agents
- **Dashboard Views**: Kanban and analytical views for management

### 🔐 Security & Access Control
- **Sales Managers**: Full access to all reports and agent data
- **Agents**: Access only to their personal commission statements
- **Accounting Team**: Read-only access for verification and payment processing
- **Commission Analysts**: Report generation and analysis capabilities

## Installation & Setup

### Prerequisites
- Odoo 17.0+
- commission_ax module (for commission data)
- enhanced_status module (for order status tracking)
- xlsxwriter Python library (for Excel export)

### Installation Steps
1. Copy the module to your Odoo addons directory
2. Update the Apps List in Odoo
3. Install the "SCHOLARIX Commission Statement System" module
4. Configure user permissions in Settings → Users & Companies → Groups

## Usage Guide

### Generating Consolidated Reports

1. **Access the Report Wizard**
   - Go to Sales → SCHOLARIX Commission → Report Generator
   - Or use the button in any partner's Commission Statement tab

2. **Configure Report Parameters**
   - Select the reporting period (quick select or custom dates)
   - Choose agent selection (all agents, specific agents, or with commission only)
   - Apply filters for commission type and payment status
   - Set sorting and grouping options

3. **Generate Report**
   - Choose output format (PDF, Excel, or both)
   - Click "Generate Report" to create the comprehensive document

### Individual Agent Statements

1. **From Partner Record**
   - Open any partner/agent record
   - Go to the "Commission Statement" tab
   - Click "Generate SCHOLARIX Statement"

2. **From Statements List**
   - Go to Sales → SCHOLARIX Commission → Commission Statements
   - Create new statement or view existing ones
   - Use the form view to manage statement details

## Technical Architecture

### Models

#### `scholarix.commission.statement`
- Main model for commission statements
- Tracks agent, period, totals, and status
- Handles commission calculation and report generation

#### `scholarix.commission.line`
- Individual order commission lines
- Links to sale orders and tracks commission details
- Categorizes commission types (direct, referral, team)

#### `scholarix.commission.report.wizard`
- Wizard for consolidated report generation
- Handles filtering, sorting, and output formatting
- Manages Excel and PDF report creation

### Integration Points

- **commission_ax**: Extracts commission data from existing commission fields
- **enhanced_status**: Uses order status for commission eligibility
- **res.partner**: Extends partner model with SCHOLARIX-specific methods
- **sale.order**: Reads commission data from sale orders

## Support

For technical support or customization requests, contact:
- **Development Team**: OSUS Properties Development Team
- **Website**: https://www.osusproperties.com

## License

This module is licensed under LGPL-3.

---

**SCHOLARIX Commission Statement System** - Empowering commission management with professional reporting and comprehensive analytics.
