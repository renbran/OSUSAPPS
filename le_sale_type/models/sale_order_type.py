from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SaleOrderType(models.Model):
    _name = 'sale.order.type'
    _description = 'Sale Order Type'
    _order = 'sequence, name'

    name = fields.Char(required=True, string="Sale Type")
    description = fields.Text(string="Description")
    sequence_id = fields.Many2one('ir.sequence', string="Sequence", required=True)
    active = fields.Boolean(string="Active", default=True)
    prefix = fields.Char("Prefix")
    sequence = fields.Integer("Sequence", default=10, help="Used to order sale types")
    color = fields.Integer("Color", default=0, help="Color for kanban view")
    
    # Statistics fields
    order_count = fields.Integer("Orders Count", compute='_compute_order_count')
    total_amount = fields.Float("Total Amount", compute='_compute_total_amount')

    @api.depends('name')
    def _compute_order_count(self):
        """Compute the number of orders for this sale type"""
        for record in self:
            record.order_count = self.env['sale.order'].search_count([
                ('sale_order_type_id', '=', record.id)
            ])

    @api.depends('name')
    def _compute_total_amount(self):
        """Compute the total amount of orders for this sale type"""
        for record in self:
            orders = self.env['sale.order'].search([
                ('sale_order_type_id', '=', record.id),
                ('state', '!=', 'cancel')
            ])
            record.total_amount = sum(orders.mapped('amount_total'))

    @api.model
    def create(self, vals):
        # Ensure the sequence prefix is updated when creating the sale order type
        if 'sequence_id' in vals and 'prefix' in vals:
            sequence = self.env['ir.sequence'].browse(vals['sequence_id'])
            if sequence:
                sequence.prefix = vals['prefix']
        
        result = super(SaleOrderType, self).create(vals)
        
        # Trigger update for dynamic filters (could be implemented via websocket in the future)
        self._trigger_filter_update()
        
        return result

    def write(self, vals):
        # Ensure the sequence prefix is updated when editing the sale order type
        for rec in self:
            if 'prefix' in vals:
                rec.sequence_id.prefix = vals.get('prefix', rec.prefix)
        
        result = super(SaleOrderType, self).write(vals)
        
        # Trigger update for dynamic filters
        self._trigger_filter_update()
        
        return result

    def _trigger_filter_update(self):
        """
        Method to trigger update of dynamic filters.
        This could be enhanced with websocket notifications in the future.
        """
        # For now, we'll just invalidate the cache
        self.env.invalidate_all()

    def action_view_orders(self):
        """Action to view orders of this type"""
        return {
            'name': f'{self.name} Orders',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('sale_order_type_id', '=', self.id)],
            'context': {
                'default_sale_order_type_id': self.id,
                'search_default_sale_order_type_id': self.id,
            }
        }

    @api.constrains('sequence_id')
    def _check_unique_sequence(self):
        for record in self:
            # Check if the sequence is already used by another sale order type
            existing_type = self.search([('sequence_id', '=', record.sequence_id.id), ('id', '!=', record.id)], limit=1)
            if existing_type:
                raise ValidationError(
                    "The sequence is already used by another Sale Order Type: %s." % existing_type.name)

    def unlink(self):
        # Check if the sale order type is used in any sale orders before deletion
        sale_order_obj = self.env['sale.order']
        for record in self:
            # Search for sale orders that reference this sale order type
            sale_orders = sale_order_obj.search([('sale_order_type_id', '=', record.id)])
            if sale_orders:
                raise ValidationError(
                    "You cannot delete the Sale Order Type '%s' because it is used in existing Sale Orders." % record.name
                )
        
        # Trigger filter update before deletion
        self._trigger_filter_update()
        
        # Proceed with deletion if no related sale orders found
        return super(SaleOrderType, self).unlink()

    @api.model
    def get_active_types_for_filters(self):
        """
        Returns active sale order types formatted for dynamic filters
        """
        types = self.search([('active', '=', True)], order='sequence, name')
        return [{
            'id': type_rec.id,
            'name': type_rec.name,
            'description': type_rec.description,
            'order_count': type_rec.order_count,
            'color': type_rec.color,
        } for type_rec in types]
