import base64
import io
import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError

class CommissionReportWizard(models.TransientModel):
    include_notes = fields.Boolean(
        'Include Commission Notes',
        default=True,
        help="Include commission notes and blocked reasons if any"
    )
    report_type = fields.Selection([
        ('detailed', 'Detailed Commission Report'),
        ('summary', 'Summary Report')
    ], default='detailed', string='Report Type', required=True)
    """Wizard to generate commission reports."""
    
    _name = 'commission.report.wizard'
    _description = 'Commission Report Generation Wizard'
    _transient_max_hours = 1.0
    
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        required=True,
        help="Sale order for report generation"
    )
    
    report_data = fields.Binary(
        string='Report',
        readonly=True,
        attachment=False
    )
    
    report_filename = fields.Char(
        string='Filename',
        readonly=True
    )
    
    report_generated = fields.Boolean(
        string='Report Generated',
        default=False
    )
    
    def action_generate_report(self):
        """Generate commission report."""
        self.ensure_one()
        
        if not self.sale_order_id:
            raise UserError(_("Please select a sale order"))
        
        _logger.info("Generating commission report for %s", self.sale_order_id.name)
        
        # Check if commission_report_generator exists
        if 'commission.report.generator' in self.env:
            try:
                report_generator = self.env['commission.report.generator']
                pdf_data = report_generator.generate_commission_report(self.sale_order_id.id)
            except Exception as e:
                _logger.error("Report generation failed: %s", str(e))
                # Fallback to standard report
                pdf_data = self._generate_standard_report()
        else:
            # Use standard Odoo report
            pdf_data = self._generate_standard_report()
        
        filename = "Commission_Report_%s_%s.pdf" % (
            self.sale_order_id.name,
            fields.Date.today()
        )
        
        self.write({
            'report_data': base64.b64encode(pdf_data),
            'report_filename': filename,
            'report_generated': True,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commission Report Generated'),
            'res_model': 'commission.report.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'report_generated': True}
        }
    
    def _generate_standard_report(self):
        """Generate report using standard Odoo reporting."""
        # Try to find a report action
        report = self.env['ir.actions.report'].search([
            ('model', '=', 'sale.order'),
            ('report_name', 'like', 'commission'),
        ], limit=1)
        
        if report:
            pdf_content, _ = report._render_qweb_pdf(self.sale_order_id.ids)
            return pdf_content
        else:
            # Generate a simple PDF if no report template exists
            return self._generate_simple_pdf()
    
    def _generate_simple_pdf(self):
        """Generate a simple PDF report."""
        from io import BytesIO
        
        # Basic PDF generation (fallback)
        buffer = BytesIO()
        
        # Simple text content
        content = """
Commission Report
=================
Order: %s
Date: %s
Customer: %s
Total: %s

Commission Details:
-------------------
Total Commission: %s
External Commission: %s
Internal Commission: %s
Company Share: %s
""" % (
            self.sale_order_id.name,
            self.sale_order_id.date_order,
            self.sale_order_id.partner_id.name,
            self.sale_order_id.amount_total,
            getattr(self.sale_order_id, 'total_commission_amount', 0),
            getattr(self.sale_order_id, 'total_external_commission_amount', 0),
            getattr(self.sale_order_id, 'total_internal_commission_amount', 0),
            getattr(self.sale_order_id, 'company_share', 0),
        )
        
        buffer.write(content.encode('utf-8'))
        return buffer.getvalue()
    
    def action_download_report(self):
        """Download the generated report."""
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