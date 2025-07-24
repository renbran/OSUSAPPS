# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Ammu Raj (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
import io
import json
import logging
import xlsxwriter
import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AgePayableReport(models.TransientModel):
    """For creating Age Payable report"""
    _name = 'age.payable.report'
    _description = 'Aged Payable Report'

    def _calculate_date_difference(self, date_maturity, today):
        """Helper method to calculate date difference handling various date formats"""
        if not date_maturity:
            return 0
        try:
            if isinstance(date_maturity, str):
                date_maturity = datetime.datetime.strptime(date_maturity, '%Y-%m-%d').date()
            if isinstance(date_maturity, datetime.date):
                return (today - date_maturity).days
        except (ValueError, TypeError):
            pass
        return 0

    def _get_move_lines(self, partner_id, paid_moves):
        """Helper method to get move lines for a partner with proper filtering"""
        move_lines = paid_moves.filtered(lambda r: r.partner_id.id == partner_id.id)
        return move_lines.read([
            'name', 'move_name', 'date', 'amount_currency', 'account_id',
            'date_maturity', 'currency_id', 'credit', 'move_id'
        ])

    def _safe_get_currency(self, currency_data):
        """Safely get currency name from currency data"""
        if currency_data and isinstance(currency_data, (list, tuple)) and len(currency_data) > 1:
            return currency_data[1]
        return ''

    @api.model
    def view_report(self):
        """
        Generate a report with move line data categorized by partner and credit
        difference.
        Returns:
            dict: Dictionary containing move line data categorized by partner
                  names. Each partner's data includes credit amounts and credit
                  differences based on days between maturity date and today. The
                  'partner_totals' key contains summary data for each partner.
        """
        partner_total = {}
        move_line_list = {}
        paid = self.env['account.move.line'].search([
            ('parent_state', '=', 'posted'),
            ('account_type', '=', 'liability_payable'),
            ('reconciled', '=', False)
        ])
        
        currency = self.env.company.currency_id
        partner_ids = paid.mapped('partner_id')
        today = fields.Date.today()

        for partner_id in partner_ids:
            move_line_data = self._get_move_lines(partner_id, paid)
            
            # Process each move line
            for val in move_line_data:
                date_maturity = val.get('date_maturity', False)
                diffrence = self._calculate_date_difference(date_maturity, today)
                
                # Calculate aging buckets
                val['diff0'] = val['credit'] if diffrence <= 0 else 0.0
                val['diff1'] = val['credit'] if 0 < diffrence <= 30 else 0.0
                val['diff2'] = val['credit'] if 30 < diffrence <= 60 else 0.0
                val['diff3'] = val['credit'] if 60 < diffrence <= 90 else 0.0
                val['diff4'] = val['credit'] if 90 < diffrence <= 120 else 0.0
                val['diff5'] = val['credit'] if diffrence > 120 else 0.0

            # Store move lines for this partner
            move_line_list[partner_id.name] = move_line_data
            
            # Calculate totals for this partner
            credit_sum = sum(val['credit'] for val in move_line_data)
            partner_total[partner_id.name] = {
                'credit_sum': credit_sum,
                'diff0_sum': round(sum(val['diff0'] for val in move_line_data), 2),
                'diff1_sum': round(sum(val['diff1'] for val in move_line_data), 2),
                'diff2_sum': round(sum(val['diff2'] for val in move_line_data), 2),
                'diff3_sum': round(sum(val['diff3'] for val in move_line_data), 2),
                'diff4_sum': round(sum(val['diff4'] for val in move_line_data), 2),
                'diff5_sum': round(sum(val['diff5'] for val in move_line_data), 2),
                'currency_id': currency.id,
                'partner_id': partner_id.id
            }

        move_line_list['partner_totals'] = partner_total
        return move_line_list

    @api.model
    def get_filter_values(self, date, partner):
        """
        Retrieve filtered move line data based on date and partner(s).
        Parameters:
            date (str): Date for filtering move lines (format: 'YYYY-MM-DD').
            partner (list): List of partner IDs to filter move lines for.
        Returns:
            dict: Dictionary with filtered move line data organized by partner
                  names. Includes credit amount categorization based on days
                  difference. Contains partner-wise summary under
                  'partner_totals' key.
        """
        partner_total = {}
        move_line_list = {}
        if date:
            paid = self.env['account.move.line'].search(
                [('parent_state', '=', 'posted'),
                 ('account_type', '=', 'liability_payable'),
                 ('reconciled', '=', False), ('date', '<=', date)])
        else:
            paid = self.env['account.move.line'].search(
                [('parent_state', '=', 'posted'),
                 ('account_type', '=', 'liability_payable'),
                 ('reconciled', '=', False)])
        currency_id = self.env.company.currency_id.symbol
        if partner:
            partner_ids = self.env['res.partner'].search(
                [('id', 'in', partner)])
        else:
            partner_ids = paid.mapped('partner_id')
        today = fields.Date.today()
        for partner_id in partner_ids:
            move_line_ids = paid.filtered(
                lambda rec: rec.partner_id in partner_id)
            move_line_data = move_line_ids.read(
                ['name', 'move_name', 'date', 'amount_currency', 'account_id',
                 'date_maturity', 'currency_id', 'credit', 'move_id'])
            for val in move_line_data:
                date_maturity = val.get('date_maturity', False)
                diffrence = self._calculate_date_difference(date_maturity, today)
                val['diff0'] = val['credit'] if diffrence <= 0 else 0.0
                val['diff1'] = val['credit'] if 0 < diffrence <= 30 else 0.0
                val['diff2'] = val['credit'] if 30 < diffrence <= 60 else 0.0
                val['diff3'] = val['credit'] if 60 < diffrence <= 90 else 0.0
                val['diff4'] = val['credit'] if 90 < diffrence <= 120 else 0.0
                val['diff5'] = val['credit'] if diffrence > 120 else 0.0
            move_line_list[partner_id.name] = move_line_data
            partner_total[partner_id.name] = {
                'credit_sum': sum(val['credit'] for val in move_line_data),
                'diff0_sum': round(sum(val['diff0'] for val in move_line_data),
                                   2),
                'diff1_sum': round(sum(val['diff1'] for val in move_line_data),
                                   2),
                'diff2_sum': round(sum(val['diff2'] for val in move_line_data),
                                   2),
                'diff3_sum': round(sum(val['diff3'] for val in move_line_data),
                                   2),
                'diff4_sum': round(sum(val['diff4'] for val in move_line_data),
                                   2),
                'diff5_sum': round(sum(val['diff5'] for val in move_line_data),
                                   2),
                'currency_id': currency_id,
                'partner_id': partner_id.id
            }
        move_line_list['partner_totals'] = partner_total
        return move_line_list

    @api.model
    def get_xlsx_report(self, data, response, report_name, report_action):
        """Generate an Excel report based on the provided data."""
        try:
            data = json.loads(data)
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            
            # Get report filters
            filters = data.get('filters', {})
            end_date = filters.get('end_date', '')
            partners = filters.get('partner', [])
            
            # Create worksheet and formats
            sheet = workbook.add_worksheet()
            formats = self._get_xlsx_formats(workbook)
            
            # Set column widths
            self._set_column_widths(sheet)
            
            # Write headers
            self._write_report_headers(sheet, formats, report_name, end_date, partners)
            
            # Write data
            if data and report_action == 'dynamic_accounts_report.action_aged_payable':
                self._write_aged_payable_data(sheet, formats, data)
            
            workbook.close()
            output.seek(0)
            response.stream.write(output.read())
            output.close()
            
        except Exception as e:
            _logger.error("Error generating XLSX report: %s", str(e))
            raise UserError(_("Error generating Excel report. Please try again or contact your administrator."))

    def _get_xlsx_formats(self, workbook):
        """Create and return dictionary of workbook formats"""
        return {
            'head': workbook.add_format({
                'align': 'center', 
                'bold': True, 
                'font_size': '15px'
            }),
            'sub_heading': workbook.add_format({
                'align': 'center', 
                'bold': True, 
                'font_size': '10px',
                'border': 1, 
                'bg_color': '#D3D3D3',
                'border_color': 'black'
            }),
            'filter_head': workbook.add_format({
                'align': 'center', 
                'bold': True, 
                'font_size': '10px',
                'border': 1, 
                'bg_color': '#D3D3D3',
                'border_color': 'black'
            }),
            'txt': workbook.add_format({
                'font_size': '10px', 
                'border': 1
            }).set_indent(2)
        }

    def _set_column_widths(self, sheet):
        """Set the column widths for the worksheet"""
        widths = [30, 20, 15, 15, 20, 20, 15, 15, 15, 15, 15, 15, 15, 15, 15]
        for i, width in enumerate(widths):
            sheet.set_column(i, i, width)

    def _write_report_headers(self, sheet, formats, report_name, end_date, partners):
        """Write report headers and filters"""
        sheet.merge_range('A1:B1', report_name, formats['head'])
        sheet.write('B3', 'Date Range', formats['filter_head'])
        sheet.write('B4', 'Partners', formats['filter_head'])
        
        if end_date:
            sheet.merge_range('C3:G3', str(end_date), formats['filter_head'])
            
        if partners:
            partner_names = [p.get('display_name', 'undefined') for p in partners]
            sheet.merge_range('C4:G4', ', '.join(partner_names), formats['filter_head'])

    def _write_aged_payable_data(self, sheet, formats, data):
        """Write the aged payable report data"""
        if not data.get('move_lines'):
            return

        # Write column headers
        headers = [
            ' ', 'Invoice Date', 'Amount Currency', 'Currency', 'Account',
            'Expected Date', 'At Date', '1-30', '31-60', '61-90', '91-120',
            'Older', 'Total'
        ]
        for col, header in enumerate(headers):
            sheet.write(6, col, header, formats['sub_heading'])

        row = 6
        for move_line in data['move_lines']:
            row = self._write_partner_data(sheet, formats, data, move_line, row)

        # Write grand totals
        self._write_grand_totals(sheet, formats, data, row)

    def _write_partner_data(self, sheet, formats, data, move_line, row):
        """Write data for a specific partner"""
        row += 1
        totals = data['total'].get(move_line, {})
        
        # Write partner summary row
        sheet.write(row, 0, move_line, formats['txt'])
        for col in range(1, 8):
            sheet.write(row, col, '', formats['txt'])
            
        # Write partner totals
        diff_fields = ['diff0_sum', 'diff1_sum', 'diff2_sum', 'diff3_sum', 
                      'diff4_sum', 'diff5_sum', 'credit_sum']
        for col, field in enumerate(diff_fields, 8):
            sheet.write(row, col, totals.get(field, 0.0), formats['txt'])

        # Write move lines
        for rec in data['data'].get(move_line, []):
            row = self._write_move_line(sheet, formats, rec, row)

        return row

    def _write_move_line(self, sheet, formats, rec, row):
        """Write a single move line"""
        row += 1
        
        # Safely get values with fallbacks
        move_name = rec.get('move_name', '')
        name = rec.get('name', '')
        date = rec.get('date', '')
        amount_currency = rec.get('amount_currency', 0.0)
        currency = self._safe_get_currency(rec.get('currency_id'))
        account = rec.get('account_id', ['', ''])[1]
        date_maturity = rec.get('date_maturity', '')
        
        # Write move line data
        sheet.write(row, 0, f"{move_name} {name}".strip(), formats['txt'])
        sheet.write(row, 1, date, formats['txt'])
        sheet.write(row, 2, amount_currency, formats['txt'])
        sheet.write(row, 3, currency, formats['txt'])
        sheet.merge_range(row, 4, row, 5, account, formats['txt'])
        sheet.merge_range(row, 6, row, 7, date_maturity, formats['txt'])
        
        # Write aging buckets
        for i, field in enumerate(['diff0', 'diff1', 'diff2', 'diff3', 
                                 'diff4', 'diff5']):
            sheet.write(row, 8 + i, rec.get(field, 0.0), formats['txt'])
            
        sheet.write(row, 14, '', formats['txt'])
        return row

    def _write_grand_totals(self, sheet, formats, data, row):
        """Write the grand totals row"""
        row += 1
        sheet.merge_range(row, 0, row, 7, 'Total', formats['filter_head'])
        
        diff_fields = ['diff0_sum', 'diff1_sum', 'diff2_sum', 'diff3_sum', 
                      'diff4_sum', 'diff5_sum']
        for col, field in enumerate(diff_fields, 8):
            sheet.write(row, col, data['grand_total'].get(field, 0.0), formats['filter_head'])
        
        sheet.write(row, 14, data['grand_total'].get('total_credit', 0.0), formats['filter_head'])
