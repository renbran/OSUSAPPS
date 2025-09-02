
import base64
import io
import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError

class CommissionReportWizard(models.TransientModel):
    _name = 'commission.report.wizard'
    _description = 'Commission Statement Report Wizard'
    _transient_max_hours = 1.0

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        required=True,
        help="Sales order for statement generation"
    )
    agent_id = fields.Many2one(
        'res.partner',
        string='Agent',
        required=True,
        help="Agent for statement"
    )
    output_format = fields.Selection([
        ('pdf', 'PDF'),
        ('xlsx', 'Excel')
    ], default='pdf', required=True, string='Format')
    report_data = fields.Binary(string='Report', readonly=True, attachment=False)
    report_filename = fields.Char(string='Filename', readonly=True)
    report_generated = fields.Boolean(string='Report Generated', default=False)

    def action_generate_report(self):
        self.ensure_one()
        if not self.sale_order_id or not self.agent_id:
            raise UserError(_("Please select both sales order and agent."))

        statement_lines = self._get_statement_lines()
        company = self.env.company
        currency = self.sale_order_id.currency_id
        filename = f"Commission_Statement_{self.sale_order_id.name}_{self.agent_id.name}."
        if self.output_format == 'pdf':
            pdf_data = self._generate_pdf(statement_lines, company, currency)
            self.report_data = base64.b64encode(pdf_data)
            self.report_filename = filename + 'pdf'
        else:
            xlsx_data = self._generate_xlsx(statement_lines, company, currency)
            self.report_data = base64.b64encode(xlsx_data)
            self.report_filename = filename + 'xlsx'
        self.report_generated = True
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commission Statement Generated'),
            'res_model': 'commission.report.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'report_generated': True}
        }

    def _get_statement_lines(self):
        # Collect all commission POs for this SO and agent
        lines = []
        for po in self.sale_order_id.purchase_order_ids.filtered(lambda p: p.agent_id == self.agent_id):
            lines.append(po._prepare_statement_line())
        return lines

    def _generate_pdf(self, lines, company, currency):
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
        except ImportError:
            raise UserError(_("reportlab is required for PDF export."))
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        elements = []
        # Header
        if company.logo:
            img = Image(io.BytesIO(base64.b64decode(company.logo)), width=80, height=40)
            elements.append(img)
        elements.append(Paragraph(f"Commission Statement – {self.sale_order_id.name}", styles['Title']))
        elements.append(Paragraph(f"Agent: {self.agent_id.name}", styles['Normal']))
        elements.append(Spacer(1, 12))
        # Table
        table_data = [[
            _('Agent Name'), _('Deal Date'), _('Commission Type'), _('Rate'), _('Property Price'),
            _('Gross Commission'), _('VAT (%)'), _('Net Commission'), _('Status'), _('PO Number'), _('Remarks')
        ]]
        for line in lines:
            table_data.append([
                line['agent_name'], line['deal_date'], line['commission_type'], line['rate'],
                self._format_currency(line['property_price'], currency),
                self._format_currency(line['gross_commission'], currency),
                line['vat'], self._format_currency(line['net_commission'], currency),
                line['status'], line['po_number'], line['remarks']
            ])
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#800020')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Printed on {fields.Datetime.now().strftime('%d-%b-%Y %H:%M UTC')}", styles['Normal']))
        doc.build(elements)
        output.seek(0)
        return output.read()

    def _generate_xlsx(self, lines, company, currency):
        try:
            import xlsxwriter
        except ImportError:
            raise UserError(_("xlsxwriter is required for Excel export."))
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(_('Commission Statement'))
        bold = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': '#,##0.00'})
        header_bg = workbook.add_format({'bg_color': '#800020', 'font_color': 'white', 'bold': True})
        headers = [
            _('Agent Name'), _('Deal Date'), _('Commission Type'), _('Rate'), _('Property Price'),
            _('Gross Commission'), _('VAT (%)'), _('Net Commission'), _('Status'), _('PO Number'), _('Remarks')
        ]
        for col, header in enumerate(headers):
            sheet.write(0, col, header, header_bg)
        row = 1
        for line in lines:
            sheet.write(row, 0, line['agent_name'])
            sheet.write(row, 1, line['deal_date'])
            sheet.write(row, 2, line['commission_type'])
            sheet.write(row, 3, line['rate'])
            sheet.write(row, 4, self._format_currency(line['property_price'], currency), money)
            sheet.write(row, 5, self._format_currency(line['gross_commission'], currency), money)
            sheet.write(row, 6, line['vat'])
            sheet.write(row, 7, self._format_currency(line['net_commission'], currency), money)
            sheet.write(row, 8, line['status'])
            sheet.write(row, 9, line['po_number'])
            sheet.write(row, 10, line['remarks'])
            row += 1
        workbook.close()
        output.seek(0)
        return output.read()

    def _format_currency(self, value, currency):
        return currency.symbol + ' ' + format(value, f'.{currency.decimal_places}f') if currency else str(value)

    def action_download_report(self):
        self.ensure_one()
        if not self.report_data:
            raise UserError(_("No report generated yet"))
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=%s&id=%d&field=report_data&download=true&filename=%s' % (
                self._name,
                self.id,
                self.report_filename
            ),
            'target': 'self',
        }