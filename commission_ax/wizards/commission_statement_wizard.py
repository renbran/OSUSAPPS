import base64
import io
import logging
from datetime import date, timedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import formatLang


class CommissionStatementWizard(models.TransientModel):
    """Wizard to generate commission statement reports."""
    
    _name = 'commission.statement.wizard'
    _description = 'Commission Statement Wizard'
    _transient_max_hours = 2.0
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Agent',
        required=True,
        domain=[('is_company', '=', False)],
        help="Agent for statement generation"
    )
    
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        help="Specific sale order for statement (leave empty for all orders)"
    )
    
    date_from = fields.Date(
        string='Date From',
        required=True,
        default=lambda self: date.today().replace(day=1),
        help="Start date for statement period"
    )
    
    date_to = fields.Date(
        string='Date To',
        required=True,
        default=lambda self: date.today(),
        help="End date for statement period"
    )
    
    output_format = fields.Selection([
        ('pdf', 'PDF Report'),
        ('xlsx', 'Excel Report'),
        ('both', 'Both PDF and Excel')
    ], string='Output Format', default='pdf', required=True)
    
    # Results
    pdf_data = fields.Binary(
        string='PDF Report',
        readonly=True,
        attachment=False
    )
    
    pdf_filename = fields.Char(
        string='PDF Filename',
        readonly=True
    )
    
    xlsx_data = fields.Binary(
        string='Excel Report',
        readonly=True,
        attachment=False
    )
    
    xlsx_filename = fields.Char(
        string='Excel Filename',
        readonly=True
    )
    
    report_generated = fields.Boolean(
        string='Report Generated',
        default=False
    )
    
    statement_line_ids = fields.One2many(
        'commission.statement.line',
        'wizard_id',
        string='Statement Lines',
        readonly=True
    )
    
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """Validate date range."""
        for wizard in self:
            if wizard.date_from > wizard.date_to:
                raise UserError(_("Date From must be before Date To"))
    
    @api.onchange('partner_id', 'date_from', 'date_to')
    def _onchange_dates_partner(self):
        """Update available sale orders when dates or partner changes."""
        if self.partner_id:
            domain = self._get_sale_order_domain()
            available_orders = self.env['sale.order'].search(domain)
            if len(available_orders) == 1:
                self.sale_order_id = available_orders.id
    
    def _get_sale_order_domain(self):
        """Get domain for sale orders with commissions for this partner."""
        if not self.partner_id:
            return [('id', '=', False)]
        
        domain = [
            ('date_order', '>=', self.date_from),
            ('date_order', '<=', self.date_to),
            ('state', 'in', ['sale', 'done']),
            '|', '|', '|', '|', '|', '|', '|', '|', '|', '|',
            ('agent1_partner_id', '=', self.partner_id.id),
            ('agent2_partner_id', '=', self.partner_id.id),
            ('broker_partner_id', '=', self.partner_id.id),
            ('referrer_partner_id', '=', self.partner_id.id),
            ('cashback_partner_id', '=', self.partner_id.id),
            ('other_external_partner_id', '=', self.partner_id.id),
            ('consultant_id', '=', self.partner_id.id),
            ('manager_id', '=', self.partner_id.id),
            ('second_agent_id', '=', self.partner_id.id),
            ('director_id', '=', self.partner_id.id),
            ('manager_partner_id', '=', self.partner_id.id),
            ('director_partner_id', '=', self.partner_id.id),
        ]
        
        if self.sale_order_id:
            domain.append(('id', '=', self.sale_order_id.id))
        
        return domain
    
    def action_generate_statement(self):
        """Generate commission statement."""
        self.ensure_one()
        
        if not self.partner_id:
            raise UserError(_("Please select an agent"))
        
        _logger.info("Generating commission statement for partner %s", self.partner_id.name)
        
        # Clear previous data
        self.statement_line_ids.unlink()
        
        # Generate statement lines
        self._generate_statement_lines()
        
        # Generate reports based on format
        if self.output_format in ['pdf', 'both']:
            self._generate_pdf_report()
        
        if self.output_format in ['xlsx', 'both']:
            self._generate_xlsx_report()
        
        self.report_generated = True
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commission Statement Generated'),
            'res_model': 'commission.statement.wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': dict(self.env.context, report_generated=True)
        }
    
    def _generate_statement_lines(self):
        """Generate statement lines from sale orders."""
        domain = self._get_sale_order_domain()
        sale_orders = self.env['sale.order'].search(domain, order='date_order desc')
        
        lines_data = []
        for order in sale_orders:
            # Get all commission entries for this partner from this order
            commission_entries = self._get_commission_entries_for_partner(order)
            
            for entry in commission_entries:
                # Find related purchase order
                po = self._find_related_purchase_order(order, entry)
                
                lines_data.append({
                    'wizard_id': self.id,
                    'sale_order_id': order.id,
                    'purchase_order_id': po.id if po else False,
                    'agent_name': self.partner_id.name,
                    'deal_date': order.date_order.date() if order.date_order else date.today(),
                    'commission_type': entry['type'],
                    'rate': entry['rate'],
                    'property_price': order.amount_total,
                    'gross_commission': entry['amount'],
                    'vat_rate': self._get_vat_rate(),
                    'vat_amount': entry['amount'] * self._get_vat_rate() / 100,
                    'net_commission': entry['amount'] * (1 - self._get_vat_rate() / 100),
                    'status': self._get_commission_status(order, entry),
                    'po_number': po.name if po else '',
                    'remarks': self._get_remarks(order, po),
                })
        
        # Create statement lines
        self.env['commission.statement.line'].create(lines_data)
    
    def _get_commission_entries_for_partner(self, order):
        """Get commission entries for specific partner from order."""
        entries = []
        
        # Check all commission fields
        commission_mappings = [
            ('agent1_partner_id', 'agent1_amount', 'agent1_rate', 'Internal - Agent 1'),
            ('agent2_partner_id', 'agent2_amount', 'agent2_rate', 'Internal - Agent 2'),
            ('broker_partner_id', 'broker_amount', 'broker_rate', 'External - Broker'),
            ('referrer_partner_id', 'referrer_amount', 'referrer_rate', 'External - Referrer'),
            ('cashback_partner_id', 'cashback_amount', 'cashback_rate', 'External - Cashback'),
            ('other_external_partner_id', 'other_external_amount', 'other_external_rate', 'External - Other'),
            ('consultant_id', 'salesperson_commission', 'consultant_comm_percentage', 'Legacy - Consultant'),
            ('manager_id', 'manager_commission', 'manager_comm_percentage', 'Legacy - Manager'),
            ('second_agent_id', 'second_agent_commission', 'second_agent_comm_percentage', 'Legacy - Second Agent'),
            ('director_id', 'director_commission', 'director_comm_percentage', 'Legacy - Director'),
            ('manager_partner_id', 'manager_amount', 'manager_rate', 'Internal - Manager'),
            ('director_partner_id', 'director_amount', 'director_rate', 'Internal - Director'),
        ]
        
        for partner_field, amount_field, rate_field, commission_type in commission_mappings:
            if (hasattr(order, partner_field) and 
                getattr(order, partner_field) == self.partner_id and
                hasattr(order, amount_field) and
                getattr(order, amount_field, 0) > 0):
                
                entries.append({
                    'type': commission_type,
                    'amount': getattr(order, amount_field, 0),
                    'rate': getattr(order, rate_field, 0),
                    'partner_field': partner_field,
                })
        
        return entries
    
    def _find_related_purchase_order(self, sale_order, commission_entry):
        """Find related purchase order for commission entry."""
        # Look for purchase orders linked to this sale order
        pos = self.env['purchase.order'].search([
            ('origin_so_id', '=', sale_order.id),
            ('partner_id', '=', self.partner_id.id),
        ], limit=1)
        
        return pos
    
    def _get_vat_rate(self):
        """Get VAT rate from company settings."""
        company = self.env.company
        # Default to 5% VAT for UAE, can be configured
        return getattr(company, 'default_vat_rate', 5.0)
    
    def _get_commission_status(self, order, entry):
        """Get commission status."""
        if order.commission_processed:
            return 'Confirmed'
        elif order.commission_status == 'calculated':
            return 'Calculated'
        else:
            return 'Draft'
    
    def _get_remarks(self, order, po):
        """Get remarks for commission entry."""
        remarks = []
        
        if po:
            if po.commission_posted:
                remarks.append('Posted')
            if po.state == 'purchase':
                remarks.append('Confirmed')
            elif po.state == 'done':
                remarks.append('Received')
            elif po.state == 'cancel':
                remarks.append('Cancelled')
        else:
            remarks.append('No PO Created')
        
        if order.invoice_status == 'invoiced':
            remarks.append('Invoiced')
        
        return ', '.join(remarks) if remarks else 'Pending'
    
    def _generate_pdf_report(self):
        """Generate PDF report."""
        try:
            report = self.env.ref('commission_ax.action_report_commission_statement')
            pdf_content, _ = report._render_qweb_pdf(self.ids)
            
            filename = self._get_filename('pdf')
            
            self.write({
                'pdf_data': base64.b64encode(pdf_content),
                'pdf_filename': filename,
            })
            
        except Exception as e:
            _logger.error("PDF generation failed: %s", str(e))
            raise UserError(_("Failed to generate PDF report: %s") % str(e))
    
    def _generate_xlsx_report(self):
        """Generate Excel report."""
        try:
            output = io.BytesIO()
            
            try:
                import xlsxwriter
            except ImportError:
                raise UserError(_("xlsxwriter library is required for Excel export"))
            
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet('Commission Statement')
            
            # Formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#800020',
                'font_color': 'white',
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
            })
            
            money_format = workbook.add_format({
                'num_format': '#,##0.00',
                'align': 'right',
            })
            
            date_format = workbook.add_format({
                'num_format': 'yyyy-mm-dd',
                'align': 'center',
            })
            
            percent_format = workbook.add_format({
                'num_format': '0.00%',
                'align': 'center',
            })
            
            # Title and header info
            worksheet.merge_range('A1:K1', 'Commission Statement', header_format)
            worksheet.write('A2', 'Agent:', workbook.add_format({'bold': True}))
            worksheet.write('B2', self.partner_id.name)
            worksheet.write('A3', 'Period:', workbook.add_format({'bold': True}))
            worksheet.write('B3', f'{self.date_from} to {self.date_to}')
            
            # Column headers
            headers = [
                'Agent Name', 'Deal Date', 'Commission Type', 'Rate (%)',
                'Property Price', 'Gross Commission', 'VAT (%)', 'Net Commission',
                'Status', 'PO Number', 'Remarks'
            ]
            
            for col, header in enumerate(headers):
                worksheet.write(5, col, header, header_format)
            
            # Data rows
            row = 6
            total_gross = 0.0
            total_net = 0.0
            
            for line in self.statement_line_ids:
                worksheet.write(row, 0, line.agent_name)
                worksheet.write(row, 1, line.deal_date, date_format)
                worksheet.write(row, 2, line.commission_type)
                worksheet.write(row, 3, line.rate / 100, percent_format)
                worksheet.write(row, 4, line.property_price, money_format)
                worksheet.write(row, 5, line.gross_commission, money_format)
                worksheet.write(row, 6, line.vat_rate / 100, percent_format)
                worksheet.write(row, 7, line.net_commission, money_format)
                worksheet.write(row, 8, line.status)
                worksheet.write(row, 9, line.po_number)
                worksheet.write(row, 10, line.remarks)
                
                total_gross += line.gross_commission
                total_net += line.net_commission
                row += 1
            
            # Total row
            if self.statement_line_ids:
                worksheet.write(row + 1, 4, 'TOTAL:', workbook.add_format({'bold': True}))
                worksheet.write(row + 1, 5, total_gross, workbook.add_format({'bold': True, 'num_format': '#,##0.00'}))
                worksheet.write(row + 1, 7, total_net, workbook.add_format({'bold': True, 'num_format': '#,##0.00'}))
            
            # Adjust column widths
            widths = [15, 12, 18, 10, 15, 15, 10, 15, 12, 15, 20]
            for i, width in enumerate(widths):
                worksheet.set_column(i, i, width)
            
            workbook.close()
            output.seek(0)
            
            filename = self._get_filename('xlsx')
            
            self.write({
                'xlsx_data': base64.b64encode(output.read()),
                'xlsx_filename': filename,
            })
            
        except Exception as e:
            _logger.error("Excel generation failed: %s", str(e))
            raise UserError(_("Failed to generate Excel report: %s") % str(e))
    
    def _get_filename(self, format_type):
        """Get filename for report."""
        safe_agent_name = self.partner_id.name.replace(' ', '_').replace('/', '_')
        
        if self.sale_order_id:
            safe_so_name = self.sale_order_id.name.replace('/', '_')
            base_name = f'Commission_Statement_{safe_so_name}_{safe_agent_name}'
        else:
            date_str = self.date_from.strftime('%Y%m%d')
            base_name = f'Commission_Statement_{safe_agent_name}_{date_str}'
        
        return f'{base_name}.{format_type}'
    
    def action_download_pdf(self):
        """Download PDF report."""
        self.ensure_one()
        if not self.pdf_data:
            raise UserError(_("No PDF report generated"))
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model={self._name}&id={self.id}&field=pdf_data&download=true&filename={self.pdf_filename}',
            'target': 'self',
        }
    
    def action_download_xlsx(self):
        """Download Excel report."""
        self.ensure_one()
        if not self.xlsx_data:
            raise UserError(_("No Excel report generated"))
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model={self._name}&id={self.id}&field=xlsx_data&download=true&filename={self.xlsx_filename}',
            'target': 'self',
        }


class CommissionStatementLine(models.TransientModel):
    """Commission statement line for display."""
    
    _name = 'commission.statement.line'
    _description = 'Commission Statement Line'
    _order = 'deal_date desc'
    
    wizard_id = fields.Many2one(
        'commission.statement.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )
    
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        required=True
    )
    
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order'
    )
    
    agent_name = fields.Char(string='Agent Name', required=True)
    deal_date = fields.Date(string='Deal Date', required=True)
    commission_type = fields.Char(string='Commission Type', required=True)
    rate = fields.Float(string='Rate (%)', digits=(5, 2))
    property_price = fields.Monetary(string='Property Price', currency_field='currency_id')
    gross_commission = fields.Monetary(string='Gross Commission', currency_field='currency_id')
    vat_rate = fields.Float(string='VAT Rate (%)', digits=(5, 2))
    vat_amount = fields.Monetary(string='VAT Amount', currency_field='currency_id')
    net_commission = fields.Monetary(string='Net Commission', currency_field='currency_id')
    status = fields.Char(string='Status')
    po_number = fields.Char(string='PO Number')
    remarks = fields.Char(string='Remarks')
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='sale_order_id.currency_id'
    )