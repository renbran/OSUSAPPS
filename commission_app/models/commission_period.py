# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class CommissionPeriod(models.Model):
    """
    Commission Period Model
    
    Manages commission calculation periods (monthly, quarterly, annual).
    Used to group commission allocations for reporting and payment.
    """
    _name = 'commission.period'
    _description = 'Commission Period'
    _order = 'date_start desc'
    _rec_name = 'name'

    # ================================
    # CORE FIELDS
    # ================================
    
    name = fields.Char(
        string='Period Name',
        required=True,
        help='Name of the commission period'
    )
    
    code = fields.Char(
        string='Code',
        required=True,
        help='Unique code for the period'
    )
    
    # Period type
    period_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
        ('custom', 'Custom Period'),
    ], string='Period Type', default='monthly', required=True)
    
    # Date range
    date_start = fields.Date(
        string='Start Date',
        required=True,
        help='Period start date'
    )
    
    date_end = fields.Date(
        string='End Date',
        required=True,
        help='Period end date'
    )
    
    # State management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('paid', 'Paid'),
    ], string='State', default='draft', tracking=True)
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    description = fields.Text(
        string='Description',
        help='Period description or notes'
    )
    
    # ================================
    # COMPUTED FIELDS
    # ================================
    
    allocation_ids = fields.One2many(
        comodel_name='commission.allocation',
        inverse_name='commission_period_id',
        string='Commission Allocations'
    )
    
    allocation_count = fields.Integer(
        string='Allocation Count',
        compute='_compute_allocation_stats'
    )
    
    total_commission = fields.Monetary(
        string='Total Commission',
        currency_field='currency_id',
        compute='_compute_allocation_stats'
    )
    
    paid_commission = fields.Monetary(
        string='Paid Commission',
        currency_field='currency_id',
        compute='_compute_allocation_stats'
    )
    
    pending_commission = fields.Monetary(
        string='Pending Commission',
        currency_field='currency_id',
        compute='_compute_allocation_stats'
    )
    
    # Progress tracking
    progress_percentage = fields.Float(
        string='Payment Progress (%)',
        compute='_compute_progress'
    )
    
    # ================================
    # COMPANY & CURRENCY
    # ================================
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    
    currency_id = fields.Many2one(
        related='company_id.currency_id',
        string='Currency',
        store=True,
        readonly=True
    )
    
    # ================================
    # COMPUTE METHODS
    # ================================
    
    @api.depends('allocation_ids.commission_amount', 'allocation_ids.state')
    def _compute_allocation_stats(self):
        """Compute allocation statistics."""
        for period in self:
            allocations = period.allocation_ids
            
            period.allocation_count = len(allocations)
            period.total_commission = sum(allocations.mapped('commission_amount'))
            
            # Paid commissions
            paid_allocations = allocations.filtered(lambda a: a.state == 'paid')
            period.paid_commission = sum(paid_allocations.mapped('commission_amount'))
            
            # Pending commissions
            pending_allocations = allocations.filtered(lambda a: a.state != 'paid')
            period.pending_commission = sum(pending_allocations.mapped('commission_amount'))
    
    @api.depends('total_commission', 'paid_commission')
    def _compute_progress(self):
        """Compute payment progress percentage."""
        for period in self:
            if period.total_commission:
                period.progress_percentage = (period.paid_commission / period.total_commission) * 100
            else:
                period.progress_percentage = 0.0
    
    # ================================
    # CONSTRAINT METHODS
    # ================================
    
    @api.constrains('code')
    def _check_code_unique(self):
        """Ensure period code is unique."""
        for period in self:
            if self.search_count([
                ('code', '=', period.code),
                ('id', '!=', period.id),
                ('company_id', '=', period.company_id.id)
            ]):
                raise ValidationError(_('Period code must be unique per company.'))
    
    @api.constrains('date_start', 'date_end')
    def _check_date_range(self):
        """Validate date range."""
        for period in self:
            if period.date_start >= period.date_end:
                raise ValidationError(_('End date must be after start date.'))
    
    @api.constrains('date_start', 'date_end', 'company_id')
    def _check_overlapping_periods(self):
        """Check for overlapping periods."""
        for period in self:
            overlapping = self.search([
                ('id', '!=', period.id),
                ('company_id', '=', period.company_id.id),
                ('date_start', '<=', period.date_end),
                ('date_end', '>=', period.date_start),
            ])
            
            if overlapping:
                raise ValidationError(_(
                    'Period dates overlap with existing period: %s'
                ) % overlapping[0].name)
    
    # ================================
    # ACTION METHODS
    # ================================
    
    def action_open_period(self):
        """Open the commission period."""
        for period in self:
            if period.state != 'draft':
                raise UserError(_('Only draft periods can be opened.'))
            
            period.state = 'open'
    
    def action_close_period(self):
        """Close the commission period."""
        for period in self:
            if period.state != 'open':
                raise UserError(_('Only open periods can be closed.'))
            
            # Calculate all pending allocations in this period
            draft_allocations = period.allocation_ids.filtered(lambda a: a.state == 'draft')
            if draft_allocations:
                draft_allocations.action_calculate()
            
            period.state = 'closed'
    
    def action_mark_paid(self):
        """Mark the period as paid."""
        for period in self:
            if period.state != 'closed':
                raise UserError(_('Only closed periods can be marked as paid.'))
            
            # Check if all allocations are paid
            unpaid_allocations = period.allocation_ids.filtered(lambda a: a.state != 'paid')
            if unpaid_allocations:
                raise UserError(_(
                    'Cannot mark period as paid. %d allocations are still unpaid.'
                ) % len(unpaid_allocations))
            
            period.state = 'paid'
    
    def action_reopen_period(self):
        """Reopen a closed period."""
        for period in self:
            if period.state not in ('closed', 'paid'):
                raise UserError(_('Only closed or paid periods can be reopened.'))
            
            period.state = 'open'
    
    # ================================
    # BUSINESS METHODS
    # ================================
    
    @api.model
    def get_period_for_date(self, date):
        """
        Get commission period for a specific date.
        
        Args:
            date: Date to find period for
            
        Returns:
            commission.period: Period record or False
        """
        if isinstance(date, str):
            date = fields.Date.from_string(date)
        elif isinstance(date, datetime):
            date = date.date()
        
        return self.search([
            ('date_start', '<=', date),
            ('date_end', '>=', date),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
    
    @api.model
    def create_period(self, year, month=None, period_type='monthly'):
        """
        Create a commission period for specified year/month.
        
        Args:
            year (int): Year
            month (int): Month (for monthly periods)
            period_type (str): Type of period
            
        Returns:
            commission.period: Created period record
        """
        if period_type == 'monthly':
            if not month:
                raise UserError(_('Month is required for monthly periods.'))
            
            date_start = datetime(year, month, 1).date()
            date_end = (date_start + relativedelta(months=1) - timedelta(days=1))
            name = date_start.strftime('%B %Y')
            code = date_start.strftime('%Y-%m')
            
        elif period_type == 'quarterly':
            # Determine quarter
            if month:
                quarter = ((month - 1) // 3) + 1
            else:
                quarter = 1  # Default to Q1
            
            start_month = (quarter - 1) * 3 + 1
            date_start = datetime(year, start_month, 1).date()
            date_end = (date_start + relativedelta(months=3) - timedelta(days=1))
            name = f'Q{quarter} {year}'
            code = f'{year}-Q{quarter}'
            
        elif period_type == 'annually':
            date_start = datetime(year, 1, 1).date()
            date_end = datetime(year, 12, 31).date()
            name = f'Year {year}'
            code = str(year)
            
        else:
            raise UserError(_('Unsupported period type: %s') % period_type)
        
        # Check if period already exists
        existing = self.search([
            ('code', '=', code),
            ('company_id', '=', self.env.company.id)
        ])
        
        if existing:
            raise UserError(_('Period %s already exists.') % name)
        
        return self.create({
            'name': name,
            'code': code,
            'period_type': period_type,
            'date_start': date_start,
            'date_end': date_end,
            'state': 'draft'
        })
    
    @api.model
    def auto_create_current_period(self):
        """Auto-create current month period if it doesn't exist."""
        today = fields.Date.today()
        current_period = self.get_period_for_date(today)
        
        if not current_period:
            return self.create_period(today.year, today.month, 'monthly')
        
        return current_period
    
    def calculate_period_commissions(self):
        """Calculate all commissions for this period."""
        self.ensure_one()
        
        # Get all sales orders in this period
        sales = self.env['sale.order'].search([
            ('date_order', '>=', self.date_start),
            ('date_order', '<=', self.date_end),
            ('state', 'in', ['sale', 'done']),
        ])
        
        # Create commission allocations
        allocations_created = 0
        for sale in sales:
            # Skip if allocations already exist
            if sale.commission_allocation_ids:
                continue
            
            # Create allocations
            allocations = self.env['commission.allocation'].create_from_sale_order(sale)
            allocations.write({'commission_period_id': self.id})
            allocations_created += len(allocations)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Commission Calculation Complete'),
                'message': _('%d commission allocations created.') % allocations_created,
                'type': 'success',
            }
        }
    
    # ================================
    # REPORTING METHODS
    # ================================
    
    def get_period_summary(self):
        """Get period summary for reporting."""
        self.ensure_one()
        
        allocations = self.allocation_ids
        
        return {
            'period_name': self.name,
            'date_range': f'{self.date_start} - {self.date_end}',
            'total_allocations': len(allocations),
            'total_commission': self.total_commission,
            'paid_commission': self.paid_commission,
            'pending_commission': self.pending_commission,
            'progress_percentage': self.progress_percentage,
            'by_state': self._get_allocations_by_state(),
            'by_partner': self._get_allocations_by_partner(),
        }
    
    def _get_allocations_by_state(self):
        """Group allocations by state."""
        result = {}
        for state_key, state_label in self.env['commission.allocation']._fields['state'].selection:
            allocations = self.allocation_ids.filtered(lambda a: a.state == state_key)
            result[state_key] = {
                'label': state_label,
                'count': len(allocations),
                'amount': sum(allocations.mapped('commission_amount'))
            }
        return result
    
    def _get_allocations_by_partner(self):
        """Group allocations by partner."""
        result = {}
        for allocation in self.allocation_ids:
            partner = allocation.partner_id
            if partner.id not in result:
                result[partner.id] = {
                    'partner_name': partner.name,
                    'count': 0,
                    'amount': 0.0
                }
            result[partner.id]['count'] += 1
            result[partner.id]['amount'] += allocation.commission_amount
        return result
    
    # ================================
    # VIEW ACTIONS
    # ================================
    
    def action_view_allocations(self):
        """View period allocations."""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commission Allocations - %s') % self.name,
            'res_model': 'commission.allocation',
            'view_mode': 'tree,form',
            'domain': [('commission_period_id', '=', self.id)],
            'context': {'default_commission_period_id': self.id}
        }