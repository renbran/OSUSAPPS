from odoo import models, fields, api
from odoo.http import request, Controller, route
from odoo.exceptions import UserError
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import logging

_logger = logging.getLogger(__name__)

class CommissionReportGenerator(models.Model):
    _name = 'commission.report.generator'
    _description = 'Commission Report Generator'

    def generate_commission_report(self, sale_order_id):
        """Generate professional commission report for a sale order"""
        sale_order = self.env['sale.order'].browse(sale_order_id)
        if not sale_order.exists():
            raise UserError("Sale order not found")
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, 
                               bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.Color(0.4, 0.1, 0.4),  # Purple color
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.white,
            backColor=colors.Color(0.6, 0.2, 0.4),  # Purple background
            spaceAfter=10,
            spaceBefore=15,
            leftIndent=10,
            rightIndent=10
        )
        
        # Company Header
        company = sale_order.company_id
        story.append(Paragraph(f"{company.name}", header_style))
        if company.street:
            story.append(Paragraph(f"{company.street}", styles['Normal']))
        if company.city:
            story.append(Paragraph(f"{company.city}, {company.country_id.name or ''}", styles['Normal']))
        if company.phone:
            story.append(Paragraph(f"Phone: {company.phone}", styles['Normal']))
        if company.email:
            story.append(Paragraph(f"Email: {company.email}", styles['Normal']))
        if company.website:
            story.append(Paragraph(f"Website: {company.website}", styles['Normal']))
        if company.vat:
            story.append(Paragraph(f"VAT: {company.vat}", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Order Summary Section
        story.append(Paragraph("ORDER SUMMARY", section_style))
        
        order_data = [
            ['DESCRIPTION', 'QTY', 'UNIT PRICE (AED)', 'SUBTOTAL (AED)']
        ]
        
        for line in sale_order.order_line:
            order_data.append([
                line.product_id.name or line.name,
                f"{line.product_uom_qty:.2f}",
                f"{line.price_unit:,.2f}",
                f"{line.price_subtotal:,.2f}"
            ])
        
        order_data.append(['', '', 'Order Total (AED):', f"{sale_order.amount_total:,.2f}"])
        
        order_table = Table(order_data, colWidths=[3*inch, 0.8*inch, 1.2*inch, 1.2*inch])
        order_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.6, 0.2, 0.4)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.Color(0.95, 0.95, 0.95)),
            ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.9, 0.9, 0.9)),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(order_table)
        story.append(Spacer(1, 20))
        
        # External Commissions Section
        if sale_order.total_external_commission_amount > 0:
            story.append(Paragraph("EXTERNAL COMMISSIONS", section_style))
            
            external_data = [['PARTY', 'PARTNER', 'TYPE', 'RATE (%)', 'AMOUNT (AED)']]
            
            if sale_order.broker_partner_id and sale_order.broker_amount > 0:
                external_data.append([
                    'Broker', 
                    sale_order.broker_partner_id.name,
                    dict(sale_order._fields['broker_commission_type'].selection).get(sale_order.broker_commission_type, ''),
                    f"{sale_order.broker_rate:.2f}",
                    f"{sale_order.broker_amount:,.2f}"
                ])
            
            if sale_order.referrer_partner_id and sale_order.referrer_amount > 0:
                external_data.append([
                    'Referrer',
                    sale_order.referrer_partner_id.name,
                    dict(sale_order._fields['referrer_commission_type'].selection).get(sale_order.referrer_commission_type, ''),
                    f"{sale_order.referrer_rate:.2f}",
                    f"{sale_order.referrer_amount:,.2f}"
                ])
            
            if sale_order.cashback_partner_id and sale_order.cashback_amount > 0:
                external_data.append([
                    'Cashback',
                    sale_order.cashback_partner_id.name,
                    dict(sale_order._fields['cashback_commission_type'].selection).get(sale_order.cashback_commission_type, ''),
                    f"{sale_order.cashback_rate:.2f}",
                    f"{sale_order.cashback_amount:,.2f}"
                ])
            
            if sale_order.other_external_partner_id and sale_order.other_external_amount > 0:
                external_data.append([
                    'Other External',
                    sale_order.other_external_partner_id.name,
                    dict(sale_order._fields['other_external_commission_type'].selection).get(sale_order.other_external_commission_type, ''),
                    f"{sale_order.other_external_rate:.2f}",
                    f"{sale_order.other_external_amount:,.2f}"
                ])
            
            external_data.append(['', '', '', 'Total External (AED):', f"{sale_order.total_external_commission_amount:,.2f}"])
            
            if len(external_data) > 2:  # Has data beyond headers and total
                external_table = Table(external_data, colWidths=[1*inch, 1.5*inch, 1.2*inch, 0.8*inch, 1*inch])
                external_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.6, 0.2, 0.4)),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 1), (1, -2), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -2), colors.Color(0.95, 0.95, 0.95)),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.9, 0.9, 0.9)),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('SPAN', (0, -1), (3, -1)),
                ]))
                
                story.append(external_table)
                story.append(Spacer(1, 15))
        
        # Internal Commissions Section
        if sale_order.total_internal_commission_amount > 0:
            story.append(Paragraph("INTERNAL COMMISSIONS", section_style))
            
            internal_data = [['ROLE', 'PARTNER', 'TYPE', 'RATE (%)', 'AMOUNT (AED)']]
            
            # New Commission Structure
            if sale_order.agent1_partner_id and sale_order.agent1_amount > 0:
                internal_data.append([
                    'Agent 1',
                    sale_order.agent1_partner_id.name,
                    dict(sale_order._fields['agent1_commission_type'].selection).get(sale_order.agent1_commission_type, ''),
                    f"{sale_order.agent1_rate:.2f}",
                    f"{sale_order.agent1_amount:,.2f}"
                ])
            
            if sale_order.agent2_partner_id and sale_order.agent2_amount > 0:
                internal_data.append([
                    'Agent 2',
                    sale_order.agent2_partner_id.name,
                    dict(sale_order._fields['agent2_commission_type'].selection).get(sale_order.agent2_commission_type, ''),
                    f"{sale_order.agent2_rate:.2f}",
                    f"{sale_order.agent2_amount:,.2f}"
                ])
            
            if sale_order.manager_partner_id and sale_order.manager_amount > 0:
                internal_data.append([
                    'Manager',
                    sale_order.manager_partner_id.name,
                    dict(sale_order._fields['manager_commission_type'].selection).get(sale_order.manager_commission_type, ''),
                    f"{sale_order.manager_rate:.2f}",
                    f"{sale_order.manager_amount:,.2f}"
                ])
            
            if sale_order.director_partner_id and sale_order.director_amount > 0:
                internal_data.append([
                    'Director',
                    sale_order.director_partner_id.name,
                    dict(sale_order._fields['director_commission_type'].selection).get(sale_order.director_commission_type, ''),
                    f"{sale_order.director_rate:.2f}",
                    f"{sale_order.director_amount:,.2f}"
                ])
            
            # Legacy Commission Structure (if any)
            if sale_order.consultant_id and sale_order.salesperson_commission > 0:
                internal_data.append([
                    'Consultant (Legacy)',
                    sale_order.consultant_id.name,
                    dict(sale_order._fields['consultant_commission_type'].selection).get(sale_order.consultant_commission_type, ''),
                    f"{sale_order.consultant_comm_percentage:.2f}",
                    f"{sale_order.salesperson_commission:,.2f}"
                ])
            
            if sale_order.manager_id and sale_order.manager_commission > 0:
                internal_data.append([
                    'Manager (Legacy)',
                    sale_order.manager_id.name,
                    dict(sale_order._fields['manager_legacy_commission_type'].selection).get(sale_order.manager_legacy_commission_type, ''),
                    f"{sale_order.manager_comm_percentage:.2f}",
                    f"{sale_order.manager_commission:,.2f}"
                ])
            
            if sale_order.second_agent_id and sale_order.second_agent_commission > 0:
                internal_data.append([
                    'Second Agent (Legacy)',
                    sale_order.second_agent_id.name,
                    dict(sale_order._fields['second_agent_commission_type'].selection).get(sale_order.second_agent_commission_type, ''),
                    f"{sale_order.second_agent_comm_percentage:.2f}",
                    f"{sale_order.second_agent_commission:,.2f}"
                ])
            
            if sale_order.director_id and sale_order.director_commission > 0:
                internal_data.append([
                    'Director (Legacy)',
                    sale_order.director_id.name,
                    dict(sale_order._fields['director_legacy_commission_type'].selection).get(sale_order.director_legacy_commission_type, ''),
                    f"{sale_order.director_comm_percentage:.2f}",
                    f"{sale_order.director_commission:,.2f}"
                ])
            
            internal_data.append(['', '', '', 'Total Internal (AED):', f"{sale_order.total_internal_commission_amount:,.2f}"])
            
            if len(internal_data) > 2:  # Has data beyond headers and total
                internal_table = Table(internal_data, colWidths=[1*inch, 1.5*inch, 1.2*inch, 0.8*inch, 1*inch])
                internal_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.6, 0.2, 0.4)),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 1), (1, -2), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -2), colors.Color(0.95, 0.95, 0.95)),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.9, 0.9, 0.9)),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('SPAN', (0, -1), (3, -1)),
                ]))
                
                story.append(internal_table)
                story.append(Spacer(1, 15))
        
        # Summary Section
        story.append(Paragraph("COMMISSION SUMMARY", section_style))
        
        summary_data = [
            ['Total Commission (AED):', f"{sale_order.total_commission_amount:,.2f}"],
            ['Net Before VAT (AED):', f"{(sale_order.amount_total - sale_order.total_commission_amount):,.2f}"],
            ['VAT Amount (5 %) (AED):', f"{(sale_order.amount_total - sale_order.amount_untaxed):,.2f}"],
            ['Net Commission (AED):', f"{sale_order.net_company_share:,.2f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[4*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Footer
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_CENTER
        )
        
        story.append(Paragraph(f"Generated on {fields.Datetime.now().strftime('%B %d, %Y at %H:%M')}", footer_style))
        story.append(Paragraph(f"Sale Order: {sale_order.name} | Commission Status: {dict(sale_order._fields['commission_status'].selection).get(sale_order.commission_status, 'Draft')}", footer_style))
        
        # Build PDF
        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data

class CommissionReportWizard(models.TransientModel):
    _name = 'commission.report.wizard'
    _description = 'Commission Report Generation Wizard'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True)
    report_data = fields.Binary(string='Report', readonly=True)
    report_filename = fields.Char(string='Filename', readonly=True)

    def action_generate_report(self):
        """Generate and download commission report"""
        report_generator = self.env['commission.report.generator']
        pdf_data = report_generator.generate_commission_report(self.sale_order_id.id)
        
        filename = f"Commission_Report_{self.sale_order_id.name}_{fields.Date.today()}.pdf"
        
        self.write({
            'report_data': base64.b64encode(pdf_data),
            'report_filename': filename
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Commission Report Generated',
            'res_model': 'commission.report.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'report_generated': True}
        }

    def action_download_report(self):
        """Download the generated report"""
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model=commission.report.wizard&id={self.id}&field=report_data&download=true&filename={self.report_filename}',
            'target': 'self',
        }