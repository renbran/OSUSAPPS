from odoo import models, fields, api
from odoo.exceptions import UserError


class CommissionLinesReplaceWizard(models.TransientModel):
    """Wizard to confirm replacement of existing commission lines"""
    _name = 'commission.lines.replace.wizard'
    _description = 'Replace Commission Lines Wizard'

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        required=True
    )

    existing_lines_count = fields.Integer(
        string='Existing Lines',
        compute='_compute_existing_lines_count'
    )

    message = fields.Text(
        string='Message',
        default='This will delete all existing commission lines and create new ones from the legacy commission fields. This action cannot be undone.'
    )

    @api.depends('sale_order_id')
    def _compute_existing_lines_count(self):
        for wizard in self:
            if wizard.sale_order_id:
                wizard.existing_lines_count = len(wizard.sale_order_id.commission_line_ids)
            else:
                wizard.existing_lines_count = 0

    def action_confirm_replace(self):
        """Confirm and replace commission lines"""
        self.ensure_one()

        if not self.sale_order_id:
            raise UserError("Sale order is required.")

        # Delete existing commission lines
        if self.sale_order_id.commission_line_ids:
            # Check if any lines are processed
            processed_lines = self.sale_order_id.commission_line_ids.filtered(
                lambda l: l.state in ['processed', 'paid']
            )
            if processed_lines:
                raise UserError(
                    "Cannot replace commission lines that have been processed or paid. "
                    "Please cancel or reset the processed lines first."
                )

            self.sale_order_id.commission_line_ids.unlink()

        # Create new commission lines
        lines_created = self.sale_order_id._create_commission_lines_from_legacy()

        if lines_created > 0:
            self.sale_order_id.use_commission_lines = True

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Replaced commission lines. Created {lines_created} new commission lines.',
                'type': 'success',
            }
        }

    def action_cancel(self):
        """Cancel the replacement"""
        return {'type': 'ir.actions.act_window_close'}