from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class OsusMainModel(models.Model):
    _name = 'osus.main.model'
    _description = 'Main Model for OSUS Enterprise'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char(string='Name', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done')
    ], default='draft', tracking=True)

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if not record.name or len(record.name) < 3:
                raise ValidationError(_("Name must be at least 3 characters long"))

    def action_confirm(self):
        self.ensure_one()
        self.state = 'confirmed'
        self.message_post(body=_("Record confirmed"))
