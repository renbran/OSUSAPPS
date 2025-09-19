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
            textColor=colors.Color(0.447, 0.184, 0.216),  # Burgundy color #722F37
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.white,
            backColor=colors.Color(0.447, 0.184, 0.216),  # Burgundy background #722F37
            spaceAfter=10,
            spaceBefore=15,
            leftIndent=10,
            rightIndent=10
        )
        
        # Company Header
        company = sale_order.company_id
        story.append(Paragraph("Deal and Commission Report", header_style))
        story.append(Paragraph(f"{company.name}", styles['Heading2']))
        
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
        
        # Deal Information
        if sale_order.client_order_ref:
            story.append(Paragraph(f"<b>Deal Reference:</b> {sale_order.client_order_ref}", styles['Normal']))
        story.append(Paragraph(f"<b>Order Date:</b> {sale_order.date_order.strftime('%B %d, %Y') if sale_order.date_order else 'N/A'}", styles['Normal']))
        story.append(Paragraph(f"<b>Salesperson:</b> {sale_order.user_id.name if sale_order.user_id else 'N/A'}", styles['Normal']))
        story.append(Spacer(1, 15))
        
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
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.447, 0.184, 0.216)),  # Burgundy
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
            ('GRID', (0, 0), (-1, -1), 1, colors.Color(0.447, 0.184, 0.216)),
        ]))
        
        story.append(order_table)
        story.append(Spacer(1, 20))
        
        # External Commissions Section
        external_commissions = self._get_external_commissions(sale_order)
        if external_commissions:
            story.append(Paragraph("EXTERNAL COMMISSIONS", section_style))
            story.append(self._create_commission_table(external_commissions))
            story.append(Spacer(1, 15))
        
        # Internal Commissions Section
        internal_commissions = self._get_internal_commissions(sale_order)
        if internal_commissions:
            story.append(Paragraph("INTERNAL COMMISSIONS", section_style))
            story.append(self._create_commission_table(internal_commissions))
            story.append(Spacer(1, 15))
        
        # Legacy Commissions Section
        legacy_commissions = self._get_legacy_commissions(sale_order)
        if legacy_commissions:
            story.append(Paragraph("LEGACY COMMISSIONS", section_style))
            story.append(self._create_commission_table(legacy_commissions))
            story.append(Spacer(1, 15))
        
        # Commission Summary Section
        story.append(Paragraph("COMMISSION SUMMARY", section_style))
        
        summary_data = []
        
        if sale_order.total_external_commission_amount and sale_order.total_external_commission_amount > 0:
            summary_data.append(['Total External Commissions (AED):', f"{sale_order.total_external_commission_amount:,.2f}"])
        
        if sale_order.total_internal_commission_amount and sale_order.total_internal_commission_amount > 0:
            summary_data.append(['Total Internal Commissions (AED):', f"{sale_order.total_internal_commission_amount:,.2f}"])
        
        summary_data.extend([
            ['Total Commission (AED):', f"{sale_order.total_commission_amount:,.2f}"],
            ['Company Share (AED):', f"{sale_order.company_share:,.2f}"],
            ['Net Company Share (AED):', f"{sale_order.net_company_share:,.2f}"]
        ])
        
        summary_table = Table(summary_data, colWidths=[4*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -2), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -2), colors.Color(0.95, 0.95, 0.95)),
            ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.447, 0.184, 0.216)),  # Burgundy for Net Company Share
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.Color(0.447, 0.184, 0.216)),
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

    def _get_external_commissions(self, sale_order):
        """Get external commission data"""
        commissions = []
        
        # Broker Commission
        if sale_order.broker_partner_id and sale_order.broker_amount and sale_order.broker_amount > 0:
            commission_type = self._format_commission_type(sale_order.broker_commission_type)
            rate = "-" if sale_order.broker_commission_type == 'fixed' else f"{sale_order.broker_rate}%"
            commissions.append([
                sale_order.broker_partner_id.name,
                commission_type,
                rate,
                f"{sale_order.broker_amount:,.2f}"
            ])
        
        # Referrer Commission
        if sale_order.referrer_partner_id and sale_order.referrer_amount and sale_order.referrer_amount > 0:
            commission_type = self._format_commission_type(sale_order.referrer_commission_type)
            rate = "-" if sale_order.referrer_commission_type == 'fixed' else f"{sale_order.referrer_rate}%"
            commissions.append([
                sale_order.referrer_partner_id.name,
                commission_type,
                rate,
                f"{sale_order.referrer_amount:,.2f}"
            ])
        
        # Cashback Commission
        if sale_order.cashback_partner_id and sale_order.cashback_amount and sale_order.cashback_amount > 0:
            commission_type = self._format_commission_type(sale_order.cashback_commission_type)
            rate = "-" if sale_order.cashback_commission_type == 'fixed' else f"{sale_order.cashback_rate}%"
            commissions.append([
                sale_order.cashback_partner_id.name,
                commission_type,
                rate,
                f"{sale_order.cashback_amount:,.2f}"
            ])
        
        # Other External Commission
        if sale_order.other_external_partner_id and sale_order.other_external_amount and sale_order.other_external_amount > 0:
            commission_type = self._format_commission_type(sale_order.other_external_commission_type)
            rate = "-" if sale_order.other_external_commission_type == 'fixed' else f"{sale_order.other_external_rate}%"
            commissions.append([
                sale_order.other_external_partner_id.name,
                commission_type,
                rate,
                f"{sale_order.other_external_amount:,.2f}"
            ])
        
        return commissions

    def _get_internal_commissions(self, sale_order):
        """Get internal commission data"""
        commissions = []
        
        # Agent 1 Commission
        if sale_order.agent1_partner_id and sale_order.agent1_amount and sale_order.agent1_amount > 0:
            commission_type = self._format_commission_type(sale_order.agent1_commission_type)
            rate = "-" if sale_order.agent1_commission_type == 'fixed' else f"{sale_order.agent1_rate}%"
            commissions.append([
                sale_order.agent1_partner_id.name,
                commission_type,
                rate,
                f"{sale_order.agent1_amount:,.2f}"
            ])
        
        # Agent 2 Commission
        if sale_order.agent2_partner_id and sale_order.agent2_amount and sale_order.agent2_amount > 0:
            commission_type = self._format_commission_type(sale_order.agent2_commission_type)
            rate = "-" if sale_order.agent2_commission_type == 'fixed' else f"{sale_order.agent2_rate}%"
            commissions.append([
                sale_order.agent2_partner_id.name,
                commission_type,
                rate,
                f"{sale_order.agent2_amount:,.2f}"
            ])
        
        # Manager Commission
        if sale_order.manager_partner_id and sale_order.manager_amount and sale_order.manager_amount > 0:
            commission_type = self._format_commission_type(sale_order.manager_commission_type)
            rate = "-" if sale_order.manager_commission_type == 'fixed' else f"{sale_order.manager_rate}%"
            commissions.append([
                sale_order.manager_partner_id.name,
                commission_type,
                rate,
                f"{sale_order.manager_amount:,.2f}"
            ])
        
        # Director Commission
        if sale_order.director_partner_id and sale_order.director_amount and sale_order.director_amount > 0:
            commission_type = self._format_commission_type(sale_order.director_commission_type)
            rate = "-" if sale_order.director_commission_type == 'fixed' else f"{sale_order.director_rate}%"
            commissions.append([
                sale_order.director_partner_id.name,
                commission_type,
                rate,
                f"{sale_order.director_amount:,.2f}"
            ])
        
        return commissions

    def _get_legacy_commissions(self, sale_order):
        """Get legacy commission data"""
        commissions = []
        
        # Consultant Commission
        if sale_order.consultant_id and sale_order.salesperson_commission and sale_order.salesperson_commission > 0:
            commission_type = self._format_commission_type(sale_order.consultant_commission_type)
            rate = "-" if sale_order.consultant_commission_type == 'fixed' else f"{sale_order.consultant_comm_percentage}%"
            commissions.append([
                sale_order.consultant_id.name,
                commission_type,
                rate,
                f"{sale_order.salesperson_commission:,.2f}"
            ])
        
        # Manager Legacy Commission
        if sale_order.manager_id and sale_order.manager_commission and sale_order.manager_commission > 0:
            commission_type = self._format_commission_type(sale_order.manager_legacy_commission_type)
            rate = "-" if sale_order.manager_legacy_commission_type == 'fixed' else f"{sale_order.manager_comm_percentage}%"
            commissions.append([
                sale_order.manager_id.name,
                commission_type,
                rate,
                f"{sale_order.manager_commission:,.2f}"
            ])
        
        # Second Agent Commission
        if sale_order.second_agent_id and sale_order.second_agent_commission and sale_order.second_agent_commission > 0:
            commission_type = self._format_commission_type(sale_order.second_agent_commission_type)
            rate = "-" if sale_order.second_agent_commission_type == 'fixed' else f"{sale_order.second_agent_comm_percentage}%"
            commissions.append([
                sale_order.second_agent_id.name,
                commission_type,
                rate,
                f"{sale_order.second_agent_commission:,.2f}"
            ])
        
        # Director Legacy Commission
        if sale_order.director_id and sale_order.director_commission and sale_order.director_commission > 0:
            commission_type = self._format_commission_type(sale_order.director_legacy_commission_type)
            rate = "-" if sale_order.director_legacy_commission_type == 'fixed' else f"{sale_order.director_comm_percentage}%"
            commissions.append([
                sale_order.director_id.name,
                commission_type,
                rate,
                f"{sale_order.director_commission:,.2f}"
            ])
        
        return commissions

    def _format_commission_type(self, commission_type):
        """Format commission type for display"""
        type_mapping = {
            'fixed': 'Fixed',
            'percent_unit_price': '% Unit Price',
            'percent_untaxed_total': '% Untaxed Total'
        }
        return type_mapping.get(commission_type, commission_type)

    def _create_commission_table(self, commission_data):
        """Create a commission table with burgundy styling"""
        if not commission_data:
            return None
        
        # Add header
        table_data = [['Partner', 'Type', 'Rate', 'Total (AED)']]
        table_data.extend(commission_data)
        
        commission_table = Table(table_data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 1.2*inch])
        commission_table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.447, 0.184, 0.216)),  # Burgundy
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body styling
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Partner names left-aligned
            ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),  # Total amounts right-aligned
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
            
            # Grid and borders
            ('GRID', (0, 0), (-1, -1), 1, colors.Color(0.447, 0.184, 0.216)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return commission_table