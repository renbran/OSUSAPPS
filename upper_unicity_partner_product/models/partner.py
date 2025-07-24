from odoo import models, fields, api, exceptions


class UniquePartner(models.Model):
    _inherit = 'res.partner'

    _sql_constraints = [
        ('res_partner_name_uniqu', 'unique(name)', 'Name of partner already exists!')
    ]

    @api.model
    def create(self, vals):
        """Ensure partner names are uppercase on creation."""
        if 'name' in vals and vals['name']:
            vals['name'] = vals['name'].upper()
        return super(UniquePartner, self).create(vals)

    def write(self, vals):
        """Ensure partner names are uppercase on update."""
        if 'name' in vals and vals['name']:
            vals['name'] = vals['name'].upper()
        return super(UniquePartner, self).write(vals)

    @api.onchange('name')
    def _onchange_name(self):
        """Convert the partner name to uppercase during form changes."""
        if self.name:
            self.name = self.name.upper()
