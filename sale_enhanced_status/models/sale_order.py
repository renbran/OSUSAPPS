from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('documentation', 'Documentation'),
        ('calculation', 'Calculation'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
    ], string='Status', default='draft', tracking=True)

    def action_set_documentation(self):
        self.write({'state': 'documentation'})

    def action_set_calculation(self):
        self.write({'state': 'calculation'})

    def action_set_approved(self):
        self.write({'state': 'approved'})

    def action_set_completed(self):
        self.write({'state': 'completed'})
