from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    """Extended Sale Order with simplified commission management via many2many assignments"""
    _inherit = 'sale.order'

    # ============== MODERN COMMISSION STRUCTURE ==============
    # Using commission assignment mixin for flexible many2many relationships
    
    # Keep the existing one2many for backward compatibility during transition
    commission_line_ids = fields.One2many(
        'commission.line',
        'sale_order_id',
        string='Commission Lines (Legacy)',
        copy=False,
        help="Legacy commission structure - being phased out in favor of assignments"
    )

    # New simplified commission fields using assignments
    use_modern_commissions = fields.Boolean(
        string='Use Modern Commission Structure',
        default=True,
        help="Use the new many2many assignment structure instead of legacy commission fields"
    )

    # Performance optimized commission totals (Override mixin fields as Monetary)
    total_commission_amount = fields.Monetary(
        string='Total Commission Amount',
        compute='_compute_commission_stats',
        store=True,
        currency_field='currency_id',
        help="Total commission amount from all assigned commission lines"
    )

    pending_commission_amount = fields.Monetary(
        string='Pending Commission Amount',
        compute='_compute_commission_stats',
        store=True,
        currency_field='currency_id',
        help="Total amount of pending commissions assigned to this record"
    )

    paid_commission_amount = fields.Monetary(
        string='Paid Commission Amount',
        compute='_compute_commission_stats',
        store=True,
        currency_field='currency_id',
        help="Total amount of paid commissions assigned to this record"
    )

    total_commission_lines_amount = fields.Monetary(
        string='Total Commission Amount (Legacy)',
        compute='_compute_commission_lines_totals',
        store=True,
        currency_field='currency_id',
        help="Total commission amount from all assigned commission lines"
    )

    internal_commission_lines_amount = fields.Monetary(
        string='Internal Commission Amount',
        compute='_compute_commission_lines_totals',
        store=True,
        currency_field='currency_id',
        help="Total internal commission amount"
    )

    external_commission_lines_amount = fields.Monetary(
        string='External Commission Amount',
        compute='_compute_commission_lines_totals',
        store=True,
        currency_field='currency_id',
        help="Total external commission amount"
    )

    commission_lines_count = fields.Integer(
        string='Commission Lines Count',
        compute='_compute_commission_lines_count',
        help="Number of commission lines assigned to this order"
    )

    # Commission Statement fields (Enhanced)
    commission_statement_count = fields.Integer(
        string='Commission Statement Count',
        compute='_compute_commission_statement_count',
        help="Number of commission partners eligible for statements"
    )

    # Performance monitoring fields
    commission_calculation_time = fields.Float(
        string='Last Calculation Time (ms)',
        readonly=True,
        help="Time taken for last commission calculation in milliseconds"
    )

    use_commission_lines = fields.Boolean(
        string='Use Commission Lines Structure',
        default=True,
        help="Use modern commission lines structure instead of legacy fields"
    )

    force_commission_processing = fields.Boolean(
        string='Force Commission Processing',
        default=False,
        help="Temporary flag to bypass invoice validation when force processing commissions"
    )
    
    # Project fields (if project module is installed)
    project_id = fields.Many2one('project.project', string='Project')
    
    # Purchase order related fields
    purchase_order_total_amount = fields.Monetary(
        string="Total Purchase Order Amount",
        compute="_compute_purchase_order_total_amount",
        store=True,
        currency_field='currency_id'
    )
    
    # ============== LEGACY COMMISSION FIELDS (DEPRECATED - Use commission_line_ids instead) ==============
    # These fields are deprecated in favor of the commission_line_ids structure
    # They are kept for backward compatibility and will be removed in future versions
    
    # Legacy Individual Commission Fields
    consultant_id = fields.Many2one('res.partner', string="Consultant (DEPRECATED)", help="Use commission_line_ids instead")
    consultant_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Consultant Commission Type", default='percent_untaxed_total')
    consultant_comm_percentage = fields.Float(string="Consultant Rate", default=0.0)
    salesperson_commission = fields.Monetary(string="Consultant Commission Amount", compute="_compute_commissions", store=True)

    manager_id = fields.Many2one('res.partner', string="Manager")
    manager_legacy_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Manager Commission Type", default='percent_untaxed_total')
    manager_comm_percentage = fields.Float(string="Manager Rate", default=0.0)
    manager_commission = fields.Monetary(string="Manager Commission Amount", compute="_compute_commissions", store=True)

    director_id = fields.Many2one('res.partner', string="Director")
    director_legacy_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Director Commission Type", default='percent_untaxed_total')
    director_comm_percentage = fields.Float(string="Director Rate", default=3.0)
    director_commission = fields.Monetary(string="Director Commission Amount", compute="_compute_commissions", store=True)

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
    broker_partner_id = fields.Many2one(
        'res.partner', 
        string="Broker",
        domain=[('supplier_rank', '>', 0)],
        help="Partner who will receive broker commission"
    )
    broker_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Broker Commission Type", default='percent_unit_price')
    broker_rate = fields.Float(string="Broker Rate")
    broker_amount = fields.Monetary(string="Broker Commission", compute="_compute_commissions", store=True)

    referrer_partner_id = fields.Many2one(
        'res.partner', 
        string="Referrer",
        domain=[('supplier_rank', '>', 0)],
        help="Partner who will receive referrer commission"
    )
    referrer_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Referrer Commission Type", default='percent_unit_price')
    referrer_rate = fields.Float(string="Referrer Rate")
    referrer_amount = fields.Monetary(string="Referrer Commission", compute="_compute_commissions", store=True)

    cashback_partner_id = fields.Many2one(
        'res.partner', 
        string="Cashback Partner",
        domain=[('supplier_rank', '>', 0)],
        help="Partner who will receive cashback commission"
    )
    cashback_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Cashback Type", default='percent_unit_price')
    cashback_rate = fields.Float(string="Cashback Rate")
    cashback_amount = fields.Monetary(string="Cashback Amount", compute="_compute_commissions", store=True)

    other_external_partner_id = fields.Many2one(
        'res.partner', 
        string="Other External Partner",
        domain=[('supplier_rank', '>', 0)],
        help="Other external partner who will receive commission"
    )
    other_external_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Other External Commission Type", default='percent_unit_price')
    other_external_rate = fields.Float(string="Other External Rate")
    other_external_amount = fields.Monetary(string="Other External Commission", compute="_compute_commissions", store=True)

    # Extended Commission Structure - Internal Commissions
    agent1_partner_id = fields.Many2one(
        'res.partner', 
        string="Agent 1",
        domain=[('supplier_rank', '>', 0)],
        help="Internal agent 1 who will receive commission"
    )
    agent1_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Agent 1 Commission Type", default='percent_unit_price')
    agent1_rate = fields.Float(string="Agent 1 Rate")
    agent1_amount = fields.Monetary(string="Agent 1 Commission", compute="_compute_commissions", store=True)

    agent2_partner_id = fields.Many2one(
        'res.partner', 
        string="Agent 2",
        domain=[('supplier_rank', '>', 0)],
        help="Internal agent 2 who will receive commission"
    )
    agent2_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Agent 2 Commission Type", default='percent_unit_price')
    agent2_rate = fields.Float(string="Agent 2 Rate")
    agent2_amount = fields.Monetary(string="Agent 2 Commission", compute="_compute_commissions", store=True)

    manager_partner_id = fields.Many2one(
        'res.partner', 
        string="Manager Partner",
        domain=[('supplier_rank', '>', 0)],
        help="Internal manager who will receive commission"
    )
    manager_commission_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent_unit_price', 'Percentage of Unit Price'),
        ('percent_untaxed_total', 'Percentage of Untaxed Total')
    ], string="Manager Commission Type", default='percent_unit_price')
    manager_rate = fields.Float(string="Manager Rate")
    manager_amount = fields.Monetary(string="Manager Commission Amount", compute="_compute_commissions", store=True)

    director_partner_id = fields.Many2one(
        'res.partner', 
        string="Director Partner",
        domain=[('supplier_rank', '>', 0)],
        help="Internal director who will receive commission"
    )
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

    # ============== COMPUTE METHODS - ENHANCED ==============

    @api.depends('commission_line_ids')
    def _compute_commission_lines_count(self):
        """Compute commission lines count from both legacy and modern structures"""
        for order in self:
            if order.use_modern_commissions:
                # Use assignment-based count (mixin not available)
                order.commission_lines_count = 0
            else:
                # Use legacy count
                order.commission_lines_count = len(order.commission_line_ids)

    @api.depends('commission_line_ids.commission_amount', 'commission_line_ids.commission_category',
                 'use_modern_commissions')
    def _compute_commission_lines_totals(self):
        """Optimized commission totals calculation using both legacy and modern structures"""
        for order in self:
            if order.use_modern_commissions:
                # Use modern assignment-based calculation
                commission_lines = order.commission_line_ids
                order.total_commission_lines_amount = order.total_commission_amount
                order.internal_commission_lines_amount = sum(
                    commission_lines.filtered(lambda l: l.commission_category == 'internal' and l.state != 'cancelled').mapped('commission_amount')
                )
                order.external_commission_lines_amount = sum(
                    commission_lines.filtered(lambda l: l.commission_category == 'external' and l.state != 'cancelled').mapped('commission_amount')
                )
            else:
                # Use legacy calculation
                lines = order.commission_line_ids.filtered(lambda l: l.state != 'cancelled')
                order.total_commission_lines_amount = sum(lines.mapped('commission_amount'))
                order.internal_commission_lines_amount = sum(
                    lines.filtered(lambda l: l.commission_category == 'internal').mapped('commission_amount')
                )
                order.external_commission_lines_amount = sum(
                    lines.filtered(lambda l: l.commission_category == 'external').mapped('commission_amount')
                )

    @api.depends('commission_line_ids')
    def _compute_commission_stats(self):
        """Compute commission statistics with currency support for sale orders"""
        for order in self:
            if order.use_modern_commissions:
                # Use assignment-based calculation (mixin not available)
                commission_lines = order.commission_line_ids  # Fallback to legacy
            else:
                # Use legacy structure
                commission_lines = order.commission_line_ids
            
            order.commission_count = len(commission_lines)
            order.total_commission_amount = sum(commission_lines.mapped('commission_amount'))
            
            # Calculate pending commissions
            pending_lines = commission_lines.filtered(lambda l: l.state in ['draft', 'calculated', 'confirmed'])
            order.pending_commission_amount = sum(pending_lines.mapped('commission_amount'))
            
            # Calculate paid commissions
            paid_lines = commission_lines.filtered(lambda l: l.state in ['paid', 'partially_paid'])
            order.paid_commission_amount = sum(paid_lines.mapped('commission_amount'))

    @api.depends('agent1_partner_id', 'agent2_partner_id', 'broker_partner_id',
                 'referrer_partner_id', 'cashback_partner_id', 'other_external_partner_id',
                 'consultant_id', 'manager_id', 'second_agent_id', 'director_id',
                 'manager_partner_id', 'director_partner_id', 'commission_line_ids.partner_id')
    def _compute_commission_statement_count(self):
        """Compute number of commission partners for this order (Enhanced with commission lines)."""
        for order in self:
            partners = set()

            # Modern commission lines approach
            if order.use_commission_lines and order.commission_line_ids:
                partners.update(order.commission_line_ids.mapped('partner_id').ids)
            else:
                # Legacy approach for backward compatibility
                commission_partners = [
                    order.agent1_partner_id,
                    order.agent2_partner_id,
                    order.broker_partner_id,
                    order.referrer_partner_id,
                    order.cashback_partner_id,
                    order.other_external_partner_id,
                    order.consultant_id,
                    order.manager_id,
                    order.second_agent_id,
                    order.director_id,
                    order.manager_partner_id,
                    order.director_partner_id,
                ]
                for partner in commission_partners:
                    if partner:
                        partners.add(partner.id)

            order.commission_statement_count = len(partners)

    @api.depends('purchase_order_ids')
    def _compute_purchase_order_total_amount(self):
        for order in self:
            total = sum(order.purchase_order_ids.mapped('amount_total'))
            order.purchase_order_total_amount = total

    @api.depends('invoice_ids', 'invoice_ids.state', 'invoice_status', 'amount_total')
    def _compute_invoice_status(self):
        """Compute invoice-related status fields with better logic"""
        for order in self:
            posted_invoices = order.invoice_ids.filtered(lambda inv: inv.state == 'posted' and inv.move_type == 'out_invoice')
            order.has_posted_invoices = bool(posted_invoices)
            
            # More flexible check for fully invoiced status
            if posted_invoices:
                total_invoiced = sum(posted_invoices.mapped('amount_total'))
                # Allow small rounding differences (0.01)
                is_amounts_match = abs(total_invoiced - order.amount_total) <= 0.01
                order.is_fully_invoiced = (order.invoice_status == 'invoiced' or is_amounts_match) and bool(posted_invoices)
            else:
                order.is_fully_invoiced = False

    @api.depends('purchase_order_ids')
    def _compute_purchase_order_count(self):
        for order in self:
            order.purchase_order_count = len(order.purchase_order_ids)

    @api.depends('amount_total')
    def _compute_sales_value(self):
        for order in self:
            order.sales_value = order.amount_total

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

    # ============== CONSTRAINT METHODS ==============
    
    @api.constrains('order_line')
    def _check_single_order_line(self):
        for order in self:
            if len(order.order_line) > 1:
                raise ValidationError("Only one order line is allowed per sale order for commission clarity.")

    # ============== ACTION METHODS ==============
    
    def action_view_commission_statement(self):
        """Open commission statement wizard for this order."""
        self.ensure_one()
        if not self.env.user.has_group('base.group_user'):
            from odoo.exceptions import AccessError
            raise AccessError("You don't have permission to view commission statements.")
        commission_partners = self._get_commission_partners()
        if not commission_partners:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Commission Partners',
                    'message': 'This sale order has no commission partners defined.',
                    'type': 'warning',
                }
            }
        context = {
            'default_sale_order_id': self.id,
            'default_date_from': self.date_order.date() if self.date_order else fields.Date.today(),
            'default_date_to': fields.Date.today(),
        }
        if len(commission_partners) == 1:
            context['default_partner_id'] = commission_partners[0].id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Commission Statement',
            'res_model': 'commission.partner.statement.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': context,
        }

    def action_open_commission_report_wizard(self):
        """Open the commission report wizard for this sale order."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Commission Report Wizard',
            'res_model': 'commission.report.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
            }
        }

    def action_view_commission_details(self):
        """View commission details for this sale order - compatibility method."""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Commission Details',
                'message': f'Commission details for order {self.name}. Total commission: {self.total_commission_amount}',
                'type': 'info',
            }
        }

    def action_view_commission_report(self):
        """Alternative method name for commission report access."""
        return self.action_open_commission_report_wizard()

    def action_confirm_commissions(self):
        """Confirm calculated commissions."""
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

    def action_process_commissions(self):
        """Enhanced commission processing with commission lines support"""
        import time
        start_time = time.time()

        for order in self:
            if not order._check_commission_prerequisites():
                raise UserError("Cannot process commissions for %s:\n%s" % (order.name, order.commission_blocked_reason))

            if order.use_commission_lines:
                # Auto-create commission lines if they don't exist
                if not order.commission_line_ids:
                    lines_created = order._create_commission_lines_from_legacy()
                    if lines_created == 0:
                        raise UserError(
                            f"No commission lines found for order {order.name} and no legacy commission data available to create them. "
                            "Please add commission partners and rates in the Commission Management section first."
                        )

                order._process_commission_lines()
            else:
                order._create_commission_purchase_orders()

        # Record performance metric
        calculation_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        self.commission_calculation_time = calculation_time

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Commission Processing Complete',
                'message': f'Processed commissions in {calculation_time:.2f}ms',
                'type': 'success',
            }
        }

    def action_force_process_commissions(self):
        """Force commission processing even if invoice check fails"""
        for order in self:
            # Set force flag to bypass invoice validation
            order.force_commission_processing = True
            try:
                if order.use_commission_lines:
                    order._process_commission_lines()
                else:
                    order._create_commission_purchase_orders()
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Commission Force Processed',
                        'message': f'Commissions have been force processed for order {order.name}',
                        'type': 'success',
                    }
                }
            except Exception as e:
                raise UserError(f"Failed to force process commissions: {str(e)}")
            finally:
                # Always reset the force flag
                order.force_commission_processing = False

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
        
        return super().action_draft()

    # ============== HELPER METHODS ==============
    
    def _get_commission_partners(self):
        """Get all partners with commissions on this order."""
        partners = []
        commission_partner_fields = [
            'agent1_partner_id',
            'agent2_partner_id', 
            'broker_partner_id',
            'referrer_partner_id',
            'cashback_partner_id',
            'other_external_partner_id',
            'consultant_id',
            'manager_id',
            'second_agent_id',
            'director_id',
            'manager_partner_id',
            'director_partner_id',
        ]
        for field_name in commission_partner_fields:
            if hasattr(self, field_name):
                partner = getattr(self, field_name)
                if partner and partner not in partners:
                    partners.append(partner)
        return partners

    def _calculate_commission_amount(self, rate, commission_type, order):
        """Calculate commission amount based on type and rate."""
        if commission_type == 'fixed':
            return rate
        elif commission_type == 'percent_unit_price':
            if order.order_line:
                return (rate / 100.0) * order.order_line[0].price_unit
            return 0.0
        elif commission_type == 'percent_untaxed_total':
            return (rate / 100.0) * order.amount_untaxed
        return 0.0

    def _check_commission_prerequisites(self):
        """Check if order meets all prerequisites for commission processing"""
        self.ensure_one()
        errors = []

        # Check if order is confirmed
        if self.state not in ['sale', 'done']:
            errors.append("❌ Sale order must be confirmed before processing commissions.")

        # Check if order is fully invoiced (more flexible check)
        if not self.is_fully_invoiced:
            # Allow manual override if user confirms it's invoiced
            if not getattr(self, 'force_commission_processing', False):
                errors.append("❌ Sale order must be fully invoiced with posted invoices before processing commissions. "
                            "Use 'Force Process' if you're certain the order is properly invoiced.")

        # Check if order has positive amount
        if self.amount_total <= 0:
            errors.append("❌ Sale order must have a positive total amount.")

        # Check if any commissions are defined (either in commission lines or legacy fields)
        has_commission_data = False

        if self.use_commission_lines and self.commission_line_ids:
            has_commission_data = True
        else:
            # Check legacy commission fields
            legacy_partners = [
                self.consultant_id, self.manager_id, self.director_id, self.second_agent_id,
                self.broker_partner_id, self.referrer_partner_id, self.cashback_partner_id,
                self.other_external_partner_id, self.agent1_partner_id, self.agent2_partner_id,
                self.manager_partner_id, self.director_partner_id
            ]

            legacy_rates = [
                self.consultant_comm_percentage, self.manager_comm_percentage,
                self.director_comm_percentage, self.second_agent_comm_percentage,
                self.broker_rate, self.referrer_rate, self.cashback_rate,
                self.other_external_rate, self.agent1_rate, self.agent2_rate,
                self.manager_rate, self.director_rate
            ]

            for partner, rate in zip(legacy_partners, legacy_rates):
                if partner and rate > 0:
                    has_commission_data = True
                    break

        if not has_commission_data:
            errors.append("❌ No commission partners or rates are defined. Please add commission information in the Legacy Commission, External Commission, or Internal Commission tabs.")

        if errors:
            self.commission_blocked_reason = "\n".join(errors)
            return False

        self.commission_blocked_reason = False
        return True

    def _process_commission_lines(self):
        """Process commission lines - create/update purchase orders"""
        self.ensure_one()

        if not self.commission_line_ids:
            raise UserError("No commission lines found. Please create commission lines first.")

        lines_to_process = self.commission_line_ids.filtered(
            lambda l: l.state == 'confirmed' and not l.purchase_order_id
        )

        if not lines_to_process:
            raise UserError("No confirmed commission lines ready for processing.")

        # Process commission lines
        processed_count = 0
        for line in lines_to_process:
            try:
                line.action_process()
                processed_count += 1
            except Exception as e:
                _logger.error(f"Error processing commission line {line.id}: {str(e)}")
                continue

        # Update order status
        if processed_count > 0:
            self.commission_status = 'calculated'
            self.commission_processed = True

        return processed_count

    def _create_commission_purchase_orders(self):
        """Enhanced commission PO creation with prerequisites check (Legacy support)"""
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
                _logger.info("Created commission PO: %s", po.name)

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
            _logger.error("Error creating commission purchase orders: %s", str(e))
            raise UserError("Failed to process commissions: %s" % str(e)) from e

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
                    _logger.warning("Could not cancel PO %s: %s", po.name, str(e))
            
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
        return super().action_cancel()

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

        if self.manager_id and self.manager_commission > 0:
            commissions.append({
                'partner': self.manager_id,
                'amount': self.manager_commission,
                'description': f"Manager Commission for SO: {self.name}"
            })

        if self.second_agent_id and self.second_agent_commission > 0:
            commissions.append({
                'partner': self.second_agent_id,
                'amount': self.second_agent_commission,
                'description': f"Second Agent Commission for SO: {self.name}"
            })

        if self.director_id and self.director_commission > 0:
            commissions.append({
                'partner': self.director_id,
                'amount': self.director_commission,
                'description': f"Director Commission for SO: {self.name}"
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

    # ============== COMMISSION LINES MANAGEMENT ==============

    def action_create_commission_lines(self):
        """Create commission lines from current commission configuration"""
        self.ensure_one()

        if self.commission_line_ids:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Confirm Replace Commission Lines',
                'res_model': 'commission.lines.replace.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_sale_order_id': self.id},
            }

        lines_created = self._create_commission_lines_from_legacy()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Commission Lines Created',
                'message': f'Created {lines_created} commission lines',
                'type': 'success',
            }
        }

    def _create_commission_lines_from_legacy(self):
        """Create commission lines from legacy commission fields"""
        self.ensure_one()

        commission_lines = []

        # Mapping legacy fields to commission lines
        legacy_mappings = [
            ('consultant_id', 'consultant_comm_percentage', 'consultant_commission_type', 'consultant', 'internal'),
            ('manager_id', 'manager_comm_percentage', 'manager_legacy_commission_type', 'manager', 'internal'),
            ('director_id', 'director_comm_percentage', 'director_legacy_commission_type', 'director', 'internal'),
            ('second_agent_id', 'second_agent_comm_percentage', 'second_agent_commission_type', 'agent', 'internal'),
            ('broker_partner_id', 'broker_rate', 'broker_commission_type', 'broker', 'external'),
            ('referrer_partner_id', 'referrer_rate', 'referrer_commission_type', 'referrer', 'external'),
            ('cashback_partner_id', 'cashback_rate', 'cashback_commission_type', 'agent', 'external'),
            ('agent1_partner_id', 'agent1_rate', 'agent1_commission_type', 'agent', 'internal'),
            ('agent2_partner_id', 'agent2_rate', 'agent2_commission_type', 'agent', 'internal'),
            ('manager_partner_id', 'manager_rate', 'manager_commission_type', 'manager', 'internal'),
            ('director_partner_id', 'director_rate', 'director_commission_type', 'director', 'internal'),
        ]

        for partner_field, rate_field, type_field, role, category in legacy_mappings:
            partner = getattr(self, partner_field, None)
            rate = getattr(self, rate_field, 0.0)
            comm_type = getattr(self, type_field, 'percent_untaxed_total')

            if partner and rate > 0:
                # Map calculation method
                calc_method = self._map_legacy_calc_method(comm_type)

                # Get or create commission type
                commission_type = self._get_or_create_commission_type_for_role(role, category)

                commission_lines.append({
                    'sale_order_id': self.id,
                    'partner_id': partner.id,
                    'commission_type_id': commission_type.id,
                    'calculation_method': calc_method,
                    'rate': rate,
                    'commission_category': category,
                    'role': role,
                    'state': 'calculated' if self.commission_processed else 'draft',
                    'sequence': len(commission_lines) * 10,
                })

        # Create commission lines
        if commission_lines:
            created_lines = self.env['commission.line'].create(commission_lines)
            self.use_commission_lines = True
            return len(created_lines)

        return 0

    def _map_legacy_calc_method(self, legacy_method):
        """Map legacy calculation method to new format"""
        mapping = {
            'fixed': 'fixed',
            'percent_unit_price': 'percentage_unit',
            'percent_untaxed_total': 'percentage_untaxed',
        }
        return mapping.get(legacy_method, 'percentage_total')

    def _get_or_create_commission_type_for_role(self, role, category):
        """Get or create commission type for specific role and category"""
        type_name = f"{role.title()} {category.title()} Commission"
        commission_type = self.env['commission.type'].search([
            ('name', '=', type_name)
        ], limit=1)

        if not commission_type:
            commission_type = self.env['commission.type'].create({
                'name': type_name,
                'code': f"{role.upper()}_{category.upper()}",
                'calculation_method': 'percentage',
                'commission_category': category if category in ['sales', 'referral', 'management', 'bonus'] else 'sales',
                'default_rate': 0.0,
            })

        return commission_type

    def action_view_commission_lines(self):
        """View commission lines for this order"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Commission Lines',
            'res_model': 'commission.line',
            'view_mode': 'tree,form',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {'default_sale_order_id': self.id},
        }

    def action_calculate_commission_lines(self):
        """Calculate amounts for all commission lines"""
        self.ensure_one()

        lines_to_calculate = self.commission_line_ids.filtered(lambda l: l.state == 'draft')

        for line in lines_to_calculate:
            line.action_calculate()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Commission Lines Calculated',
                'message': f'Calculated {len(lines_to_calculate)} commission lines',
                'type': 'success',
            }
        }

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
            _logger.info("Created commission product: %s", commission_type)
        
        return product

    def action_migrate_to_commission_lines(self):
        """Migrate order from legacy commission structure to commission lines"""
        self.ensure_one()

        if self.commission_line_ids:
            raise UserError("This order already has commission lines.")

        lines_created = self._create_commission_lines_from_legacy()

        if lines_created > 0:
            # Optionally disable legacy fields to prevent confusion
            # This would require careful consideration in production
            pass

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Migration Complete',
                'message': f'Successfully migrated to commission lines structure. Created {lines_created} commission lines.',
                'type': 'success',
            }
        }

    def action_migrate_to_modern_commissions(self):
        """Migrate order from legacy commission structure to modern assignment-based structure"""
        self.ensure_one()
        
        if self.use_modern_commissions:
            raise UserError("This order is already using the modern commission structure.")
        
        assignments_created = 0
        
        # Migrate existing commission lines to assignments
        for commission_line in self.commission_line_ids:
            assignment = self.env['commission.assignment'].create({
                'source_model': self._name,
                'source_id': self.id,
                'commission_line_id': commission_line.id,
                'assignment_type': 'migrated',
            })
            assignments_created += 1
        
        # Enable modern commission structure
        self.use_modern_commissions = True
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Migration to Modern Structure Complete',
                'message': f'Successfully migrated to modern commission assignment structure. Created {assignments_created} assignments.',
                'type': 'success',
            }
        }

    @api.model
    def migrate_all_to_modern_commissions(self):
        """Migrate all sale orders to modern commission structure"""
        orders = self.search([('use_modern_commissions', '=', False)])
        migrated_count = 0
        
        for order in orders:
            try:
                order.action_migrate_to_modern_commissions()
                migrated_count += 1
            except Exception as e:
                _logger.warning(f"Failed to migrate order {order.name}: {str(e)}")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Bulk Migration Complete',
                'message': f'Successfully migrated {migrated_count} orders to modern commission structure.',
                'type': 'success',
            }
        }

    def _prepare_purchase_order_vals(self, partner, product, amount, description):
        """Prepare values for purchase order creation with vendor reference auto-population."""
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
            'partner_ref': self.client_order_ref or '',  # Auto-populate vendor reference from customer reference
            'order_line': [(0, 0, {
                'product_id': product.id,
                'name': description,
                'product_qty': 1.0,
                'product_uom': product.uom_id.id,
                'price_unit': amount,
                'taxes_id': [(6, 0, product.supplier_taxes_id.ids)],
            })]
        }

    def action_commission_performance_report(self):
        """Open commission performance report for this order's timeframe"""
        self.ensure_one()

        # Set date range around this order's date
        order_date = self.date_order.date() if self.date_order else fields.Date.today()
        date_from = order_date.replace(day=1)  # First day of month

        return {
            'type': 'ir.actions.act_window',
            'name': 'Commission Performance Report',
            'res_model': 'commission.performance.report',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_date_from': date_from,
                'default_date_to': order_date,
            }
        }

    def action_view_commission_dashboard(self):
        """View commission dashboard filtered for this order"""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Commission Dashboard',
            'res_model': 'commission.dashboard',
            'view_mode': 'graph,pivot,list',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {
                'search_default_group_by_partner': 1,
            }
        }

    def _check_legacy_commission_usage(self):
        """Check if order uses legacy commission fields and log deprecation warning"""
        legacy_fields = [
            'consultant_id', 'manager_id', 'director_id', 'second_agent_id',
            'broker_partner_id', 'referrer_partner_id', 'cashback_partner_id',
            'agent1_partner_id', 'agent2_partner_id', 'manager_partner_id', 'director_partner_id'
        ]
        
        for field_name in legacy_fields:
            if getattr(self, field_name, False):
                _logger.warning(
                    "DEPRECATION WARNING: Sale Order %s uses legacy commission field '%s'. "
                    "Please migrate to commission_line_ids structure for better performance and features.",
                    self.name, field_name
                )
                return True
        return False

    @api.model
    def migrate_all_legacy_commissions(self):
        """Migrate all orders from legacy commission structure to commission lines"""
        legacy_orders = self.search([
            '|', '|', '|', '|', '|', '|', '|', '|', '|', '|',
            ('consultant_id', '!=', False),
            ('manager_id', '!=', False),
            ('director_id', '!=', False),
            ('second_agent_id', '!=', False),
            ('broker_partner_id', '!=', False),
            ('referrer_partner_id', '!=', False),
            ('cashback_partner_id', '!=', False),
            ('agent1_partner_id', '!=', False),
            ('agent2_partner_id', '!=', False),
            ('manager_partner_id', '!=', False),
            ('director_partner_id', '!=', False),
        ])
        
        migrated_count = 0
        for order in legacy_orders:
            if not order.commission_line_ids:  # Only migrate if no commission lines exist
                try:
                    order._create_commission_lines_from_legacy()
                    migrated_count += 1
                    _logger.info("Migrated commission data for order %s", order.name)
                except Exception as e:
                    _logger.error("Failed to migrate order %s: %s", order.name, str(e))
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Migration Complete',
                'message': f'Successfully migrated {migrated_count} orders to commission lines structure.',
                'type': 'success',
            }
        }