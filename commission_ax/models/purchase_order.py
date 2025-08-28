from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    description = fields.Text(
        string="Description",
        help="Additional description for the purchase order"
    )
    origin_so_id = fields.Many2one(
        'sale.order', 
        string="Origin Sale Order",
        help="The sale order that generated this commission purchase order"
    )
    commission_posted = fields.Boolean(
        string="Commission Posted", 
        default=False,
        help="Indicates if this commission purchase order has been posted"
    )
    is_commission_po = fields.Boolean(
        string="Is Commission PO",
        compute="_compute_is_commission_po",
        store=True,
        help="Indicates if this is a commission-related purchase order"
    )
    
    # Commission-related computed fields from origin sale order
    agent1_partner_id = fields.Many2one(
        'res.partner',
        string="Agent 1",
        compute="_compute_commission_fields",
        store=True,
        help="Agent 1 from the origin sale order"
    )
    agent2_partner_id = fields.Many2one(
        'res.partner',
        string="Agent 2", 
        compute="_compute_commission_fields",
        store=True,
        help="Agent 2 from the origin sale order"
    )
    project_id = fields.Many2one(
        'project.project',
        string="Project",
        compute="_compute_commission_fields",
        store=True,
        help="Project from the origin sale order"
    )
    unit_id = fields.Many2one(
        'product.product',
        string="Unit",
        compute="_compute_commission_fields", 
        store=True,
        help="Unit from the origin sale order"
    )

    @api.depends('origin_so_id')
    def _compute_is_commission_po(self):
        for po in self:
            po.is_commission_po = bool(po.origin_so_id)
    
    @api.depends('origin_so_id')
    def _compute_commission_fields(self):
        for po in self:
            so = po.origin_so_id
            if so:
                po.agent1_partner_id = so.agent1_partner_id
                po.agent2_partner_id = so.agent2_partner_id
                po.project_id = so.project_id
                po.unit_id = so.unit_id
            else:
                po.agent1_partner_id = False
                po.agent2_partner_id = False
                po.project_id = False
                po.unit_id = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('origin_so_id'):
                sale_order = self.env['sale.order'].browse(vals['origin_so_id'])
                if sale_order.exists():
                    _logger.info(f"Creating commission PO from SO: {sale_order.name}")
        
        return super().create(vals_list)

    def action_view_origin_sale_order(self):
        self.ensure_one()
        if not self.origin_so_id:
            raise UserError("No origin sale order found for this purchase order.")
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Origin Sale Order',
            'res_model': 'sale.order',
            'res_id': self.origin_so_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.constrains('origin_so_id', 'partner_id')
    def _check_commission_partner(self):
        for po in self:
            if po.origin_so_id and po.partner_id:
                commission_partners = po.origin_so_id._get_all_commission_partners()
                if po.partner_id.id not in commission_partners:
                    raise ValidationError(
                        f"Partner '{po.partner_id.name}' is not configured as a commission "
                        f"partner in the origin sale order '{po.origin_so_id.name}'"
                    )

    def _get_commission_info(self):
        self.ensure_one()
        if not self.origin_so_id:
            return {}
        
        commission_info = {}
        sale_order = self.origin_so_id
        
        commission_mappings = {
            'consultant': sale_order.consultant_id,
            'manager': sale_order.manager_id,
            'director': sale_order.director_id,
            'second_agent': sale_order.second_agent_id,
            'broker': sale_order.broker_partner_id,
            'referrer': sale_order.referrer_partner_id,
            'cashback': sale_order.cashback_partner_id,
            'other_external': sale_order.other_external_partner_id,
            'agent1': sale_order.agent1_partner_id,
            'agent2': sale_order.agent2_partner_id,
            'manager_partner': sale_order.manager_partner_id,
            'director_partner': sale_order.director_partner_id,
        }
        
        for commission_type, partner in commission_mappings.items():
            if partner and partner.id == self.partner_id.id:
                commission_info = {
                    'type': commission_type,
                    'partner': partner,
                    'sale_order': sale_order,
                    'customer_reference': sale_order.client_order_ref,
                }
                break
        
        return commission_info

    def unlink(self):
        for po in self:
            if po.origin_so_id and po.state not in ['draft', 'cancel']:
                raise UserError(
                    f"Cannot delete confirmed commission purchase order {po.name}. "
                    f"Please cancel it first."
                )
        
        return super().unlink()