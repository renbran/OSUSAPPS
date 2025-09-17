# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class CommissionLine(models.Model):
    """Commission Line Model for managing commission entries integrated with commission_ax"""
    _name = 'commission.line'
    _description = 'Commission Line'
    _order = 'booking_date desc, id desc'
    _rec_name = 'display_name'

    # Core Identification Fields
    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        help='Commission line reference'
    )
    
    display_name = fields.Char(
        string='Display Name', 
        compute='_compute_display_name', 
        store=True,
        help='Display name for the commission line'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Set active to false to hide the commission line without removing it.'
    )
    
    # Partner and Commission Details
    partner_id = fields.Many2one(
        'res.partner',
        string='Commission Partner',
        required=True,
        domain=[('supplier_rank', '>', 0)],
        help='Partner who will receive the commission'
    )
    
    # Sale Order Integration
    sale_order_id = fields.Many2one(
        'sale.order', 
        string='Sale Order', 
        ondelete='cascade',
        help='Related sale order'
    )
    order_ref = fields.Char(
        string='Order Reference', 
        related='sale_order_id.name', 
        store=True,
        help='Sale order reference number'
    )
    customer_reference = fields.Char(
        string='Customer Reference', 
        related='sale_order_id.client_order_ref', 
        store=True,
        help='Customer reference from sale order'
    )
    
    # Purchase Order Integration  
    purchase_order_id = fields.Many2one(
        'purchase.order', 
        string='Purchase Order', 
        ondelete='set null',
        help='Related purchase order for commission payment'
    )
    po_ref = fields.Char(
        string='PO Reference', 
        related='purchase_order_id.name', 
        store=True,
        help='Purchase order reference'
    )
    vendor_reference = fields.Char(
        string='Vendor Reference', 
        related='purchase_order_id.partner_ref', 
        store=True,
        help='Vendor reference in purchase order'
    )
    
    # Commission Categories (from commission_ax analysis)
    commission_category = fields.Selection([
        ('internal', 'Internal Commission'),
        ('external', 'External Commission'), 
        ('legacy', 'Legacy Commission'),
    ], string='Commission Category', required=True, default='internal',
       help='Category of commission based on partner type')
    
    commission_type = fields.Selection([
        ('consultant', 'Consultant'),
        ('manager', 'Manager'),
        ('director', 'Director'),
        ('second_agent', 'Second Agent'),
        ('broker', 'Broker'),
        ('referrer', 'Referrer'),
        ('cashback', 'Cashback'),
        ('agent1', 'Agent 1'),
        ('agent2', 'Agent 2'),
        ('other_external', 'Other External'),
    ], string='Commission Type', required=True,
       help='Type of commission role')
    
    # Financial Fields
    sale_value = fields.Monetary(
        string='Sale Value', 
        currency_field='currency_id',
        help='Total sale value for commission calculation'
    )
    commission_rate = fields.Float(
        string='Commission Rate (%)', 
        digits=(16, 2),
        help='Commission rate percentage'
    )
    commission_amount = fields.Monetary(
        string='Commission Amount', 
        currency_field='currency_id',
        help='Calculated commission amount'
    )
    
    # Date Fields
    booking_date = fields.Date(
        string='Booking Date', 
        required=True, 
        default=fields.Date.context_today,
        help='Date when the sale was booked'
    )
    invoice_date = fields.Date(
        string='Invoice Date', 
        help='Date when the sale order was invoiced'
    )
    commission_date = fields.Date(
        string='Commission Date', 
        default=fields.Date.context_today,
        required=True,
        help='Date when commission was processed'
    )
    
    # Status and Processing
    state = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('approved', 'Approved'),
        ('billed', 'Billed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True,
       help='Current status of the commission line')
    
    # Additional Info
    description = fields.Text(string='Description', help='Commission description')
    notes = fields.Text(string='Notes', help='Additional notes')
    
    # Currency and Company
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    # Computed Fields for Status Tracking
    is_invoiced = fields.Boolean(
        string='Is Invoiced', 
        compute='_compute_invoice_status', 
        store=True,
        help='Whether the related sale order is invoiced'
    )
    commission_processed = fields.Boolean(
        string='Commission Processed', 
        related='sale_order_id.commission_processed', 
        store=True,
        help='Whether commission has been processed in commission_ax'
    )
    
    # Integration Fields
    source_commission_field = fields.Char(
        string='Source Field',
        help='Original field from commission_ax that generated this line'
    )
    
    # Related Partner Fields
    partner_email = fields.Char(
        related='partner_id.email',
        string='Partner Email',
        readonly=True
    )
    
    partner_phone = fields.Char(
        related='partner_id.phone',
        string='Partner Phone',
        readonly=True
    )

    # ============================================================================
    # CONSTRAINT METHODS
    # ============================================================================
    
    @api.constrains('commission_amount')
    def _check_commission_amount(self):
        """Validate commission amount"""
        for record in self:
            if record.commission_amount < 0:
                raise ValidationError(_("Commission amount cannot be negative."))

    @api.constrains('commission_rate')
    def _check_commission_rate(self):
        """Validate commission rate"""
        for record in self:
            if record.commission_rate < 0 or record.commission_rate > 100:
                raise ValidationError(_("Commission rate must be between 0 and 100."))

    # ============================================================================
    # COMPUTE METHODS
    # ============================================================================
    
    @api.depends('partner_id', 'sale_order_id', 'commission_type')
    def _compute_display_name(self):
        """Compute display name for commission line"""
        for record in self:
            if record.partner_id and record.sale_order_id:
                record.display_name = f"{record.partner_id.name} - {record.sale_order_id.name} ({record.commission_type})"
            elif record.partner_id:
                record.display_name = f"{record.partner_id.name} ({record.commission_type})"
            else:
                record.display_name = record.name or _('New')
    
    @api.depends('sale_order_id.invoice_status', 'sale_order_id.invoice_ids')
    def _compute_invoice_status(self):
        """Compute invoice status"""
        for record in self:
            if record.sale_order_id:
                record.is_invoiced = record.sale_order_id.invoice_status == 'invoiced'
            else:
                record.is_invoiced = False

    # ============================================================================
    # CRUD METHODS
    # ============================================================================
    
    @api.model
    def create(self, vals):
        """Override create to generate sequence"""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('commission.line') or _('New')
        return super(CommissionLine, self).create(vals)

    # ============================================================================
    # ACTION METHODS
    # ============================================================================
    
    def action_calculate(self):
        """Calculate commission amount based on sale value and rate"""
        for record in self:
            if record.sale_value and record.commission_rate:
                record.commission_amount = (record.sale_value * record.commission_rate) / 100
                record.state = 'calculated'
            else:
                raise UserError(_("Sale value and commission rate are required for calculation."))
        return True
    
    def action_approve(self):
        """Approve calculated commission"""
        for record in self:
            if record.state != 'calculated':
                raise UserError(_("Only calculated commissions can be approved."))
            record.state = 'approved'
        return True
    
    def action_bill(self):
        """Mark commission as billed (PO created)"""
        for record in self:
            if record.state != 'approved':
                raise UserError(_("Only approved commissions can be billed."))
            record.state = 'billed'
        return True
    
    def action_mark_paid(self):
        """Mark commission as paid"""
        for record in self:
            if record.state != 'billed':
                raise UserError(_("Only billed commissions can be marked as paid."))
            record.state = 'paid'
        return True
    
    def action_cancel(self):
        """Cancel commission line"""
        for record in self:
            record.state = 'cancelled'
        return True
    
    def action_reset_to_draft(self):
        """Reset commission line to draft"""
        for record in self:
            record.state = 'draft'
        return True

    # ============================================================================
    # INTEGRATION METHODS
    # ============================================================================
    
    @api.model
    def create_from_sale_order(self, sale_order, force_create=False):
        """Create commission lines from sale order commission data"""
        if not sale_order:
            return self.env['commission.line']
        
        # Check if SO is invoiced or force_create is True
        if not force_create and not sale_order.is_fully_invoiced:
            raise UserError(_("Sale order must be fully invoiced before generating commission lines."))
        
        commission_lines = self.env['commission.line']
        
        # Get commission entries from commission_ax
        commission_entries = sale_order._get_commission_entries()
        
        for entry in commission_entries:
            # Check if commission line already exists
            existing = self.search([
                ('sale_order_id', '=', sale_order.id),
                ('partner_id', '=', entry['partner'].id),
                ('commission_type', '=', self._map_commission_type(entry['description']))
            ])
            
            if existing:
                continue  # Skip if already exists
            
            # Determine commission category and type
            commission_category, commission_type = self._determine_commission_category(entry, sale_order)
            
            # Create commission line
            vals = {
                'partner_id': entry['partner'].id,
                'sale_order_id': sale_order.id,
                'commission_category': commission_category,
                'commission_type': commission_type,
                'sale_value': sale_order.amount_total,
                'commission_amount': entry['amount'],
                'commission_rate': self._calculate_rate_from_amount(entry['amount'], sale_order.amount_total),
                'booking_date': sale_order.date_order.date() if sale_order.date_order else fields.Date.today(),
                'description': entry['description'],
                'state': 'calculated',
                'source_commission_field': self._get_source_field(entry, sale_order),
            }
            
            commission_line = self.create(vals)
            commission_lines |= commission_line
        
        return commission_lines
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _map_commission_type(self, description):
        """Map commission description to commission type"""
        description_lower = description.lower()
        if 'consultant' in description_lower:
            return 'consultant'
        elif 'manager' in description_lower:
            return 'manager'
        elif 'director' in description_lower:
            return 'director'
        elif 'second agent' in description_lower:
            return 'second_agent'
        elif 'broker' in description_lower:
            return 'broker'
        elif 'referrer' in description_lower:
            return 'referrer'
        elif 'cashback' in description_lower:
            return 'cashback'
        elif 'agent 1' in description_lower:
            return 'agent1'
        elif 'agent 2' in description_lower:
            return 'agent2'
        else:
            return 'other_external'
    
    def _determine_commission_category(self, entry, sale_order):
        """Determine commission category based on partner and type"""
        partner = entry['partner']
        description = entry['description'].lower()
        
        # Legacy commission types
        if any(x in description for x in ['consultant', 'manager', 'director', 'second agent']):
            return 'legacy', self._map_commission_type(description)
        
        # External commission types  
        if any(x in description for x in ['broker', 'referrer', 'cashback', 'other external']):
            return 'external', self._map_commission_type(description)
        
        # Internal commission types
        if any(x in description for x in ['agent 1', 'agent 2']):
            return 'internal', self._map_commission_type(description)
        
        return 'internal', self._map_commission_type(description)
    
    def _calculate_rate_from_amount(self, amount, sale_value):
        """Calculate commission rate percentage from amount and sale value"""
        if sale_value and amount:
            return (amount / sale_value) * 100
        return 0.0
    
    def _get_source_field(self, entry, sale_order):
        """Get the source field name that generated this commission"""
        description = entry['description'].lower()
        field_mapping = {
            'consultant': 'consultant_id',
            'manager': 'manager_id', 
            'director': 'director_id',
            'second agent': 'second_agent_id',
            'broker': 'broker_partner_id',
            'referrer': 'referrer_partner_id',
            'cashback': 'cashback_partner_id',
            'agent 1': 'agent1_partner_id',
            'agent 2': 'agent2_partner_id',
            'other external': 'other_external_partner_id',
        }
        
        for key, field in field_mapping.items():
            if key in description:
                return field
        return 'unknown'