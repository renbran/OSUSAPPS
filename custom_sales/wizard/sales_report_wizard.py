# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import io
import logging

_logger = logging.getLogger(__name__)

class SalesReportWizard(models.TransientModel):
    _name = 'sales.report.wizard'
    _description = 'Sales Report Export Wizard'
    
    date_from = fields.Date(
        string='From Date',
        required=True,
        default=fields.Date.today
    )
    
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=fields.Date.today
    )
    
    report_type = fields.Selection([
        ('summary', 'Summary Report'),
        ('detailed', 'Detailed Report'),
        ('analytics', 'Analytics Report'),
    ], string='Report Type', default='summary', required=True)
    
    format_type = fields.Selection([
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ], string='Format', default='pdf', required=True)
    
    include_charts = fields.Boolean(
        string='Include Charts',
        default=True,
        help="Include charts in the report"
    )
    
    def action_generate_report(self):
        """Generate and download the report"""
        self.ensure_one()
        
        if self.date_from > self.date_to:
            raise UserError("From Date cannot be later than To Date")
        
        if self.format_type == 'pdf':
            return self._generate_pdf_report()
        elif self.format_type == 'excel':
            return self._generate_excel_report()
        elif self.format_type == 'csv':
            return self._generate_csv_report()
    
    def _generate_pdf_report(self):
        """Generate PDF report"""
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'report_type': self.report_type,
            'include_charts': self.include_charts,
        }
        
        return self.env.ref('custom_sales.action_report_sales_wizard').report_action(self, data=data)
    
    def _generate_excel_report(self):
        """Generate Excel report"""
        try:
            import xlsxwriter
            
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Sales Report')
            
            # Add headers
            worksheet.write('A1', 'Sales Report')
            worksheet.write('A2', f'Period: {self.date_from} to {self.date_to}')
            
            # Get data
            domain = [
                ('create_date', '>=', self.date_from),
                ('create_date', '<=', self.date_to)
            ]
            sales_orders = self.env['custom.sales.order'].search(domain)
            
            # Write data
            row = 4
            worksheet.write('A4', 'Order Reference')
            worksheet.write('B4', 'Customer')
            worksheet.write('C4', 'Date')
            worksheet.write('D4', 'Revenue')
            worksheet.write('E4', 'Status')
            
            for order in sales_orders:
                worksheet.write(row, 0, order.name)
                worksheet.write(row, 1, order.custom_field_3.name if order.custom_field_3 else '')
                worksheet.write(row, 2, str(order.create_date))
                worksheet.write(row, 3, order.actual_revenue)
                worksheet.write(row, 4, order.state)
                row += 1
            
            workbook.close()
            output.seek(0)
            
            attachment = self.env['ir.attachment'].create({
                'name': f'sales_report_{self.date_from}_{self.date_to}.xlsx',
                'type': 'binary',
                'datas': base64.b64encode(output.getvalue()),
                'res_model': self._name,
                'res_id': self.id,
                'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            })
            
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'self',
            }
            
        except ImportError:
            raise UserError("Excel export requires xlsxwriter package to be installed")
    
    def _generate_csv_report(self):
        """Generate CSV report"""
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['Order Reference', 'Customer', 'Date', 'Revenue', 'Status'])
        
        # Get data
        domain = [
            ('create_date', '>=', self.date_from),
            ('create_date', '<=', self.date_to)
        ]
        sales_orders = self.env['custom.sales.order'].search(domain)
        
        # Write data
        for order in sales_orders:
            writer.writerow([
                order.name,
                order.custom_field_3.name if order.custom_field_3 else '',
                str(order.create_date),
                order.actual_revenue,
                order.state
            ])
        
        output.seek(0)
        
        attachment = self.env['ir.attachment'].create({
            'name': f'sales_report_{self.date_from}_{self.date_to}.csv',
            'type': 'binary',
            'datas': base64.b64encode(output.getvalue().encode()),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'text/csv'
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
