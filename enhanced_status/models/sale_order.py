from odoo import models, fields, api
from odoo.exceptions import AccessError

class SaleOrder(models.Model):
    picking_ids = fields.One2many('stock.picking', 'sale_id', string='Pickings')
    _inherit = 'sale.order'

    # Custom workflow fields
    custom_state = fields.Selection([
        ('draft', 'Draft'),
        ('documentation', 'Documentation'),
        ('calculation', 'Calculation'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
    ], string='Process Status', default='draft', tracking=True)

    stage_id = fields.Many2one(
        'sale.order.stage', 
        string='Stage', 
        tracking=True, 
        index=True,
        group_expand='_read_group_stage_ids',
        default=lambda self: self._get_default_stage()
    )

    # Financial tracking
    billing_status = fields.Selection([
        ('unraised', 'Unraised'),
        ('partially_invoiced', 'Partially Invoiced'),
        ('fully_invoiced', 'Fully Invoiced'),
    ], string='Billing Status', compute='_compute_financial_status', store=True)

    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('partially_paid', 'Partially Paid'),
        ('fully_paid', 'Fully Paid'),
    ], string='Payment Status', compute='_compute_financial_status', store=True)

    invoiced_amount = fields.Monetary(
        string='Invoiced Amount', 
        compute='_compute_financial_amounts',
        store=True
    )
    
    paid_amount = fields.Monetary(
        string='Paid Amount',
        compute='_compute_financial_amounts',
        store=True
    )
    
    balance_amount = fields.Monetary(
        string='Balance',
        compute='_compute_financial_amounts',
        store=True
    )

    reconciliation_notes = fields.Text(string='Reconciliation Notes')

    # Control fields
    is_locked = fields.Boolean(compute='_compute_is_locked')
    can_unlock = fields.Boolean(compute='_compute_can_unlock')

    @api.model
    def _get_default_stage(self):
        return self.env['sale.order.stage'].search([('stage_code', '=', 'draft')], limit=1)

    @api.depends('custom_state')
    def _compute_is_locked(self):
        for order in self:
            order.is_locked = order.custom_state == 'completed'

    def _compute_can_unlock(self):
        for order in self:
            order.can_unlock = self.env.user.has_group('sales_team.group_sale_manager')

    @api.depends('invoice_ids', 'invoice_ids.amount_total', 'invoice_ids.state', 'invoice_ids.amount_residual')
    def _compute_financial_amounts(self):
        for order in self:
            invoiced_amount = 0.0
            paid_amount = 0.0
            
            posted_invoices = order.invoice_ids.filtered(lambda inv: inv.state == 'posted')
            for invoice in posted_invoices:
                if invoice.move_type == 'out_invoice':
                    invoiced_amount += invoice.amount_total
                    paid_amount += (invoice.amount_total - invoice.amount_residual)
                elif invoice.move_type == 'out_refund':
                    invoiced_amount -= invoice.amount_total
                    paid_amount -= (invoice.amount_total - invoice.amount_residual)
            
            order.invoiced_amount = invoiced_amount
            order.paid_amount = paid_amount
            order.balance_amount = invoiced_amount - paid_amount

    @api.depends('amount_total', 'invoiced_amount', 'paid_amount')
    def _compute_financial_status(self):
        for order in self:
            # Billing Status
            if order.invoiced_amount == 0:
                order.billing_status = 'unraised'
            elif order.invoiced_amount >= order.amount_total:
                order.billing_status = 'fully_invoiced'
            else:
                order.billing_status = 'partially_invoiced'
            
            # Payment Status
            if order.paid_amount == 0:
                order.payment_status = 'unpaid'
            elif order.paid_amount >= order.invoiced_amount:
                order.payment_status = 'fully_paid'
            else:
                order.payment_status = 'partially_paid'

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['sale.order.stage'].search([])

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        if self.stage_id and self.stage_id.stage_code:
            self.custom_state = self.stage_id.stage_code

    def write(self, vals):
        # Prevent editing locked orders
        for order in self:
            if order.is_locked and not order.can_unlock:
                restricted_fields = set(vals.keys()) - {
                    'reconciliation_notes', 'stage_id', 'custom_state', 
                    'billing_status', 'payment_status', 'invoiced_amount', 
                    'paid_amount', 'balance_amount'
                }
                if restricted_fields:
                    raise AccessError("This order is completed and locked.")
        
        result = super().write(vals)
        
        # Notify followers of stage changes
        if 'custom_state' in vals or 'stage_id' in vals:
            self._notify_stage_change()
        
        # Auto-complete if criteria met
        self._check_auto_completion()
        
        return result

    def _notify_stage_change(self):
        for order in self:
            if order.message_follower_ids:
                stage_name = dict(order._fields['custom_state'].selection).get(order.custom_state, order.custom_state)
                message = f"Sale Order {order.name} moved to: {stage_name}"
                order.message_post(
                    body=message,
                    message_type='notification',
                    subtype_xmlid='mail.mt_note'
                )

    def _check_auto_completion(self):
        for order in self:
            if (order.custom_state == 'approved' and 
                order.state == 'sale' and
                order._is_order_complete()):
                order._auto_complete_order()

    def _is_order_complete(self):
        self.ensure_one()
        
        # Check financial completion
        financial_complete = (
            self.billing_status == 'fully_invoiced' and 
            self.payment_status == 'fully_paid'
        )
        
        # Check PO completion
        po_complete = self._check_po_completion()
        
        # Check delivery completion
        delivery_complete = self._check_delivery_completion()
        
        return financial_complete and po_complete and delivery_complete

    def _check_po_completion(self):
        # Find related POs
        related_pos = self.env['purchase.order'].search([
            ('origin', 'like', self.name),
            ('state', 'not in', ['cancel', 'draft'])
        ])
        
        if not related_pos:
            return True
        
        for po in related_pos:
            # Check if PO is fully processed
            po_invoices = po.invoice_ids.filtered(lambda inv: inv.state == 'posted')
            po_invoiced = sum(po_invoices.mapped('amount_total'))
            po_paid = sum(po_invoices.mapped(lambda inv: inv.amount_total - inv.amount_residual))
            
            if po_invoiced < po.amount_total or po_paid < po_invoiced:
                return False
        
        return True

    def _check_delivery_completion(self):
        if not self.picking_ids:
            return True
        return all(picking.state == 'done' for picking in self.picking_ids)

    def _auto_complete_order(self):
        completed_stage = self.env['sale.order.stage'].search([('stage_code', '=', 'completed')], limit=1)
        if completed_stage:
            self.sudo().write({
                'stage_id': completed_stage.id,
                'custom_state': 'completed'
            })

    # Workflow action methods
    def action_move_to_documentation(self):
        self.ensure_one()
        stage = self.env['sale.order.stage'].search([('stage_code', '=', 'documentation')], limit=1)
        if stage:
            self.write({'stage_id': stage.id, 'custom_state': 'documentation'})

    def action_move_to_calculation(self):
        self.ensure_one()
        stage = self.env['sale.order.stage'].search([('stage_code', '=', 'calculation')], limit=1)
        if stage:
            self.write({'stage_id': stage.id, 'custom_state': 'calculation'})

    def action_move_to_approved(self):
        self.ensure_one()
        stage = self.env['sale.order.stage'].search([('stage_code', '=', 'approved')], limit=1)
        if stage:
            self.write({'stage_id': stage.id, 'custom_state': 'approved'})

    def action_complete_order(self):
        self.ensure_one()
        stage = self.env['sale.order.stage'].search([('stage_code', '=', 'completed')], limit=1)
        if stage:
            self.write({'stage_id': stage.id, 'custom_state': 'completed'})

    def action_unlock_order(self):
        self.ensure_one()
        if not self.can_unlock:
            raise AccessError("Insufficient permissions to unlock order.")
        stage = self.env['sale.order.stage'].search([('stage_code', '=', 'approved')], limit=1)
        if stage:
            self.write({'stage_id': stage.id, 'custom_state': 'approved'})

    def action_emergency_complete(self):
        self.ensure_one()
        if not self.env.user.has_group('sales_team.group_sale_manager'):
            raise AccessError("Only administrators can emergency complete orders.")
        
        stage = self.env['sale.order.stage'].search([('stage_code', '=', 'completed')], limit=1)
        if stage:
            self.write({'stage_id': stage.id, 'custom_state': 'completed'})
            self.message_post(
                body=f"EMERGENCY COMPLETION by {self.env.user.name}",
                message_type='notification'
            )

    def action_emergency_reset(self):
        self.ensure_one()
        if not self.env.user.has_group('sales_team.group_sale_manager'):
            raise AccessError("Only administrators can emergency reset orders.")
        
        stage = self.env['sale.order.stage'].search([('stage_code', '=', 'approved')], limit=1)
        if stage:
            self.write({'stage_id': stage.id, 'custom_state': 'approved'})
            self.message_post(
                body=f"EMERGENCY RESET by {self.env.user.name}",
                message_type='notification'
            )

    @api.model
    def _cron_update_financial_status(self):
        orders = self.search([('state', 'not in', ['draft', 'cancel'])])
        orders._compute_financial_amounts()
        orders._compute_financial_status()
