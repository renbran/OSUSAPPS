from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    commission_line_ids = fields.One2many('commission.line', 'sale_order_id', string='Commission Lines')
    commission_count = fields.Integer(string='Commission Count', compute='_compute_commission_count')
    total_commission_amount = fields.Monetary(string='Total Commission Amount', 
                                               compute='_compute_total_commission_amount',
                                               currency_field='currency_id')
    commission_generated = fields.Boolean(string='Commission Generated', default=False)

    @api.depends('commission_line_ids')
    def _compute_commission_count(self):
        for order in self:
            order.commission_count = len(order.commission_line_ids)

    @api.depends('commission_line_ids.commission_amount')
    def _compute_total_commission_amount(self):
        for order in self:
            order.total_commission_amount = sum(order.commission_line_ids.mapped('commission_amount'))

    def action_generate_commission(self):
        """Generate commission lines for this sale order"""
        self.ensure_one()
        if self.commission_generated:
            return
        
        if not self.user_id or not self.user_id.partner_id:
            return
        
        # Get commission rate from salesperson or use default
        commission_rate = self.user_id.partner_id.commission_rate or 5.0
        
        commission_line = self.env['commission.line'].create_from_sale_order(self, commission_rate)
        self.commission_generated = True
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Commission Line',
            'view_mode': 'form',
            'res_model': 'commission.line',
            'res_id': commission_line.id,
            'target': 'current',
        }

    def action_view_commission_lines(self):
        """View commission lines for this sale order"""
        self.ensure_one()
        action = self.env.ref('commission_lines.action_commission_line').read()[0]
        action['domain'] = [('sale_order_id', '=', self.id)]
        action['context'] = {'default_sale_order_id': self.id}
        return action

    def action_confirm(self):
        """Override to auto-generate commission when order is confirmed"""
        result = super(SaleOrder, self).action_confirm()
        
        # Auto-generate commission if enabled in settings
        auto_generate = self.env['ir.config_parameter'].sudo().get_param(
            'commission_lines.auto_generate_commission', default=False)
        
        if auto_generate and not self.commission_generated:
            self.action_generate_commission()
        
        return result