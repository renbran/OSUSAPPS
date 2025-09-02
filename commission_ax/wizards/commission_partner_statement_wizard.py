from odoo import models, fields, api
from odoo.exceptions import UserError
import io
import base64
import xlsxwriter

class CommissionPartnerStatementWizard(models.TransientModel):
    _name = 'commission.partner.statement.wizard'
    _description = 'Commission Partner Statement Wizard'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    file_data = fields.Binary('Report File')
    file_name = fields.Char('Filename')
    pdf_data = fields.Binary('PDF File')
    pdf_name = fields.Char('PDF Filename')

    def action_generate_report(self):
        SaleOrder = self.env['sale.order']
        # Search for all sale orders where the partner is involved in any commission field
        domain = ['|'] * 13 + [
            ('agent1_partner_id', '=', self.partner_id.id),
            ('agent2_partner_id', '=', self.partner_id.id),
            ('manager_partner_id', '=', self.partner_id.id),
            ('director_partner_id', '=', self.partner_id.id),
            ('consultant_id', '=', self.partner_id.id),
            ('SM_ID', '=', self.partner_id.id),
            ('second_agent_id', '=', self.partner_id.id),
            ('CXO_ID', '=', self.partner_id.id),
            ('broker_partner_id', '=', self.partner_id.id),
            ('referrer_partner_id', '=', self.partner_id.id),
            ('cashback_partner_id', '=', self.partner_id.id),
            ('other_external_partner_id', '=', self.partner_id.id),
        ]
        orders = SaleOrder.search(domain)

        # Prepare data rows for both Excel and PDF
        data_rows = []
        for order in orders:
            for line in order.order_line:
                commission_entries = []
                if order.consultant_id and order.consultant_id.id == self.partner_id.id:
                    commission_entries.append(('consultant', order.consultant_commission_type, order.consultant_comm_percentage, order.salesperson_commission))
                if order.SM_ID and order.SM_ID.id == self.partner_id.id:
                    commission_entries.append(('manager_legacy', order.manager_legacy_commission_type, order.manager_comm_percentage, order.manager_commission))
                if order.second_agent_id and order.second_agent_id.id == self.partner_id.id:
                    commission_entries.append(('second_agent', order.second_agent_commission_type, order.second_agent_comm_percentage, order.second_agent_commission))
                if order.CXO_ID and order.CXO_ID.id == self.partner_id.id:
                    commission_entries.append(('director_legacy', order.director_legacy_commission_type, order.director_comm_percentage, order.director_commission))
                if order.broker_partner_id and order.broker_partner_id.id == self.partner_id.id:
                    commission_entries.append(('broker', order.broker_commission_type, order.broker_rate, order.broker_amount))
                if order.referrer_partner_id and order.referrer_partner_id.id == self.partner_id.id:
                    commission_entries.append(('referrer', order.referrer_commission_type, order.referrer_rate, order.referrer_amount))
                if order.cashback_partner_id and order.cashback_partner_id.id == self.partner_id.id:
                    commission_entries.append(('cashback', order.cashback_commission_type, order.cashback_rate, order.cashback_amount))
                if order.other_external_partner_id and order.other_external_partner_id.id == self.partner_id.id:
                    commission_entries.append(('other_external', order.other_external_commission_type, order.other_external_rate, order.other_external_amount))
                if order.agent1_partner_id and order.agent1_partner_id.id == self.partner_id.id:
                    commission_entries.append(('agent1', order.agent1_commission_type, order.agent1_rate, order.agent1_amount))
                if order.agent2_partner_id and order.agent2_partner_id.id == self.partner_id.id:
                    commission_entries.append(('agent2', order.agent2_commission_type, order.agent2_rate, order.agent2_amount))
                if order.manager_partner_id and order.manager_partner_id.id == self.partner_id.id:
                    commission_entries.append(('manager', order.manager_commission_type, order.manager_rate, order.manager_amount))
                if order.director_partner_id and order.director_partner_id.id == self.partner_id.id:
                    commission_entries.append(('director', order.director_commission_type, order.director_rate, order.director_amount))
                for entry in commission_entries:
                    partner_type, commission_type, rate, amount = entry
                    data_rows.append([
                        order.date_order,
                        line.name,
                        partner_type,
                        commission_type,
                        line.price_unit,
                        rate,
                        amount
                    ])
        # Excel generation
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Statement')
        bold = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': '#,##0.00'})
        worksheet.write('A1', 'Name:', bold)
        worksheet.write('B1', self.partner_id.name)
        worksheet.write('A2', 'All Sales', bold)
        headers = ['Booking Date', 'Orderline/name', 'partner_type', 'commission_type', 'Unit price', 'rate', 'Amount']
        for col, header in enumerate(headers):
            worksheet.write(3, col, header, bold)
        for row_idx, row_data in enumerate(data_rows, start=4):
            worksheet.write(row_idx, 0, row_data[0])
            worksheet.write(row_idx, 1, row_data[1])
            worksheet.write(row_idx, 2, row_data[2])
            worksheet.write(row_idx, 3, row_data[3])
            worksheet.write(row_idx, 4, row_data[4], money)
            worksheet.write(row_idx, 5, row_data[5])
            worksheet.write(row_idx, 6, row_data[6], money)
        workbook.close()
        output.seek(0)
        file_data = base64.b64encode(output.read())
        self.file_data = file_data
        self.file_name = f'Commission_Statement_{self.partner_id.name}.xlsx'

        # PDF generation (simple table using reportlab)
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.lib import colors
            from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            pdf_output = io.BytesIO()
            doc = SimpleDocTemplate(pdf_output, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            elements.append(Paragraph(f"Name: {self.partner_id.name}", styles['Heading2']))
            elements.append(Paragraph("All Sales", styles['Normal']))
            elements.append(Spacer(1, 12))
            table_data = [headers] + data_rows
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            elements.append(table)
            doc.build(elements)
            pdf_output.seek(0)
            self.pdf_data = base64.b64encode(pdf_output.read())
            self.pdf_name = f'Commission_Statement_{self.partner_id.name}.pdf'
        except ImportError:
            self.pdf_data = False
            self.pdf_name = False

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'commission.partner.statement.wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': self.env.context,
        }
