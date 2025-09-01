from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
from io import BytesIO
import logging

# Only import reportlab if available, make it optional
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

_logger = logging.getLogger(__name__)

class CommissionReportGenerator(models.Model):
    _name = 'commission.report.generator'
    _description = 'Commission Report Generator'

    def generate_commission_report(self, sale_order_id):
        """Generate professional commission report for a sale order"""
        if not REPORTLAB_AVAILABLE:
            raise UserError("ReportLab library is not installed. Please install it with: pip install reportlab")
            
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
        
        # Commission Summary Section
        story.append(Paragraph("COMMISSION SUMMARY", section_style))
        
        summary_data = [
            ['Total Commission (AED):', f"{sale_order.total_commission_amount:,.2f}"],
            ['External Commissions (AED):', f"{sale_order.total_external_commission_amount:,.2f}"],
            ['Internal Commissions (AED):', f"{sale_order.total_internal_commission_amount:,.2f}"],
            ['Company Share (AED):', f"{sale_order.company_share:,.2f}"],
            ['Net Company Share (AED):', f"{sale_order.net_company_share:,.2f}"]
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