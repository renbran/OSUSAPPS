# -*- coding: utf-8 -*-
import base64
import io
import xlsxwriter
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class ScholarixCommissionReportWizard(models.TransientModel):
    """Wizard for generating consolidated SCHOLARIX commission reports"""
    _name = 'scholarix.commission.report.wizard'
    _description = 'SCHOLARIX Commission Report Wizard'

    # Period selection
    period_start = fields.Date(
        string='Period Start',
        required=True,
        default=lambda self: date.today().replace(day=1),
        help='Start date for commission period'
    )
    period_end = fields.Date(
        string='Period End',
        required=True,
        default=lambda self: (date.today().replace(day=1) + relativedelta(months=1) - timedelta(days=1)),
        help='End date for commission period'
    )
    
    # Quick period selection
    period_type = fields.Selection([
        ('custom', 'Custom Period'),
        ('current_month', 'Current Month'),
        ('last_month', 'Last Month'),
        ('current_quarter', 'Current Quarter'),
        ('last_quarter', 'Last Quarter'),
        ('current_year', 'Current Year'),
        ('last_year', 'Last Year'),
    ], string='Period Type', default='last_month')
    
    # Agent selection
    agent_selection = fields.Selection([
        ('all', 'All Agents'),
        ('specific', 'Specific Agents'),
        ('with_commission', 'Agents with Commission Only'),
    ], string='Agent Selection', default='with_commission', required=True)
    
    agent_ids = fields.Many2many(
        'res.partner',
        string='Select Agents',
        domain=[('is_company', '=', False)],
        help='Select specific agents to include in report'
    )
    
    # Filtering options
    commission_type_filter = fields.Selection([
        ('all', 'All Commission Types'),
        ('direct_sales', 'Direct Sales Only'),
        ('referral', 'Referral Bonus Only'),
        ('team_override', 'Team Override Only'),
    ], string='Commission Type Filter', default='all')
    
    payment_status_filter = fields.Selection([
        ('all', 'All Payment Status'),
        ('pending', 'Pending Only'),
        ('paid', 'Paid Only'),
        ('cancelled', 'Cancelled Only'),
    ], string='Payment Status Filter', default='all')
    
    min_commission_amount = fields.Monetary(
        string='Minimum Commission Amount',
        default=0.0,
        help='Only include agents with commission above this amount'
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id.id
    )
    
    # Sorting and grouping
    sort_by = fields.Selection([
        ('agent_name', 'Agent Name'),
        ('commission_desc', 'Commission Amount (High to Low)'),
        ('commission_asc', 'Commission Amount (Low to High)'),
        ('sales_desc', 'Sales Volume (High to Low)'),
        ('payment_status', 'Payment Status'),
    ], string='Sort By', default='agent_name')
    
    group_by = fields.Selection([
        ('none', 'No Grouping'),
        ('payment_status', 'Payment Status'),
        ('commission_type', 'Commission Type'),
        ('sales_team', 'Sales Team'),
    ], string='Group By', default='none')
    
    # Report options
    report_format = fields.Selection([
        ('pdf', 'PDF Report'),
        ('excel', 'Excel Spreadsheet'),
        ('both', 'PDF and Excel'),
    ], string='Report Format', default='pdf', required=True)
    
    include_details = fields.Boolean(
        string='Include Order Details',
        default=True,
        help='Include individual order details for each agent'
    )
    include_summary = fields.Boolean(
        string='Include Executive Summary',
        default=True,
        help='Include executive summary section'
    )
    
    # Company branding
    company_logo = fields.Binary(
        related='company_id.logo',
        string='Company Logo'
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company
    )
    
    @api.onchange('period_type')
    def _onchange_period_type(self):
        """Update period dates based on selection"""
        today = date.today()
        
        if self.period_type == 'current_month':
            self.period_start = today.replace(day=1)
            self.period_end = (today.replace(day=1) + relativedelta(months=1) - timedelta(days=1))
        elif self.period_type == 'last_month':
            first_day_last_month = (today.replace(day=1) - relativedelta(months=1))
            self.period_start = first_day_last_month
            self.period_end = (today.replace(day=1) - timedelta(days=1))
        elif self.period_type == 'current_quarter':
            quarter_start = today.replace(month=((today.month - 1) // 3) * 3 + 1, day=1)
            self.period_start = quarter_start
            self.period_end = (quarter_start + relativedelta(months=3) - timedelta(days=1))
        elif self.period_type == 'last_quarter':
            current_quarter_start = today.replace(month=((today.month - 1) // 3) * 3 + 1, day=1)
            last_quarter_start = current_quarter_start - relativedelta(months=3)
            self.period_start = last_quarter_start
            self.period_end = (current_quarter_start - timedelta(days=1))
        elif self.period_type == 'current_year':
            self.period_start = today.replace(month=1, day=1)
            self.period_end = today.replace(month=12, day=31)
        elif self.period_type == 'last_year':
            last_year = today.year - 1
            self.period_start = date(last_year, 1, 1)
            self.period_end = date(last_year, 12, 31)
    
    @api.onchange('agent_selection')
    def _onchange_agent_selection(self):
        """Clear agent selection when changing selection type"""
        if self.agent_selection != 'specific':
            self.agent_ids = [(5, 0, 0)]
    
    @api.constrains('period_start', 'period_end')
    def _check_period_dates(self):
        """Validate period dates"""
        if self.period_start and self.period_end:
            if self.period_start > self.period_end:
                raise ValidationError(_("Period start date must be before end date."))
    
    def action_generate_report(self):
        """Generate the commission report based on wizard settings"""
        self.ensure_one()
        
        # Determine agent IDs based on selection
        if self.agent_selection == 'specific':
            if not self.agent_ids:
                raise UserError(_("Please select at least one agent."))
            agent_ids = self.agent_ids.ids
        else:
            agent_ids = None
        
        # Generate consolidated report data
        Commission = self.env['scholarix.commission.statement']
        report_data = Commission.generate_consolidated_report(
            self.period_start,
            self.period_end,
            agent_ids
        )
        
        # Apply filters and sorting
        statements = self._filter_and_sort_statements(report_data['statements'])
        report_data['statements'] = statements
        report_data['filtered_count'] = len(statements)
        
        # Store wizard data for report access
        report_data.update({
            'wizard_id': self.id,
            'period_start': self.period_start,
            'period_end': self.period_end,
            'report_format': self.report_format,
            'include_details': self.include_details,
            'include_summary': self.include_summary,
            'sort_by': self.sort_by,
            'group_by': self.group_by,
        })
        
        # Generate report based on format selection
        if self.report_format == 'pdf':
            return self._generate_pdf_report(report_data)
        elif self.report_format == 'excel':
            return self._generate_excel_report(report_data)
        elif self.report_format == 'both':
            # Generate both and return PDF with Excel as attachment
            return self._generate_combined_report(report_data)
    
    def _filter_and_sort_statements(self, statements):
        """Apply filters and sorting to statements"""
        filtered_statements = statements
        
        # Apply commission type filter
        if self.commission_type_filter != 'all':
            filtered_statements = [s for s in filtered_statements if self._matches_commission_type(s)]
        
        # Apply payment status filter
        if self.payment_status_filter != 'all':
            filtered_statements = [s for s in filtered_statements if s.payment_status == self.payment_status_filter]
        
        # Apply minimum commission filter
        if self.min_commission_amount > 0:
            filtered_statements = [s for s in filtered_statements if s.gross_commission >= self.min_commission_amount]
        
        # Apply agent selection filter
        if self.agent_selection == 'with_commission':
            filtered_statements = [s for s in filtered_statements if s.gross_commission > 0]
        
        # Sort statements
        if self.sort_by == 'agent_name':
            filtered_statements.sort(key=lambda s: s.agent_id.name)
        elif self.sort_by == 'commission_desc':
            filtered_statements.sort(key=lambda s: s.gross_commission, reverse=True)
        elif self.sort_by == 'commission_asc':
            filtered_statements.sort(key=lambda s: s.gross_commission)
        elif self.sort_by == 'sales_desc':
            filtered_statements.sort(key=lambda s: s.total_sales, reverse=True)
        elif self.sort_by == 'payment_status':
            filtered_statements.sort(key=lambda s: s.payment_status)
        
        return filtered_statements
    
    def _matches_commission_type(self, statement):
        """Check if statement matches commission type filter"""
        if self.commission_type_filter == 'direct_sales':
            return statement.direct_sales_commission > 0
        elif self.commission_type_filter == 'referral':
            return statement.referral_bonus > 0
        elif self.commission_type_filter == 'team_override':
            return statement.team_override > 0
        return True
    
    def _generate_pdf_report(self, report_data):
        """Generate PDF report"""
        # DEFENSIVE FIX: Ensure proper ID handling to prevent list corruption
        wizard_id = self.id
        if isinstance(wizard_id, (list, tuple)):
            wizard_id = wizard_id[0] if wizard_id else False
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning("Wizard ID was unexpectedly a list: %s. Using %s", self.id, wizard_id)
        
        if not wizard_id:
            raise UserError(_("Cannot generate report: Invalid wizard ID"))
            
        report = self.env.ref('commission_partner_statement.action_scholarix_consolidated_report')
        
        # Pass the wizard record properly, ensuring it's a single record
        wizard_record = self.browse(wizard_id)
        return report.report_action(wizard_record, data=report_data)
    
    def _generate_excel_report(self, report_data):
        """Generate Excel report"""
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Create worksheets
        summary_sheet = workbook.add_worksheet('Executive Summary')
        detail_sheet = workbook.add_worksheet('Agent Details')
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#2E86AB',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        subheader_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#F5F5F5',
            'align': 'center',
            'border': 1
        })
        
        money_format = workbook.add_format({
            'num_format': '$#,##0.00',
            'align': 'right',
            'border': 1
        })
        
        percent_format = workbook.add_format({
            'num_format': '0.00%',
            'align': 'right',
            'border': 1
        })
        
        # Write executive summary
        self._write_excel_summary(summary_sheet, report_data, header_format, subheader_format, money_format)
        
        # Write agent details
        self._write_excel_details(detail_sheet, report_data, header_format, subheader_format, money_format, percent_format)
        
        workbook.close()
        output.seek(0)
        
        # Create attachment
        filename = f"SCHOLARIX_Commission_Report_{self.period_start}_{self.period_end}.xlsx"
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
    
    def _write_excel_summary(self, sheet, report_data, header_format, subheader_format, money_format):
        """Write executive summary to Excel"""
        row = 0
        
        # Title
        sheet.merge_range(row, 0, row, 4, 'SCHOLARIX COMMISSION STATEMENT REPORT', header_format)
        row += 2
        
        # Period
        sheet.write(row, 0, 'Period:', subheader_format)
        sheet.merge_range(row, 1, row, 4, f"{self.period_start} to {self.period_end}")
        row += 1
        
        # Generation date
        sheet.write(row, 0, 'Generated:', subheader_format)
        sheet.merge_range(row, 1, row, 4, datetime.now().strftime('%Y-%m-%d %H:%M'))
        row += 2
        
        # Summary statistics
        sheet.write(row, 0, 'Total Agents:', subheader_format)
        sheet.write(row, 1, report_data['total_agents'])
        row += 1
        
        sheet.write(row, 0, 'Total Sales:', subheader_format)
        sheet.write(row, 1, report_data['total_sales'], money_format)
        row += 1
        
        sheet.write(row, 0, 'Total Commission:', subheader_format)
        sheet.write(row, 1, report_data['total_commission'], money_format)
        row += 1
        
        sheet.write(row, 0, 'Average Commission per Agent:', subheader_format)
        sheet.write(row, 1, report_data['average_commission_per_agent'], money_format)
    
    def _write_excel_details(self, sheet, report_data, header_format, subheader_format, money_format, percent_format):
        """Write agent details to Excel"""
        # Headers
        headers = [
            'Agent Name', 'Total Sales', 'Commission Rate', 'Gross Commission',
            'Direct Sales', 'Referral Bonus', 'Team Override', 'Net Commission', 'Status'
        ]
        
        for col, header in enumerate(headers):
            sheet.write(0, col, header, header_format)
        
        # Data rows
        row = 1
        for statement in report_data['statements']:
            sheet.write(row, 0, statement.agent_id.name)
            sheet.write(row, 1, statement.total_sales, money_format)
            sheet.write(row, 2, statement.commission_rate / 100, percent_format)
            sheet.write(row, 3, statement.gross_commission, money_format)
            sheet.write(row, 4, statement.direct_sales_commission, money_format)
            sheet.write(row, 5, statement.referral_bonus, money_format)
            sheet.write(row, 6, statement.team_override, money_format)
            sheet.write(row, 7, statement.net_commission, money_format)
            sheet.write(row, 8, statement.payment_status.title())
            row += 1
    
    def _generate_combined_report(self, report_data):
        """Generate both PDF and Excel reports"""
        # Generate Excel first
        excel_action = self._generate_excel_report(report_data)
        
        # Then generate PDF
        return self._generate_pdf_report(report_data)
    
    def action_preview_report(self):
        """Preview report without generating files"""
        self.ensure_one()
        
        # Generate preview data (limited to first 10 agents)
        Commission = self.env['scholarix.commission.statement']
        report_data = Commission.generate_consolidated_report(
            self.period_start,
            self.period_end,
            self.agent_ids.ids if self.agent_selection == 'specific' else None
        )
        
        # Limit to preview size
        statements = self._filter_and_sort_statements(report_data['statements'])[:10]
        
        return {
            'name': 'Commission Report Preview',
            'type': 'ir.actions.act_window',
            'res_model': 'scholarix.commission.statement',
            'view_mode': 'tree',
            'domain': [('id', 'in', [s.id for s in statements])],
            'context': {
                'search_default_group_by_payment_status': 1 if self.group_by == 'payment_status' else 0,
            }
        }
