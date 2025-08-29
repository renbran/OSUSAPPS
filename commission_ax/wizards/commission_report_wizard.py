from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class CommissionCancelWizard(models.TransientModel):
    _name = 'commission.cancel.wizard'
    _description = 'Commission Cancel Confirmation Wizard'

    sale_order_ids = fields.Many2many('sale.order', string='Sale Orders')
    message = fields.Text(string='Cancellation Impact', readonly=True)

    def action_confirm_cancel(self):
        """Confirm the cancellation and execute it"""
        for order in self.sale_order_ids:
            order._execute_cancellation()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Cancelled',
                'message': f'Sale orders and related commission documents have been cancelled.',
                'type': 'success',
            }
        }

    def action_abort_cancel(self):
        """Abort the cancellation"""
        return {'type': 'ir.actions.act_window_close'}


class CommissionDraftWizard(models.TransientModel):
    _name = 'commission.draft.wizard'
    _description = 'Commission Draft Confirmation Wizard'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    message = fields.Text(string='Draft Impact', readonly=True)

    def action_confirm_draft(self):
        """Confirm setting to draft and execute it"""
        order = self.sale_order_id
        
        # Cancel confirmed purchase orders
        confirmed_pos = order.purchase_order_ids.filtered(
            lambda po: po.state not in ['draft', 'cancel']
        )
        for po in confirmed_pos:
            try:
                po.button_cancel()
                po.message_post(body=f"Cancelled due to sale order {order.name} set to draft")
            except Exception as e:
                _logger.warning(f"Could not cancel PO {po.name}: {str(e)}")
        
        # Cancel draft POs
        draft_pos = order.purchase_order_ids.filtered(lambda po: po.state == 'draft')
        draft_pos.button_cancel()
        
        # Reset commission status
        order.commission_status = 'draft'
        order.commission_processed = False
        order.commission_blocked_reason = False
        
        # Set to draft
        order.action_draft()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Set to Draft',
                'message': f'Sale order set to draft. Related commission documents cancelled.',
                'type': 'success',
            }
        }

    def action_abort_draft(self):
        """Abort setting to draft"""
        return {'type': 'ir.actions.act_window_close'}


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
        
        import base64
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