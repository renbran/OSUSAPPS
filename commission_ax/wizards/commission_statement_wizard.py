# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class CommissionStatementWizard(models.TransientModel):
    """Commission Statement Report Wizard"""
    _name = 'commission.statement.wizard'
    _description = 'Commission Statement Report Wizard'

    # Partner Selection
    partner_id = fields.Many2one(
        'res.partner', 
        string='Commission Partner', 
        required=True,
        domain=[('supplier_rank', '>', 0)],
        help='Partner for whom to generate the commission statement'
    )
    
    # Date Range
    date_from = fields.Date(
        string='Date From', 
        required=True,
        default=lambda self: fields.Date.today().replace(day=1),
        help='Start date for commission statement'
    )
    
    date_to = fields.Date(
        string='Date To', 
        required=True,
        default=fields.Date.today,
        help='End date for commission statement'
    )
    
    # Filter Options
    commission_category = fields.Selection([
        ('all', 'All Categories'),
        ('internal', 'Internal Commission'),
        ('external', 'External Commission'), 
        ('legacy', 'Legacy Commission'),
    ], string='Commission Category', default='all',
       help='Filter by commission category')
    
    state_filter = fields.Selection([
        ('all', 'All Status'),
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('approved', 'Approved'),
        ('billed', 'Billed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Status Filter', default='all',
       help='Filter by commission status')
    
    # Report Options
    report_format = fields.Selection([
        ('pdf', 'PDF Report'),
        ('xlsx', 'Excel Export'),
    ], string='Report Format', default='pdf',
       help='Format for the commission statement')
    
    include_cancelled = fields.Boolean(
        string='Include Cancelled',
        default=False,
        help='Include cancelled commission lines in the report'
    )
    
    # Summary Fields (computed)
    commission_line_count = fields.Integer(
        string='Commission Lines Count',
        compute='_compute_commission_summary',
        help='Number of commission lines found'
    )
    
    total_commission_amount = fields.Monetary(
        string='Total Commission Amount',
        compute='_compute_commission_summary',
        currency_field='currency_id',
        help='Total commission amount for the period'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    # ============================================================================
    # COMPUTE METHODS
    # ============================================================================
    
    @api.depends('partner_id', 'date_from', 'date_to', 'commission_category', 'state_filter')
    def _compute_commission_summary(self):
        """Compute commission summary"""
        for wizard in self:
            domain = wizard._get_commission_lines_domain()
            commission_lines = self.env['commission.line'].search(domain)
            
            wizard.commission_line_count = len(commission_lines)
            wizard.total_commission_amount = sum(commission_lines.mapped('commission_amount'))

    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _get_commission_lines_domain(self):
        """Get domain for commission lines based on wizard filters"""
        domain = [
            ('partner_id', '=', self.partner_id.id),
            ('date_commission', '>=', self.date_from),
            ('date_commission', '<=', self.date_to),
        ]
        
        if self.commission_category != 'all':
            domain.append(('commission_category', '=', self.commission_category))
        
        if self.state_filter != 'all':
            domain.append(('state', '=', self.state_filter))
        
        if not self.include_cancelled:
            domain.append(('state', '!=', 'cancelled'))
        
        return domain
    
    def _get_commission_lines_data(self):
        """Get commission lines data for the report"""
        domain = self._get_commission_lines_domain()
        commission_lines = self.env['commission.line'].search(domain, order='date_commission desc, id desc')
        
        data = []
        for line in commission_lines:
            data.append({
                'booking_date': line.date_commission,
                'order_ref': line.sale_order_id.name or '',
                'customer_reference': line.sale_order_id.client_order_ref or '',
                'sale_value': line.base_amount,
                'commission_rate': line.rate,
                'commission_amount': line.commission_amount,
                'state': line.state,
                'commission_type': line.commission_type_id.name or '',
                'commission_category': line.commission_category,
                'po_ref': line.purchase_order_id.name or '',
                'vendor_reference': line.purchase_order_id.partner_ref or '',
            })
        
        return data

    # ============================================================================
    # ACTION METHODS
    # ============================================================================
    
    def action_generate_report(self):
        """Generate commission statement report"""
        self.ensure_one()
        
        if not self.partner_id:
            raise UserError(_("Please select a commission partner."))
        
        if self.date_from > self.date_to:
            raise UserError(_("Date From cannot be later than Date To."))
        
        # Check if there are commission lines
        domain = self._get_commission_lines_domain()
        commission_lines = self.env['commission.line'].search(domain)
        
        if not commission_lines:
            raise UserError(_("No commission lines found for the selected criteria."))
        
        # Generate report based on format
        if self.report_format == 'pdf':
            return self._generate_pdf_report()
        elif self.report_format == 'xlsx':
            return self._generate_xlsx_report()
    
    def _generate_pdf_report(self):
        """Generate PDF commission statement report"""
        return self.env.ref('commission_lines.action_commission_statement_report').report_action(self)
    
    def _generate_xlsx_report(self):
        """Generate Excel commission statement report"""
        # Check if xlsxwriter is available
        try:
            import xlsxwriter
        except ImportError:
            raise UserError(_("Excel export requires xlsxwriter. Please install: pip install xlsxwriter"))
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/commission_lines/statement/excel?wizard_id={self.id}',
            'target': 'new',
        }
    
    def action_preview_lines(self):
        """Preview commission lines before generating report"""
        self.ensure_one()
        
        domain = self._get_commission_lines_domain()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commission Lines Preview'),
            'res_model': 'commission.line',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {
                'create': False,
                'edit': False,
                'delete': False,
            },
            'target': 'new',
        }   