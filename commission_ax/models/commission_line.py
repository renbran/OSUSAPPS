from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class CommissionLine(models.Model):
    """Enhanced Commission Line Model for optimized performance and better data structure"""
    _name = 'commission.line'
    _description = 'Commission Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sale_order_id, sequence, id'
    _rec_name = 'display_name'

    # Core relationships
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        required=True,
        ondelete='cascade',
        index=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Commission Partner',
        required=True,
        domain=[('supplier_rank', '>', 0)],
        ondelete='restrict',
        index=True
    )
    commission_type_id = fields.Many2one(
        'commission.type',
        string='Commission Type',
        required=True,
        ondelete='restrict',
        index=True
    )

    # Sequence and display
    sequence = fields.Integer(string='Sequence', default=10)
    display_name = fields.Char(
        string='Name',
        compute='_compute_display_name',
        store=True
    )

    # Commission calculation fields
    calculation_method = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage_unit', 'Percentage of Unit Price'),
        ('percentage_total', 'Percentage of Total'),
        ('percentage_untaxed', 'Percentage of Untaxed Amount'),
        ('percentage_sales_value', 'Percentage of Sales Value'),
    ], string='Calculation Method', required=True, default='percentage_sales_value')

    rate = fields.Float(
        string='Rate/Amount',
        digits=(16, 6),
        help='Commission rate as percentage or fixed amount'
    )

    # Sales value field for commission calculation
    sales_value = fields.Monetary(
        string='Sales Value',
        currency_field='currency_id',
        help='Specific sales value for commission calculation (e.g., price_unit of related product)',
        tracking=True
    )

    # Computed amounts
    base_amount = fields.Monetary(
        string='Base Amount',
        compute='_compute_amounts',
        store=True,
        currency_field='currency_id',
        help='Amount on which commission is calculated'
    )

    commission_amount = fields.Monetary(
        string='Commission Amount',
        compute='_compute_amounts',
        store=True,
        currency_field='currency_id',
        help='Calculated commission amount'
    )

    commission_amount_company_currency = fields.Monetary(
        string='Commission Amount (Company Currency)',
        compute='_compute_amounts',
        store=True,
        currency_field='company_currency_id',
        help='Commission amount in company currency'
    )

    # Status and workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('confirmed', 'Confirmed'),
        ('processed', 'Processed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, index=True)

    # Purchase order integration
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Commission Purchase Order',
        readonly=True,
        ondelete='set null',
        copy=False
    )

    purchase_line_id = fields.Many2one(
        'purchase.order.line',
        string='Commission Purchase Line',
        readonly=True,
        ondelete='set null',
        copy=False
    )

    # Assignment relationship (Many2many bridge) - Temporarily disabled
    # assignment_ids = fields.One2many(
    #     'commission.assignment',
    #     'commission_line_id',
    #     string='Assignments',
    #     help='Records that this commission line is assigned to via many2many bridge'
    # )

    assignment_count = fields.Integer(
        string='Assignment Count',
        # compute='_compute_assignment_count',
        default=0,
        help='Number of records this commission line is assigned to'
    )

    # Category and grouping
    commission_category = fields.Selection([
        ('internal', 'Internal Commission'),
        ('external', 'External Commission'),
        ('management', 'Management Override'),
        ('bonus', 'Bonus Commission'),
    ], string='Category', required=True, default='internal', index=True)

    role = fields.Selection([
        ('agent', 'Sales Agent'),
        ('manager', 'Sales Manager'),
        ('director', 'Director'),
        ('broker', 'External Broker'),
        ('referrer', 'Referrer'),
        ('consultant', 'Consultant'),
        ('other', 'Other'),
    ], string='Role', default='agent')

    # Currency and company
    currency_id = fields.Many2one(
        'res.currency',
        related='sale_order_id.currency_id',
        store=True,
        string='Currency',
        ondelete='restrict'
    )

    company_currency_id = fields.Many2one(
        'res.currency',
        related='sale_order_id.company_id.currency_id',
        store=True,
        string='Company Currency',
        ondelete='restrict'
    )

    company_id = fields.Many2one(
        'res.company',
        related='sale_order_id.company_id',
        store=True,
        string='Company',
        ondelete='restrict'
    )

    # Additional fields
    description = fields.Text(string='Description')
    date_commission = fields.Date(
        string='Commission Date',
        default=fields.Date.context_today,
        index=True
    )

    # Enhanced Payment tracking
    invoice_amount = fields.Monetary(
        string='Invoiced Amount',
        currency_field='currency_id',
        help='Amount invoiced for this commission',
        tracking=True
    )

    paid_amount = fields.Monetary(
        string='Paid Amount',
        currency_field='currency_id',
        help='Amount paid for this commission',
        tracking=True
    )

    # Quantity tracking fields
    sales_qty = fields.Float(
        string='Sales Quantity',
        digits=(16, 6),
        compute='_compute_quantities',
        store=True,
        help='Total quantity from sale order lines'
    )

    invoiced_qty = fields.Float(
        string='Invoiced Quantity',
        digits=(16, 6),
        compute='_compute_quantities',
        store=True,
        help='Total invoiced quantity from related invoices'
    )

    qty_percentage = fields.Float(
        string='Invoiced Qty %',
        digits=(16, 6),
        compute='_compute_quantities',
        store=True,
        help='Percentage of sales quantity that has been invoiced (without rounding)'
    )

    outstanding_amount = fields.Monetary(
        string='Outstanding Amount',
        compute='_compute_payment_amounts',
        store=True,
        currency_field='currency_id',
        help='Outstanding commission amount'
    )

    # Payment status tracking
    payment_status = fields.Selection([
        ('pending', 'Pending Payment'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled')
    ], string='Payment Status', compute='_compute_payment_status', store=True, index=True)

    payment_date = fields.Date(
        string='Payment Date',
        help='Date when commission was fully paid',
        tracking=True
    )

    expected_payment_date = fields.Date(
        string='Expected Payment Date',
        compute='_compute_expected_payment_date',
        store=True,
        help='Expected payment date based on payment terms'
    )

    days_overdue = fields.Integer(
        string='Days Overdue',
        compute='_compute_payment_amounts',
        store=True,
        help='Number of days payment is overdue'
    )

    # Invoice tracking from purchase order
    invoice_ids = fields.Many2many(
        'account.move',
        string='Related Invoices',
        compute='_compute_invoice_info',
        help='Invoices created from commission purchase order'
    )

    invoice_count = fields.Integer(
        string='Invoice Count',
        compute='_compute_invoice_info'
    )

    # Payment tracking from invoices
    payment_ids = fields.Many2many(
        'account.payment',
        string='Related Payments',
        compute='_compute_payment_info',
        help='Payments made for commission invoices'
    )

    payment_count = fields.Integer(
        string='Payment Count',
        compute='_compute_payment_info'
    )

    # Commission aging
    aging_days = fields.Integer(
        string='Aging (Days)',
        compute='_compute_aging',
        store=True,
        help='Days since commission was processed'
    )

    aging_category = fields.Selection([
        ('current', 'Current (0-30 days)'),
        ('30_days', '31-60 days'),
        ('60_days', '61-90 days'),
        ('90_days', '90+ days')
    ], string='Aging Category', compute='_compute_aging', store=True)

    # Performance optimization fields
    is_legacy = fields.Boolean(
        string='Legacy Commission',
        default=False,
        help='Indicates if this was migrated from legacy structure'
    )

    # Constraints and validations
    _sql_constraints = [
        ('rate_positive', 'CHECK(rate >= 0)', 'Commission rate must be positive!'),
        ('unique_partner_type_order',
         'UNIQUE(sale_order_id, partner_id, commission_type_id)',
         'Cannot have duplicate commission for same partner and type on one order!'),
    ]

    @api.depends('partner_id', 'commission_type_id', 'sale_order_id')
    def _compute_display_name(self):
        """Compute display name for commission line"""
        for line in self:
            if line.partner_id and line.commission_type_id:
                line.display_name = f"{line.partner_id.name} - {line.commission_type_id.name}"
            else:
                line.display_name = _('Commission Line')

    # @api.depends('assignment_ids')  # Temporarily disabled
    def _compute_assignment_count(self):
        """Compute the number of assignments for this commission line"""
        for line in self:
            line.assignment_count = 0  # len(line.assignment_ids)

    @api.depends('sale_order_id.amount_total', 'sale_order_id.amount_untaxed',
                 'rate', 'calculation_method', 'sales_value', 'sale_order_id.order_line.price_unit')
    def _compute_amounts(self):
        """Enhanced commission amount calculation with proper sales value handling"""
        for line in self:
            if not line.sale_order_id:
                line.base_amount = 0.0
                line.commission_amount = 0.0
                line.commission_amount_company_currency = 0.0
                continue

            order = line.sale_order_id

            # Determine base amount based on calculation method
            if line.calculation_method == 'fixed':
                line.base_amount = 1.0  # Fixed amount doesn't need base
                line.commission_amount = line.rate
            
            elif line.calculation_method == 'percentage_sales_value':
                # Use the specific sales_value field for calculation
                line.base_amount = line.sales_value or 0.0
                line.commission_amount = (line.rate / 100.0) * line.base_amount
            
            elif line.calculation_method == 'percentage_unit':
                # Use sales_value if available, otherwise fallback to first order line
                if line.sales_value:
                    line.base_amount = line.sales_value
                elif order.order_line:
                    # Calculate sum of all order line unit prices instead of just first one
                    total_price_unit = sum(ol.price_unit * ol.product_uom_qty for ol in order.order_line)
                    line.base_amount = total_price_unit
                else:
                    line.base_amount = 0.0
                line.commission_amount = (line.rate / 100.0) * line.base_amount
            
            elif line.calculation_method == 'percentage_untaxed':
                line.base_amount = order.amount_untaxed
                line.commission_amount = (line.rate / 100.0) * line.base_amount
            
            else:  # percentage_total
                line.base_amount = order.amount_total
                line.commission_amount = (line.rate / 100.0) * line.base_amount

            # Convert to company currency
            if line.currency_id and line.company_currency_id and line.currency_id != line.company_currency_id:
                line.commission_amount_company_currency = line.currency_id._convert(
                    line.commission_amount,
                    line.company_currency_id,
                    line.company_id,
                    line.date_commission or fields.Date.context_today(line)
                )
            else:
                line.commission_amount_company_currency = line.commission_amount

    @api.depends('commission_amount', 'invoice_amount', 'paid_amount', 'expected_payment_date')
    def _compute_payment_amounts(self):
        """Enhanced computation of payment-related amounts and status"""
        today = fields.Date.today()

        for line in self:
            line.outstanding_amount = line.commission_amount - line.paid_amount

            # Calculate days overdue
            if line.expected_payment_date and line.outstanding_amount > 0:
                if today > line.expected_payment_date:
                    line.days_overdue = (today - line.expected_payment_date).days
                else:
                    line.days_overdue = 0
            else:
                line.days_overdue = 0

    @api.depends('sale_order_id.order_line', 'sale_order_id.order_line.product_uom_qty', 
                 'sale_order_id.order_line.qty_invoiced')
    def _compute_quantities(self):
        """Compute sales quantity, invoiced quantity, and percentage without rounding"""
        for line in self:
            if not line.sale_order_id or not line.sale_order_id.order_line:
                line.sales_qty = 0.0
                line.invoiced_qty = 0.0
                line.qty_percentage = 0.0
                continue

            # Calculate total sales quantity
            total_sales_qty = sum(line.sale_order_id.order_line.mapped('product_uom_qty'))
            
            # Calculate total invoiced quantity  
            total_invoiced_qty = sum(line.sale_order_id.order_line.mapped('qty_invoiced'))
            
            line.sales_qty = total_sales_qty
            line.invoiced_qty = total_invoiced_qty
            
            # Calculate percentage without rounding - preserve full precision
            if total_sales_qty > 0:
                # Use high precision division to avoid rounding
                line.qty_percentage = (total_invoiced_qty / total_sales_qty) * 100.0
            else:
                line.qty_percentage = 0.0

    @api.depends('outstanding_amount', 'commission_amount', 'paid_amount', 'days_overdue', 'state')
    def _compute_payment_status(self):
        """Compute payment status based on amounts and dates"""
        for line in self:
            if line.state in ['draft', 'calculated', 'confirmed']:
                line.payment_status = 'pending'
            elif line.state == 'cancelled':
                line.payment_status = 'cancelled'
            elif line.outstanding_amount <= 0:
                line.payment_status = 'paid'
            elif line.paid_amount > 0:
                line.payment_status = 'partial'
            elif line.days_overdue > 0:
                line.payment_status = 'overdue'
            else:
                line.payment_status = 'pending'

    @api.depends('purchase_order_id', 'purchase_order_id.date_order', 'partner_id.property_supplier_payment_term_id')
    def _compute_expected_payment_date(self):
        """Compute expected payment date based on purchase order and payment terms"""
        for line in self:
            if line.purchase_order_id and line.purchase_order_id.date_order:
                # Default to 30 days from PO date if no payment terms specified
                payment_days = 30

                # Check if partner has specific payment terms
                if line.partner_id.property_supplier_payment_term_id:
                    payment_term = line.partner_id.property_supplier_payment_term_id
                    if payment_term.line_ids:
                        # Get the maximum days from payment terms
                        payment_days = max(payment_term.line_ids.mapped('days'))

                line.expected_payment_date = line.purchase_order_id.date_order.date() + timedelta(days=payment_days)
            else:
                line.expected_payment_date = False

    @api.depends('date_commission', 'state')
    def _compute_aging(self):
        """Compute commission aging in days"""
        today = fields.Date.today()

        for line in self:
            if line.state in ['processed', 'paid'] and line.date_commission:
                line.aging_days = (today - line.date_commission).days

                # Categorize aging
                if line.aging_days <= 30:
                    line.aging_category = 'current'
                elif line.aging_days <= 60:
                    line.aging_category = '30_days'
                elif line.aging_days <= 90:
                    line.aging_category = '60_days'
                else:
                    line.aging_category = '90_days'
            else:
                line.aging_days = 0
                line.aging_category = 'current'

    @api.depends('purchase_order_id')
    def _compute_invoice_info(self):
        """Compute invoice information from purchase order"""
        for line in self:
            if line.purchase_order_id:
                # Find invoices related to this purchase order
                invoices = self.env['account.move'].search([
                    ('purchase_id', '=', line.purchase_order_id.id),
                    ('move_type', '=', 'in_invoice'),
                    ('state', '!=', 'cancel')
                ])
                line.invoice_ids = [(6, 0, invoices.ids)]
                line.invoice_count = len(invoices)
            else:
                line.invoice_ids = [(6, 0, [])]
                line.invoice_count = 0

    @api.depends('invoice_ids')
    def _compute_payment_info(self):
        """Compute payment information from invoices"""
        for line in self:
            if line.invoice_ids:
                payments = self.env['account.payment']
                for invoice in line.invoice_ids:
                    # Get payments for each invoice
                    invoice_payments = invoice.payment_ids.filtered(
                        lambda p: p.state == 'posted'
                    )
                    payments |= invoice_payments

                line.payment_ids = [(6, 0, payments.ids)]
                line.payment_count = len(payments)
            else:
                line.payment_ids = [(6, 0, [])]
                line.payment_count = 0

    @api.constrains('rate', 'calculation_method')
    def _check_rate_consistency(self):
        """Validate rate based on calculation method"""
        for line in self:
            if line.calculation_method != 'fixed' and line.rate > 100:
                raise ValidationError(
                    _("Percentage-based commission rate cannot exceed 100%.")
                )
            if line.rate < 0:
                raise ValidationError(
                    _("Commission rate cannot be negative.")
                )

    @api.constrains('partner_id', 'commission_type_id', 'sale_order_id')
    def _check_required_references(self):
        """Validate that all required Many2one references exist"""
        for line in self:
            if line.partner_id and not line.partner_id.exists():
                raise ValidationError(
                    _("The commission partner for this line no longer exists.")
                )
            if line.commission_type_id and not line.commission_type_id.exists():
                raise ValidationError(
                    _("The commission type for this line no longer exists.")
                )
            if line.sale_order_id and not line.sale_order_id.exists():
                raise ValidationError(
                    _("The sale order for this line no longer exists.")
                )

    def _validate_for_processing(self):
        """Validate commission line is ready for processing"""
        self.ensure_one()

        if self.state != 'confirmed':
            raise UserError(_("Commission line must be confirmed before processing."))

        if self.commission_amount <= 0:
            raise UserError(_("Commission amount must be greater than zero."))

        if not self.partner_id:
            raise UserError(_("Commission partner is required."))

        if not self.partner_id.supplier_rank:
            raise UserError(_("Commission partner must be configured as a vendor."))

        if not self.sale_order_id:
            raise UserError(_("Sale order is required."))

        if self.sale_order_id.state not in ['sale', 'done']:
            raise UserError(_("Sale order must be confirmed before processing commissions."))

        # Check if partner has necessary payment configuration
        if not self.partner_id.property_supplier_payment_term_id:
            _logger.warning(f"Partner {self.partner_id.name} has no payment terms configured")

    @api.onchange('commission_type_id')
    def _onchange_commission_type(self):
        """Auto-fill fields from commission type with proper error handling"""
        if self.commission_type_id:
            try:
                # Map commission type calculation method to commission line method
                calculation_method_mapping = {
                    'percentage': 'percentage_sales_value',  # Changed default to sales_value
                    'fixed': 'fixed',
                    'tiered': 'percentage_sales_value',
                }
                
                commission_type_method = self.commission_type_id.calculation_method or 'percentage'
                mapped_method = calculation_method_mapping.get(commission_type_method, 'percentage_sales_value')
                
                # Double-check that the mapped method is valid
                valid_methods = [opt[0] for opt in self._fields['calculation_method'].selection]
                if mapped_method in valid_methods:
                    self.calculation_method = mapped_method
                else:
                    _logger.warning(f"Invalid calculation method mapping: {commission_type_method} -> {mapped_method}")
                    self.calculation_method = 'percentage_sales_value'
                
                self.rate = self.commission_type_id.default_rate or 0.0
                self.commission_category = self.commission_type_id.commission_category or 'internal'
                
            except Exception as e:
                _logger.error(f"Error in commission type onchange: {e}")
                # Set safe defaults to prevent RPC errors
                self.calculation_method = 'percentage_sales_value'
                self.rate = 0.0
                self.commission_category = 'internal'

    @api.onchange('sale_order_id', 'calculation_method')
    def _onchange_sale_order_auto_populate_sales_value(self):
        """Auto-populate sales_value when sale order or calculation method changes"""
        if self.sale_order_id and self.calculation_method in ['percentage_sales_value', 'percentage_unit']:
            if not self.sales_value or self.sales_value == 0.0:
                # Try to set a reasonable default sales_value
                order = self.sale_order_id
                if order.order_line:
                    if len(order.order_line) == 1:
                        # Single line order - use the line's subtotal
                        line = order.order_line[0]
                        self.sales_value = line.price_subtotal
                    else:
                        # Multiple lines - could use total subtotal or ask user to specify
                        # For now, use the order subtotal as default
                        self.sales_value = order.amount_untaxed

    @api.model
    def _cleanup_orphaned_records(self):
        """Clean up commission lines with orphaned references"""
        _logger.info("Starting cleanup of orphaned commission lines...")
        
        # Find lines with non-existent partners
        orphaned_lines = self.search([])
        to_delete = []
        
        for line in orphaned_lines:
            try:
                # Test if referenced records exist
                if line.partner_id and not line.partner_id.exists():
                    to_delete.append(line.id)
                    continue
                if line.commission_type_id and not line.commission_type_id.exists():
                    to_delete.append(line.id)
                    continue
                if line.sale_order_id and not line.sale_order_id.exists():
                    to_delete.append(line.id)
                    continue
                # Check optional references
                if line.purchase_order_id and not line.purchase_order_id.exists():
                    line.purchase_order_id = False
                    line.purchase_line_id = False
            except Exception as e:
                _logger.warning("Error checking commission line %s: %s", line.id, str(e))
                to_delete.append(line.id)
        
        if to_delete:
            orphaned_records = self.browse(to_delete)
            orphaned_records.unlink()
            _logger.info("Deleted %s orphaned commission lines", len(to_delete))
        
        return len(to_delete)

    def action_calculate(self):
        """Calculate commission amounts"""
        for line in self:
            if line.state == 'draft':
                line.state = 'calculated'
        return True

    def action_confirm(self):
        """Confirm commission calculation"""
        for line in self:
            if line.state in ['draft', 'calculated']:
                line.state = 'confirmed'
        return True

    def action_process(self):
        """Process commission (create purchase order)"""
        processed_count = 0
        errors = []

        for line in self.filtered(lambda l: l.state == 'confirmed'):
            try:
                # Validate commission line before processing
                line._validate_for_processing()

                if not line.purchase_order_id:
                    line._create_purchase_order()

                line.state = 'processed'
                line.date_commission = fields.Date.today()
                processed_count += 1

                line.message_post(
                    body=f"Commission processed successfully. Purchase order: {line.purchase_order_id.name if line.purchase_order_id else 'N/A'}"
                )

            except Exception as e:
                error_msg = f"Error processing commission line {line.id}: {str(e)}"
                errors.append(error_msg)
                _logger.error(error_msg)

                line.message_post(
                    body=f"Failed to process commission: {str(e)}",
                    message_type='comment'
                )

        if errors:
            if processed_count == 0:
                raise UserError(f"Failed to process all commission lines:\n" + "\n".join(errors))
            else:
                # Partial success - show warning
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Partial Success',
                        'message': f'Processed {processed_count} commission lines. {len(errors)} failed.',
                        'type': 'warning',
                    }
                }

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Successfully processed {processed_count} commission lines.',
                'type': 'success',
            }
        }

    def action_mark_paid(self):
        """Mark commission as fully paid"""
        for line in self:
            if line.state == 'processed':
                line.paid_amount = line.commission_amount
                line.payment_date = fields.Date.today()
                line.state = 'paid'
                line.message_post(
                    body=f"Commission marked as fully paid: {line.commission_amount} {line.currency_id.name}"
                )
        return True

    def action_record_partial_payment(self):
        """Open wizard to record partial payment"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Record Partial Payment',
            'res_model': 'commission.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_commission_line_id': self.id,
                'default_max_amount': self.outstanding_amount,
            }
        }

    def action_view_invoices(self):
        """View related invoices"""
        self.ensure_one()
        if not self.invoice_ids:
            raise UserError(_("No invoices found for this commission line."))

        if len(self.invoice_ids) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Commission Invoice'),
                'res_model': 'account.move',
                'res_id': self.invoice_ids[0].id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Commission Invoices'),
                'res_model': 'account.move',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', self.invoice_ids.ids)],
                'target': 'current',
            }

    def action_view_payments(self):
        """View related payments"""
        self.ensure_one()
        if not self.payment_ids:
            raise UserError(_("No payments found for this commission line."))

        if len(self.payment_ids) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Commission Payment'),
                'res_model': 'account.payment',
                'res_id': self.payment_ids[0].id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Commission Payments'),
                'res_model': 'account.payment',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', self.payment_ids.ids)],
                'target': 'current',
            }

    def action_cancel(self):
        """Cancel commission line"""
        for line in self:
            if line.purchase_order_id and line.purchase_order_id.state not in ['cancel']:
                raise UserError(
                    _("Cannot cancel commission line with confirmed purchase order. "
                      "Please cancel the purchase order first.")
                )
            line.state = 'cancelled'
        return True

    def action_reset_to_draft(self):
        """Reset to draft state"""
        for line in self:
            if line.purchase_order_id:
                if line.purchase_order_id.state == 'draft':
                    line.purchase_order_id.button_cancel()
                else:
                    raise UserError(
                        _("Cannot reset commission line with confirmed purchase order.")
                    )
            line.state = 'draft'
            line.purchase_order_id = False
            line.purchase_line_id = False
        return True

    def action_view_purchase_order(self):
        """View the related purchase order"""
        self.ensure_one()
        
        if not self.purchase_order_id:
            raise UserError(_("No purchase order found for this commission line."))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Purchase Order'),
            'res_model': 'purchase.order',
            'res_id': self.purchase_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_assignments(self):
        """View all assignments for this commission line"""
        # TEMPORARILY DISABLED - Assignment model not loaded
        self.ensure_one()
        
        raise UserError(_("Commission assignment functionality is temporarily disabled. Using legacy commission structure."))
        
        # Disabled assignment view code
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': _('Commission Assignments'),
        #     'res_model': 'commission.assignment',
        #     'view_mode': 'tree,form',
        #     'domain': [('commission_line_id', '=', self.id)],
        #     'context': {
        #         'default_commission_line_id': self.id,
        #     },
        #     'target': 'current',
        # }

    def _create_purchase_order(self):
        """Create purchase order for commission payment"""
        self.ensure_one()

        if self.commission_amount <= 0:
            raise UserError(_("Cannot create purchase order with zero commission amount."))

        # Get commission product
        commission_product = self._get_commission_product()

        # Prepare purchase order values
        po_vals = {
            'partner_id': self.partner_id.id,
            'date_order': fields.Date.today(),
            'currency_id': self.currency_id.id,
            'company_id': self.company_id.id,
            'origin': self.sale_order_id.name,
            'origin_so_id': self.sale_order_id.id,
            'partner_ref': self.sale_order_id.client_order_ref or '',
        }

        # Create purchase order
        purchase_order = self.env['purchase.order'].create(po_vals)

        # Create purchase order line
        po_line_vals = {
            'order_id': purchase_order.id,
            'product_id': commission_product.id,
            'name': f"{self.commission_type_id.name} - {self.sale_order_id.name}",
            'product_qty': 1.0,
            'product_uom': commission_product.uom_id.id,
            'price_unit': self.commission_amount,
            'taxes_id': [(6, 0, commission_product.supplier_taxes_id.ids)],
        }

        po_line = self.env['purchase.order.line'].create(po_line_vals)

        # Update commission line
        self.purchase_order_id = purchase_order.id
        self.purchase_line_id = po_line.id

        _logger.info(f"Created commission PO {purchase_order.name} for {self.partner_id.name}")

        return purchase_order

    def _get_commission_product(self):
        """Get or create commission product"""
        product = self.env['product.product'].search([
            ('name', '=', 'Commission Payment'),
            ('type', '=', 'service')
        ], limit=1)

        if not product:
            # Try to get service category or use default
            try:
                categ_id = self.env.ref('product.product_category_5').id  # Service category
            except:
                try:
                    categ_id = self.env.ref('product.product_category_all').id
                except:
                    # Create a service category if none exists
                    service_category = self.env['product.category'].search([
                        ('name', 'ilike', 'service')
                    ], limit=1)
                    if not service_category:
                        service_category = self.env['product.category'].create({
                            'name': 'Services',
                        })
                    categ_id = service_category.id

            # Get default UOM for services
            try:
                uom_id = self.env.ref('uom.product_uom_unit').id
            except:
                uom_id = self.env['uom.uom'].search([('name', '=', 'Units')], limit=1).id

            product = self.env['product.product'].create({
                'name': 'Commission Payment',
                'type': 'service',
                'categ_id': categ_id,
                'uom_id': uom_id,
                'uom_po_id': uom_id,
                'list_price': 0.0,
                'standard_price': 0.0,
                'sale_ok': False,
                'purchase_ok': True,
                'detailed_type': 'service',
                'description': 'Service product for commission payments to partners',
            })

            _logger.info(f"Created commission product: {product.name} (ID: {product.id})")

        return product

    @api.model
    def migrate_legacy_commissions(self):
        """Migrate existing commission data to commission lines structure"""
        _logger.info("Starting legacy commission migration...")

        # Find sale orders with legacy commission data
        legacy_orders = self.env['sale.order'].search([
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
            # Skip if already has commission lines
            if order.commission_line_ids:
                continue

            commission_lines = []

            # Legacy commission mappings
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
                partner = getattr(order, partner_field, None)
                rate = getattr(order, rate_field, 0.0)
                comm_type = getattr(order, type_field, 'percent_untaxed_total')

                if partner and rate > 0:
                    # Map calculation method
                    calc_method = 'percentage_total'
                    if comm_type == 'fixed':
                        calc_method = 'fixed'
                    elif comm_type == 'percent_unit_price':
                        calc_method = 'percentage_unit'
                    elif comm_type == 'percent_untaxed_total':
                        calc_method = 'percentage_untaxed'

                    # Get or create commission type
                    commission_type = self._get_or_create_commission_type(role, category)

                    commission_lines.append({
                        'sale_order_id': order.id,
                        'partner_id': partner.id,
                        'commission_type_id': commission_type.id,
                        'calculation_method': calc_method,
                        'rate': rate,
                        'commission_category': category,
                        'role': role,
                        'state': 'calculated' if hasattr(order, 'commission_processed') and order.commission_processed else 'draft',
                        'is_legacy': True,
                    })

            # Create commission lines
            if commission_lines:
                self.create(commission_lines)
                migrated_count += 1
                _logger.info(f"Migrated {len(commission_lines)} commission lines for order {order.name}")

        _logger.info(f"Migration completed. Migrated {migrated_count} orders.")
        return migrated_count

    @api.model
    def _get_or_create_commission_type(self, role, category):
        """Get or create commission type for migration"""
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

    # Performance optimization methods
    @api.model
    def search_read_optimized(self, domain=None, search_fields=None, offset=0, limit=None, order=None):
        """Optimized search_read for commission lines with proper indexing"""
        if not domain:
            domain = []

        # Add company domain for multi-company support
        domain += [('company_id', '=', self.env.company.id)]
        
        # Limit default results to prevent URI too long errors
        if limit is None:
            limit = 80
        
        # Define essential fields only to reduce payload
        if search_fields is None:
            search_fields = [
                'id', 'display_name', 'partner_id', 'commission_type_id', 
                'commission_amount', 'state', 'sale_order_id'
            ]

        return super().search_read(domain, search_fields, offset, limit, order)

    @api.model
    def update_payment_status_from_invoices(self):
        """Update commission payment status based on related invoices"""
        _logger.info("Updating commission payment status from invoices...")

        processed_lines = self.search([
            ('state', 'in', ['processed']),
            ('purchase_order_id', '!=', False)
        ])

        updated_count = 0
        for line in processed_lines:
            try:
                # Get total invoiced amount
                total_invoiced = 0
                total_paid = 0

                for invoice in line.invoice_ids:
                    if invoice.state == 'posted':
                        total_invoiced += invoice.amount_total
                        if invoice.payment_state == 'paid':
                            total_paid += invoice.amount_total
                        elif invoice.payment_state == 'partial':
                            # Calculate partial payment amount
                            paid_amount = sum(invoice.payment_ids.filtered(
                                lambda p: p.state == 'posted'
                            ).mapped('amount'))
                            total_paid += paid_amount

                # Update commission line amounts
                if total_invoiced != line.invoice_amount or total_paid != line.paid_amount:
                    line.write({
                        'invoice_amount': total_invoiced,
                        'paid_amount': total_paid,
                    })

                    # Auto-update state to paid if fully paid
                    if line.outstanding_amount <= 0.01 and line.state != 'paid':
                        line.write({
                            'state': 'paid',
                            'payment_date': fields.Date.today()
                        })
                        line.message_post(
                            body=f"Commission automatically marked as paid. Amount: {line.commission_amount} {line.currency_id.name}"
                        )

                    updated_count += 1

            except Exception as e:
                _logger.error(f"Error updating payment status for commission line {line.id}: {str(e)}")
                continue

        _logger.info(f"Updated payment status for {updated_count} commission lines")
        return updated_count

    @api.model
    def _cron_update_payment_status(self):
        """Scheduled action to update payment status"""
        try:
            self.update_payment_status_from_invoices()
        except Exception as e:
            _logger.error(f"Error in commission payment status update cron: {str(e)}")

    def send_overdue_notification(self):
        """Send notification for overdue commission payments"""
        overdue_lines = self.search([
            ('payment_status', '=', 'overdue'),
            ('days_overdue', '>', 7)  # Only notify after 7 days
        ])

        for line in overdue_lines:
            # Create activity for sales manager
            line.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=f'Overdue Commission Payment: {line.partner_id.name}',
                note=f'Commission payment is {line.days_overdue} days overdue.\n'
                     f'Amount: {line.outstanding_amount} {line.currency_id.name}\n'
                     f'Sale Order: {line.sale_order_id.name}',
                user_id=line.sale_order_id.user_id.id or self.env.user.id
            )

        return len(overdue_lines)

    def read(self, fields=None, load='_classic_read'):
        """Override read to handle orphaned Many2one references safely"""
        try:
            return super().read(fields, load)
        except AttributeError as e:
            if "'_unknown' object has no attribute 'id'" in str(e):
                # Handle orphaned references by cleaning them up
                _logger.warning("Found orphaned references in commission lines, cleaning up...")
                self._cleanup_orphaned_records()
                # Try reading again with cleaned data
                return super().read(fields, load)
            else:
                raise