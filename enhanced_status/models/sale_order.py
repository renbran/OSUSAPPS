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
                               group_expand='_read_group_stage_ids',
                               default=lambda self: self._get_default_stage())
    
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
    ], string='Billing Status', default='unraised', tracking=True,
       compute='_compute_billing_payment_status', store=True)

    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('partially_paid', 'Partially Paid'),
        ('fully_paid', 'Fully Paid'),
    ], string='Payment Status', default='unpaid', tracking=True,
       compute='_compute_billing_payment_status', store=True)

    # Financial tracking fields
    invoiced_amount = fields.Monetary(string='Invoiced Amount', 
                                      compute='_compute_financial_amounts',
                                      store=True)
    
    paid_amount = fields.Monetary(string='Paid Amount',
                                  compute='_compute_financial_amounts',
                                  store=True)
    
    balance_amount = fields.Monetary(string='Balance',
                                     compute='_compute_financial_amounts',
                                     store=True)

    # Reconciliation field
    reconciliation_notes = fields.Text(string='Reconciliation Notes')

    # Computed fields for workflow control
    is_locked = fields.Boolean(compute='_compute_is_locked', store=True)
    can_unlock = fields.Boolean(compute='_compute_can_unlock')
    
    # Button visibility fields
    show_confirm_button = fields.Boolean(compute='_compute_button_visibility')
    show_documentation_button = fields.Boolean(compute='_compute_button_visibility')
    show_calculation_button = fields.Boolean(compute='_compute_button_visibility')
    show_approve_button = fields.Boolean(compute='_compute_button_visibility')
    show_complete_button = fields.Boolean(compute='_compute_button_visibility')
    show_unlock_button = fields.Boolean(compute='_compute_button_visibility')

    @api.model
    def _get_default_stage(self):
        """Get default draft stage"""
        return self.env['sale.order.stage'].search([('stage_code', '=', 'draft')], limit=1)

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

    @api.depends('state', 'is_locked', 'can_unlock')
    def _compute_button_visibility(self):
        """Compute button visibility based on current state"""
        for order in self:
            order.show_confirm_button = order.state == 'draft'
            order.show_documentation_button = order.state == 'draft'
            order.show_calculation_button = order.state == 'documentation'
            order.show_approve_button = order.state == 'calculation'
            order.show_complete_button = order.state == 'approved'
            order.show_unlock_button = order.is_locked and order.can_unlock

    @api.depends('invoice_ids', 'invoice_ids.amount_total', 'invoice_ids.state',
                 'invoice_ids.payment_state', 'invoice_ids.amount_residual')
    def _compute_financial_amounts(self):
        """Compute invoiced amount, paid amount, and balance"""
        for order in self:
            invoiced_amount = 0.0
            paid_amount = 0.0
            
            for invoice in order.invoice_ids.filtered(lambda inv: inv.state == 'posted'):
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
    def _compute_billing_payment_status(self):
        """Compute billing and payment status"""
        for order in self:
            total_amount = order.amount_total
            invoiced_amount = order.invoiced_amount
            paid_amount = order.paid_amount
            
            # Billing Status
            if invoiced_amount == 0:
                order.billing_status = 'unraised'
            elif invoiced_amount >= total_amount:
                order.billing_status = 'fully_invoiced'
            else:
                order.billing_status = 'partially_invoiced'
            
            # Payment Status
            if paid_amount == 0:
                order.payment_status = 'unpaid'
            elif paid_amount >= invoiced_amount:
                order.payment_status = 'fully_paid'
            else:
                order.payment_status = 'partially_paid'

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """Return all stages for kanban view"""
        stage_ids = self.env['sale.order.stage'].search([])
        return stage_ids

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        """Update state when stage changes"""
        if self.stage_id and self.stage_id.stage_code:
            self.state = self.stage_id.stage_code

    def write(self, vals):
        """Override write to prevent editing locked orders"""
        # Fields that can always be updated
        allowed_fields = {'reconciliation_notes', 'stage_id', 'state', 'billing_status', 
                         'payment_status', 'invoiced_amount', 'paid_amount', 'balance_amount'}
        
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

    def action_move_to_documentation(self):
        """Move to documentation stage"""
        self.ensure_one()
        documentation_stage = self.env['sale.order.stage'].search([('stage_code', '=', 'documentation')], limit=1)
        if documentation_stage:
            self.stage_id = documentation_stage
            self.state = 'documentation'

    def action_move_to_calculation(self):
        """Move to calculation stage"""
        self.ensure_one()
        calculation_stage = self.env['sale.order.stage'].search([('stage_code', '=', 'calculation')], limit=1)
        if calculation_stage:
            self.stage_id = calculation_stage
            self.state = 'calculation'

    def action_move_to_approved(self):
        """Move to approved stage"""
        self.ensure_one()
        approved_stage = self.env['sale.order.stage'].search([('stage_code', '=', 'approved')], limit=1)
        if approved_stage:
            self.stage_id = approved_stage
            self.state = 'approved'

    def action_confirm(self):
        """Override confirm to set appropriate stage"""
        result = super(SaleOrder, self).action_confirm()
        # Move to approved stage when confirmed
        approved_stage = self.env['sale.order.stage'].search([('stage_code', '=', 'approved')], limit=1)
        if approved_stage:
            self.stage_id = approved_stage
            self.state = 'approved'
        return result

    def action_complete_order(self):
        """Mark order as completed"""
        self.ensure_one()
        completed_stage = self.env['sale.order.stage'].search([('stage_code', '=', 'completed')], limit=1)
        if completed_stage:
            self.stage_id = completed_stage
            self.state = 'completed'

    def action_unlock_order(self):
        """Unlock completed order (admin only)"""
        self.ensure_one()
        if not self.can_unlock:
            raise AccessError("You don't have permission to unlock completed orders.")
        # Move back to approved stage
        approved_stage = self.env['sale.order.stage'].search([('stage_code', '=', 'approved')], limit=1)
        if approved_stage:
            self.stage_id = approved_stage
            self.state = 'approved'

    @api.model
    def _cron_update_billing_payment_status(self):
        """Cron job to update billing and payment status"""
        orders = self.search([('state', 'not in', ['draft', 'cancel'])])
        orders._compute_financial_amounts()
        orders._compute_billing_payment_status()
