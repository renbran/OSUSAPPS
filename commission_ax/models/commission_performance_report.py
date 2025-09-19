# -*- coding: utf-8 -*-
"""
Commission Performance Report
============================

World-class commission performance reporting system:
- Advanced analytics and KPIs
- Comparative performance analysis
- Trend analysis and forecasting
- Executive dashboards
- Performance benchmarking
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
from datetime import datetime, timedelta
from collections import defaultdict

_logger = logging.getLogger(__name__)


class CommissionPerformanceReport(models.TransientModel):
    """Commission Performance Analysis and Reporting"""
    _name = 'commission.performance.report'
    _description = 'Commission Performance Report'

    # Report configuration
    name = fields.Char(string='Report Name', default='Commission Performance Report')
    report_type = fields.Selection([
        ('summary', 'Executive Summary'),
        ('detailed', 'Detailed Analysis'),
        ('comparative', 'Comparative Analysis'),
        ('trend', 'Trend Analysis'),
        ('partner', 'Partner Performance'),
        ('team', 'Team Performance'),
    ], string='Report Type', default='summary', required=True)

    # Date filters
    date_from = fields.Date(string='Date From', required=True, default=fields.Date.today().replace(day=1))
    date_to = fields.Date(string='Date To', required=True, default=fields.Date.today())
    comparison_period = fields.Selection([
        ('previous_month', 'Previous Month'),
        ('previous_quarter', 'Previous Quarter'),
        ('previous_year', 'Previous Year'),
        ('same_period_last_year', 'Same Period Last Year'),
    ], string='Comparison Period', default='previous_month')

    # Filters
    partner_ids = fields.Many2many('res.partner', string='Commission Partners',
                                   domain=[('supplier_rank', '>', 0)])
    commission_type_ids = fields.Many2many('commission.type', string='Commission Types')
    team_ids = fields.Many2many('crm.team', string='Sales Teams')
    company_ids = fields.Many2many('res.company', string='Companies',
                                   default=lambda self: self.env.company)

    # Report options
    include_draft = fields.Boolean(string='Include Draft Commissions', default=False)
    include_cancelled = fields.Boolean(string='Include Cancelled Commissions', default=False)
    group_by = fields.Selection([
        ('partner', 'By Partner'),
        ('type', 'By Commission Type'),
        ('team', 'By Sales Team'),
        ('month', 'By Month'),
        ('quarter', 'By Quarter'),
    ], string='Group By', default='partner')

    # Output options
    output_format = fields.Selection([
        ('pdf', 'PDF Report'),
        ('excel', 'Excel Spreadsheet'),
        ('dashboard', 'Interactive Dashboard'),
    ], string='Output Format', default='dashboard')

    # Computed metrics (readonly fields for display)
    total_commission_amount = fields.Float(string='Total Commission Amount', readonly=True)
    total_orders = fields.Integer(string='Total Orders', readonly=True)
    average_commission = fields.Float(string='Average Commission', readonly=True)
    top_performer = fields.Char(string='Top Performer', readonly=True)
    growth_rate = fields.Float(string='Growth Rate %', readonly=True)

    def action_generate_report(self):
        """Generate the commission performance report"""
        self.ensure_one()

        try:
            # Calculate metrics
            self._calculate_metrics()

            if self.output_format == 'dashboard':
                return self._generate_dashboard()
            elif self.output_format == 'excel':
                return self._generate_excel_report()
            else:  # PDF
                return self._generate_pdf_report()

        except Exception as e:
            _logger.error(f"Error generating commission performance report: {str(e)}")
            raise UserError(_("Failed to generate report: %s") % str(e))

    def _calculate_metrics(self):
        """Calculate performance metrics"""
        # Build domain for commission lines
        domain = [
            ('sale_order_id.date_order', '>=', self.date_from),
            ('sale_order_id.date_order', '<=', self.date_to),
        ]

        if not self.include_draft:
            domain.append(('state', '!=', 'draft'))
        if not self.include_cancelled:
            domain.append(('state', '!=', 'cancelled'))
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))
        if self.commission_type_ids:
            domain.append(('commission_type_id', 'in', self.commission_type_ids.ids))
        if self.company_ids:
            domain.append(('company_id', 'in', self.company_ids.ids))

        # Get commission lines
        commission_lines = self.env['commission.line'].search(domain)

        # Calculate basic metrics
        self.total_commission_amount = sum(commission_lines.mapped('amount'))
        self.total_orders = len(commission_lines.mapped('sale_order_id'))
        self.average_commission = self.total_commission_amount / len(commission_lines) if commission_lines else 0.0

        # Find top performer
        if commission_lines:
            partner_amounts = defaultdict(float)
            for line in commission_lines:
                partner_amounts[line.partner_id.name] += line.amount
            self.top_performer = max(partner_amounts.items(), key=lambda x: x[1])[0] if partner_amounts else ''

        # Calculate growth rate
        self.growth_rate = self._calculate_growth_rate(commission_lines)

    def _calculate_growth_rate(self, current_lines):
        """Calculate growth rate compared to previous period"""
        if not current_lines:
            return 0.0

        # Get comparison period dates
        comp_date_from, comp_date_to = self._get_comparison_period_dates()

        # Build domain for comparison period
        comp_domain = [
            ('sale_order_id.date_order', '>=', comp_date_from),
            ('sale_order_id.date_order', '<=', comp_date_to),
            ('state', '!=', 'draft'),
        ]

        if self.partner_ids:
            comp_domain.append(('partner_id', 'in', self.partner_ids.ids))
        if self.commission_type_ids:
            comp_domain.append(('commission_type_id', 'in', self.commission_type_ids.ids))
        if self.company_ids:
            comp_domain.append(('company_id', 'in', self.company_ids.ids))

        comp_lines = self.env['commission.line'].search(comp_domain)
        comp_amount = sum(comp_lines.mapped('amount'))

        if comp_amount > 0:
            return ((self.total_commission_amount - comp_amount) / comp_amount) * 100
        else:
            return 100.0 if self.total_commission_amount > 0 else 0.0

    def _get_comparison_period_dates(self):
        """Get date range for comparison period"""
        if self.comparison_period == 'previous_month':
            first_day = self.date_from.replace(day=1)
            last_month = first_day - timedelta(days=1)
            comp_date_from = last_month.replace(day=1)
            comp_date_to = last_month
        elif self.comparison_period == 'previous_quarter':
            # Calculate previous quarter
            quarter = ((self.date_from.month - 1) // 3) + 1
            if quarter == 1:
                prev_quarter = 4
                prev_year = self.date_from.year - 1
            else:
                prev_quarter = quarter - 1
                prev_year = self.date_from.year

            comp_date_from = datetime(prev_year, (prev_quarter - 1) * 3 + 1, 1).date()
            comp_date_to = datetime(prev_year, prev_quarter * 3, 1).date()
        elif self.comparison_period == 'previous_year':
            comp_date_from = self.date_from.replace(year=self.date_from.year - 1)
            comp_date_to = self.date_to.replace(year=self.date_to.year - 1)
        else:  # same_period_last_year
            comp_date_from = self.date_from.replace(year=self.date_from.year - 1)
            comp_date_to = self.date_to.replace(year=self.date_to.year - 1)

        return comp_date_from, comp_date_to

    def _generate_dashboard(self):
        """Generate interactive dashboard view"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Commission Performance Dashboard',
            'res_model': 'commission.performance.report',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
            'context': {'dashboard_mode': True}
        }

    def _generate_excel_report(self):
        """Generate Excel report"""
        try:
            import xlsxwriter
            import base64
            from io import BytesIO

            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)

            # Create worksheets
            summary_sheet = workbook.add_worksheet('Summary')
            details_sheet = workbook.add_worksheet('Details')

            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4F81BD',
                'font_color': 'white',
                'border': 1
            })

            currency_format = workbook.add_format({'num_format': '#,##0.00'})
            percent_format = workbook.add_format({'num_format': '0.00%'})

            # Write summary data
            self._write_excel_summary(summary_sheet, header_format, currency_format, percent_format)

            # Write detailed data
            self._write_excel_details(details_sheet, header_format, currency_format)

            workbook.close()
            output.seek(0)

            # Create attachment
            attachment = self.env['ir.attachment'].create({
                'name': f'Commission_Performance_Report_{fields.Date.today()}.xlsx',
                'type': 'binary',
                'datas': base64.b64encode(output.read()),
                'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            })

            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'self',
            }

        except ImportError:
            raise UserError(_("Excel export requires xlsxwriter library. Please install it."))
        except Exception as e:
            _logger.error(f"Error generating Excel report: {str(e)}")
            raise UserError(_("Failed to generate Excel report: %s") % str(e))

    def _write_excel_summary(self, sheet, header_format, currency_format, percent_format):
        """Write summary data to Excel sheet"""
        # Headers
        sheet.write('A1', 'Metric', header_format)
        sheet.write('B1', 'Value', header_format)

        # Data
        row = 1
        metrics = [
            ('Total Commission Amount', self.total_commission_amount, currency_format),
            ('Total Orders', self.total_orders, None),
            ('Average Commission', self.average_commission, currency_format),
            ('Top Performer', self.top_performer, None),
            ('Growth Rate', self.growth_rate / 100, percent_format),
        ]

        for metric, value, format_obj in metrics:
            sheet.write(row, 0, metric)
            if format_obj:
                sheet.write(row, 1, value, format_obj)
            else:
                sheet.write(row, 1, value)
            row += 1

        # Auto-adjust column widths
        sheet.set_column('A:A', 25)
        sheet.set_column('B:B', 20)

    def _write_excel_details(self, sheet, header_format, currency_format):
        """Write detailed data to Excel sheet"""
        # Get commission lines for details
        domain = [
            ('sale_order_id.date_order', '>=', self.date_from),
            ('sale_order_id.date_order', '<=', self.date_to),
        ]

        if not self.include_draft:
            domain.append(('state', '!=', 'draft'))
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))

        commission_lines = self.env['commission.line'].search(domain)

        # Headers
        headers = ['Partner', 'Sale Order', 'Commission Type', 'Amount', 'State', 'Date']
        for col, header in enumerate(headers):
            sheet.write(0, col, header, header_format)

        # Data
        for row, line in enumerate(commission_lines, 1):
            sheet.write(row, 0, line.partner_id.name)
            sheet.write(row, 1, line.sale_order_id.name)
            sheet.write(row, 2, line.commission_type_id.name)
            sheet.write(row, 3, line.amount, currency_format)
            sheet.write(row, 4, dict(line._fields['state'].selection)[line.state])
            sheet.write(row, 5, line.sale_order_id.date_order.strftime('%Y-%m-%d'))

        # Auto-adjust column widths
        for col in range(len(headers)):
            sheet.set_column(col, col, 15)

    def _generate_pdf_report(self):
        """Generate PDF report"""
        return self.env.ref('commission_ax.commission_performance_report_pdf').report_action(self)

    @api.model
    def get_dashboard_data(self, date_from=None, date_to=None):
        """Get dashboard data for API calls"""
        if not date_from:
            date_from = fields.Date.today().replace(day=1)
        if not date_to:
            date_to = fields.Date.today()

        # Create temporary report record
        report = self.create({
            'date_from': date_from,
            'date_to': date_to,
        })

        report._calculate_metrics()

        return {
            'total_commission_amount': report.total_commission_amount,
            'total_orders': report.total_orders,
            'average_commission': report.average_commission,
            'top_performer': report.top_performer,
            'growth_rate': report.growth_rate,
        }