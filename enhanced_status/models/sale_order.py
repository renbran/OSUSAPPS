# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # Custom state field for workflow tracking
    custom_state = fields.Selection([
        ('draft', 'Draft'),
        ('documentation', 'Documentation'),
        ('calculation', 'Calculation'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
    ], string='Custom State', 
       default='draft', 
       tracking=True,
       help="Custom workflow state for enhanced order tracking"
    )

    # Enhanced workflow fields
    stage_id = fields.Many2one(
        'sale.order.stage', 
        string='Workflow Stage', 
        tracking=True, 
        index=True,
        group_expand='_read_group_stage_ids',
        help="Current stage in the custom workflow"
    )

    # Financial tracking with enhanced computation
    billing_status = fields.Selection([
        ('unraised', 'Unraised'),
        ('partially_invoiced', 'Partially Invoiced'),
        ('fully_invoiced', 'Fully Invoiced'),
    ], string='Billing Status', compute='_compute_financial_status', store=True, tracking=True)

    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('partially_paid', 'Partially Paid'),
        ('fully_paid', 'Fully Paid'),
    ], string='Payment Status', compute='_compute_financial_status', store=True, tracking=True)

    invoiced_amount = fields.Monetary(
        string='Invoiced Amount', 
        compute='_compute_financial_amounts',
        store=True,
        help="Total amount invoiced for this order"
    )
    
    paid_amount = fields.Monetary(
        string='Paid Amount',
        compute='_compute_financial_amounts',
        store=True,
        help="Total amount paid for invoices related to this order"
    )
    
    balance_amount = fields.Monetary(
        string='Outstanding Balance',
        compute='_compute_financial_amounts',
        store=True,
        help="Remaining amount to be paid"
    )

    # Workflow control fields
    is_locked = fields.Boolean(
        string='Is Locked',
        compute='_compute_is_locked',
        help="True if order is in completed state and locked for editing"
    )
    
    can_unlock = fields.Boolean(
        string='Can Unlock',
        compute='_compute_can_unlock',
        help="True if current user can unlock completed orders"
    )

    # Business logic fields
    reconciliation_notes = fields.Text(
        string='Reconciliation Notes',
        help="Notes regarding financial reconciliation and completion"
    )
    
    workflow_notes = fields.Text(
        string='Workflow Notes',
        help="Internal notes about workflow progression and decisions"
    )
    
    completion_criteria_met = fields.Boolean(
        string='Auto-Completion Criteria Met',
        compute='_compute_completion_criteria',
        store=True,
        help="True when all criteria for automatic completion are satisfied"
    )

    @api.depends('state')
    def _compute_is_locked(self):
        """Compute if order is locked for editing"""
        for order in self:
            order.is_locked = order.state == 'completed'

    def _compute_can_unlock(self):
        """Compute if current user can unlock orders"""
        can_unlock = self.env.user.has_group('sales_team.group_sale_manager')
        for order in self:
            order.can_unlock = can_unlock

    @api.depends('invoice_ids', 'invoice_ids.amount_total', 'invoice_ids.state', 'invoice_ids.amount_residual')
    def _compute_financial_amounts(self):
        """Enhanced financial computation with better error handling"""
        for order in self:
            invoiced_amount = 0.0
            paid_amount = 0.0
            
            try:
                # Get all posted invoices (customer invoices and refunds)
                posted_invoices = order.invoice_ids.filtered(
                    lambda inv: inv.state == 'posted' and inv.move_type in ('out_invoice', 'out_refund')
                )
                
                for invoice in posted_invoices:
                    if invoice.move_type == 'out_invoice':
                        invoiced_amount += invoice.amount_total
                        paid_amount += (invoice.amount_total - invoice.amount_residual)
                    elif invoice.move_type == 'out_refund':
                        invoiced_amount -= invoice.amount_total
                        paid_amount -= (invoice.amount_total - invoice.amount_residual)
                
            except Exception as e:
                # Log error but don't break the computation
                import logging
                _logger = logging.getLogger(__name__)
                _logger.warning(f"Error computing financial amounts for SO {order.name}: {str(e)}")
            
            order.invoiced_amount = invoiced_amount
            order.paid_amount = paid_amount
            order.balance_amount = invoiced_amount - paid_amount

    @api.depends('amount_total', 'invoiced_amount', 'paid_amount')
    def _compute_financial_status(self):
        """Compute billing and payment status with tolerance for rounding"""
        for order in self:
            # Billing Status (with small tolerance for rounding)
            tolerance = 0.01
            
            if order.invoiced_amount <= tolerance:
                order.billing_status = 'unraised'
            elif order.invoiced_amount >= (order.amount_total - tolerance):
                order.billing_status = 'fully_invoiced'
            else:
                order.billing_status = 'partially_invoiced'
            
            # Payment Status
            if order.paid_amount <= tolerance:
                order.payment_status = 'unpaid'
            elif order.paid_amount >= (order.invoiced_amount - tolerance):
                order.payment_status = 'fully_paid'
            else:
                order.payment_status = 'partially_paid'

    @api.depends('billing_status', 'payment_status')
    def _compute_completion_criteria(self):
        """Check if order meets criteria for automatic completion"""
        for order in self:
            financial_complete = (
                order.billing_status == 'fully_invoiced' and 
                order.payment_status == 'fully_paid'
            )
            
            delivery_complete = order._check_delivery_completion()
            
            order.completion_criteria_met = financial_complete and delivery_complete

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """Return all stages for kanban group_by"""
        return self.env['sale.order.stage'].search([])

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        """Synchronize stage with custom_state"""
        if self.stage_id and self.stage_id.stage_code:
            self.custom_state = self.stage_id.stage_code

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to ensure custom_state is properly set"""
        records = super().create(vals_list)
        for record in records:
            if not record.custom_state:
                if record.stage_id and record.stage_id.stage_code:
                    record.custom_state = record.stage_id.stage_code
                else:
                    record.custom_state = 'draft'
        return records

    def write(self, vals):
        """Override write with safe custom_state handling"""
        result = super().write(vals)
        
        # Ensure custom_state is set for all records
        for order in self:
            if not order.custom_state:
                order.custom_state = 'draft'
        
        # Auto-complete if criteria met
        self._check_auto_completion()
        
        return result

    def _check_auto_completion(self):
        """Check if order should be auto-completed"""
        for order in self:
            # Safely check custom_state with fallback
            custom_state = getattr(order, 'custom_state', 'draft') or 'draft'
            if (custom_state == 'approved' and 
                order.state == 'sale' and
                order._is_order_complete()):
                order._auto_complete_order()

    def _is_order_complete(self):
        """Check if order is complete"""
        self.ensure_one()
        
        # Check financial completion
        financial_complete = (
            self.billing_status == 'fully_invoiced' and 
            self.payment_status == 'fully_paid'
        )
        
        # Check delivery completion
        delivery_complete = self._check_delivery_completion()
        
        return financial_complete and delivery_complete

    def _check_delivery_completion(self):
        """Check if all deliveries are completed"""
        self.ensure_one()
        # Safely check for picking_ids field (may not be available during module loading)
        if not hasattr(self, 'picking_ids'):
            return True
        if not self.picking_ids:
            return True
        return all(picking.state == 'done' for picking in self.picking_ids)

    def _auto_complete_order(self):
        """Automatically complete order"""
        completed_stage = self.env['sale.order.stage'].search([('stage_code', '=', 'completed')], limit=1)
        if completed_stage:
            self.sudo().write({
                'stage_id': completed_stage.id,
                'custom_state': 'completed'
            })

    # ============== WORKFLOW ACTIONS ==============
    
    def action_move_to_documentation(self):
        """Move order to documentation stage"""
        self.ensure_one()
        stage = self.env['sale.order.stage'].search([('stage_code', '=', 'documentation')], limit=1)
        if stage:
            self.write({'stage_id': stage.id, 'custom_state': 'documentation'})

    def action_move_to_calculation(self):
        """Move order to calculation stage"""
        self.ensure_one()
        stage = self.env['sale.order.stage'].search([('stage_code', '=', 'calculation')], limit=1)
        if stage:
            self.write({'stage_id': stage.id, 'custom_state': 'calculation'})

    def action_move_to_approved(self):
        """Move order to approved stage"""
        self.ensure_one()
        stage = self.env['sale.order.stage'].search([('stage_code', '=', 'approved')], limit=1)
        if stage:
            self.write({'stage_id': stage.id, 'custom_state': 'approved'})

    def action_complete_order(self):
        """Complete the order"""
        self.ensure_one()
        stage = self.env['sale.order.stage'].search([('stage_code', '=', 'completed')], limit=1)
        if stage:
            self.write({'stage_id': stage.id, 'custom_state': 'completed'})

    def action_unlock_order(self):
        """Unlock completed order (admin only)"""
        self.ensure_one()
        if not self.can_unlock:
            raise AccessError("Insufficient permissions to unlock order.")
        stage = self.env['sale.order.stage'].search([('stage_code', '=', 'approved')], limit=1)
        if stage:
            self.write({'stage_id': stage.id, 'custom_state': 'approved'})
