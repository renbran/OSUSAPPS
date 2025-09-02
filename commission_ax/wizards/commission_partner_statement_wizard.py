# wizards/__init__.py
# -*- coding: utf-8 -*-
"""Commission wizards initialization."""

from . import commission_cancel_wizard
from . import commission_draft_wizard
from . import commission_report_wizard
from . import commission_partner_statement_wizard


# wizards/commission_cancel_wizard.py
# -*- coding: utf-8 -*-
"""Wizard for commission cancellation confirmation."""

import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CommissionCancelWizard(models.TransientModel):
    """Wizard to confirm commission cancellation."""
    
    _name = 'commission.cancel.wizard'
    _description = 'Commission Cancel Wizard'
    _transient_max_hours = 1.0
    
    sale_order_ids = fields.Many2many(
        'sale.order',
        string='Sale Orders',
        required=True,
        help="Sale orders to be cancelled"
    )
    
    message = fields.Text(
        string='Cancellation Impact',
        readonly=True,
        compute='_compute_message'
    )
    
    @api.depends('sale_order_ids')
    def _compute_message(self):
        """Compute warning message about cancellation impact."""
        for wizard in self:
            if not wizard.sale_order_ids:
                wizard.message = _("No sale orders selected.")
                continue
                
            po_count = sum(len(order.purchase_order_ids) for order in wizard.sale_order_ids)
            
            message_parts = [
                _("You are about to cancel %d sale order(s).") % len(wizard.sale_order_ids),
            ]
            
            if po_count > 0:
                message_parts.append(
                    _("This will also cancel %d related commission purchase order(s).") % po_count
                )
            
            message_parts.append(_("This action cannot be undone."))
            
            wizard.message = "\n".join(message_parts)
    
    def action_confirm_cancel(self):
        """Confirm and execute the cancellation."""
        self.ensure_one()
        _logger.info("Cancelling %d sale orders", len(self.sale_order_ids))
        
        for order in self.sale_order_ids:
            # Cancel related purchase orders first
            for po in order.purchase_order_ids:
                if po.state != 'cancel':
                    try:
                        po.button_cancel()
                        po.message_post(
                            body=_("Cancelled due to sale order %s cancellation") % order.name
                        )
                    except Exception as e:
                        _logger.warning("Could not cancel PO %s: %s", po.name, str(e))
            
            # Cancel the sale order
            order.action_cancel()
            order.commission_status = 'cancelled'
            order.message_post(body=_("Commission cancelled via wizard"))
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Cancelled'),
                'message': _('%d sale order(s) and related documents cancelled.') % len(self.sale_order_ids),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_abort_cancel(self):
        """Abort the cancellation."""
        return {'type': 'ir.actions.act_window_close'}


# wizards/commission_draft_wizard.py
# -*- coding: utf-8 -*-
"""Wizard for setting commission to draft."""

