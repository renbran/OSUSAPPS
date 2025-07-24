# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class OrderStatusChangeWizard(models.TransientModel):
    _name = 'order.status.change.wizard'
    _description = 'Change Order Status Wizard'
    
    order_id = fields.Many2one('sale.order', string='Sale Order', required=True)
    current_status_id = fields.Many2one('order.status', string='Current Status', readonly=True)
    new_status_id = fields.Many2one('order.status', string='New Status', required=True)
    notes = fields.Text(string='Notes')
    
    @api.onchange('current_status_id')
    def _onchange_current_status(self):
        if self.current_status_id:
            return {'domain': {'new_status_id': [('id', 'in', self.current_status_id.next_status_ids.ids)]}}
        return {'domain': {'new_status_id': []}}
    
    def change_status(self):
        self.ensure_one()
        # Validate transition is allowed
        if (self.current_status_id.next_status_ids and 
            self.new_status_id.id not in self.current_status_id.next_status_ids.ids):
            raise UserError(_("The selected status transition is not allowed. Please choose a valid next status."))
        
        # Apply the new status
        self.order_id._change_status(self.new_status_id.id, self.notes)
        
        return {'type': 'ir.actions.act_window_close'}