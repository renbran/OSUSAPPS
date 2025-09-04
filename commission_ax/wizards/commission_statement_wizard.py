from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging
import io
import xlsxwriter
import base64
from datetime import datetime

_logger = logging.getLogger(__name__)

class CommissionPartnerStatementWizard(models.TransientModel):
    _name = 'commission.partner.statement.wizard'
    _description = 'Commission Partner Statement Wizard'

    # Filter fields
    date_from = fields.Date(string='Date From', required=True, default=fields.Date.today)
    date_to = fields.Date(string='Date To', required=True, default=fields.Date.today)
    partner_id = fields.Many2one('res.partner', string='Commission Partner', help='Leave empty to include all partners')
    sale_order_id = fields.Many2one('sale.order', string='Specific Sale Order', help='Generate report for specific order only')
    commission_type_filter = fields.Selection([
        ('all', 'All Commission Types'),
        ('internal', 'Internal Commissions Only'),
        ('external', 'External Commissions Only'),
        ('legacy', 'Legacy Commissions Only')
    ], string='Commission Type Filter', default='all')
    
    # Report options
    include_zero_commissions = fields.Boolean(string='Include Zero Commissions', default=False)
    group_by_partner = fields.Boolean(string='Group by Partner', default=True)
    show_customer_details = fields.Boolean(string='Show Customer Details', default=True)

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for wizard in self:
            if wizard.date_from > wizard.date_to:
                raise ValidationError("Date From cannot be later than Date To")

    def action_generate_pdf_report(self):
        """Generate PDF commission statement report"""
        self.ensure_one()
        data = self._prepare_report_data()
        
        if not data['commission_lines']:
            raise UserError("No commission data found for the selected criteria.")
        
        return self.env.ref('your_module.action_commission_statement_pdf').report_action(self, data=data)

    def action_generate_excel_report(self):
        """Generate Excel commission statement report"""
        self.ensure_one()
        data = self._prepare_report_data()
        
        if not data['commission_lines']:
            raise UserError("No commission data found for the selected criteria.")
        
        # Create Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Commission Statement')
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#D3D3D3',
            'border': 1,
            'align': 'center'
        })
        
        currency_format = workbook.add_format({
            'num_format': '#,##0.00',
            'border': 1
        })
        
        percentage_format = workbook.add_format({
            'num_format': '0.00%',
            'border': 1
        })
        
        text_format = workbook.add_format({
            'border': 1,
            'align': 'left'
        })
        
        # Write headers
        headers = [
            'COMMISSION NAME',
            'ORDER REF',
            'CUSTOMER REFERENCE',
            'COMMISSION TYPE',
            'RATE',
            'TOTAL'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Set column widths
        worksheet.set_column(0, 0, 20)  # Commission Name
        worksheet.set_column(1, 1, 15)  # Order Ref
        worksheet.set_column(2, 2, 25)  # Customer Reference
        worksheet.set_column(3, 3, 20)  # Commission Type
        worksheet.set_column(4, 4, 10)  # Rate
        worksheet.set_column(5, 5, 15)  # Total
        
        # Write data
        row = 1
        for line in data['commission_lines']:
            worksheet.write(row, 0, line['partner_name'], text_format)
            worksheet.write(row, 1, line['order_ref'], text_format)
            worksheet.write(row, 2, line['customer_ref'], text_format)
            worksheet.write(row, 3, line['commission_type_display'], text_format)
            
            # Handle rate display
            if line['commission_type'] == 'fixed':
                worksheet.write(row, 4, 'Fixed', text_format)
            else:
                worksheet.write(row, 4, line['rate'] / 100, percentage_format)
            
            worksheet.write(row, 5, line['amount'], currency_format)
            row += 1
        
        # Add totals row
        if data['commission_lines']:
            total_amount = sum(line['amount'] for line in data['commission_lines'])
            worksheet.write(row + 1, 4, 'TOTAL:', header_format)
            worksheet.write(row + 1, 5, total_amount, currency_format)
        
        workbook.close()
        output.seek(0)
        
        # Create attachment
        filename = f"Commission_Statement_{self.date_from}_{self.date_to}.xlsx"
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def _prepare_report_data(self):
        """Prepare data for both PDF and Excel reports"""
        domain = self._get_sale_order_domain()
        sale_orders = self.env['sale.order'].search(domain, order='date_order desc')
        
        commission_lines = []
        
        for order in sale_orders:
            lines = self._extract_commission_lines(order)
            commission_lines.extend(lines)
        
        # Sort by partner name if grouping is enabled
        if self.group_by_partner:
            commission_lines.sort(key=lambda x: x['partner_name'])
        
        return {
            'commission_lines': commission_lines,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'partner_filter': self.partner_id.name if self.partner_id else 'All Partners',
            'total_amount': sum(line['amount'] for line in commission_lines),
            'total_lines': len(commission_lines),
            'report_generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def _get_sale_order_domain(self):
        """Build domain for sale order search"""
        domain = [
            ('date_order', '>=', self.date_from),
            ('date_order', '<=', self.date_to),
            ('state', 'in', ['sale', 'done'])
        ]
        
        if self.sale_order_id:
            domain.append(('id', '=', self.sale_order_id.id))
        
        return domain

    def _extract_commission_lines(self, order):
        """Extract commission lines from a sale order"""
        lines = []
        
        # Helper function to add commission line
        def add_commission_line(partner, amount, comm_type, rate, category):
            if not partner or (not self.include_zero_commissions and amount <= 0):
                return
            
            if self.partner_id and partner.id != self.partner_id.id:
                return
            
            # Filter by commission type
            if self.commission_type_filter != 'all':
                if self.commission_type_filter == 'internal' and category != 'internal':
                    return
                elif self.commission_type_filter == 'external' and category != 'external':
                    return
                elif self.commission_type_filter == 'legacy' and category != 'legacy':
                    return
            
            commission_type_display = self._get_commission_type_display(comm_type)
            
            lines.append({
                'partner_name': partner.name,
                'partner_id': partner.id,
                'order_ref': order.name,
                'customer_ref': order.partner_id.name,
                'commission_type': comm_type,
                'commission_type_display': commission_type_display,
                'rate': rate,
                'amount': amount,
                'category': category,
                'sale_order_id': order.id
            })
        
        # Legacy commissions
        if order.consultant_id:
            add_commission_line(
                order.consultant_id, 
                order.salesperson_commission, 
                order.consultant_commission_type,
                order.consultant_comm_percentage,
                'legacy'
            )
        
        if order.manager_id:
            add_commission_line(
                order.manager_id, 
                order.manager_commission, 
                order.manager_legacy_commission_type,
                order.manager_comm_percentage,
                'legacy'
            )
        
        if order.second_agent_id:
            add_commission_line(
                order.second_agent_id, 
                order.second_agent_commission, 
                order.second_agent_commission_type,
                order.second_agent_comm_percentage,
                'legacy'
            )
        
        if order.director_id:
            add_commission_line(
                order.director_id, 
                order.director_commission, 
                order.director_legacy_commission_type,
                order.director_comm_percentage,
                'legacy'
            )
        
        # External commissions
        external_commissions = [
            (order.broker_partner_id, order.broker_amount, order.broker_commission_type, order.broker_rate),
            (order.referrer_partner_id, order.referrer_amount, order.referrer_commission_type, order.referrer_rate),
            (order.cashback_partner_id, order.cashback_amount, order.cashback_commission_type, order.cashback_rate),
            (order.other_external_partner_id, order.other_external_amount, order.other_external_commission_type, order.other_external_rate),
        ]
        
        for partner, amount, comm_type, rate in external_commissions:
            if partner:
                add_commission_line(partner, amount, comm_type, rate, 'external')
        
        # Internal commissions
        internal_commissions = [
            (order.agent1_partner_id, order.agent1_amount, order.agent1_commission_type, order.agent1_rate),
            (order.agent2_partner_id, order.agent2_amount, order.agent2_commission_type, order.agent2_rate),
            (order.manager_partner_id, order.manager_amount, order.manager_commission_type, order.manager_rate),
            (order.director_partner_id, order.director_amount, order.director_commission_type, order.director_rate),
        ]
        
        for partner, amount, comm_type, rate in internal_commissions:
            if partner:
                add_commission_line(partner, amount, comm_type, rate, 'internal')
        
        return lines

    def _get_commission_type_display(self, commission_type):
        """Get human-readable commission type"""
        type_mapping = {
            'fixed': 'Fixed Amount',
            'percent_unit_price': 'Unit Price %',
            'percent_untaxed_total': 'Total %'
        }
        return type_mapping.get(commission_type, commission_type)

    def action_preview_data(self):
        """Preview the data that will be included in the report"""
        data = self._prepare_report_data()
        
        if not data['commission_lines']:
            raise UserError("No commission data found for the selected criteria.")
        
        # Create a simple tree view to preview the data
        lines = []
        for line_data in data['commission_lines']:
            lines.append((0, 0, {
                'partner_name': line_data['partner_name'],
                'order_ref': line_data['order_ref'],
                'customer_ref': line_data['customer_ref'],
                'commission_type_display': line_data['commission_type_display'],
                'rate': line_data['rate'],
                'amount': line_data['amount'],
            }))
        
        preview_wizard = self.env['commission.statement.preview'].create({
            'line_ids': lines,
            'total_amount': data['total_amount'],
            'total_lines': data['total_lines'],
        })
        
        return {
            'name': 'Commission Statement Preview',
            'type': 'ir.actions.act_window',
            'res_model': 'commission.statement.preview',
            'res_id': preview_wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }


class CommissionStatementPreview(models.TransientModel):
    _name = 'commission.statement.preview'
    _description = 'Commission Statement Preview'

    line_ids = fields.One2many('commission.statement.preview.line', 'preview_id', string='Commission Lines')
    total_amount = fields.Float(string='Total Amount')
    total_lines = fields.Integer(string='Total Lines')


class CommissionStatementPreviewLine(models.TransientModel):
    _name = 'commission.statement.preview.line'
    _description = 'Commission Statement Preview Line'

    preview_id = fields.Many2one('commission.statement.preview', string='Preview')
    partner_name = fields.Char(string='Commission Name')
    order_ref = fields.Char(string='Order Ref')
    customer_ref = fields.Char(string='Customer Reference')
    commission_type_display = fields.Char(string='Commission Type')
    rate = fields.Float(string='Rate')
    amount = fields.Float(string='Total')