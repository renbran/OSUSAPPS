# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json
import io
import xlsxwriter


class CommissionLinesController(http.Controller):
    """Controller for commission lines functionality"""

    @http.route('/commission_lines/statement/excel', type='http', auth='user', methods=['GET'])
    def commission_statement_excel(self, wizard_id, **kwargs):
        """Generate Excel commission statement report"""
        try:
            # Get wizard record
            wizard = request.env['commission.statement.wizard'].browse(int(wizard_id))
            if not wizard.exists():
                return request.not_found()

            # Get commission lines data
            commission_data = wizard._get_commission_lines_data()
            
            # Create Excel file in memory
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Commission Statement')

            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D7E4BC',
                'border': 1,
                'align': 'center'
            })
            
            title_format = workbook.add_format({
                'bold': True,
                'font_size': 16,
                'align': 'center'
            })
            
            info_format = workbook.add_format({
                'bold': True,
            })
            
            currency_format = workbook.add_format({
                'num_format': '#,##0.00',
                'align': 'right'
            })
            
            percent_format = workbook.add_format({
                'num_format': '0.00%',
                'align': 'right'
            })
            
            date_format = workbook.add_format({
                'num_format': 'yyyy-mm-dd',
                'align': 'center'
            })

            # Write title and header information
            worksheet.merge_range('A1:G1', 'Commission Statement', title_format)
            
            # Partner information
            row = 3
            worksheet.write(row, 0, 'Partner Name:', info_format)
            worksheet.write(row, 1, wizard.partner_id.name)
            worksheet.write(row, 3, 'Date Range:', info_format)
            worksheet.write(row, 4, f"{wizard.date_from} - {wizard.date_to}")
            
            row += 1
            worksheet.write(row, 0, 'Partner Email:', info_format)
            worksheet.write(row, 1, wizard.partner_id.email or '')
            worksheet.write(row, 3, 'Report Generated:', info_format)
            worksheet.write(row, 4, wizard.create_date.strftime('%Y-%m-%d %H:%M:%S'))

            # Table headers
            row += 3
            headers = [
                'Booking Date', 'Order Ref', 'Customer Reference', 
                'Sale Value', 'Commission Rate', 'Total Amount', 'Status'
            ]
            
            for col, header in enumerate(headers):
                worksheet.write(row, col, header, header_format)

            # Table data
            total_sale_value = 0
            total_commission = 0
            
            for line_data in commission_data:
                row += 1
                
                # Write data
                worksheet.write(row, 0, line_data['booking_date'], date_format)
                worksheet.write(row, 1, line_data['order_ref'])
                worksheet.write(row, 2, line_data['customer_reference'])
                worksheet.write(row, 3, line_data['sale_value'] or 0, currency_format)
                worksheet.write(row, 4, (line_data['commission_rate'] or 0) / 100, percent_format)
                worksheet.write(row, 5, line_data['commission_amount'] or 0, currency_format)
                worksheet.write(row, 6, line_data['state'].title())
                
                # Update totals
                total_sale_value += line_data['sale_value'] or 0
                total_commission += line_data['commission_amount'] or 0

            # Summary section
            row += 2
            worksheet.write(row, 3, 'Total Sale Value:', info_format)
            worksheet.write(row, 4, total_sale_value, currency_format)
            
            row += 1
            worksheet.write(row, 3, 'Total Commission:', info_format)
            worksheet.write(row, 4, total_commission, currency_format)
            
            if total_sale_value > 0:
                row += 1
                worksheet.write(row, 3, 'Overall Rate:', info_format)
                worksheet.write(row, 4, total_commission / total_sale_value, percent_format)

            # Auto-adjust column widths
            worksheet.set_column('A:A', 12)  # Booking Date
            worksheet.set_column('B:B', 15)  # Order Ref
            worksheet.set_column('C:C', 18)  # Customer Reference
            worksheet.set_column('D:D', 12)  # Sale Value
            worksheet.set_column('E:E', 15)  # Commission Rate
            worksheet.set_column('F:F', 15)  # Total Amount
            worksheet.set_column('G:G', 12)  # Status

            workbook.close()
            output.seek(0)

            # Create response
            filename = f"Commission_Statement_{wizard.partner_id.name}_{wizard.date_from}_{wizard.date_to}.xlsx"
            
            response = request.make_response(
                output.read(),
                headers=[
                    ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                    ('Content-Disposition', f'attachment; filename="{filename}"')
                ]
            )
            
            return response

        except Exception as e:
            return request.render('http_routing.http_error', {
                'status_code': '500',
                'status_message': 'Internal Server Error',
                'error_message': f'Error generating Excel report: {str(e)}'
            })

    @http.route('/commission_lines/api/partner_summary/<int:partner_id>', 
                type='json', auth='user', methods=['POST'])
    def get_partner_commission_summary(self, partner_id, **kwargs):
        """Get commission summary for a partner (API endpoint)"""
        try:
            partner = request.env['res.partner'].browse(partner_id)
            if not partner.exists():
                return {'error': 'Partner not found'}

            commission_lines = partner.commission_line_ids.filtered(lambda l: l.state != 'cancelled')
            
            summary = {
                'partner_name': partner.name,
                'total_lines': len(commission_lines),
                'total_amount': sum(commission_lines.mapped('commission_amount')),
                'currency': partner.currency_id.name or request.env.company.currency_id.name,
                'status_breakdown': {
                    'draft': len(commission_lines.filtered(lambda l: l.state == 'draft')),
                    'calculated': len(commission_lines.filtered(lambda l: l.state == 'calculated')),
                    'approved': len(commission_lines.filtered(lambda l: l.state == 'approved')),
                    'billed': len(commission_lines.filtered(lambda l: l.state == 'billed')),
                    'paid': len(commission_lines.filtered(lambda l: l.state == 'paid')),
                }
            }
            
            return summary

        except Exception as e:
            return {'error': str(e)}