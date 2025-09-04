# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # Override the default state field to integrate with custom workflow
    state = fields.Selection(
        selection_add=[
            ('documentation', 'Documentation'),
            ('calculation', 'Calculation'),
            ('approved', 'Approved'),
            ('completed', 'Completed'),
        ],
        ondelete={
            'documentation': 'set default',
            'calculation': 'set default', 
            'approved': 'set default',
            'completed': 'set default'
        }
    )

    # Enhanced workflow fields
    stage_id = fields.Many2one(
        'sale.order.stage', 
        string='Workflow Stage', 
        tracking=True, 
        index=True,
        group_expand='_read_group_stage_ids',
        default=lambda self: self._get_default_stage(),
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

    # Related fields for enhanced tracking
    related_purchase_orders = fields.Many2many(
        'purchase.order',
        compute='_compute_related_purchase_orders',
        string='Related Purchase Orders',
        help="Purchase orders created from this sale order"
    )

    @api.model
    def _get_default_stage(self):
        """Get default stage for new sale orders"""
        return self.env['sale.order.stage'].search([('stage_code', '=', 'draft')], limit=1)

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
            po_complete = order._check_purchase_completion()
            
            order.completion_criteria_met = financial_complete and delivery_complete and po_complete

    def _compute_related_purchase_orders(self):
        """Find purchase orders related to this sale order"""
        for order in self:
            related_pos = self.env['purchase.order'].search([
                '|',
                ('origin', 'ilike', order.name),
                ('partner_ref', 'ilike', order.name)
            ])
            order.related_purchase_orders = related_pos

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """Return all stages for kanban group_by"""
        return self.env['sale.order.stage'].search([])

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        """Synchronize stage with state"""
        if self.stage_id and self.stage_id.stage_code:
            # Map stage codes to states
            stage_state_mapping = {
                'draft': 'draft',
                'documentation': 'documentation', 
                'calculation': 'calculation',
                'approved': 'approved',
                'completed': 'completed'
            }
            
            new_state = stage_state_mapping.get(self.stage_id.stage_code)
            if new_state and new_state != self.state:
                self.state = new_state

    # ============== WORKFLOW OVERRIDE METHODS ==============
    
    def action_confirm(self):
        """Override confirm to integrate with custom workflow"""
        # Call parent method first
        result = super().action_confirm()
        
        # Move to approved state if currently in calculation
        for order in self:
            if order.state == 'calculation':
                order._move_to_approved()
            elif order.state in ['draft', 'sent']:
                # Move to documentation for new confirmations
                order._move_to_documentation()
        
        return result

    def action_cancel(self):
        """Override cancel with workflow considerations"""
        # Check if any orders are locked
        locked_orders = self.filtered('is_locked')
        if locked_orders and not self.env.user.has_group('sales_team.group_sale_manager'):
            raise AccessError("Cannot cancel completed orders without administrator privileges.")
        
        # Reset workflow state before cancellation
        for order in self:
            if order.stage_id:
                draft_stage = self.env['sale.order.stage'].search([('stage_code', '=', 'draft')], limit=1)
                if draft_stage:
                    order.stage_id = draft_stage
        
        return super().action_cancel()

    def action_draft(self):
        """Override draft with workflow reset"""
        result = super().action_draft()
        
        # Reset to draft stage
        for order in self:
            draft_stage = self.env['sale.order.stage'].search([('stage_code', '=', 'draft')], limit=1)
            if draft_stage:
                order.stage_id = draft_stage
        
        return result

    # ============== CUSTOM WORKFLOW ACTIONS ==============
    
    def action_move_to_documentation(self):
        """Move order to documentation stage"""
        self._check_workflow_transition('documentation')
        return self._move_to_documentation()
        
    def _move_to_documentation(self):
        """Internal method to move to documentation"""
        stage = self.env['sale.order.stage'].search([('stage_code', '=', 'documentation')], limit=1)
        if stage:
            self.write({'stage_id': stage.id, 'state': 'documentation'})
            self.message_post(body="Order moved to Documentation stage")
        return True

    def action_move_to_calculation(self):
        """Move order to calculation stage"""
        self._check_workflow_transition('calculation')
        return self._move_to_calculation()
        
    def _move_to_calculation(self):
        """Internal method to move to calculation"""
        stage = self.env['sale.order.stage'].search([('stage_code', '=', 'calculation')], limit=1)
        if stage:
            self.write({'stage_id': stage.id, 'state': 'calculation'})
            self.message_post(body="Order moved to Calculation stage")
        return True

    def action_move_to_approved(self):
        """Move order to approved stage"""
        self._check_workflow_transition('approved')
        return self._move_to_approved()
        
    def _move_to_approved(self):
        """Internal method to move to approved"""
        stage = self.env['sale.order.stage'].search([('stage_code', '=', 'approved')], limit=1)
        if stage:
            self.write({'stage_id': stage.id, 'state': 'approved'})
            self.message_post(body="Order approved and ready for execution")
        return True

    def action_complete_order(self):
        """Complete the order (manual completion)"""
        self._check_workflow_transition('completed')
        return self._complete_order()
        
    def _complete_order(self):
        """Internal method to complete order"""
        stage = self.env['sale.order.stage'].search([('stage_code', '=', 'completed')], limit=1)
        if stage:
            self.write({'stage_id': stage.id, 'state': 'completed'})
            self.message_post(body="Order completed and locked")
        return True

    def action_unlock_order(self):
        """Unlock completed order (admin only)"""
        self.ensure_one()
        if not self.can_unlock:
            raise AccessError("Insufficient permissions to unlock order.")
            
        approved_stage = self.env['sale.order.stage'].search([('stage_code', '=', 'approved')], limit=1)
        if approved_stage:
            self.write({'stage_id': approved_stage.id, 'state': 'approved'})
            self.message_post(
                body=f"Order unlocked by {self.env.user.name}",
                message_type='notification'
            )
        return True

    # ============== WORKFLOW VALIDATION ==============
    
    def _check_workflow_transition(self, target_state):
        """Validate workflow transitions"""
        self.ensure_one()
        
        # Define valid transitions
        valid_transitions = {
            'documentation': ['draft', 'sent'],
            'calculation': ['documentation', 'sent'], 
            'approved': ['calculation', 'sale'],
            'completed': ['approved', 'sale']
        }
        
        current_state = self.state
        if target_state in valid_transitions:
            if current_state not in valid_transitions[target_state]:
                raise UserError(
                    f"Invalid workflow transition from {current_state} to {target_state}. "
                    f"Valid transitions for {target_state}: {', '.join(valid_transitions[target_state])}"
                )
        
        # Additional business rule validations
        if target_state == 'completed':
            self._validate_completion_requirements()

    def _validate_completion_requirements(self):
        """Validate that order can be completed"""
        self.ensure_one()
        
        errors = []
        
        # Check if order is confirmed
        if self.state not in ['approved', 'sale']:
            errors.append("Order must be approved before completion")
        
        # Check financial status (optional warning, not blocking)
        if self.billing_status != 'fully_invoiced':
            # This is a warning, not an error
            self.message_post(
                body="⚠️ Warning: Order is being completed but is not fully invoiced",
                message_type='notification'
            )
        
        if errors:
            raise ValidationError("\n".join(errors))

    # ============== BUSINESS LOGIC HELPERS ==============
    
    def _check_delivery_completion(self):
        """Check if all deliveries are completed"""
        self.ensure_one()
        # Safely check for picking_ids field (may not be available during module loading)
        if not hasattr(self, 'picking_ids'):
            return True
        if not self.picking_ids:
            return True
        return all(picking.state == 'done' for picking in self.picking_ids)

    def _check_purchase_completion(self):
        """Check if related purchase orders are completed"""
        self.ensure_one()
        
        # This is optional - some sales may not have related POs
        if not self.related_purchase_orders:
            return True
            
        # Check if all POs are in final states
        for po in self.related_purchase_orders:
            if po.state not in ['done', 'cancel']:
                return False
        
        return True

    # ============== AUTOMATED WORKFLOW ==============
    
    @api.model
    def _cron_check_auto_completion(self):
        """Cron job to automatically complete eligible orders"""
        eligible_orders = self.search([
            ('state', '=', 'approved'),
            ('completion_criteria_met', '=', True)
        ])
        
        for order in eligible_orders:
            try:
                order._complete_order()
                order.message_post(body="Order automatically completed based on completion criteria")
            except Exception as e:
                import logging
                _logger = logging.getLogger(__name__)
                _logger.warning(f"Failed to auto-complete order {order.name}: {str(e)}")

    @api.model
    def _cron_update_financial_status(self):
        """Cron job to update financial status for all active orders"""
        orders = self.search([('state', 'not in', ['draft', 'cancel', 'completed'])])
        
        # Trigger recomputation
        orders._compute_financial_amounts()
        orders._compute_financial_status()
        orders._compute_completion_criteria()

    # ============== CONSTRAINTS AND VALIDATIONS ==============
    
    def write(self, vals):
        """Override write with enhanced locking logic"""
        # Check for locked orders
        for order in self:
            if order.is_locked and not order.can_unlock:
                # Define fields that can be modified even when locked
                allowed_fields = {
                    'reconciliation_notes', 'workflow_notes', 'stage_id', 'state',
                    'billing_status', 'payment_status', 'invoiced_amount', 
                    'paid_amount', 'balance_amount', 'completion_criteria_met',
                    'message_follower_ids', 'message_ids'
                }
                
                restricted_fields = set(vals.keys()) - allowed_fields
                if restricted_fields:
                    raise AccessError(
                        f"Cannot modify {', '.join(restricted_fields)} - "
                        "order is completed and locked. Contact administrator to unlock."
                    )
        
        result = super().write(vals)
        
        # Trigger workflow notifications
        if 'state' in vals or 'stage_id' in vals:
            self._notify_stage_change()
        
        return result

    def _notify_stage_change(self):
        """Notify followers of stage changes"""
        for order in self:
            if order.message_follower_ids:
                stage_name = order.stage_id.name if order.stage_id else order.state.title()
                message = f"Sale Order {order.name} moved to: {stage_name}"
                order.message_post(
                    body=message,
                    message_type='notification',
                    subtype_xmlid='mail.mt_note'
                )

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
