from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    """Simplified Sale Order with commission management"""
    _inherit = ['sale.order', 'commission.assignment.mixin']

    # Direct commission lines relationship
    commission_line_ids = fields.One2many(
        'commission.line',
        'sale_order_id',
        string='Commission Lines',
        copy=False,
        help="Commission lines for this sale order"
    )

    # Commission totals
    total_commission_amount = fields.Monetary(
        string='Total Commission Amount',
        compute='_compute_commission_totals',
        store=True,
        currency_field='currency_id',
        help="Total commission amount from all commission lines"
    )

    commission_lines_count = fields.Integer(
        string='Commission Lines Count',
        compute='_compute_commission_totals',
        help="Number of commission lines for this order"
    )

    # Commission status
    commission_status = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
    ], string='Commission Status', default='draft', copy=False, tracking=True)

    @api.depends('commission_line_ids.commission_amount')
    def _compute_commission_totals(self):
        """Compute commission totals"""
        for order in self:
            order.commission_lines_count = len(order.commission_line_ids)
            order.total_commission_amount = sum(order.commission_line_ids.mapped('commission_amount'))

    def action_calculate_commissions(self):
        """Calculate commission lines for this order"""
        self.ensure_one()
        if not self.commission_line_ids:
            raise UserError("No commission lines configured for this order.")

        for line in self.commission_line_ids:
            line._compute_amounts()

        self.commission_status = 'calculated'
        return True

    def action_confirm_commissions(self):
        """Confirm commission calculations"""
        self.ensure_one()
        if self.commission_status != 'calculated':
            raise UserError("Please calculate commissions first.")

        self.commission_line_ids.write({'state': 'confirmed'})
        self.commission_status = 'confirmed'
        return True

    def action_create_commission_purchase_orders(self):
        """Create purchase orders for commissions"""
        self.ensure_one()
        purchase_orders = []

        for line in self.commission_line_ids.filtered(lambda l: l.state == 'confirmed'):
            po_vals = self._prepare_purchase_order_vals(line)
            po = self.env['purchase.order'].create(po_vals)
            line.purchase_order_id = po.id
            line.state = 'processed'
            purchase_orders.append(po)

        if purchase_orders:
            self.commission_status = 'paid'

        return purchase_orders

    def _prepare_purchase_order_vals(self, commission_line):
        """Prepare purchase order values for commission"""
        product = self.env.ref('commission_ax.commission_service_product', raise_if_not_found=False)
        if not product:
            raise UserError("Commission service product not found. Please configure it first.")

        return {
            'partner_id': commission_line.partner_id.id,
            'partner_ref': self.client_order_ref or '',
            'origin_so_id': self.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'name': f"Commission: {self.name} - {commission_line.commission_type_id.name}",
                'product_qty': 1,
                'price_unit': commission_line.commission_amount,
                'date_planned': fields.Datetime.now(),
            })],
        }

    def action_view_commission_purchase_orders(self):
        """View commission purchase orders"""
        self.ensure_one()
        po_ids = self.commission_line_ids.mapped('purchase_order_id').ids

        if not po_ids:
            raise UserError("No commission purchase orders found.")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Commission Purchase Orders',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', po_ids)],
            'context': {'create': False},
        }