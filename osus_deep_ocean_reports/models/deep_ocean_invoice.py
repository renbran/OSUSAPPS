# -*- coding: utf-8 -*-

from odoo import models, fields, api
import qrcode
import base64
from io import BytesIO
from num2words import num2words


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Deep Ocean Theme Fields
    deep_ocean_theme_enabled = fields.Boolean(
        string='Use Deep Ocean Theme',
        default=True,
        help="Enable Deep Ocean professional styling for this document"
    )
    
    company_tagline = fields.Char(
        string='Company Tagline',
        default='Professional depths with azure highlights - perfect for data analytics and enterprise consulting',
        help="Company tagline to display on reports"
    )
    
    # Enhanced QR Code with Deep Ocean styling
    def generate_deep_ocean_qr_code(self):
        """Generate QR code with Deep Ocean styling"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # QR Code content with company info
        qr_content = f"""
Document: {self.name}
Company: {self.company_id.name}
Date: {self.invoice_date}
Amount: {self.amount_total} {self.currency_id.name}
Partner: {self.partner_id.name}
Reference: {self.ref or 'N/A'}
        """.strip()
        
        qr.add_data(qr_content)
        qr.make(fit=True)
        
        # Create QR code image with Deep Ocean colors
        img = qr.make_image(fill_color="#1e3a8a", back_color="#f8fafc")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return img_str

    @api.depends('amount_total')
    def _compute_deep_ocean_qr_code(self):
        """Compute QR code for Deep Ocean theme"""
        for record in self:
            if record.deep_ocean_theme_enabled:
                record.deep_ocean_qr_image = record.generate_deep_ocean_qr_code()
            else:
                record.deep_ocean_qr_image = False

    deep_ocean_qr_image = fields.Binary(
        string='Deep Ocean QR Code',
        compute='_compute_deep_ocean_qr_code',
        store=True,
        help="Deep Ocean themed QR code for this document"
    )

    def action_print_deep_ocean_invoice(self):
        """Print Deep Ocean themed invoice"""
        self.ensure_one()
        return self.env.ref('osus_deep_ocean_reports.action_report_deep_ocean_invoice').report_action(self)

    def action_print_deep_ocean_receipt(self):
        """Print Deep Ocean themed receipt"""
        self.ensure_one()
        return self.env.ref('osus_deep_ocean_reports.action_report_deep_ocean_receipt').report_action(self)

    @api.depends('amount_total')
    def _compute_amount_words_deep_ocean(self):
        """Compute amount in words with Deep Ocean styling"""
        for record in self:
            if record.amount_total:
                try:
                    # Convert amount to words in English
                    words = num2words(record.amount_total, to='currency', lang='en')
                    record.amount_total_words_deep_ocean = words.title()
                except Exception:
                    record.amount_total_words_deep_ocean = "Amount conversion error"
            else:
                record.amount_total_words_deep_ocean = "Zero"

    amount_total_words_deep_ocean = fields.Char(
        string='Amount in Words (Deep Ocean)',
        compute='_compute_amount_words_deep_ocean',
        help="Total amount expressed in words with Deep Ocean styling"
    )

    # Professional business fields for Deep Ocean theme
    business_analytics_ref = fields.Char(
        string='Analytics Reference',
        help="Reference for data analytics and consulting purposes"
    )
    
    enterprise_consultation_notes = fields.Text(
        string='Enterprise Consultation Notes',
        help="Notes for enterprise consulting engagement"
    )
    
    technical_expertise_level = fields.Selection([
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert')
    ], string='Technical Expertise Level', default='advanced',
    help="Level of technical expertise required for this engagement")

    def get_deep_ocean_colors(self):
        """Return Deep Ocean color palette"""
        return {
            'deep_navy': '#1e3a8a',
            'ocean_blue': '#3b82f6', 
            'sky_blue': '#0ea5e9',
            'ice_white': '#f8fafc',
            'gradient_primary': 'linear-gradient(135deg, #1e3a8a, #3b82f6)',
            'gradient_secondary': 'linear-gradient(135deg, #3b82f6, #0ea5e9)',
            'shadow_primary': '0 4px 20px rgba(30, 58, 138, 0.3)',
            'shadow_secondary': '0 2px 10px rgba(59, 130, 246, 0.2)'
        }