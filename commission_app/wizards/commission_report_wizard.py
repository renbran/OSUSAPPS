# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
import base64
import io
import logging

_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class CommissionReportWizard(models.TransientModel):
    """
    Wizard for generating commission reports including deal reports and category summaries
    """
    _name = 'commission.report.wizard'
    _description = 'Commission Report Wizard'

    # Report type
    report_type = fields.Selection([
        ('deal_report', 'Deal Report with Commission Summary'),
        ('category_summary', 'Commission Summary by Category'),
        ('partner_statement', 'Partner Commission Statement'),
        ('period_analysis', 'Period Analysis Report'),
        ('detailed_listing', 'Detailed Commission Listing')
    ], string='Report Type', required=True, default='deal_report')

    # Date range
    date_from = fields.Date(
        string='From Date',
        required=True,
        default=lambda self: date.today().replace(day=1)
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
        default=fields.Date.today
    )

    # Filters
    partner_ids = fields.Many2many(
        'res.partner',
        'commission_report_partner_rel',
        string='Commission Partners',
        domain=[('is_commission_partner', '=', True)]
    )
    commission_period_ids = fields.Many2many(
        'commission.period',
        string='Commission Periods'
    )
    commission_rule_ids = fields.Many2many(
        'commission.rule',
        string='Commission Rules'
    )
    commission_categories = fields.Selection([
        ('all', 'All Categories'),
        ('legacy', 'Legacy Commission Only'),
        ('external', 'External Commission Only'),
        ('internal', 'Internal Commission Only'),
        ('management', 'Management Commission Only'),
        ('bonus', 'Bonus Commission Only'),
        ('referral', 'Referral Commission Only'),
        ('sales', 'Sales Commission Only')
    ], string='Commission Categories', default='all')

    state_filter = fields.Selection([
        ('all', 'All States'),
        ('draft', 'Draft Only'),
        ('calculated', 'Calculated Only'),
        ('confirmed', 'Confirmed Only'),
        ('processed', 'Processed Only'),
        ('paid', 'Paid Only'),
        ('unpaid', 'Unpaid (Draft to Processed)')
    ], string='State Filter', default='all')

    # Output options
    output_format = fields.Selection([
        ('pdf', 'PDF Report'),
        ('xlsx', 'Excel Spreadsheet'),
        ('csv', 'CSV File')
    ], string='Output Format', default='xlsx')

    group_by_partner = fields.Boolean(
        string='Group by Partner',
        default=True
    )
    group_by_category = fields.Boolean(
        string='Group by Category',
        default=True
    )
    group_by_period = fields.Boolean(
        string='Group by Period',
        default=False
    )

    include_totals = fields.Boolean(
        string='Include Totals',
        default=True
    )
    include_details = fields.Boolean(
        string='Include Allocation Details',
        default=True
    )

    # Generated report
    report_file = fields.Binary(
        string='Generated Report',
        readonly=True
    )
    report_filename = fields.Char(
        string='Filename',
        readonly=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )

    def action_generate_report(self):
        """Generate the selected commission report"""
        self.ensure_one()
        
        # Validate inputs
        if self.date_from > self.date_to:
            raise ValidationError(_("From Date cannot be later than To Date"))

        try:
            # Generate report based on type
            if self.report_type == 'deal_report':
                return self._generate_deal_report()
            elif self.report_type == 'category_summary':
                return self._generate_category_summary()
            elif self.report_type == 'partner_statement':
                return self._generate_partner_statement()
            elif self.report_type == 'period_analysis':
                return self._generate_period_analysis()
            elif self.report_type == 'detailed_listing':
                return self._generate_detailed_listing()
            else:
                raise ValidationError(_("Invalid report type selected"))

        except Exception as e:
            _logger.error("Error generating commission report: %s", str(e))
            raise ValidationError(_("Error generating report: %s") % str(e))

    def _generate_deal_report(self):
        """Generate deal report with commission summary for all categories"""
        data = self._get_report_data()
        
        if self.output_format == 'xlsx':
            return self._create_deal_report_xlsx(data)
        elif self.output_format == 'pdf':
            return self._create_deal_report_pdf(data)
        else:
            return self._create_deal_report_csv(data)

    def _generate_category_summary(self):
        """Generate commission summary by category"""
        data = self._get_category_summary_data()
        
        if self.output_format == 'xlsx':
            return self._create_category_summary_xlsx(data)
        else:
            return self._create_category_summary_csv(data)

    def _generate_partner_statement(self):
        """Generate partner commission statement"""
        data = self._get_partner_statement_data()
        
        if self.output_format == 'xlsx':
            return self._create_partner_statement_xlsx(data)
        else:
            return self._create_partner_statement_csv(data)

    def _generate_period_analysis(self):
        """Generate period analysis report"""
        data = self._get_period_analysis_data()
        
        if self.output_format == 'xlsx':
            return self._create_period_analysis_xlsx(data)
        else:
            return self._create_period_analysis_csv(data)

    def _generate_detailed_listing(self):
        """Generate detailed commission listing"""
        data = self._get_detailed_listing_data()
        
        if self.output_format == 'xlsx':
            return self._create_detailed_listing_xlsx(data)
        else:
            return self._create_detailed_listing_csv(data)

    def _get_report_data(self):
        """Get data for deal report"""
        # Base domain for allocations
        domain = self._build_base_domain()
        
        # Get allocations with related data
        allocations = self.env['commission.allocation'].search(domain)
        
        # Group data by sale order
        deals = {}
        for allocation in allocations:
            order_id = allocation.sale_order_id.id
            if order_id not in deals:
                deals[order_id] = {
                    'sale_order': allocation.sale_order_id,
                    'customer': allocation.customer_id,
                    'salesperson': allocation.salesperson_id,
                    'total_amount': allocation.sale_amount_total,
                    'date': allocation.sale_date,
                    'commissions': {
                        'legacy': [],
                        'external': [],
                        'internal': [],
                        'management': [],
                        'bonus': [],
                        'referral': [],
                        'sales': []
                    },
                    'totals': {
                        'legacy': 0.0,
                        'external': 0.0,
                        'internal': 0.0,
                        'management': 0.0,
                        'bonus': 0.0,
                        'referral': 0.0,
                        'sales': 0.0,
                        'total': 0.0
                    }
                }
            
            # Add commission to appropriate category
            category = allocation.commission_rule_id.commission_category
            deals[order_id]['commissions'][category].append(allocation)
            deals[order_id]['totals'][category] += allocation.commission_amount
            deals[order_id]['totals']['total'] += allocation.commission_amount

        return deals

    def _get_category_summary_data(self):
        """Get data for category summary report"""
        domain = self._build_base_domain()
        allocations = self.env['commission.allocation'].search(domain)
        
        # Group by category
        summary = {
            'legacy': {'count': 0, 'amount': 0.0, 'allocations': []},
            'external': {'count': 0, 'amount': 0.0, 'allocations': []},
            'internal': {'count': 0, 'amount': 0.0, 'allocations': []},
            'management': {'count': 0, 'amount': 0.0, 'allocations': []},
            'bonus': {'count': 0, 'amount': 0.0, 'allocations': []},
            'referral': {'count': 0, 'amount': 0.0, 'allocations': []},
            'sales': {'count': 0, 'amount': 0.0, 'allocations': []}
        }
        
        for allocation in allocations:
            category = allocation.commission_rule_id.commission_category
            summary[category]['count'] += 1
            summary[category]['amount'] += allocation.commission_amount
            summary[category]['allocations'].append(allocation)
        
        return summary

    def _build_base_domain(self):
        """Build base domain for filtering allocations"""
        domain = []
        
        # Date filter - using sale_date for deal reports
        if self.report_type == 'deal_report':
            domain.extend([
                ('sale_date', '>=', self.date_from),
                ('sale_date', '<=', self.date_to)
            ])
        
        # Partner filter
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))
        
        # Period filter
        if self.commission_period_ids:
            domain.append(('commission_period_id', 'in', self.commission_period_ids.ids))
        
        # Rule filter
        if self.commission_rule_ids:
            domain.append(('commission_rule_id', 'in', self.commission_rule_ids.ids))
        
        # Category filter
        if self.commission_categories != 'all':
            domain.append(('commission_rule_id.commission_category', '=', self.commission_categories))
        
        # State filter
        if self.state_filter == 'unpaid':
            domain.append(('state', 'in', ['draft', 'calculated', 'confirmed', 'processed']))
        elif self.state_filter != 'all':
            domain.append(('state', '=', self.state_filter))
        
        return domain

    def _create_deal_report_xlsx(self, deals_data):
        """Create Excel deal report"""
        if not xlsxwriter:
            raise ValidationError(_("xlsxwriter library is required for Excel export"))
        
        # Create workbook
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Add formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })
        money_format = workbook.add_format({'num_format': '#,##0.00'})
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        
        # Create worksheet
        worksheet = workbook.add_worksheet('Deal Report')
        worksheet.set_column('A:A', 15)  # Order
        worksheet.set_column('B:B', 25)  # Customer
        worksheet.set_column('C:C', 20)  # Salesperson
        worksheet.set_column('D:D', 12)  # Date
        worksheet.set_column('E:E', 15)  # Total Amount
        worksheet.set_column('F:L', 12)  # Commission categories
        
        # Headers
        headers = [
            'Sale Order', 'Customer', 'Salesperson', 'Sale Date', 'Total Amount',
            'Legacy Comm.', 'External Comm.', 'Internal Comm.', 'Management Comm.',
            'Bonus Comm.', 'Referral Comm.', 'Sales Comm.', 'Total Commission'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Data rows
        row = 1
        grand_total_amount = 0.0
        grand_total_commission = 0.0
        
        for deal_data in deals_data.values():
            worksheet.write(row, 0, deal_data['sale_order'].name)
            worksheet.write(row, 1, deal_data['customer'].name if deal_data['customer'] else '')
            worksheet.write(row, 2, deal_data['salesperson'].name if deal_data['salesperson'] else '')
            worksheet.write(row, 3, deal_data['date'], date_format)
            worksheet.write(row, 4, deal_data['total_amount'], money_format)
            
            # Commission categories
            worksheet.write(row, 5, deal_data['totals']['legacy'], money_format)
            worksheet.write(row, 6, deal_data['totals']['external'], money_format)
            worksheet.write(row, 7, deal_data['totals']['internal'], money_format)
            worksheet.write(row, 8, deal_data['totals']['management'], money_format)
            worksheet.write(row, 9, deal_data['totals']['bonus'], money_format)
            worksheet.write(row, 10, deal_data['totals']['referral'], money_format)
            worksheet.write(row, 11, deal_data['totals']['sales'], money_format)
            worksheet.write(row, 12, deal_data['totals']['total'], money_format)
            
            grand_total_amount += deal_data['total_amount']
            grand_total_commission += deal_data['totals']['total']
            row += 1
        
        # Totals row
        if self.include_totals:
            worksheet.write(row, 0, 'TOTAL', header_format)
            worksheet.write(row, 4, grand_total_amount, money_format)
            worksheet.write(row, 12, grand_total_commission, money_format)
        
        workbook.close()
        output.seek(0)
        
        # Save file
        filename = f"deal_report_{self.date_from}_{self.date_to}.xlsx"
        self.write({
            'report_file': base64.b64encode(output.getvalue()),
            'report_filename': filename
        })
        
        return self._download_report()

    def _download_report(self):
        """Return action to download generated report"""
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/commission.report.wizard/%s/report_file/%s?download=true' % (
                self.id, self.report_filename
            ),
            'target': 'self',
        }

    # Additional helper methods would continue here for other report types...
    
    def _get_partner_statement_data(self):
        """Get data for partner statement"""
        domain = self._build_base_domain()
        allocations = self.env['commission.allocation'].search(domain)
        
        # Group by partner
        statements = {}
        for allocation in allocations:
            partner = allocation.partner_id
            if partner not in statements:
                statements[partner] = {
                    'partner': partner,
                    'allocations': [],
                    'total_amount': 0.0,
                    'by_category': {
                        'legacy': 0.0, 'external': 0.0, 'internal': 0.0,
                        'management': 0.0, 'bonus': 0.0, 'referral': 0.0, 'sales': 0.0
                    },
                    'by_state': {
                        'draft': 0.0, 'calculated': 0.0, 'confirmed': 0.0,
                        'processed': 0.0, 'paid': 0.0
                    }
                }
            
            statements[partner]['allocations'].append(allocation)
            statements[partner]['total_amount'] += allocation.commission_amount
            
            # By category
            category = allocation.commission_rule_id.commission_category
            statements[partner]['by_category'][category] += allocation.commission_amount
            
            # By state
            statements[partner]['by_state'][allocation.state] += allocation.commission_amount
        
        return statements

    def _get_period_analysis_data(self):
        """Get data for period analysis"""
        # This would analyze commission trends over periods
        pass

    def _get_detailed_listing_data(self):
        """Get data for detailed listing"""
        domain = self._build_base_domain()
        return self.env['commission.allocation'].search(domain, order='sale_date desc, partner_id')

    # Additional methods for creating other report formats would be implemented here...