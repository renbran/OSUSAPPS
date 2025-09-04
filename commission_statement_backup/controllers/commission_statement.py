# -*- coding: utf-8 -*-
import base64
import io
import xlsxwriter
from datetime import date

from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError


class CommissionStatementController(http.Controller):
    
    @http.route(['/commission_partner_statement/excel_report/<int:partner_id>'], 
                type='http', auth="user")
    def download_commission_excel_report(self, partner_id, **kwargs):
        """Download Excel commission statement report"""
        try:
            # Get partner and check access
            partner = request.env['res.partner'].browse(partner_id)
            if not partner.exists():
                return request.not_found()
                
            # Check access rights
            if not request.env.user.has_group('commission_partner_statement.group_commission_statement_user'):
                raise AccessError(_("You don't have permission to download commission statements."))
                
            # Get commission statement data
            data = partner.commission_statement_query()
            
            if not data['statement_lines']:
                return request.render('web.http_error', {
                    'error_message': _("No commission data found for the selected period."),
                    'error_code': 404
                })
            
            # Create Excel file
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet('Commission Statement')
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'font_size': 14,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#2E86AB',
                'font_color': 'white',
                'border': 1
            })
            
            subheader_format = workbook.add_format({
                'bold': True,
                'font_size': 11,
                'align': 'center',
                'bg_color': '#E8F4F8',
                'border': 1
            })
            
            cell_format = workbook.add_format({
                'font_size': 10,
                'align': 'left',
                'valign': 'vcenter',
                'border': 1
            })
            
            currency_format = workbook.add_format({
                'font_size': 10,
                'num_format': '#,##0.00',
                'align': 'right',
                'border': 1
            })
            
            date_format = workbook.add_format({
                'font_size': 10,
                'num_format': 'yyyy-mm-dd',
                'align': 'center',
                'border': 1
            })
            
            total_format = workbook.add_format({
                'bold': True,
                'font_size': 11,
                'num_format': '#,##0.00',
                'align': 'right',
                'bg_color': '#F0F0F0',
                'border': 2
            })
            
            # Set column widths
            worksheet.set_column('A:A', 15)  # Order Ref
            worksheet.set_column('B:B', 12)  # Date
            worksheet.set_column('C:C', 25)  # Customer
            worksheet.set_column('D:D', 12)  # Type
            worksheet.set_column('E:E', 15)  # Category
            worksheet.set_column('F:F', 10)  # Rate
            worksheet.set_column('G:G', 15)  # Order Total
            worksheet.set_column('H:H', 15)  # Commission
            
            # Write header information
            worksheet.merge_range('A1:H1', 'COMMISSION STATEMENT REPORT', header_format)
            
            # Partner information
            worksheet.write('A3', 'Partner:', subheader_format)
            worksheet.merge_range('B3:D3', partner.name, cell_format)
            worksheet.write('A4', 'Period:', subheader_format)
            worksheet.merge_range('B4:D4', f"{data['date_from']} to {data['date_to']}", cell_format)
            worksheet.write('A5', 'Total Orders:', subheader_format)
            worksheet.write('B5', data['orders_count'], cell_format)
            worksheet.write('A6', 'Total Commission:', subheader_format)
            worksheet.write('B6', data['total_amount'], currency_format)
            
            # Table headers
            row = 8
            headers = ['Order Ref', 'Date', 'Customer', 'Type', 'Category', 'Rate (%)', 'Order Total', 'Commission']
            for col, header in enumerate(headers):
                worksheet.write(row, col, header, subheader_format)
            
            # Write statement lines
            row += 1
            total_commission = 0
            for line in data['statement_lines']:
                worksheet.write(row, 0, line['order_ref'], cell_format)
                worksheet.write(row, 1, line['order_date'], date_format)
                worksheet.write(row, 2, line['customer_name'], cell_format)
                worksheet.write(row, 3, line['commission_type'], cell_format)
                worksheet.write(row, 4, line['commission_category'], cell_format)
                worksheet.write(row, 5, line['rate'] if line['rate'] > 0 else '', cell_format)
                worksheet.write(row, 6, line['order_total'], currency_format)
                worksheet.write(row, 7, line['amount'], currency_format)
                
                total_commission += line['amount']
                row += 1
            
            # Write total
            worksheet.write(row, 6, 'TOTAL:', subheader_format)
            worksheet.write(row, 7, total_commission, total_format)
            
            workbook.close()
            output.seek(0)
            
            # Prepare response
            filename = f'Commission_Statement_{partner.name}_{date.today().strftime("%Y%m%d")}.xlsx'
            response = request.make_response(
                output.getvalue(),
                headers=[
                    ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                    ('Content-Disposition', f'attachment; filename="{filename}"')
                ]
            )
            
            return response
            
        except Exception as e:
            return request.render('web.http_error', {
                'error_message': str(e),
                'error_code': 500
            })