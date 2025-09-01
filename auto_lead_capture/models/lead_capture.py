from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging


class AutoLeadCapture(models.Model):
    _name = 'auto.lead.capture'
    _description = 'Auto Lead Capture'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Lead Name', required=True, tracking=True)
    source = fields.Selection([
        ('web', 'Web Form'),
        ('email', 'Email'),
        ('integration', 'Integration'),
    ], string='Source', default='web', tracking=True)
    assigned_user_id = fields.Many2one('res.users', string='Assigned User', tracking=True)
    state = fields.Selection([
        ('new', 'New'),
        ('assigned', 'Assigned'),
        ('converted', 'Converted'),
        ('lost', 'Lost'),
    ], default='new', tracking=True)

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if not record.name or len(record.name) < 3:
                raise ValidationError(_("Lead name must be at least 3 characters long"))

    def action_assign(self):
        self.ensure_one()
        self.state = 'assigned'
        self.message_post(body=_("Lead assigned"))
