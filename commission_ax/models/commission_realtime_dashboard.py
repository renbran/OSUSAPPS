# -*- coding: utf-8 -*-
"""
Real-Time Commission Performance Dashboard
=========================================

Enterprise-grade real-time monitoring dashboard providing:
- Live commission metrics and KPIs
- Real-time alerts and notifications
- Interactive analytics with drill-down capabilities
- Performance benchmarking and targets
- Executive summary reporting
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import json
from datetime import datetime, timedelta
from collections import defaultdict

_logger = logging.getLogger(__name__)


class CommissionRealtimeDashboard(models.TransientModel):
    """Real-Time Commission Performance Dashboard"""
    _name = 'commission.realtime.dashboard'
    _description = 'Real-Time Commission Dashboard'

    # Dashboard configuration
    dashboard_name = fields.Char(string='Dashboard Name', default='Commission Performance Dashboard')
    refresh_interval = fields.Selection([
        ('30', '30 seconds'),
        ('60', '1 minute'),
        ('300', '5 minutes'),
        ('900', '15 minutes'),
        ('1800', '30 minutes'),
    ], string='Refresh Interval', default='300')

    # Date filters
    date_from = fields.Date(string='Date From', default=fields.Date.today().replace(day=1))
    date_to = fields.Date(string='Date To', default=fields.Date.today())
    comparison_period = fields.Selection([
        ('previous_month', 'Previous Month'),
        ('previous_quarter', 'Previous Quarter'),
        ('previous_year', 'Previous Year'),
        ('same_period_last_year', 'Same Period Last Year'),
    ], string='Comparison Period', default='previous_month')

    # Filters
    partner_ids = fields.Many2many('res.partner', string='Commission Partners')
    commission_category = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External'),
        ('management', 'Management'),
        ('bonus', 'Bonus'),
    ], string='Commission Category')

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    # Real-time metrics (computed)
    total_commission_today = fields.Monetary(string='Commission Today', compute='_compute_realtime_metrics')
    total_commission_mtd = fields.Monetary(string='Commission MTD', compute='_compute_realtime_metrics')
    total_commission_ytd = fields.Monetary(string='Commission YTD', compute='_compute_realtime_metrics')

    pending_commissions = fields.Integer(string='Pending Commissions', compute='_compute_realtime_metrics')
    overdue_commissions = fields.Integer(string='Overdue Commissions', compute='_compute_realtime_metrics')
    processed_today = fields.Integer(string='Processed Today', compute='_compute_realtime_metrics')

    avg_processing_time = fields.Float(string='Avg Processing Time (days)', compute='_compute_realtime_metrics')
    top_performer_today = fields.Char(string='Top Performer Today', compute='_compute_realtime_metrics')

    # Performance indicators
    commission_growth_rate = fields.Float(string='Growth Rate (%)', compute='_compute_performance_indicators')
    processing_efficiency = fields.Float(string='Processing Efficiency (%)', compute='_compute_performance_indicators')
    payment_completion_rate = fields.Float(string='Payment Completion Rate (%)', compute='_compute_performance_indicators')

    # Alert counts
    critical_alerts = fields.Integer(string='Critical Alerts', compute='_compute_alert_metrics')
    high_alerts = fields.Integer(string='High Priority Alerts', compute='_compute_alert_metrics')
    medium_alerts = fields.Integer(string='Medium Priority Alerts', compute='_compute_alert_metrics')

    @api.depends('date_from', 'date_to', 'partner_ids', 'commission_category')
    def _compute_realtime_metrics(self):
        """Compute real-time commission metrics"""
        for dashboard in self:
            today = fields.Date.today()

            # Base domain
            base_domain = [
                ('company_id', '=', dashboard.company_id.id),
                ('state', 'not in', ['cancelled'])
            ]

            if dashboard.partner_ids:
                base_domain += [('partner_id', 'in', dashboard.partner_ids.ids)]
            if dashboard.commission_category:
                base_domain += [('commission_category', '=', dashboard.commission_category)]

            commission_lines = self.env['commission.line']

            # Today's commission
            today_domain = base_domain + [('date_commission', '=', today)]
            today_lines = commission_lines.search(today_domain)
            dashboard.total_commission_today = sum(today_lines.mapped('commission_amount'))

            # Month-to-date
            mtd_domain = base_domain + [
                ('date_commission', '>=', today.replace(day=1)),
                ('date_commission', '<=', today)
            ]
            mtd_lines = commission_lines.search(mtd_domain)
            dashboard.total_commission_mtd = sum(mtd_lines.mapped('commission_amount'))

            # Year-to-date
            ytd_domain = base_domain + [
                ('date_commission', '>=', today.replace(month=1, day=1)),
                ('date_commission', '<=', today)
            ]
            ytd_lines = commission_lines.search(ytd_domain)
            dashboard.total_commission_ytd = sum(ytd_lines.mapped('commission_amount'))

            # Status counts
            dashboard.pending_commissions = commission_lines.search_count(
                base_domain + [('state', 'in', ['draft', 'calculated'])]
            )

            dashboard.overdue_commissions = commission_lines.search_count(
                base_domain + [('payment_status', '=', 'overdue')]
            )

            dashboard.processed_today = commission_lines.search_count(
                base_domain + [
                    ('state', '=', 'processed'),
                    ('write_date', '>=', datetime.combine(today, datetime.min.time()))
                ]
            )

            # Average processing time
            processed_lines = commission_lines.search(
                base_domain + [('state', 'in', ['processed', 'paid'])]
            )
            if processed_lines:
                processing_times = []
                for line in processed_lines:
                    if line.date_commission and line.write_date:
                        days = (line.write_date.date() - line.date_commission).days
                        processing_times.append(max(0, days))

                dashboard.avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            else:
                dashboard.avg_processing_time = 0

            # Top performer today
            if today_lines:
                partner_totals = defaultdict(float)
                for line in today_lines:
                    partner_totals[line.partner_id.name] += line.commission_amount

                if partner_totals:
                    top_partner = max(partner_totals.items(), key=lambda x: x[1])
                    dashboard.top_performer_today = f"{top_partner[0]} ({top_partner[1]:,.2f})"
                else:
                    dashboard.top_performer_today = "No data"
            else:
                dashboard.top_performer_today = "No commissions today"

    @api.depends('date_from', 'date_to', 'comparison_period')
    def _compute_performance_indicators(self):
        """Compute performance indicators with comparisons"""
        for dashboard in self:
            # Current period data
            current_data = dashboard._get_period_data(dashboard.date_from, dashboard.date_to)

            # Comparison period data
            comp_from, comp_to = dashboard._get_comparison_dates()
            comparison_data = dashboard._get_period_data(comp_from, comp_to)

            # Growth rate calculation
            if comparison_data['total_amount'] > 0:
                dashboard.commission_growth_rate = (
                    (current_data['total_amount'] - comparison_data['total_amount']) /
                    comparison_data['total_amount'] * 100
                )
            else:
                dashboard.commission_growth_rate = 0

            # Processing efficiency (processed vs total)
            total_commissions = current_data['total_count']
            processed_commissions = current_data['processed_count']

            dashboard.processing_efficiency = (
                (processed_commissions / total_commissions * 100) if total_commissions > 0 else 0
            )

            # Payment completion rate
            paid_commissions = current_data['paid_count']
            dashboard.payment_completion_rate = (
                (paid_commissions / total_commissions * 100) if total_commissions > 0 else 0
            )

    def _compute_alert_metrics(self):
        """Compute alert metrics"""
        for dashboard in self:
            alerts = self.env['commission.alert'].search([
                ('company_id', '=', dashboard.company_id.id),
                ('state', 'in', ['new', 'acknowledged'])
            ])

            dashboard.critical_alerts = len(alerts.filtered(lambda a: a.priority == 'critical'))
            dashboard.high_alerts = len(alerts.filtered(lambda a: a.priority == 'high'))
            dashboard.medium_alerts = len(alerts.filtered(lambda a: a.priority == 'medium'))

    def _get_period_data(self, date_from, date_to):
        """Get commission data for a specific period"""
        domain = [
            ('date_commission', '>=', date_from),
            ('date_commission', '<=', date_to),
            ('company_id', '=', self.company_id.id),
        ]

        if self.partner_ids:
            domain += [('partner_id', 'in', self.partner_ids.ids)]
        if self.commission_category:
            domain += [('commission_category', '=', self.commission_category)]

        lines = self.env['commission.line'].search(domain)

        return {
            'total_amount': sum(lines.mapped('commission_amount')),
            'total_count': len(lines),
            'processed_count': len(lines.filtered(lambda l: l.state in ['processed', 'paid'])),
            'paid_count': len(lines.filtered(lambda l: l.state == 'paid')),
        }

    def _get_comparison_dates(self):
        """Get comparison period dates"""
        if self.comparison_period == 'previous_month':
            # Previous month
            first_day = self.date_from.replace(day=1)
            last_month = first_day - timedelta(days=1)
            comp_from = last_month.replace(day=1)
            comp_to = last_month

        elif self.comparison_period == 'previous_quarter':
            # Previous quarter
            current_quarter = (self.date_from.month - 1) // 3 + 1
            if current_quarter == 1:
                prev_quarter_start = self.date_from.replace(year=self.date_from.year - 1, month=10, day=1)
                comp_to = self.date_from.replace(year=self.date_from.year - 1, month=12, day=31)
            else:
                prev_quarter_month = (current_quarter - 2) * 3 + 1
                prev_quarter_start = self.date_from.replace(month=prev_quarter_month, day=1)
                comp_to = self.date_from.replace(month=prev_quarter_month + 2, day=1) - timedelta(days=1)
            comp_from = prev_quarter_start

        elif self.comparison_period == 'previous_year':
            # Previous year same period
            comp_from = self.date_from.replace(year=self.date_from.year - 1)
            comp_to = self.date_to.replace(year=self.date_to.year - 1)

        else:  # same_period_last_year
            # Same period last year
            comp_from = self.date_from.replace(year=self.date_from.year - 1)
            comp_to = self.date_to.replace(year=self.date_to.year - 1)

        return comp_from, comp_to

    @api.model
    def get_dashboard_data(self, dashboard_id=None):
        """Get comprehensive dashboard data for frontend"""
        if dashboard_id:
            dashboard = self.browse(dashboard_id)
        else:
            dashboard = self.create({})

        # Force computation of all computed fields
        dashboard._compute_realtime_metrics()
        dashboard._compute_performance_indicators()
        dashboard._compute_alert_metrics()

        # Get detailed analytics
        charts_data = dashboard._get_charts_data()
        kpi_data = dashboard._get_kpi_data()
        alerts_data = dashboard._get_alerts_data()

        return {
            'dashboard_info': {
                'name': dashboard.dashboard_name,
                'refresh_interval': int(dashboard.refresh_interval),
                'last_updated': fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            },
            'kpis': kpi_data,
            'charts': charts_data,
            'alerts': alerts_data,
            'filters': {
                'date_from': dashboard.date_from.strftime('%Y-%m-%d'),
                'date_to': dashboard.date_to.strftime('%Y-%m-%d'),
                'partner_ids': dashboard.partner_ids.ids,
                'commission_category': dashboard.commission_category,
            }
        }

    def _get_kpi_data(self):
        """Get KPI data for dashboard"""
        return {
            'commission_today': {
                'value': self.total_commission_today,
                'currency': self.currency_id.symbol,
                'trend': 'up' if self.commission_growth_rate > 0 else 'down',
                'change': f"{self.commission_growth_rate:+.1f}%"
            },
            'commission_mtd': {
                'value': self.total_commission_mtd,
                'currency': self.currency_id.symbol,
            },
            'commission_ytd': {
                'value': self.total_commission_ytd,
                'currency': self.currency_id.symbol,
            },
            'pending_count': {
                'value': self.pending_commissions,
                'status': 'warning' if self.pending_commissions > 10 else 'success'
            },
            'overdue_count': {
                'value': self.overdue_commissions,
                'status': 'danger' if self.overdue_commissions > 0 else 'success'
            },
            'processing_efficiency': {
                'value': f"{self.processing_efficiency:.1f}%",
                'status': 'success' if self.processing_efficiency > 90 else 'warning' if self.processing_efficiency > 70 else 'danger'
            },
            'payment_completion': {
                'value': f"{self.payment_completion_rate:.1f}%",
                'status': 'success' if self.payment_completion_rate > 95 else 'warning' if self.payment_completion_rate > 80 else 'danger'
            },
            'avg_processing_time': {
                'value': f"{self.avg_processing_time:.1f} days",
                'status': 'success' if self.avg_processing_time < 3 else 'warning' if self.avg_processing_time < 7 else 'danger'
            }
        }

    def _get_charts_data(self):
        """Get chart data for dashboard"""
        # Monthly trend chart
        monthly_trend = self._get_monthly_trend_data()

        # Commission category distribution
        category_distribution = self._get_category_distribution()

        # Top performers chart
        top_performers = self._get_top_performers_data()

        # Payment status distribution
        payment_status = self._get_payment_status_distribution()

        return {
            'monthly_trend': {
                'type': 'line',
                'title': 'Monthly Commission Trend',
                'data': monthly_trend,
                'options': {
                    'responsive': True,
                    'scales': {
                        'y': {'beginAtZero': True}
                    }
                }
            },
            'category_distribution': {
                'type': 'doughnut',
                'title': 'Commission by Category',
                'data': category_distribution,
                'options': {
                    'responsive': True,
                    'plugins': {
                        'legend': {'position': 'bottom'}
                    }
                }
            },
            'top_performers': {
                'type': 'bar',
                'title': 'Top Performers (Current Period)',
                'data': top_performers,
                'options': {
                    'responsive': True,
                    'indexAxis': 'y'
                }
            },
            'payment_status': {
                'type': 'pie',
                'title': 'Payment Status Distribution',
                'data': payment_status,
                'options': {
                    'responsive': True,
                    'plugins': {
                        'legend': {'position': 'right'}
                    }
                }
            }
        }

    def _get_monthly_trend_data(self):
        """Get monthly trend chart data"""
        # Get last 12 months of data
        end_date = fields.Date.today()
        start_date = end_date.replace(month=1) if end_date.month == 12 else end_date.replace(year=end_date.year - 1, month=end_date.month + 1)

        monthly_data = defaultdict(float)

        domain = [
            ('date_commission', '>=', start_date),
            ('date_commission', '<=', end_date),
            ('company_id', '=', self.company_id.id),
            ('state', 'not in', ['cancelled'])
        ]

        lines = self.env['commission.line'].search(domain)

        for line in lines:
            month_key = line.date_commission.strftime('%Y-%m')
            monthly_data[month_key] += line.commission_amount

        # Prepare chart data
        months = sorted(monthly_data.keys())
        labels = [datetime.strptime(month, '%Y-%m').strftime('%b %Y') for month in months]
        values = [monthly_data[month] for month in months]

        return {
            'labels': labels,
            'datasets': [{
                'label': 'Commission Amount',
                'data': values,
                'borderColor': 'rgb(75, 192, 192)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'tension': 0.4
            }]
        }

    def _get_category_distribution(self):
        """Get commission category distribution"""
        domain = [
            ('date_commission', '>=', self.date_from),
            ('date_commission', '<=', self.date_to),
            ('company_id', '=', self.company_id.id),
            ('state', 'not in', ['cancelled'])
        ]

        lines = self.env['commission.line'].search(domain)

        category_totals = defaultdict(float)
        for line in lines:
            category_totals[line.commission_category or 'other'] += line.commission_amount

        labels = list(category_totals.keys())
        values = list(category_totals.values())
        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']

        return {
            'labels': [label.title() for label in labels],
            'datasets': [{
                'data': values,
                'backgroundColor': colors[:len(labels)],
                'borderWidth': 2
            }]
        }

    def _get_top_performers_data(self):
        """Get top performers chart data"""
        domain = [
            ('date_commission', '>=', self.date_from),
            ('date_commission', '<=', self.date_to),
            ('company_id', '=', self.company_id.id),
            ('state', 'not in', ['cancelled'])
        ]

        lines = self.env['commission.line'].search(domain)

        partner_totals = defaultdict(float)
        for line in lines:
            partner_totals[line.partner_id.name] += line.commission_amount

        # Get top 10 performers
        top_partners = sorted(partner_totals.items(), key=lambda x: x[1], reverse=True)[:10]

        labels = [partner[0] for partner in top_partners]
        values = [partner[1] for partner in top_partners]

        return {
            'labels': labels,
            'datasets': [{
                'label': 'Commission Amount',
                'data': values,
                'backgroundColor': 'rgba(54, 162, 235, 0.8)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 1
            }]
        }

    def _get_payment_status_distribution(self):
        """Get payment status distribution"""
        domain = [
            ('date_commission', '>=', self.date_from),
            ('date_commission', '<=', self.date_to),
            ('company_id', '=', self.company_id.id),
            ('state', 'not in', ['cancelled'])
        ]

        lines = self.env['commission.line'].search(domain)

        status_counts = defaultdict(int)
        for line in lines:
            status_counts[line.payment_status or 'pending'] += 1

        labels = [status.replace('_', ' ').title() for status in status_counts.keys()]
        values = list(status_counts.values())
        colors = {
            'pending': '#FFA500',
            'partial': '#FFFF00',
            'paid': '#00FF00',
            'overdue': '#FF0000',
            'cancelled': '#808080'
        }

        background_colors = [colors.get(status, '#CCCCCC') for status in status_counts.keys()]

        return {
            'labels': labels,
            'datasets': [{
                'data': values,
                'backgroundColor': background_colors,
                'borderWidth': 2
            }]
        }

    def _get_alerts_data(self):
        """Get alerts data for dashboard"""
        alerts = self.env['commission.alert'].search([
            ('company_id', '=', self.company_id.id),
            ('state', 'in', ['new', 'acknowledged'])
        ], limit=10, order='priority DESC, create_date DESC')

        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'title': alert.name,
                'description': alert.description,
                'type': alert.alert_type,
                'priority': alert.priority,
                'state': alert.state,
                'created': alert.create_date.strftime('%Y-%m-%d %H:%M'),
                'amount': alert.amount if alert.amount else 0,
            })

        return alerts_data

    def action_refresh_dashboard(self):
        """Refresh dashboard data"""
        # Force recomputation of all fields
        self._compute_realtime_metrics()
        self._compute_performance_indicators()
        self._compute_alert_metrics()

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_drill_down_commissions(self, filter_type, filter_value=None):
        """Drill down into commission details"""
        domain = [
            ('company_id', '=', self.company_id.id),
            ('date_commission', '>=', self.date_from),
            ('date_commission', '<=', self.date_to),
        ]

        if filter_type == 'pending':
            domain += [('state', 'in', ['draft', 'calculated'])]
        elif filter_type == 'overdue':
            domain += [('payment_status', '=', 'overdue')]
        elif filter_type == 'category' and filter_value:
            domain += [('commission_category', '=', filter_value)]
        elif filter_type == 'partner' and filter_value:
            domain += [('partner_id', '=', filter_value)]

        return {
            'type': 'ir.actions.act_window',
            'name': f'Commission Lines - {filter_type.title()}',
            'res_model': 'commission.line',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {'create': False},
        }

    @api.model
    def create_dashboard_shortcut(self, name, config):
        """Create dashboard shortcut for quick access"""
        shortcut = self.create({
            'dashboard_name': name,
            **config
        })

        return {
            'type': 'ir.actions.act_window',
            'name': name,
            'res_model': 'commission.realtime.dashboard',
            'res_id': shortcut.id,
            'view_mode': 'form',
            'target': 'main',
        }