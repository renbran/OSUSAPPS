from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
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
    ], string='Calculation Method', required=True, default='percentage_total')

    rate = fields.Float(
        string='Rate/Amount',
        digits=(16, 6),
        help='Commission rate as percentage or fixed amount'
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

    # Payment tracking
    invoice_amount = fields.Monetary(
        string='Invoiced Amount',
        currency_field='currency_id',
        help='Amount invoiced for this commission'
    )

    paid_amount = fields.Monetary(
        string='Paid Amount',
        currency_field='currency_id',
        help='Amount paid for this commission'
    )

    outstanding_amount = fields.Monetary(
        string='Outstanding Amount',
        compute='_compute_payment_amounts',
        store=True,
        currency_field='currency_id',
        help='Outstanding commission amount'
    )

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

    @api.depends('sale_order_id.amount_total', 'sale_order_id.amount_untaxed',
                 'rate', 'calculation_method', 'sale_order_id.order_line.price_unit')
    def _compute_amounts(self):
        """Optimized commission amount calculation"""
        for line in self:
            if not line.sale_order_id:
                line.base_amount = 0.0
                line.commission_amount = 0.0
                line.commission_amount_company_currency = 0.0
                continue

            order = line.sale_order_id

            # Determine base amount
            if line.calculation_method == 'fixed':
                line.base_amount = 1.0  # Fixed amount doesn't need base
                line.commission_amount = line.rate
            elif line.calculation_method == 'percentage_unit':
                if order.order_line:
                    line.base_amount = order.order_line[0].price_unit
                    line.commission_amount = (line.rate / 100.0) * line.base_amount
                else:
                    line.base_amount = 0.0
                    line.commission_amount = 0.0
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

    @api.depends('commission_amount', 'invoice_amount', 'paid_amount')
    def _compute_payment_amounts(self):
        """Compute payment-related amounts"""
        for line in self:
            line.outstanding_amount = line.commission_amount - line.paid_amount

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

    @api.onchange('commission_type_id')
    def _onchange_commission_type(self):
        """Auto-fill fields from commission type"""
        if self.commission_type_id:
            self.calculation_method = self.commission_type_id.calculation_method or 'percentage_total'
            self.rate = self.commission_type_id.default_rate or 0.0
            self.commission_category = self.commission_type_id.commission_category or 'internal'

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
        for line in self.filtered(lambda l: l.state == 'confirmed'):
            if not line.purchase_order_id:
                line._create_purchase_order()
            line.state = 'processed'
        return True

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
            product = self.env['product.product'].create({
                'name': 'Commission Payment',
                'type': 'service',
                'categ_id': self.env.ref('product.product_category_all').id,
                'list_price': 0.0,
                'standard_price': 0.0,
                'sale_ok': False,
                'purchase_ok': True,
            })

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
                        'state': 'calculated' if order.commission_processed else 'draft',
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

        return super(CommissionLine, self).search_read(domain, search_fields, offset, limit, order)

    def read(self, fields=None, load='_classic_read'):
        """Override read to handle orphaned Many2one references safely"""
        try:
            return super(CommissionLine, self).read(fields, load)
        except AttributeError as e:
            if "'_unknown' object has no attribute 'id'" in str(e):
                # Handle orphaned references by cleaning them up
                _logger.warning("Found orphaned references in commission lines, cleaning up...")
                self._cleanup_orphaned_records()
                # Try reading again with cleaned data
                return super(CommissionLine, self).read(fields, load)
            else:
                raise