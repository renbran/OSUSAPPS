# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class FixPDFError(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        """Override _render_qweb_pdf to fix empty PDF error"""
        _logger.info("Using enhanced PDF rendering with error handling")
        
        # Fix for PyPDF2.errors.EmptyFileError: Cannot read an empty file
        try:
            return super(FixPDFError, self)._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)
        except Exception as e:
            _logger.warning(f"Error rendering PDF: {str(e)}")
            # If failed, try again with wkhtmltopdf error handling options
            try:
                # Save original wkhtmltopdf_args
                original_args = self.env['ir.config_parameter'].sudo().get_param(
                    'report.url_wkhtmltopdf_args',
                    default='--disable-local-file-access --viewport-size 1280x1024'
                )
                
                # Add error handling options
                enhanced_args = original_args + ' --load-error-handling ignore --load-media-error-handling ignore'
                self.env['ir.config_parameter'].sudo().set_param(
                    'report.url_wkhtmltopdf_args', 
                    enhanced_args
                )
                
                # Try rendering with enhanced options
                _logger.info(f"Retrying PDF generation with enhanced options: {enhanced_args}")
                result = super(FixPDFError, self)._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)
                
                # Restore original args
                self.env['ir.config_parameter'].sudo().set_param(
                    'report.url_wkhtmltopdf_args', 
                    original_args
                )
                
                return result
            except Exception as retry_error:
                _logger.error(f"PDF generation failed with enhanced options: {str(retry_error)}")
                # Generate simple fallback PDF with error message
                return self._generate_fallback_pdf(f"Error rendering PDF: {str(e)}")
    
    def _generate_fallback_pdf(self, error_message):
        """Generate a simple fallback PDF with error message"""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from io import BytesIO
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setFont("Helvetica", 14)
        
        # Add company logo if available
        company = self.env.company
        if company.logo:
            from reportlab.lib.utils import ImageReader
            from io import BytesIO
            import base64
            
            logo_data = base64.b64decode(company.logo)
            logo_image = ImageReader(BytesIO(logo_data))
            c.drawImage(logo_image, 50, 700, width=100, height=100)
        
        # Add header and error message
        c.drawString(50, 650, f"{company.name} - Error Report")
        c.drawString(50, 600, "We encountered an error generating this report.")
        c.drawString(50, 570, "Please contact system administrator with the details below:")
        
        # Error details
        c.setFont("Helvetica", 12)
        y_position = 520
        for line in error_message.split("\n"):
            c.drawString(50, y_position, line)
            y_position -= 20
        
        # Add timestamp
        c.setFont("Helvetica", 10)
        timestamp = fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.drawString(50, 100, f"Generated: {timestamp}")
        c.drawString(50, 80, f"System: Odoo {self.env.cr.dbname}")
        
        # Add footer
        c.drawString(50, 50, f"© {datetime.now().year} {company.name}")
        
        c.save()
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content, 'pdf'
