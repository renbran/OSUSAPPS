# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    """Extend Sale Order to integrate with commission_lines"""
    _inherit = 'sale.order'

    # Commission Lines Integration
    commission_line_ids = fields.One2many(
        'commission.line', 
        'sale_order_id', 
        string='Commission Lines',
        help='Commission lines generated for this sale order'
    )
    
    commission_line_count = fields.Integer(
        string='Commission Lines Count',
        compute='_compute_commission_line_count',
        help='Number of commission lines for this order'
    )
    
    has_commission_lines = fields.Boolean(
        string='Has Commission Lines',
        compute='_compute_commission_line_count',
        help='Whether this order has commission lines'
    )

    # ============================================================================
    # COMPUTE METHODS
    # ============================================================================
    
    @api.depends('commission_line_ids')
    def _compute_commission_line_count(self):
        """Compute commission line count"""
        for order in self:
            order.commission_line_count = len(order.commission_line_ids)
            order.has_commission_lines = bool(order.commission_line_ids)

    # ============================================================================
    # ACTION METHODS
    # ============================================================================
    
    def action_view_commission_lines(self):
        """View commission lines for this sale order"""
        self.ensure_one()
        action = self.env.ref('commission_lines.action_commission_line').read()[0]
        action['domain'] = [('sale_order_id', '=', self.id)]
        action['context'] = {
            'default_sale_order_id': self.id,
            'create': False,  # Don't allow manual creation
        }
        return action
    
    def action_generate_commission_lines(self):
        """Generate commission lines from commission_ax data"""
        self.ensure_one()
        
        # Check if order is invoiced
        if not self.is_fully_invoiced:
            raise UserError(_("Sale order must be fully invoiced before generating commission lines."))
        
        # Check if commission lines already exist
        if self.commission_line_ids:
            existing_count = len(self.commission_line_ids)
            raise UserError(_("Commission lines already exist for this order (%d lines). Delete existing lines first if you need to regenerate.") % existing_count)
        
        # Generate commission lines
        commission_lines = self.env['commission.line'].create_from_sale_order(self)
        
        if commission_lines:
            message = _("Generated %d commission lines successfully.") % len(commission_lines)
            self.message_post(body=message)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': message,
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Commission Lines'),
                    'message': _('No commission partners or amounts found for this order.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }

    # ============================================================================
    # OVERRIDE METHODS
    # ============================================================================
    
    def _create_commission_purchase_orders(self):
        """Override to also update commission line status when PO is created"""
        result = super(SaleOrder, self)._create_commission_purchase_orders()
        
        # Update commission line status to billed when PO is created
        for commission_line in self.commission_line_ids:
            if commission_line.state == 'approved':
                # Find matching PO for this commission line
                matching_po = self.purchase_order_ids.filtered(
                    lambda po: po.partner_id == commission_line.partner_id
                )
                if matching_po:
                    commission_line.purchase_order_id = matching_po[0]
                    commission_line.action_bill()
        
        return result

    # ============================================================================
    # AUTOMATION METHODS
    # ============================================================================
    
    def _action_confirm(self):
        """Override to auto-generate commission lines when order is confirmed and invoiced"""
        result = super(SaleOrder, self)._action_confirm()
        
        # Check if we should auto-generate commission lines
        auto_generate = self.env['ir.config_parameter'].sudo().get_param(
            'commission_lines.auto_generate_on_invoice', 
            default=False
        )
        
        if auto_generate:
            # We'll generate lines when the order gets invoiced, not when confirmed
            pass
            
        return result
    
    def _auto_generate_commission_lines_on_invoice(self):
        """Auto-generate commission lines when order is fully invoiced"""
        if self.is_fully_invoiced and not self.commission_line_ids:
            try:
                commission_lines = self.env['commission.line'].create_from_sale_order(self)
                if commission_lines:
                    self.message_post(
                        body=_("Auto-generated %d commission lines upon full invoicing.") % len(commission_lines)
                    )
            except Exception as e:
                _logger.warning("Failed to auto-generate commission lines for SO %s: %s", self.name, str(e))

    # Hook into invoice posting to trigger auto-generation
    def _create_invoices(self, grouped=False, final=False):
        """Override to check for auto-generation after invoice creation"""
        invoices = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final)
        
        # Check if auto-generation is enabled
        auto_generate = self.env['ir.config_parameter'].sudo().get_param(
            'commission_lines.auto_generate_on_invoice', 
            default=False
        )
        
        if auto_generate:
            for order in self:
                if order.is_fully_invoiced:
                    order._auto_generate_commission_lines_on_invoice()
        
        return invoices