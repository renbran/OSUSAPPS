# -*- coding: utf-8 -*-
"""
Excel report generation utilities for commission modules
This module provides standardized Excel report generation functionality
"""

import base64
import io
import logging
import xlsxwriter
from datetime import datetime

_logger = logging.getLogger(__name__)

def generate_excel_report(data, format_options=None):
    """
    Unified Excel report generation function for commission reports
    
    Args:
        data (dict): Report data with structure:
            {
                'lines': List of commission data lines,
                'company': Company record,
                'currency': Currency record,
                'title': Report title (optional),
                'subtitle': Report subtitle (optional),
                'date_from': Start date (optional),
                'date_to': End date (optional),
                'filters': Additional filter information (optional)
            }
        format_options (dict): Optional formatting parameters:
            {
                'header_format': Header cell format options,
                'data_format': Data cell format options,
                'money_format': Money format options,
                'title_format': Title format options,
                'include_logo': Whether to include company logo (default: True)
            }
    
    Returns:
        bytes: Excel file data
    """
    if format_options is None:
        format_options = {}
    
    # Create workbook in memory
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('Commission Report')

    # Define formats
    header_format = workbook.add_format(format_options.get('header_format', {
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#007bff',
        'color': 'white',
        'border': 1,
    }))
    
    title_format = workbook.add_format(format_options.get('title_format', {
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 14,
        'color': '#333333',
    }))
    
    subtitle_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 12,
        'color': '#666666',
    })
    
    money_format = workbook.add_format(format_options.get('money_format', {
        'num_format': '#,##0.00',
        'align': 'right',
    }))
    
    date_format = workbook.add_format({
        'num_format': 'yyyy-mm-dd',
        'align': 'center',
    })
    
    data_format = workbook.add_format(format_options.get('data_format', {
        'align': 'left',
        'valign': 'vcenter',
        'border': 1,
    }))
    
    # Insert title
    title = data.get('title', 'Commission Report')
    subtitle = data.get('subtitle', '')
    report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Add company logo if available and requested
    current_row = 0
    company = data.get('company')
    if company and company.logo and format_options.get('include_logo', True):
        try:
            logo_data = base64.b64decode(company.logo)
            logo_path = io.BytesIO(logo_data)
            worksheet.insert_image(current_row, 0, 'company_logo.png', 
                                 {'image_data': logo_path, 'x_scale': 0.5, 'y_scale': 0.5})
            current_row += 6
        except Exception as e:
            _logger.warning("Could not insert company logo: %s", e)
    
    # Add report title
    worksheet.merge_range(current_row, 0, current_row, 6, title, title_format)
    current_row += 1
    
    # Add subtitle if provided
    if subtitle:
        worksheet.merge_range(current_row, 0, current_row, 6, subtitle, subtitle_format)
        current_row += 1
    
    # Add report date
    worksheet.merge_range(current_row, 0, current_row, 6, f"Generated on: {report_date}", subtitle_format)
    current_row += 1
    
    # Add date range if provided
    date_from = data.get('date_from')
    date_to = data.get('date_to')
    if date_from and date_to:
        date_range = f"Period: {date_from} to {date_to}"
        worksheet.merge_range(current_row, 0, current_row, 6, date_range, subtitle_format)
        current_row += 1
    
    # Add filters if provided
    filters = data.get('filters')
    if filters:
        worksheet.merge_range(current_row, 0, current_row, 6, f"Filters: {filters}", subtitle_format)
        current_row += 1
    
    current_row += 1  # Add space before headers
    
    # Determine columns dynamically from the first data line or use default columns
    lines = data.get('lines', [])
    if not lines:
        _logger.warning("No commission data provided for Excel report")
        workbook.close()
        output.seek(0)
        return output.read()
    
    # Dynamically determine columns if first line has keys, otherwise use default columns
    if hasattr(lines[0], 'keys'):
        columns = list(lines[0].keys())
    else:
        columns = [
            'partner_name', 'order_ref', 'customer_ref', 'commission_type_display',
            'rate', 'amount', 'base_amount'
        ]
    
    # Map DB field names to display names
    column_headers = {
        'partner_name': 'Agent/Partner',
        'order_ref': 'Order Reference',
        'customer_ref': 'Customer',
        'commission_type_display': 'Commission Type',
        'rate': 'Rate (%)',
        'amount': 'Commission Amount',
        'base_amount': 'Base Amount',
        'date': 'Date',
    }
    
    # Write headers
    for col, field in enumerate(columns):
        header = column_headers.get(field, field.replace('_', ' ').title())
        worksheet.write(current_row, col, header, header_format)
    
    # Set column widths
    worksheet.set_column(0, 0, 25)  # Partner name
    worksheet.set_column(1, len(columns)-1, 15)  # Other columns
    
    # Write data
    for row, line in enumerate(lines, current_row + 1):
        for col, field in enumerate(columns):
            value = line.get(field) if isinstance(line, dict) else getattr(line, field, '')
            
            # Format based on field type
            if field in ('amount', 'base_amount') or 'amount' in field:
                worksheet.write(row, col, value, money_format)
            elif field == 'rate':
                worksheet.write(row, col, value, money_format)
            elif field in ('date', 'date_from', 'date_to'):
                worksheet.write(row, col, value, date_format)
            else:
                worksheet.write(row, col, value, data_format)
    
    # Add totals row if applicable
    if any('amount' in col for col in columns):
        total_row = current_row + len(lines) + 1
        worksheet.write(total_row, 0, 'Total', workbook.add_format({'bold': True}))
        
        # Add total formulas for amount columns
        for col, field in enumerate(columns):
            if field == 'amount' or 'amount' in field:
                start_cell = xlsxwriter.utility.xl_col_to_name(col) + str(current_row + 2)
                end_cell = xlsxwriter.utility.xl_col_to_name(col) + str(total_row)
                formula = f"=SUM({start_cell}:{end_cell})"
                worksheet.write_formula(total_row, col, formula, workbook.add_format({
                    'bold': True, 'num_format': '#,##0.00', 'top': 1, 'bottom': 3
                }))
    
    workbook.close()
    output.seek(0)
    return output.read()