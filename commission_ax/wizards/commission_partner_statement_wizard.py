from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64
import io
try:
    import xlsxwriter
    xlsxwriter_available = True
except ImportError:
    xlsxwriter_available = False

class CommissionPartnerStatementWizard(models.TransientModel):
    """Wizard for generating Commission Partner Statement Reports"""
    _name = 'commission.partner.statement.wizard'
    _description = 'Commission Partner Statement Report Wizard'

    # Date filters
    date_from = fields.Date(
        string='From Date',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1)
    )
    date_to = fields.Date(
        string='To Date', 
        required=True,
        default=fields.Date.today
    )

    # Partner filter
    partner_ids = fields.Many2many(
        'res.partner',
        string='Commission Partners',
        domain=[('is_commission_agent', '=', True)],
        help='Select specific partners or leave empty for all commission partners'
    )

    # Report format
    report_format = fields.Selection([
        ('pdf', 'PDF Report'),
        ('excel', 'Excel Export'),
        ('both', 'Both PDF and Excel')
    ], string='Report Format', default='pdf', required=True)

    # Additional filters
    commission_state = fields.Selection([
        ('all', 'All States'),
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('confirmed', 'Confirmed'),
        ('processed', 'Processed'), 
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Commission Status', default='all')

    # Project filter - Temporarily disabled until project module is available
    # project_ids = fields.Many2many(
    #     'project.project',
    #     string='Projects',
    #     help='Filter by specific projects'
    # )

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from > record.date_to:
                raise ValidationError(_('From Date cannot be greater than To Date.'))

    def _get_commission_data(self):
        """Get commission data based on filters"""
        domain = [
            ('sale_order_id.date_order', '>=', self.date_from),
            ('sale_order_id.date_order', '<=', self.date_to),
        ]
        
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))
        else:
            domain.append(('partner_id.is_commission_agent', '=', True))
            
        if self.commission_state != 'all':
            domain.append(('state', '=', self.commission_state))
            
        # Project filtering temporarily disabled until project module is available
        # if self.project_ids:
        #     domain.append(('sale_order_id.project_id', 'in', self.project_ids.ids))

        commission_lines = self.env['commission.line'].search(domain, order='partner_id, sale_order_id.date_order')
        
        # Prepare data structure
        report_data = []
        for line in commission_lines:
            sale_order = line.sale_order_id
            
            # Get unit information from order lines
            unit_info = ""
            if sale_order.order_line:
                units = []
                for order_line in sale_order.order_line:
                    if order_line.product_qty > 0:
                        units.append(f"{order_line.product_id.name} ({order_line.product_qty} {order_line.product_uom.name})")
                unit_info = "; ".join(units)
            
            report_data.append({
                'partner_name': line.partner_id.name,
                'booking_date': sale_order.date_order.date() if sale_order.date_order else '',
                'project_name': 'No Project',  # Project module not available
                'unit': unit_info or 'No Units',
                'sale_value': sale_order.amount_total,
                'commission_rate': line.rate,
                'calculation_method': dict(line._fields['calculation_method'].selection).get(line.calculation_method, ''),
                'commission_amount': line.commission_amount,
                'commission_status': dict(line._fields['state'].selection).get(line.state, ''),
                'sale_order_name': sale_order.name,
                'currency': sale_order.currency_id.name,
            })
            
        return report_data

    def action_generate_report(self):
        """Generate the commission partner statement report"""
        self.ensure_one()
        
        if self.report_format == 'pdf':
            return self._generate_pdf_report()
        elif self.report_format == 'excel':
            return self._generate_excel_report()
        elif self.report_format == 'both':
            # Generate Excel first, then PDF
            excel_result = self._generate_excel_report()
            pdf_result = self._generate_pdf_report()
            return pdf_result  # Return PDF for immediate view
            
    def _generate_pdf_report(self):
        """Generate PDF report"""
        report_data = self._get_commission_data()
        
        return {
            'type': 'ir.actions.report',
            'report_name': 'commission_ax.commission_partner_statement_report',
            'report_type': 'qweb-pdf',
            'data': {
                'report_data': report_data,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'commission_state': self.commission_state,
                'partner_names': ', '.join(self.partner_ids.mapped('name')) if self.partner_ids else 'All Partners',
                'project_names': 'All Projects'  # Project module not available
            },
            'context': self.env.context,
        }

    def _generate_excel_report(self):
        """Generate Excel report"""
        if not xlsxwriter_available:
            raise ValidationError(_('XlsxWriter library is not installed. Please install it to use Excel export.'))
            
        report_data = self._get_commission_data()
        
        # Create Excel file in memory
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Commission Partner Statement')
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#366092',
            'color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        data_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'top'
        })
        
        number_format = workbook.add_format({
            'border': 1,
            'align': 'right',
            'num_format': '#,##0.00'
        })
        
        date_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'num_format': 'dd/mm/yyyy'
        })
        
        # Write title
        worksheet.merge_range(0, 0, 0, 7, f'Commission Partner Statement ({self.date_from} to {self.date_to})', header_format)
        
        # Write headers
        headers = [
            'Partner Name',
            'Booking Date', 
            'Project',
            'Unit',
            'Sale Value',
            'Commission Rate',
            'Commission Amount', 
            'Status'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, header_format)
        
        # Set column widths
        worksheet.set_column(0, 0, 20)  # Partner Name
        worksheet.set_column(1, 1, 12)  # Booking Date
        worksheet.set_column(2, 2, 20)  # Project
        worksheet.set_column(3, 3, 30)  # Unit
        worksheet.set_column(4, 4, 15)  # Sale Value
        worksheet.set_column(5, 5, 12)  # Commission Rate
        worksheet.set_column(6, 6, 15)  # Commission Amount
        worksheet.set_column(7, 7, 12)  # Status
        
        # Write data
        row = 3
        for data in report_data:
            worksheet.write(row, 0, data['partner_name'], data_format)
            worksheet.write(row, 1, data['booking_date'], date_format)
            worksheet.write(row, 2, data['project_name'], data_format)
            worksheet.write(row, 3, data['unit'], data_format)
            worksheet.write(row, 4, data['sale_value'], number_format)
            
            # Format commission rate based on calculation method
            rate_display = f"{data['commission_rate']}"
            if 'percentage' in data['calculation_method'].lower():
                rate_display += '%'
            worksheet.write(row, 5, rate_display, data_format)
            
            worksheet.write(row, 6, data['commission_amount'], number_format)
            worksheet.write(row, 7, data['commission_status'], data_format)
            row += 1
        
        # Add totals row
        if report_data:
            total_sale_value = sum(data['sale_value'] for data in report_data)
            total_commission = sum(data['commission_amount'] for data in report_data)
            
            worksheet.write(row + 1, 3, 'TOTALS:', header_format)
            worksheet.write(row + 1, 4, total_sale_value, number_format)
            worksheet.write(row + 1, 6, total_commission, number_format)
        
        workbook.close()
        
        # Prepare file data
        file_data = output.getvalue()
        output.close()
        
        # Create attachment
        filename = f'commission_partner_statement_{self.date_from}_{self.date_to}.xlsx'
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(file_data),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true&filename={filename}',
            'target': 'new',
        }