from odoo import models, fields, api, tools
from odoo.exceptions import UserError
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class CommissionDashboard(models.Model):
    """Commission Dashboard for unified monitoring and analytics"""
    _name = 'commission.dashboard'
    _description = 'Commission Dashboard'
    _auto = False  # This is a view-based model for analytics

    # Date fields
    date = fields.Date(string='Date', readonly=True)
    month = fields.Selection([
        ('01', 'January'), ('02', 'February'), ('03', 'March'),
        ('04', 'April'), ('05', 'May'), ('06', 'June'),
        ('07', 'July'), ('08', 'August'), ('09', 'September'),
        ('10', 'October'), ('11', 'November'), ('12', 'December')
    ], string='Month', readonly=True)
    year = fields.Char(string='Year', readonly=True)

    # Sale Order fields
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=True)
    order_amount = fields.Monetary(string='Order Amount', readonly=True)
    customer_id = fields.Many2one('res.partner', string='Customer', readonly=True)

    # Commission fields
    commission_line_id = fields.Many2one('commission.line', string='Commission Line', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Commission Partner', readonly=True)
    commission_type_id = fields.Many2one('commission.type', string='Commission Type', readonly=True)
    commission_amount = fields.Monetary(string='Commission Amount', readonly=True)
    commission_category = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External'),
        ('management', 'Management'),
        ('bonus', 'Bonus'),
    ], string='Category', readonly=True)

    # Status fields
    commission_state = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('confirmed', 'Confirmed'),
        ('processed', 'Processed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], string='Commission Status', readonly=True)

    order_state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Order Status', readonly=True)

    # Performance fields
    days_to_process = fields.Integer(string='Days to Process', readonly=True)
    is_overdue = fields.Boolean(string='Overdue', readonly=True)

    # Company and currency
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)

    def init(self):
        """Create the view for commission dashboard"""
        tools.drop_view_if_exists(self.env.cr, self._table)

        try:
            # Create a simple placeholder view that works during installation
            self.env.cr.execute("""
                CREATE VIEW %s AS (
                    SELECT
                        1 AS id,
                        CURRENT_DATE AS date,
                        TO_CHAR(CURRENT_DATE, 'MM') AS month,
                        TO_CHAR(CURRENT_DATE, 'YYYY') AS year,
                        1 AS sale_order_id,
                        0.0 AS order_amount,
                        1 AS customer_id,
                        1 AS commission_line_id,
                        1 AS partner_id,
                        1 AS commission_type_id,
                        0.0 AS commission_amount,
                        'internal' AS commission_category,
                        'draft' AS commission_state,
                        'draft' AS order_state,
                        0 AS days_to_process,
                        FALSE AS is_overdue,
                        1 AS company_id,
                        1 AS currency_id
                    WHERE FALSE
                )
            """ % self._table)
            _logger.info("Commission dashboard placeholder view created successfully")
            
        except Exception as e:
            _logger.error(f"Error creating commission dashboard view: {e}")
            raise

    @api.model
    def get_commission_summary(self, domain=None, period='month'):
        """Get commission summary for dashboard"""
        if not domain:
            domain = []

        # Add company filter
        domain += [('company_id', '=', self.env.company.id)]

        # Add date filter based on period
        today = fields.Date.today()
        if period == 'week':
            start_date = today - timedelta(days=7)
        elif period == 'month':
            start_date = today.replace(day=1)
        elif period == 'quarter':
            quarter_start = today.replace(month=(today.month-1)//3*3+1, day=1)
            start_date = quarter_start
        elif period == 'year':
            start_date = today.replace(month=1, day=1)
        else:
            start_date = today - timedelta(days=30)

        domain += [('date', '>=', start_date)]

        records = self.search(domain)

        # Calculate summary data
        summary = {
            'total_orders': len(set(records.mapped('sale_order_id.id'))),
            'total_commission_amount': sum(records.mapped('commission_amount')),
            'internal_commission': sum(records.filtered(lambda r: r.commission_category == 'internal').mapped('commission_amount')),
            'external_commission': sum(records.filtered(lambda r: r.commission_category == 'external').mapped('commission_amount')),
            'draft_count': len(records.filtered(lambda r: r.commission_state == 'draft')),
            'processed_count': len(records.filtered(lambda r: r.commission_state == 'processed')),
            'overdue_count': len(records.filtered(lambda r: r.is_overdue)),
            'average_processing_time': 0,
        }

        # Calculate average processing time
        processed_records = records.filtered(lambda r: r.days_to_process is not False)
        if processed_records:
            summary['average_processing_time'] = sum(processed_records.mapped('days_to_process')) / len(processed_records)

        return summary

    @api.model
    def get_commission_trends(self, months=12):
        """Get commission trends for the last N months"""
        end_date = fields.Date.today()
        start_date = end_date - timedelta(days=months * 30)

        domain = [
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('company_id', '=', self.env.company.id)
        ]

        # Read grouped data by month/year
        grouped_data = self.read_group(
            domain,
            ['commission_amount:sum', 'date'],
            ['month', 'year'],
            orderby='year DESC, month DESC'
        )

        trends = []
        for data in grouped_data:
            trends.append({
                'month': data['month'],
                'year': data['year'],
                'total_amount': data['commission_amount'],
                'count': data['__count']
            })

        return trends

    @api.model
    def get_top_performers(self, limit=10, period='month'):
        """Get top commission performers"""
        today = fields.Date.today()
        start_date = today.replace(day=1) if period == 'month' else today - timedelta(days=30)

        domain = [
            ('date', '>=', start_date),
            ('company_id', '=', self.env.company.id),
            ('commission_state', 'in', ['processed', 'paid'])
        ]

        # Group by partner
        grouped_data = self.read_group(
            domain,
            ['commission_amount:sum', 'partner_id'],
            ['partner_id'],
            limit=limit,
            orderby='commission_amount DESC'
        )

        performers = []
        for data in grouped_data:
            partner = self.env['res.partner'].browse(data['partner_id'][0])
            performers.append({
                'partner_id': partner.id,
                'partner_name': partner.name,
                'total_commission': data['commission_amount'],
                'commission_count': data['__count']
            })

        return performers

    @api.model
    def get_pending_commissions(self):
        """Get pending commissions that need attention"""
        domain = [
            ('commission_state', 'in', ['draft', 'calculated']),
            ('company_id', '=', self.env.company.id),
            ('is_overdue', '=', True)
        ]

        pending = self.search(domain, limit=50)

        return [{
            'sale_order': record.sale_order_id.name,
            'customer': record.customer_id.name,
            'partner': record.partner_id.name,
            'amount': record.commission_amount,
            'days_pending': (fields.Date.today() - record.date).days,
            'state': record.commission_state,
        } for record in pending]

    def action_view_commission_line(self):
        """Action to view commission line details"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Commission Line Details',
            'res_model': 'commission.line',
            'res_id': self.commission_line_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_sale_order(self):
        """Action to view related sale order"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order Details',
            'res_model': 'sale.order',
            'res_id': self.sale_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


class CommissionPerformanceReport(models.TransientModel):
    """Commission Performance Analysis Wizard"""
    _name = 'commission.performance.report'
    _description = 'Commission Performance Report'

    date_from = fields.Date(string='Date From', required=True, default=fields.Date.today().replace(day=1))
    date_to = fields.Date(string='Date To', required=True, default=fields.Date.today())
    partner_ids = fields.Many2many('res.partner', string='Commission Partners')
    commission_category = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External'),
        ('management', 'Management'),
        ('bonus', 'Bonus'),
    ], string='Commission Category')
    group_by = fields.Selection([
        ('partner', 'By Partner'),
        ('month', 'By Month'),
        ('category', 'By Category'),
        ('commission_type', 'By Commission Type'),
    ], string='Group By', default='partner')

    def generate_report(self):
        """Generate performance report"""
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('company_id', '=', self.env.company.id)
        ]

        if self.partner_ids:
            domain += [('partner_id', 'in', self.partner_ids.ids)]

        if self.commission_category:
            domain += [('commission_category', '=', self.commission_category)]

        # Get dashboard data
        dashboard_records = self.env['commission.dashboard'].search(domain)

        # Group data based on selection
        if self.group_by == 'partner':
            grouped_data = dashboard_records.read_group(
                [],
                ['commission_amount:sum', 'partner_id'],
                ['partner_id']
            )
        elif self.group_by == 'month':
            grouped_data = dashboard_records.read_group(
                [],
                ['commission_amount:sum'],
                ['month', 'year']
            )
        elif self.group_by == 'category':
            grouped_data = dashboard_records.read_group(
                [],
                ['commission_amount:sum'],
                ['commission_category']
            )
        else:  # commission_type
            grouped_data = dashboard_records.read_group(
                [],
                ['commission_amount:sum'],
                ['commission_type_id']
            )

        # Return action to display results
        return {
            'type': 'ir.actions.act_window',
            'name': f'Commission Performance Report - {self.group_by.replace("_", " ").title()}',
            'res_model': 'commission.dashboard',
            'view_mode': 'graph,pivot,list',
            'domain': domain,
            'context': {
                'search_default_group_by_' + self.group_by: 1,
            }
        }


