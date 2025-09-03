import base64
import io
import logging
from datetime import date
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class CommissionStatementWizard(models.TransientModel):
    """Enhanced wizard to generate commission statement reports."""
    
    _name = 'commission.statement.wizard'
    _description = 'Commission Statement Wizard'
    _transient_max_hours = 2.0
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Commission Agent',
        domain=[('is_company', '=', False)],
        help="Select specific agent or leave empty for all agents"
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
    ], string='Output Format', default='both', required=True)
    
    include_draft = fields.Boolean(
        string='Include Draft Orders',
        default=False,
        help="Include draft sale orders in the report"
    )
    
    # Results
    pdf_data = fields.Binary(string='PDF Report', readonly=True, attachment=False)
    pdf_filename = fields.Char(string='PDF Filename', readonly=True)
    xlsx_data = fields.Binary(string='Excel Report', readonly=True, attachment=False)
    xlsx_filename = fields.Char(string='Excel Filename', readonly=True)
    report_generated = fields.Boolean(string='Report Generated', default=False)
    
    statement_line_ids = fields.One2many(
        'commission.statement.line',
        'wizard_id',
        string='Statement Lines',
        readonly=True
    )
    
    def action_generate_statement(self):
        """Generate commission statement with enhanced structure."""
        self.ensure_one()
        
        _logger.info("Generating commission statement report")
        
        # Clear previous data
        self.statement_line_ids.unlink()
        
        # Generate statement lines
        self._generate_enhanced_statement_lines()
        
        # Generate reports based on format
        if self.output_format in ['pdf', 'both']:
            self._generate_enhanced_pdf_report()
        
        if self.output_format in ['xlsx', 'both']:
            self._generate_enhanced_xlsx_report()
        
        self.report_generated = True
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commission Statement Report'),
            'res_model': 'commission.statement.wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': dict(self.env.context, report_generated=True)
        }
    
    def _generate_enhanced_statement_lines(self):
        """Generate statement lines with required columns."""
        # Build domain for sale orders
        domain = [
            ('date_order', '>=', fields.Datetime.combine(self.date_from, fields.Datetime.min.time())),
            ('date_order', '<=', fields.Datetime.combine(self.date_to, fields.Datetime.max.time())),
        ]
        
        if not self.include_draft:
            domain.append(('state', 'in', ['sale', 'done']))
        
        # If specific partner selected, filter by that partner
        if self.partner_id:
            partner_domain = [
                '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|',
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
            domain.extend(partner_domain)
        
        sale_orders = self.env['sale.order'].search(domain, order='date_order desc')
        
        lines_data = []
        for order in sale_orders:
            # Get all commission entries from this order
            commission_entries = self._extract_all_commissions(order)
            
            for entry in commission_entries:
                # Skip if specific partner selected and doesn't match
                if self.partner_id and entry['partner_id'] != self.partner_id.id:
                    continue
                
                lines_data.append({
                    'wizard_id': self.id,
                    'commission_name': entry['partner_name'],
                    'order_ref': order.name,
                    'customer_reference': self._get_customer_reference(order),
                    'commission_type': entry['commission_type'],
                    'rate': entry['rate'],
                    'total': entry['amount'],
                    'currency_id': order.currency_id.id,
                    'sale_order_id': order.id,
                    'partner_id': entry['partner_id'],
                })
        
        # Create statement lines
        if lines_data:
            self.env['commission.statement.line'].create(lines_data)
    
    def _extract_all_commissions(self, order):
        """Extract all commission entries from a sale order."""
        commissions = []
        
        # Mapping of commission fields
        commission_mappings = [
            ('agent1_partner_id', 'agent1_amount', 'agent1_rate', 'agent1_commission_type', 'Agent 1'),
            ('agent2_partner_id', 'agent2_amount', 'agent2_rate', 'agent2_commission_type', 'Agent 2'),
            ('broker_partner_id', 'broker_amount', 'broker_rate', 'broker_commission_type', 'Broker'),
            ('referrer_partner_id', 'referrer_amount', 'referrer_rate', 'referrer_commission_type', 'Referrer'),
            ('cashback_partner_id', 'cashback_amount', 'cashback_rate', 'cashback_commission_type', 'Cashback'),
            ('other_external_partner_id', 'other_external_amount', 'other_external_rate', 'other_external_commission_type', 'Other External'),
            ('consultant_id', 'salesperson_commission', 'consultant_comm_percentage', 'consultant_commission_type', 'Consultant'),
            ('manager_id', 'manager_commission', 'manager_comm_percentage', 'manager_legacy_commission_type', 'Manager'),
            ('second_agent_id', 'second_agent_commission', 'second_agent_comm_percentage', 'second_agent_commission_type', 'Second Agent'),
            ('director_id', 'director_commission', 'director_comm_percentage', 'director_legacy_commission_type', 'Director'),
            ('manager_partner_id', 'manager_amount', 'manager_rate', 'manager_commission_type', 'Manager Partner'),
            ('director_partner_id', 'director_amount', 'director_rate', 'director_commission_type', 'Director Partner'),
        ]
        
        for partner_field, amount_field, rate_field, type_field, label in commission_mappings:
            partner = getattr(order, partner_field, False)
            if partner:
                amount = getattr(order, amount_field, 0)
                if amount > 0:
                    rate = getattr(order, rate_field, 0)
                    commission_type = getattr(order, type_field, 'percent_unit_price')
                    
                    # Format commission type
                    type_display = self._format_commission_type(commission_type)
                    
                    commissions.append({
                        'partner_id': partner.id,
                        'partner_name': partner.name,
                        'amount': amount,
                        'rate': rate,
                        'commission_type': type_display,
                        'label': label,
                    })
        
        return commissions
    
    def _format_commission_type(self, commission_type):
        """Format commission type for display."""
        type_mapping = {
            'fixed': 'Fixed',
            'percent_unit_price': 'Unit Price',
            'percent_untaxed_total': 'Untaxed Total',
        }
        return type_mapping.get(commission_type, commission_type)
    
    def _get_customer_reference(self, order):
        """Get customer reference from order."""
        references = []
        
        # Add project name if available
        if order.project_id:
            references.append(order.project_id.name)
        
        # Add unit if available
        if hasattr(order, 'unit_id') and order.unit_id:
            references.append(order.unit_id.name)
        
        # Add partner name
        if order.partner_id:
            references.append(order.partner_id.name)
        
        return ' - '.join(references) if references else order.name
    
    def _generate_enhanced_pdf_report(self):
        """Generate enhanced PDF report."""
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.lib.enums import TA_CENTER, TA_RIGHT
        except ImportError:
            raise UserError(_("reportlab library is required for PDF export. Please install it with: pip install reportlab"))
        
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=landscape(A4), 
                               topMargin=0.5*inch, bottomMargin=0.5*inch,
                               leftMargin=0.5*inch, rightMargin=0.5*inch)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#800020'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=12
        )
        
        # Company info
        company = self.env.company
        elements.append(Paragraph(f"<b>{company.name}</b>", title_style))
        elements.append(Paragraph("COMMISSION STATEMENT REPORT", title_style))
        
        # Report info
        period_text = f"Period: {self.date_from.strftime('%d/%m/%Y')} - {self.date_to.strftime('%d/%m/%Y')}"
        elements.append(Paragraph(period_text, header_style))
        
        if self.partner_id:
            elements.append(Paragraph(f"Agent: {self.partner_id.name}", header_style))
        else:
            elements.append(Paragraph("All Agents", header_style))
        
        elements.append(Spacer(1, 20))
        
        # Table data
        table_data = [[
            'COMMISSION NAME',
            'ORDER REF',
            'CUSTOMER REFERENCE',
            'COMMISSION TYPE',
            'RATE',
            'TOTAL'
        ]]
        
        total_amount = 0.0
        currency_symbol = self.env.company.currency_id.symbol or ''
        
        for line in self.statement_line_ids:
            rate_display = f"{line.rate:.2f}%" if line.rate else "Fixed"
            total_display = f"{currency_symbol}{line.total:,.2f}"
            
            table_data.append([
                line.commission_name or '',
                line.order_ref or '',
                line.customer_reference or '',
                line.commission_type or '',
                rate_display,
                total_display
            ])
            
            total_amount += line.total
        
        # Add total row
        table_data.append([
            '', '', '', '', 'TOTAL:',
            f"{currency_symbol}{total_amount:,.2f}"
        ])
        
        # Create table
        col_widths = [1.8*inch, 1.2*inch, 2.5*inch, 1.5*inch, 0.8*inch, 1.2*inch]
        table = Table(table_data, colWidths=col_widths)
        
        # Table style
        table_style = TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#800020')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('ALIGN', (4, 1), (5, -1), 'RIGHT'),  # Align rate and total columns
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -2), 1, colors.black),
            
            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#800020')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (4, -1), (5, -1), 'RIGHT'),
        ])
        
        table.setStyle(table_style)
        elements.append(table)
        
        # Footer
        elements.append(Spacer(1, 30))
        footer_text = f"Generated on: {fields.Datetime.now().strftime('%d/%m/%Y %H:%M')}"
        elements.append(Paragraph(footer_text, styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        output.seek(0)
        
        filename = f"Commission_Statement_{self.date_from.strftime('%Y%m%d')}_{self.date_to.strftime('%Y%m%d')}.pdf"
        
        self.write({
            'pdf_data': base64.b64encode(output.read()),
            'pdf_filename': filename,
        })
    
    def _generate_enhanced_xlsx_report(self):
        """Generate enhanced Excel report."""
        try:
            import xlsxwriter
        except ImportError:
            raise UserError(_("xlsxwriter library is required for Excel export. Please install it with: pip install xlsxwriter"))
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Commission Statement')
        
        # Formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'font_color': '#800020',
            'align': 'center',
            'valign': 'vcenter',
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#800020',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })
        
        data_format = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'border': 1,
        })
        
        money_format = workbook.add_format({
            'num_format': '#,##0.00',
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
        })
        
        percent_format = workbook.add_format({
            'num_format': '0.00%',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })
        
        total_label_format = workbook.add_format({
            'bold': True,
            'bg_color': '#800020',
            'font_color': 'white',
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
        })
        
        total_value_format = workbook.add_format({
            'bold': True,
            'bg_color': '#800020',
            'font_color': 'white',
            'num_format': '#,##0.00',
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
        })
        
        # Title
        worksheet.merge_range('A1:F1', f"{self.env.company.name}", title_format)
        worksheet.merge_range('A2:F2', "COMMISSION STATEMENT REPORT", title_format)
        
        # Period info
        period_text = f"Period: {self.date_from.strftime('%d/%m/%Y')} - {self.date_to.strftime('%d/%m/%Y')}"
        worksheet.merge_range('A3:F3', period_text, workbook.add_format({'align': 'center'}))
        
        if self.partner_id:
            worksheet.merge_range('A4:F4', f"Agent: {self.partner_id.name}", workbook.add_format({'align': 'center'}))
            start_row = 6
        else:
            worksheet.merge_range('A4:F4', "All Agents", workbook.add_format({'align': 'center'}))
            start_row = 6
        
        # Headers
        headers = [
            'COMMISSION NAME',
            'ORDER REF',
            'CUSTOMER REFERENCE',
            'COMMISSION TYPE',
            'RATE',
            'TOTAL'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(start_row, col, header, header_format)
        
        # Data rows
        row = start_row + 1
        total_amount = 0.0
        
        for line in self.statement_line_ids:
            worksheet.write(row, 0, line.commission_name or '', data_format)
            worksheet.write(row, 1, line.order_ref or '', data_format)
            worksheet.write(row, 2, line.customer_reference or '', data_format)
            worksheet.write(row, 3, line.commission_type or '', data_format)
            
            if line.rate:
                worksheet.write(row, 4, line.rate / 100, percent_format)
            else:
                worksheet.write(row, 4, 'Fixed', data_format)
            
            worksheet.write(row, 5, line.total, money_format)
            
            total_amount += line.total
            row += 1
        
        # Total row
        worksheet.merge_range(row, 0, row, 4, 'TOTAL:', total_label_format)
        worksheet.write(row, 5, total_amount, total_value_format)
        
        # Column widths
        worksheet.set_column('A:A', 20)  # Commission Name
        worksheet.set_column('B:B', 15)  # Order Ref
        worksheet.set_column('C:C', 30)  # Customer Reference
        worksheet.set_column('D:D', 18)  # Commission Type
        worksheet.set_column('E:E', 10)  # Rate
        worksheet.set_column('F:F', 15)  # Total
        
        # Footer
        row += 2
        worksheet.write(row, 0, f"Generated on: {fields.Datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        workbook.close()
        output.seek(0)
        
        filename = f"Commission_Statement_{self.date_from.strftime('%Y%m%d')}_{self.date_to.strftime('%Y%m%d')}.xlsx"
        
        self.write({
            'xlsx_data': base64.b64encode(output.read()),
            'xlsx_filename': filename,
        })
    
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
    """Enhanced commission statement line model."""
    
    _name = 'commission.statement.line'
    _description = 'Commission Statement Line'
    _order = 'order_ref desc'
    
    wizard_id = fields.Many2one(
        'commission.statement.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )
    
    # Main columns as requested
    commission_name = fields.Char(string='Commission Name', required=True)
    order_ref = fields.Char(string='Order Ref', required=True)
    customer_reference = fields.Char(string='Customer Reference', required=True)
    commission_type = fields.Char(string='Commission Type', required=True)
    rate = fields.Float(string='Rate', digits=(5, 2))
    total = fields.Monetary(string='Total', currency_field='currency_id', required=True)
    
    # Additional fields for reference
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    partner_id = fields.Many2one('res.partner', string='Partner')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
