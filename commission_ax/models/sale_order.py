# Add logger import at the top of the file
import logging

# Define logger for this module
_logger = logging.getLogger(__name__)
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging

class SaleOrder(models.Model):
    project_id = fields.Many2one('project.project', string='Project')
    purchase_order_total_amount = fields.Monetary(
        string="Total Purchase Order Amount",
        compute="_compute_purchase_order_total_amount",
        store=True,
        currency_field='currency_id'
    )

    def _compute_purchase_order_total_amount(self):
        for order in self:
            total = sum(order.purchase_order_ids.mapped('amount_total'))
            order.purchase_order_total_amount = total
    def action_confirm_commissions(self):
        """Confirm calculated commissions."""
        # Implement your business logic here
        self.commission_status = 'confirmed'
        self.message_post(body="Commissions confirmed.")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Commissions Confirmed',
                'message': 'Commissions have been confirmed.',
                'type': 'success',
            }
        }

    def action_reset_commissions(self):
        """Reset commission status to draft and cancel related purchase orders."""
        self.commission_status = 'draft'
        # Cancel related draft purchase orders
        draft_pos = self.purchase_order_ids.filtered(lambda po: po.state == 'draft')
        for po in draft_pos:
            po.button_cancel()
        self.message_post(body="Commission status reset to draft. Related draft purchase orders cancelled.")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Reset to Draft',
                'message': 'Commission status reset to draft. Related draft purchase orders cancelled.',
                'type': 'success',
            }
        }
    _inherit = 'sale.order'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        help='Related project for this sale order',
    )

    unit_id = fields.Many2one(
        'project.unit',
        string='Unit',
        help='Related unit for this sale order',
    )
    # [Previous fields remain the same - keeping all existing fields]
    # Legacy Commission fields with enhanced commission type logic
    consultant_id = fields.Many2one('res.partner', string="Consultant")
    consultant_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Consultant Commission Type", default='percent_untaxed_total')
    consultant_comm_percentage = fields.Float(string="Consultant Rate", default=0.0)
    salesperson_commission = fields.Monetary(string="Consultant Commission Amount", compute="_compute_commissions", store=True)

    SM_ID = fields.Many2one('res.partner', string="Senior Manager", help="Senior Manager for this deal")
    manager_legacy_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Senior Manager Commission Type", default='percent_untaxed_total')
    manager_comm_percentage = fields.Float(string="Senior Manager Rate", default=0.0)
    manager_commission = fields.Monetary(string="Senior Manager Commission Amount", compute="_compute_commissions", store=True)

    CXO_ID = fields.Many2one('res.partner', string="Management", help="Management (CXO/Director) for this deal")
    director_legacy_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Management Commission Type", default='percent_untaxed_total')
    director_comm_percentage = fields.Float(string="Management Rate", default=3.0)
    director_commission = fields.Monetary(string="Management Commission Amount", compute="_compute_commissions", store=True)

    # Second Agent fields
    second_agent_id = fields.Many2one('res.partner', string="Second Agent")
    second_agent_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Second Agent Commission Type", default='percent_untaxed_total')
    second_agent_comm_percentage = fields.Float(string="Second Agent Rate", default=0.0)
    second_agent_commission = fields.Monetary(string="Second Agent Commission Amount", compute="_compute_commissions", store=True)

    # Extended Commission Structure - External Commissions
    broker_partner_id = fields.Many2one('res.partner', string="Broker")
    broker_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Broker Commission Type", default='percent_unit_price')
    broker_rate = fields.Float(string="Broker Rate")
    broker_amount = fields.Monetary(string="Broker Commission", compute="_compute_commissions", store=True)

    referrer_partner_id = fields.Many2one('res.partner', string="Referrer")
    referrer_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Referrer Commission Type", default='percent_unit_price')
    referrer_rate = fields.Float(string="Referrer Rate")
    referrer_amount = fields.Monetary(string="Referrer Commission", compute="_compute_commissions", store=True)

    cashback_partner_id = fields.Many2one('res.partner', string="Cashback Partner")
    cashback_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Cashback Type", default='percent_unit_price')
    cashback_rate = fields.Float(string="Cashback Rate")
    cashback_amount = fields.Monetary(string="Cashback Amount", compute="_compute_commissions", store=True)

    other_external_partner_id = fields.Many2one('res.partner', string="Other External Partner")
    other_external_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Other External Commission Type", default='percent_unit_price')
    other_external_rate = fields.Float(string="Other External Rate")
    other_external_amount = fields.Monetary(string="Other External Commission", compute="_compute_commissions", store=True)

    # Extended Commission Structure - Internal Commissions
    agent1_partner_id = fields.Many2one('res.partner', string="Agent 1")
    agent1_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Agent 1 Commission Type", default='percent_unit_price')
    agent1_rate = fields.Float(string="Agent 1 Rate")
    agent1_amount = fields.Monetary(string="Agent 1 Commission", compute="_compute_commissions", store=True)

    agent2_partner_id = fields.Many2one('res.partner', string="Agent 2")
    agent2_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Agent 2 Commission Type", default='percent_unit_price')
    agent2_rate = fields.Float(string="Agent 2 Rate")
    agent2_amount = fields.Monetary(string="Agent 2 Commission", compute="_compute_commissions", store=True)

    manager_partner_id = fields.Many2one('res.partner', string="Manager Partner")
    manager_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Manager Commission Type", default='percent_unit_price')
    manager_rate = fields.Float(string="Manager Rate")
    manager_amount = fields.Monetary(string="Manager Commission Amount", compute="_compute_commissions", store=True)

    director_partner_id = fields.Many2one('res.partner', string="Director Partner")
    director_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Director Commission Type", default='percent_unit_price')
    director_rate = fields.Float(string="Director Rate", default=3.0)
    director_amount = fields.Monetary(string="Director Commission Amount", compute="_compute_commissions", store=True)

    # Summary fields
    total_external_commission_amount = fields.Monetary(string="Total External Commissions", compute="_compute_commissions", store=True)
    total_internal_commission_amount = fields.Monetary(string="Total Internal Commissions", compute="_compute_commissions", store=True)
    total_commission_amount = fields.Monetary(string="Total Commission Amount", compute="_compute_commissions", store=True)

    # Computed fields
    company_share = fields.Monetary(string="Company Share", compute="_compute_commissions", store=True)
    net_company_share = fields.Monetary(string="Net Company Share", compute="_compute_commissions", store=True)

    # Sales Value field for commission computation
    sales_value = fields.Monetary(string="Sales Value", compute="_compute_sales_value", store=True)

    # Related fields
    purchase_order_ids = fields.One2many('purchase.order', 'origin_so_id', string="Generated Purchase Orders")
    purchase_order_count = fields.Integer(string="PO Count", compute="_compute_purchase_order_count")
    commission_processed = fields.Boolean(string="Commissions Processed", default=False)
    commission_status = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('confirmed', 'Confirmed')
    ], string="Commission Processing Status", default='draft')

    # NEW FIELDS FOR ENHANCED BUSINESS LOGIC
    is_fully_invoiced = fields.Boolean(string="Fully Invoiced", compute="_compute_invoice_status", store=True)
    has_posted_invoices = fields.Boolean(string="Has Posted Invoices", compute="_compute_invoice_status", store=True)
    commission_blocked_reason = fields.Text(string="Commission Blocked Reason", readonly=True)

    @api.depends('invoice_ids', 'invoice_ids.state', 'invoice_status')
    def _compute_invoice_status(self):
        """Compute invoice-related status fields"""
        for order in self:
            posted_invoices = order.invoice_ids.filtered(lambda inv: inv.state == 'posted' and inv.move_type == 'out_invoice')
            order.has_posted_invoices = bool(posted_invoices)
            order.is_fully_invoiced = order.invoice_status == 'invoiced' and bool(posted_invoices)

    @api.depends('purchase_order_ids')
    def _compute_purchase_order_count(self):
        for order in self:
            order.purchase_order_count = len(order.purchase_order_ids)

    @api.constrains('order_line')
    def _check_single_order_line(self):
        for order in self:
            if len(order.order_line) > 1:
                raise ValidationError("Only one order line is allowed per sale order for commission clarity.")

    def _check_commission_prerequisites(self):
        """Check if order meets all prerequisites for commission processing"""
        self.ensure_one()
        errors = []
        
        # Check if order is confirmed
        if self.state not in ['sale', 'done']:
            errors.append("Sale order must be confirmed before processing commissions.")
        
        # Check if order is fully invoiced
        if not self.is_fully_invoiced:
            errors.append("Sale order must be fully invoiced with posted invoices before processing commissions.")
        
        # Check if order has positive amount
        if self.amount_total <= 0:
            errors.append("Sale order must have a positive total amount.")
        
        # Check if any commissions are defined
        commissions = self._get_commission_entries()
        if not commissions:
            errors.append("No commission partners or amounts are defined for this order.")
        
        if errors:
            self.commission_blocked_reason = "\n".join(errors)
            return False
        
        self.commission_blocked_reason = False
        return True

    def _create_commission_purchase_orders(self):
        """Enhanced commission PO creation with prerequisites check"""
        self.ensure_one()
        
        # Check prerequisites
        if not self._check_commission_prerequisites():
            raise UserError(f"Cannot process commissions:\n{self.commission_blocked_reason}")
        
        if self.commission_processed:
            raise UserError("Commissions have already been processed for this order.")
        
        # Update status
        self.commission_status = 'calculated'
        
        try:
            # Get commission product
            commission_product = self._get_or_create_commission_product()
            created_pos = []

            # Get all commission entries
            commissions = self._get_commission_entries()

            # Create purchase orders
            for commission in commissions:
                po_vals = self._prepare_purchase_order_vals(
                    partner=commission['partner'],
                    product=commission_product,
                    amount=commission['amount'],
                    description=commission['description']
                )
                po = self.env['purchase.order'].create(po_vals)
                created_pos.append(po)
                _logger.info(f"Created commission PO: {po.name}")

            # Mark as processed
            self.commission_processed = True
            self.commission_blocked_reason = False
            
            if created_pos:
                message = f"Successfully created {len(created_pos)} commission purchase orders"
                self.message_post(body=message)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': message,
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                self.commission_status = 'draft'
                raise UserError("No commissions were created. Please check commission settings.")
                
        except Exception as e:
            self.commission_status = 'draft'
            _logger.error(f"Error creating commission purchase orders: {str(e)}")
            raise UserError(f"Failed to process commissions: {str(e)}")

    def action_cancel(self):
        """Override cancel with enhanced cascade logic and user notification"""
        commission_orders = self.filtered('purchase_order_ids')
        
        if commission_orders:
            # Collect information about what will be cancelled
            cancel_info = []
            for order in commission_orders:
                po_info = []
                invoice_info = []
                
                # Check purchase orders
                for po in order.purchase_order_ids:
                    if po.state not in ['cancel', 'draft']:
                        po_info.append(f"- PO {po.name} (State: {po.state})")
                
                # Check related invoices for commission POs
                for po in order.purchase_order_ids:
                    for line in po.order_line:
                        invoice_lines = self.env['account.move.line'].search([
                            ('purchase_line_id', '=', line.id)
                        ])
                        for inv_line in invoice_lines:
                            if inv_line.move_id.state == 'posted':
                                invoice_info.append(f"- Invoice {inv_line.move_id.name}")
                
                if po_info or invoice_info:
                    cancel_info.append(f"Sale Order {order.name}:")
                    if po_info:
                        cancel_info.extend(["  Commission Purchase Orders:"] + po_info)
                    if invoice_info:
                        cancel_info.extend(["  Related Invoices:"] + invoice_info)
            
            if cancel_info:
                message = "The following commission-related documents will be cancelled:\n\n" + "\n".join(cancel_info)
                
                # Show confirmation dialog
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Confirm Cancellation',
                    'res_model': 'commission.cancel.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_sale_order_ids': [(6, 0, self.ids)],
                        'default_message': message,
                    }
                }
        
        # If no commission orders or user confirmed, proceed with cancellation
        return self._execute_cancellation()

    def _execute_cancellation(self):
        """Execute the actual cancellation with cascade logic"""
        for order in self:
            # Cancel related purchase orders
            for po in order.purchase_order_ids:
                try:
                    if po.state == 'draft':
                        po.button_cancel()
                    elif po.state in ['sent', 'to approve', 'purchase']:
                        # Force cancel confirmed POs
                        po.button_cancel()
                        po.message_post(body=f"Automatically cancelled due to sale order {order.name} cancellation")
                except Exception as e:
                    _logger.warning(f"Could not cancel PO {po.name}: {str(e)}")
            
            # Reset commission status
            order.commission_status = 'draft'
            order.commission_processed = False
            order.commission_blocked_reason = False
            
            # Post message about cascade cancellation
            if order.purchase_order_ids:
                order.message_post(
                    body=f"Sale order cancelled. {len(order.purchase_order_ids)} related commission purchase orders were also cancelled."
                )
        
        # Call original cancel method
        return super(SaleOrder, self).action_cancel()

    def action_draft(self):
        """Override draft action with cascade logic"""
        for order in self:
            if order.purchase_order_ids:
                confirmed_pos = order.purchase_order_ids.filtered(
                    lambda po: po.state not in ['draft', 'cancel']
                )
                
                if confirmed_pos:
                    po_names = ", ".join(confirmed_pos.mapped('name'))
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'Confirm Set to Draft',
                        'res_model': 'commission.draft.wizard',
                        'view_mode': 'form',
                        'target': 'new',
                        'context': {
                            'default_sale_order_id': order.id,
                            'default_message': f"Setting this sale order to draft will cancel the following confirmed commission purchase orders:\n{po_names}\n\nDo you want to continue?",
                        }
                    }
                else:
                    # Cancel draft POs
                    draft_pos = order.purchase_order_ids.filtered(lambda po: po.state == 'draft')
                    draft_pos.button_cancel()
                    
                    # Reset commission status
                    order.commission_status = 'draft'
                    order.commission_processed = False
                    order.commission_blocked_reason = False
        
        return super(SaleOrder, self).action_draft()

    def action_process_commissions(self):
        """Enhanced commission processing with prerequisite checks"""
        for order in self:
            if not order._check_commission_prerequisites():
                raise UserError(f"Cannot process commissions for {order.name}:\n{order.commission_blocked_reason}")
            order._create_commission_purchase_orders()
        return True

    # [Keep all other existing methods - compute functions, etc.]
    
    def _calculate_commission_amount(self, rate, commission_type, order):
        if commission_type == 'fixed':
            return rate
        elif commission_type == 'percent_unit_price':
            if order.order_line:
                return (rate / 100.0) * order.order_line[0].price_unit
            return 0.0
        elif commission_type == 'percent_untaxed_total':
            return (rate / 100.0) * order.amount_untaxed
        return 0.0

    @api.depends('amount_total', 'consultant_comm_percentage', 'consultant_commission_type',
                 'manager_comm_percentage', 'manager_legacy_commission_type', 
                 'director_comm_percentage', 'director_legacy_commission_type', 
                 'second_agent_comm_percentage', 'second_agent_commission_type',
                 'broker_rate', 'broker_commission_type', 'referrer_rate', 'referrer_commission_type',
                 'cashback_rate', 'cashback_commission_type', 'other_external_rate', 'other_external_commission_type',
                 'agent1_rate', 'agent1_commission_type', 'agent2_rate', 'agent2_commission_type',
                 'manager_rate', 'manager_commission_type', 'director_rate', 'director_commission_type',
                 'order_line.price_unit', 'order_line.price_subtotal', 'amount_untaxed')
    def _compute_commissions(self):
        """Compute commission amounts and company shares."""
        for order in self:
            base_amount = order.amount_total

            # Legacy commission calculations with flexible commission types
            order.salesperson_commission = self._calculate_commission_amount(
                order.consultant_comm_percentage, 
                order.consultant_commission_type, 
                order
            )
            order.manager_commission = self._calculate_commission_amount(
                order.manager_comm_percentage, 
                order.manager_legacy_commission_type, 
                order
            )
            order.second_agent_commission = self._calculate_commission_amount(
                order.second_agent_comm_percentage, 
                order.second_agent_commission_type, 
                order
            )
            order.director_commission = self._calculate_commission_amount(
                order.director_comm_percentage, 
                order.director_legacy_commission_type, 
                order
            )

            # External commissions
            order.broker_amount = self._calculate_commission_amount(order.broker_rate, order.broker_commission_type, order)
            order.referrer_amount = self._calculate_commission_amount(order.referrer_rate, order.referrer_commission_type, order)
            order.cashback_amount = self._calculate_commission_amount(order.cashback_rate, order.cashback_commission_type, order)
            order.other_external_amount = self._calculate_commission_amount(order.other_external_rate, order.other_external_commission_type, order)

            # Internal commissions
            order.agent1_amount = self._calculate_commission_amount(order.agent1_rate, order.agent1_commission_type, order)
            order.agent2_amount = self._calculate_commission_amount(order.agent2_rate, order.agent2_commission_type, order)
            order.manager_amount = self._calculate_commission_amount(order.manager_rate, order.manager_commission_type, order)
            order.director_amount = self._calculate_commission_amount(order.director_rate, order.director_commission_type, order)

            # Calculate totals
            order.total_external_commission_amount = (
                order.broker_amount + order.referrer_amount + 
                order.cashback_amount + order.other_external_amount
            )

            order.total_internal_commission_amount = (
                order.agent1_amount + order.agent2_amount + 
                order.manager_amount + order.director_amount +
                order.salesperson_commission + order.manager_commission + 
                order.second_agent_commission + order.director_commission
            )

            order.total_commission_amount = (
                order.total_external_commission_amount + order.total_internal_commission_amount
            )

            # Company share calculations
            order.company_share = base_amount - order.total_commission_amount
            order.net_company_share = order.company_share

    @api.depends('amount_total')
    def _compute_sales_value(self):
        for order in self:
            order.sales_value = order.amount_total

    def _get_commission_entries(self):
        """Get all commission entries that need purchase orders."""
        self.ensure_one()
        commissions = []

        # Legacy commissions
        if self.consultant_id and self.salesperson_commission > 0:
            commissions.append({
                'partner': self.consultant_id,
                'amount': self.salesperson_commission,
                'description': f"Consultant Commission for SO: {self.name}"
            })

        if self.SM_ID and self.manager_commission > 0:
            commissions.append({
                'partner': self.SM_ID,
                'amount': self.manager_commission,
                'description': f"Senior Manager Commission for SO: {self.name}"
            })

        if self.second_agent_id and self.second_agent_commission > 0:
            commissions.append({
                'partner': self.second_agent_id,
                'amount': self.second_agent_commission,
                'description': f"Second Agent Commission for SO: {self.name}"
            })

        if self.CXO_ID and self.director_commission > 0:
            commissions.append({
                'partner': self.CXO_ID,
                'amount': self.director_commission,
                'description': f"Management Commission for SO: {self.name}"
            })

        # External commissions
        if self.broker_partner_id and self.broker_amount > 0:
            commissions.append({
                'partner': self.broker_partner_id,
                'amount': self.broker_amount,
                'description': f"Broker Commission for SO: {self.name}"
            })

        if self.referrer_partner_id and self.referrer_amount > 0:
            commissions.append({
                'partner': self.referrer_partner_id,
                'amount': self.referrer_amount,
                'description': f"Referrer Commission for SO: {self.name}"
            })

        if self.cashback_partner_id and self.cashback_amount > 0:
            commissions.append({
                'partner': self.cashback_partner_id,
                'amount': self.cashback_amount,
                'description': f"Cashback for SO: {self.name}"
            })

        if self.other_external_partner_id and self.other_external_amount > 0:
            commissions.append({
                'partner': self.other_external_partner_id,
                'amount': self.other_external_amount,
                'description': f"Other External Commission for SO: {self.name}"
            })

        # Internal commissions
        if self.agent1_partner_id and self.agent1_amount > 0:
            commissions.append({
                'partner': self.agent1_partner_id,
                'amount': self.agent1_amount,
                'description': f"Agent 1 Commission for SO: {self.name}"
            })

        if self.agent2_partner_id and self.agent2_amount > 0:
            commissions.append({
                'partner': self.agent2_partner_id,
                'amount': self.agent2_amount,
                'description': f"Agent 2 Commission for SO: {self.name}"
            })

        if self.manager_partner_id and self.manager_amount > 0:
            commissions.append({
                'partner': self.manager_partner_id,
                'amount': self.manager_amount,
                'description': f"Manager Commission for SO: {self.name}"
            })

        if self.director_partner_id and self.director_amount > 0:
            commissions.append({
                'partner': self.director_partner_id,
                'amount': self.director_amount,
                'description': f"Director Commission for SO: {self.name}"
            })

        return commissions

    def _get_or_create_commission_product(self, commission_type="Sales Commission"):
        """Get or create commission product."""
        product = self.env['product.product'].search([
            ('name', '=', commission_type),
            ('type', '=', 'service')
        ], limit=1)
        
        if not product:
            product = self.env['product.product'].create({
                'name': commission_type,
                'type': 'service',
                'categ_id': self.env.ref('product.product_category_all').id,
                'list_price': 0.0,
                'standard_price': 0.0,
                'sale_ok': False,
                'purchase_ok': True,
                'detailed_type': 'service',
            })
            _logger.info(f"Created commission product: {commission_type}")
        
        return product

    def _prepare_purchase_order_vals(self, partner, product, amount, description):
        """Prepare values for purchase order creation."""
        if not partner:
            raise UserError("Partner is required for purchase order creation")
        
        if amount <= 0:
            raise UserError("Commission amount must be greater than zero")
        
        return {
            'partner_id': partner.id,
            'date_order': fields.Date.today(),
            'currency_id': self.currency_id.id,
            'company_id': self.company_id.id,
            'origin': self.name,
            'description': description,
            'origin_so_id': self.id,
            'commission_posted': False,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'name': description,
                'product_qty': 1.0,
                'product_uom': product.uom_id.id,
                'price_unit': amount,
                'taxes_id': [(6, 0, product.supplier_taxes_id.ids)],
            })]
        }