import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CommissionDraftWizard(models.TransientModel):
    """Wizard to confirm setting commission to draft."""
    
    _name = 'commission.draft.wizard'
    _description = 'Commission Draft Wizard'
    _transient_max_hours = 1.0
    
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        required=True,
        help="Sale order to reset to draft"
    )
    
    message = fields.Text(
        string='Draft Impact',
        readonly=True,
        compute='_compute_message'
    )
    
    @api.depends('sale_order_id')
    def _compute_message(self):
        """Compute warning message about reset to draft impact."""
        for wizard in self:
            if not wizard.sale_order_id:
                wizard.message = _("No sale order selected.")
                continue
            
            order = wizard.sale_order_id
            po_count = len(order.purchase_order_ids)
            
            message_parts = [
                _("Setting sale order %s to draft will:") % order.name,
            ]
            
            if po_count > 0:
                message_parts.append(
                    _("• Cancel %d related commission purchase order(s)") % po_count
                )
            
            message_parts.extend([
                _("• Reset commission status to draft"),
                _("• Clear commission processed flag"),
                _("• Remove commission blocked reason"),
            ])
            
            wizard.message = "\n".join(message_parts)
    
    def action_confirm_draft(self):
        """Confirm and execute setting to draft."""
        self.ensure_one()
        order = self.sale_order_id
        
        _logger.info("Setting sale order %s to draft", order.name)
        
        # Cancel related purchase orders
        for po in order.purchase_order_ids:
            if po.state not in ['draft', 'cancel']:
                try:
                    po.button_cancel()
                    po.message_post(
                        body=_("Cancelled due to sale order %s set to draft") % order.name
                    )
                except Exception as e:
                    _logger.warning("Could not cancel PO %s: %s", po.name, str(e))
        
        # Reset commission fields
        order.write({
            'commission_status': 'draft',
            'commission_processed': False,
            'commission_blocked_reason': False,
        })
        
        # Set to draft if method exists
        if hasattr(order, 'action_draft'):
            order.action_draft()
        
        order.message_post(body=_("Commission reset to draft via wizard"))
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Reset to Draft'),
                'message': _('Sale order reset to draft. Related documents cancelled.'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_abort_draft(self):
        """Abort setting to draft."""
        return {'type': 'ir.actions.act_window_close'}


# wizards/commission_report_wizard.py
# -*- coding: utf-8 -*-
"""Wizard for commission report generation."""

import base64
import io
import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CommissionReportWizard(models.TransientModel):
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


# wizards/commission_partner_statement_wizard.py
# -*- coding: utf-8 -*-
"""Wizard for partner commission statement generation."""

import base64
import io
import logging
from datetime import date, timedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class CommissionPartnerStatementWizard(models.TransientModel):
    """Wizard to generate partner commission statements."""
    
    _name = 'commission.partner.statement.wizard'
    _description = 'Commission Partner Statement Wizard'
    _transient_max_hours = 1.0
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
        help="Partner for statement generation"
    )
    
    date_from = fields.Date(
        string='Date From',
        required=True,
        default=lambda self: date.today().replace(day=1) - timedelta(days=1),
        help="Start date for statement period"
    )
    
    date_to = fields.Date(
        string='Date To',
        required=True,
        default=lambda self: date.today(),
        help="End date for statement period"
    )
    
    file_data = fields.Binary(
        string='Excel Report',
        readonly=True,
        attachment=False
    )
    
    file_name = fields.Char(
        string='Excel Filename',
        readonly=True
    )
    
    pdf_data = fields.Binary(
        string='PDF Report',
        readonly=True,
        attachment=False
    )
    
    pdf_name = fields.Char(
        string='PDF Filename',
        readonly=True
    )
    
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """Validate date range."""
        for wizard in self:
            if wizard.date_from > wizard.date_to:
                raise UserError(_("Date From must be before Date To"))
    
    def action_generate_report(self):
        """Generate partner commission statement."""
        self.ensure_one()
        
        _logger.info("Generating statement for partner %s from %s to %s",
                    self.partner_id.name, self.date_from, self.date_to)
        
        # Generate Excel report
        excel_data = self._generate_excel_report()
        self.file_data = base64.b64encode(excel_data)
        self.file_name = 'Commission_Statement_%s_%s.xlsx' % (
            self.partner_id.name.replace(' ', '_'),
            fields.Date.today()
        )
        
        # Generate PDF report
        pdf_data = self._generate_pdf_report()
        if pdf_data:
            self.pdf_data = base64.b64encode(pdf_data)
            self.pdf_name = 'Commission_Statement_%s_%s.pdf' % (
                self.partner_id.name.replace(' ', '_'),
                fields.Date.today()
            )
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'commission.partner.statement.wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': self.env.context,
        }
    
    def _generate_excel_report(self):
        """Generate Excel report."""
        output = io.BytesIO()
        
        try:
            import xlsxwriter
        except ImportError:
            raise UserError(_("xlsxwriter library is required for Excel export"))
        
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Commission Statement')
        
        # Formats
        bold = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': '#,##0.00'})
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#800020',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
        })
        
        # Header
        worksheet.write('A1', 'Partner:', bold)
        worksheet.write('B1', self.partner_id.name)
        worksheet.write('A2', 'Period:', bold)
        worksheet.write('B2', '%s to %s' % (self.date_from, self.date_to))
        
        # Get commission data
        data_rows = self._get_commission_data()
        
        # Table headers
        headers = ['Date', 'Order', 'Customer', 'Type', 'Base Amount', 'Rate (%)', 'Commission']
        for col, header in enumerate(headers):
            worksheet.write(4, col, header, header_format)
        
        # Data rows
        row = 5
        total_commission = 0.0
        
        for data in data_rows:
            worksheet.write(row, 0, data['date'], date_format)
            worksheet.write(row, 1, data['order'])
            worksheet.write(row, 2, data['customer'])
            worksheet.write(row, 3, data['type'])
            worksheet.write(row, 4, data['base_amount'], money)
            worksheet.write(row, 5, data['rate'])
            worksheet.write(row, 6, data['commission'], money)
            total_commission += data['commission']
            row += 1
        
        # Total row
        worksheet.write(row + 1, 5, 'Total:', bold)
        worksheet.write(row + 1, 6, total_commission, money)
        
        # Adjust column widths
        worksheet.set_column('A:A', 12)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:D', 12)
        worksheet.set_column('E:G', 15)
        
        workbook.close()
        output.seek(0)
        return output.read()
    
    def _generate_pdf_report(self):
        """Generate PDF report."""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
        except ImportError:
            _logger.warning("reportlab not installed, PDF generation skipped")
            return False
        
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        elements.append(Paragraph("Commission Statement", styles['Title']))
        elements.append(Spacer(1, 12))
        
        # Partner info
        elements.append(Paragraph("<b>Partner:</b> %s" % self.partner_id.name, styles['Normal']))
        elements.append(Paragraph("<b>Period:</b> %s to %s" % (self.date_from, self.date_to), styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Data table
        data_rows = self._get_commission_data()
        table_data = [['Date', 'Order', 'Customer', 'Type', 'Base', 'Rate', 'Commission']]
        
        total = 0.0
        for data in data_rows:
            table_data.append([
                str(data['date']),
                data['order'],
                data['customer'][:30],  # Truncate long names
                data['type'],
                '%.2f' % data['base_amount'],
                '%.1f%%' % data['rate'],
                '%.2f' % data['commission'],
            ])
            total += data['commission']
        
        # Add total row
        table_data.append(['', '', '', '', '', 'Total:', '%.2f' % total])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.5, 0, 0.125)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(table)
        
        doc.build(elements)
        output.seek(0)
        return output.read()
    
    def _get_commission_data(self):
        """Get commission data for the partner."""
        data = []
        
        # Search for sale orders with commissions
        domain = [
            ('date_order', '>=', self.date_from),
            ('date_order', '<=', self.date_to),
            '|', '|', '|', '|', '|',
            ('agent1_partner_id', '=', self.partner_id.id),
            ('agent2_partner_id', '=', self.partner_id.id),
            ('broker_partner_id', '=', self.partner_id.id),
            ('referrer_partner_id', '=', self.partner_id.id),
            ('consultant_id', '=', self.partner_id.id),
            ('manager_partner_id', '=', self.partner_id.id),
        ]
        
        orders = self.env['sale.order'].search(domain, order='date_order')
        
        for order in orders:
            # Determine commission for this partner
            if order.agent1_partner_id == self.partner_id:
                data.append({
                    'date': order.date_order.date() if order.date_order else date.today(),
                    'order': order.name,
                    'customer': order.partner_id.name,
                    'type': 'Agent 1',
                    'base_amount': order.amount_total,
                    'rate': getattr(order, 'agent1_rate', 0),
                    'commission': getattr(order, 'agent1_amount', 0),
                })
            
            if order.agent2_partner_id == self.partner_id:
                data.append({
                    'date': order.date_order.date() if order.date_order else date.today(),
                    'order': order.name,
                    'customer': order.partner_id.name,
                    'type': 'Agent 2',
                    'base_amount': order.amount_total,
                    'rate': getattr(order, 'agent2_rate', 0),
                    'commission': getattr(order, 'agent2_amount', 0),
                })
            
            # Add other commission types similarly...
            
        return data