class CommissionAlert(models.Model):
    """Commission Alert System for monitoring and notifications"""
    _name = 'commission.alert'
    _description = 'Commission Alert'
    _order = 'create_date DESC'

    name = fields.Char(string='Alert Title', required=True)
    description = fields.Text(string='Description')
    alert_type = fields.Selection([
        ('overdue', 'Overdue Commission'),
        ('high_amount', 'High Commission Amount'),
        ('threshold', 'Threshold Exceeded'),
        ('error', 'Processing Error'),
    ], string='Alert Type', required=True)

    sale_order_id = fields.Many2one('sale.order', string='Related Sale Order')
    commission_line_id = fields.Many2one('commission.line', string='Related Commission Line')
    partner_id = fields.Many2one('res.partner', string='Commission Partner')

    amount = fields.Monetary(string='Amount')
    currency_id = fields.Many2one('res.currency', string='Currency')

    state = fields.Selection([
        ('new', 'New'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ], string='Status', default='new')

    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], string='Priority', default='medium')

    assigned_to = fields.Many2one('res.users', string='Assigned To')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def action_acknowledge(self):
        """Acknowledge the alert"""
        self.state = 'acknowledged'
        self.assigned_to = self.env.user

    def action_resolve(self):
        """Mark alert as resolved"""
        self.state = 'resolved'

    def action_dismiss(self):
        """Dismiss the alert"""
        self.state = 'dismissed'

    @api.model
    def create_overdue_alerts(self):
        """Create alerts for overdue commissions"""
        overdue_threshold = fields.Date.today() - timedelta(days=30)

        overdue_commissions = self.env['commission.line'].search([
            ('state', 'in', ['draft', 'calculated']),
            ('date_commission', '<', overdue_threshold),
            ('sale_order_id.state', 'in', ['sale', 'done'])
        ])

        for commission in overdue_commissions:
            # Check if alert already exists
            existing_alert = self.search([
                ('commission_line_id', '=', commission.id),
                ('alert_type', '=', 'overdue'),
                ('state', 'in', ['new', 'acknowledged'])
            ])

            if not existing_alert:
                self.create({
                    'name': f'Overdue Commission: {commission.sale_order_id.name}',
                    'description': f'Commission for {commission.partner_id.name} is overdue by {(fields.Date.today() - commission.date_commission).days} days',
                    'alert_type': 'overdue',
                    'sale_order_id': commission.sale_order_id.id,
                    'commission_line_id': commission.id,
                    'partner_id': commission.partner_id.id,
                    'amount': commission.commission_amount,
                    'currency_id': commission.currency_id.id,
                    'priority': 'high',
                })

    @api.model
    def _cron_create_alerts(self):
        """Scheduled action to create commission alerts"""
        try:
            self.create_overdue_alerts()
            _logger.info("Commission alerts created successfully")
        except Exception as e:
            _logger.error(f"Error creating commission alerts: {str(e)}")