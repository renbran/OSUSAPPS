from odoo import models, fields, api

class SaleOrderStage(models.Model):
    _name = 'sale.order.stage'
    _description = 'Sale Order Stages'
    _order = 'sequence, name'

    name = fields.Char('Stage Name', required=True)
    sequence = fields.Integer('Sequence', default=10)
    description = fields.Text('Description')
    responsible_user_id = fields.Many2one('res.users', string='Responsible User')
    responsible_group_id = fields.Many2one('res.groups', string='Responsible Group')
    fold = fields.Boolean('Folded in Kanban')
    
    @api.model
    def _get_default_stages(self):
        """Return default stages for sale orders"""
        return [
            {'name': 'Draft', 'sequence': 1},
            {'name': 'Documentation', 'sequence': 2},
            {'name': 'Calculation', 'sequence': 3},
            {'name': 'Approved', 'sequence': 4},
            {'name': 'Completed', 'sequence': 5},
        ]

# models/sale_order.py
from odoo import models, fields, api
from odoo.exceptions import AccessError, ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Override the default state field behavior
    state = fields.Selection([
        ('draft', 'Draft'),
        ('documentation', 'Documentation'),
        ('calculation', 'Calculation'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True,
       tracking=True, default='draft')

    # Stage management
    stage_id = fields.Many2one('sale.order.stage', string='Stage', 
                               tracking=True, index=True,
                               group_expand='_read_group_stage_ids')
    
    # Responsible persons
    stage_responsible_user_id = fields.Many2one('res.users', 
                                                string='Stage Responsible User',
                                                related='stage_id.responsible_user_id',
                                                readonly=True)
    stage_responsible_group_id = fields.Many2one('res.groups', 
                                                 string='Stage Responsible Group',
                                                 related='stage_id.responsible_group_id',
                                                 readonly=True)

    # Billing and Payment Status
    billing_status = fields.Selection([
        ('unraised', 'Unraised'),
        ('partially_invoiced', 'Partially Invoiced'),
        ('fully_invoiced', 'Fully Invoiced'),
    ], string='Billing Status', default='unraised', tracking=True)

    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('partially_paid', 'Partially Paid'),
        ('fully_paid', 'Fully Paid'),
    ], string='Payment Status', default='unpaid', tracking=True)

    invoiced_amount = fields.Monetary(string='Invoiced Amount', 
                                      compute='_compute_invoiced_amount',
                                      store=True)

    # Reconciliation field
    reconciliation_notes = fields.Text(string='Reconciliation Notes')

    # Computed fields for workflow control
    is_locked = fields.Boolean(compute='_compute_is_locked', store=True)
    can_unlock = fields.Boolean(compute='_compute_can_unlock')

    @api.depends('state')
    def _compute_is_locked(self):
        """Compute if order is locked (completed state)"""
        for order in self:
            order.is_locked = order.state == 'completed'

    @api.depends('is_locked')
    def _compute_can_unlock(self):
        """Check if current user can unlock completed orders"""
        for order in self:
            order.can_unlock = self.env.user.has_group('sale_enhanced_status.group_sale_order_unlock')

    @api.depends('invoice_ids', 'invoice_ids.amount_total', 'invoice_ids.state')
    def _compute_invoiced_amount(self):
        """Compute total invoiced amount"""
        for order in self:
            invoiced_amount = 0.0
            for invoice in order.invoice_ids.filtered(lambda inv: inv.state == 'posted'):
                if invoice.move_type == 'out_invoice':
                    invoiced_amount += invoice.amount_total
                elif invoice.move_type == 'out_refund':
                    invoiced_amount -= invoice.amount_total
            order.invoiced_amount = invoiced_amount

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """Return all stages for kanban view"""
        stage_ids = self.env['sale.order.stage'].search([])
        return stage_ids

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        """Update state when stage changes"""
        if self.stage_id:
            stage_mapping = {
                'Draft': 'draft',
                'Documentation': 'documentation',
                'Calculation': 'calculation',
                'Approved': 'approved',
                'Completed': 'completed',
            }
            self.state = stage_mapping.get(self.stage_id.name, 'draft')

    def write(self, vals):
        """Override write to prevent editing locked orders"""
        # Fields that can always be updated
        allowed_fields = {'reconciliation_notes', 'stage_id', 'state', 'billing_status', 
                         'payment_status', 'invoiced_amount'}
        
        for order in self:
            if order.is_locked and not order.can_unlock:
                # Check if trying to update restricted fields
                restricted_fields = set(vals.keys()) - allowed_fields
                if restricted_fields:
                    raise AccessError(
                        "This sale order is completed and locked. "
                        "Only administrators can modify completed orders."
                    )
        
        return super(SaleOrder, self).write(vals)

    def action_confirm(self):
        """Override confirm to set appropriate stage"""
        result = super(SaleOrder, self).action_confirm()
        # Move to approved stage when confirmed
        approved_stage = self.env['sale.order.stage'].search([('name', '=', 'Approved')], limit=1)
        if approved_stage:
            self.stage_id = approved_stage
            self.state = 'approved'
        return result

    def action_complete_order(self):
        """Mark order as completed"""
        self.ensure_one()
        completed_stage = self.env['sale.order.stage'].search([('name', '=', 'Completed')], limit=1)
        if completed_stage:
            self.stage_id = completed_stage
            self.state = 'completed'

    def action_unlock_order(self):
        """Unlock completed order (admin only)"""
        self.ensure_one()
        if not self.can_unlock:
            raise AccessError("You don't have permission to unlock completed orders.")
        # Move back to approved stage
        approved_stage = self.env['sale.order.stage'].search([('name', '=', 'Approved')], limit=1)
        if approved_stage:
            self.stage_id = approved_stage
            self.state = 'approved'

    @api.model
    def _update_billing_payment_status(self):
        """Cron job to update billing and payment status"""
        orders = self.search([('state', 'not in', ['draft', 'cancel'])])
        for order in orders:
            # Update billing status
            total_amount = order.amount_total
            invoiced_amount = order.invoiced_amount
            
            if invoiced_amount == 0:
                billing_status = 'unraised'
            elif invoiced_amount >= total_amount:
                billing_status = 'fully_invoiced'
            else:
                billing_status = 'partially_invoiced'
            
            # Update payment status based on invoice payments
            paid_amount = sum(order.invoice_ids.filtered(
                lambda inv: inv.state == 'posted'
            ).mapped('amount_residual_signed'))
            
            if paid_amount == 0 and invoiced_amount > 0:
                payment_status = 'fully_paid'
            elif paid_amount < invoiced_amount and paid_amount > 0:
                payment_status = 'partially_paid'
            else:
                payment_status = 'unpaid'

            order.write({
                'billing_status': billing_status,
                'payment_status': payment_status,
            })