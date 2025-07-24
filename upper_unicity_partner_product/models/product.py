from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        """Convert specified fields to uppercase on creation."""
        fields_to_capitalize = ['x_project', 'x_unit']  # Add custom fields here
        for field in fields_to_capitalize:
            if field in vals and vals[field]:
                # Convert the name field of the related Many2one record to uppercase
                if field == 'x_project':
                    related_record = self.env['account.analytic.account'].browse(vals[field])
                elif field == 'x_unit':
                    related_record = self.env['product.category'].browse(vals[field])
                if related_record.name:
                    related_record.name = related_record.name.upper()  # Update related name to uppercase
        return super(SaleOrder, self).create(vals)

    def write(self, vals):
        """Convert specified fields to uppercase on update."""
        fields_to_capitalize = ['x_project', 'x_unit']  # Add custom fields here
        for field in fields_to_capitalize:
            if field in vals and vals[field]:
                if field == 'x_project':
                    related_record = self.env['account.analytic.account'].browse(vals[field])
                elif field == 'x_unit':
                    related_record = self.env['product.category'].browse(vals[field])
                if related_record.name:
                    related_record.name = related_record.name.upper()  # Update related name to uppercase
        return super(SaleOrder, self).write(vals)

    @api.onchange('x_project', 'x_unit')
    def _onchange_capitalize_fields(self):
        """Convert specified fields to uppercase during form changes."""
        fields_to_capitalize = ['x_project', 'x_unit']  # Add custom fields here
        for field in fields_to_capitalize:
            related_record = getattr(self, field, False)
            if related_record and related_record.name:
                related_record.name = related_record.name.upper()  # Apply uppercase conversion
