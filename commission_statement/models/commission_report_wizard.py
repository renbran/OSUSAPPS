from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging
import io
import xlsxwriter
import base64
from datetime import datetime

_logger = logging.getLogger(__name__)

class CommissionStatementWizard(models.TransientModel):
    _name = 'commission.statement.wizard'
    _description = 'Commission Statement Report Wizard'

    # Filter fields
    date_from = fields.Date(string='Date From', required=True, default=fields.Date.today)
    date_to = fields.Date(string='Date To', required=True, default=fields.Date.today)
    partner_id = fields.Many2one('res.partner', string='Commission Partner', help='Leave empty to include all partners')
    sale_order_id = fields.Many2one('sale.order', string='Specific Sale Order', help='Generate report for specific order only')
    commission_type_filter = fields.Selection([
        ('all', 'All Commission Types'),
        ('internal', 'Internal Commissions Only'),
        ('external', 'External Commissions Only'),
        ('legacy', 'Legacy Commissions Only')
    ], string='Commission Type Filter', default='all')
    
    # Report options
    include_zero_commissions = fields.Boolean(string='Include Zero Commissions', default=False)
    group_by_partner = fields.Boolean(string='Group by Partner', default=True)
    show_customer_details = fields.Boolean(string='Show Customer Details', default=True)
    
    # Company and currency
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id', string='Currency', readonly=True)

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for wizard in self:
            if wizard.date_from > wizard.date_to:
                raise ValidationError("Date From cannot be later than Date To")

    def action_generate_pdf_report(self):
        """Generate PDF commission statement report"""
        self.ensure_one()
        data = self._prepare_report_data()
        
        if not data['commission_lines']:
            # Enhanced debugging information
            domain = self._get_sale_order_domain()
            orders = self.env['sale.order'].search(domain)
            
            debug_info = [
                f"Date range: {self.date_from} to {self.date_to}",
                f"Found {len(orders)} orders in date range",
                f"Order states filter: sale, done",
            ]
            
            if self.partner_id:
                debug_info.append(f"Partner filter: {self.partner_id.name}")
            if self.sale_order_id:
                debug_info.append(f"Order filter: {self.sale_order_id.name}")
                
            # Check if commission_ax module is installed
            commission_module = self.env['ir.module.module'].search([
                ('name', '=', 'commission_ax'),
                ('state', '=', 'installed')
            ])
            
            if not commission_module:
                debug_info.append("⚠️  commission_ax module not installed - commission fields not available")
            else:
                debug_info.append("✓ commission_ax module is installed")
                
            # Check first few orders for commission data
            if orders:
                sample_order = orders[0]
                has_commission_fields = hasattr(sample_order, 'total_commission_amount')
                debug_info.append(f"Commission fields available: {has_commission_fields}")
                
                if has_commission_fields:
                    total_comm = getattr(sample_order, 'total_commission_amount', 0)
                    debug_info.append(f"Sample order {sample_order.name} total commission: {total_comm}")
            
            error_msg = "No commission data found for the selected criteria.\n\nDebugging info:\n" + "\n".join(debug_info)
            raise UserError(error_msg)
        
        return self.env.ref('commission_statement.action_commission_statement_pdf').report_action(self, data=data)

    def action_generate_excel_report(self):
        """Generate Excel commission statement report"""
        self.ensure_one()
        data = self._prepare_report_data()
        
        if not data['commission_lines']:
            # Enhanced debugging information (same as PDF method)
            domain = self._get_sale_order_domain()
            orders = self.env['sale.order'].search(domain)
            
            debug_info = [
                f"Date range: {self.date_from} to {self.date_to}",
                f"Found {len(orders)} orders in date range",
                f"Order states filter: sale, done",
            ]
            
            if self.partner_id:
                debug_info.append(f"Partner filter: {self.partner_id.name}")
            if self.sale_order_id:
                debug_info.append(f"Order filter: {self.sale_order_id.name}")
                
            # Check if commission_ax module is installed
            commission_module = self.env['ir.module.module'].search([
                ('name', '=', 'commission_ax'),
                ('state', '=', 'installed')
            ])
            
            if not commission_module:
                debug_info.append("⚠️  commission_ax module not installed - commission fields not available")
            else:
                debug_info.append("✓ commission_ax module is installed")
                
            # Check first few orders for commission data
            if orders:
                sample_order = orders[0]
                has_commission_fields = hasattr(sample_order, 'total_commission_amount')
                debug_info.append(f"Commission fields available: {has_commission_fields}")
                
                if has_commission_fields:
                    total_comm = getattr(sample_order, 'total_commission_amount', 0)
                    debug_info.append(f"Sample order {sample_order.name} total commission: {total_comm}")
            
            error_msg = "No commission data found for the selected criteria.\n\nDebugging info:\n" + "\n".join(debug_info)
            raise UserError(error_msg)
        
        # Create Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Commission Statement')
        
        # Define formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })
        
        currency_format = workbook.add_format({
            'num_format': f'#,##0.00 "{self.currency_id.symbol or ""}"',
            'border': 1,
            'align': 'right'
        })
        
        percentage_format = workbook.add_format({
            'num_format': '0.00%',
            'border': 1,
            'align': 'right'
        })
        
        text_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'vcenter'
        })
        
        center_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        subtotal_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9E1F2',
            'border': 1,
            'align': 'right'
        })
        
        total_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'align': 'right'
        })
        
        # Write title and metadata
        worksheet.merge_range('A1:F1', 'COMMISSION STATEMENT REPORT', title_format)
        
        # Metadata
        row = 3
        worksheet.write(row, 0, f'Date Range:', text_format)
        worksheet.write(row, 1, f'{self.date_from} to {self.date_to}', text_format)
        worksheet.write(row, 3, f'Partner Filter:', text_format)
        worksheet.write(row, 4, data['partner_filter'], text_format)
        
        row += 1
        worksheet.write(row, 0, f'Report Generated:', text_format)
        worksheet.write(row, 1, data['report_generated_date'], text_format)
        worksheet.write(row, 3, f'Total Records:', text_format)
        worksheet.write(row, 4, data['total_lines'], text_format)
        
        # Headers
        row += 2
        headers = [
            'COMMISSION NAME',
            'ORDER REF',
            'CUSTOMER REFERENCE',
            'COMMISSION TYPE',
            'RATE',
            'TOTAL'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, header_format)
        
        # Set column widths
        worksheet.set_column(0, 0, 25)  # Commission Name
        worksheet.set_column(1, 1, 15)  # Order Ref
        worksheet.set_column(2, 2, 30)  # Customer Reference
        worksheet.set_column(3, 3, 20)  # Commission Type
        worksheet.set_column(4, 4, 12)  # Rate
        worksheet.set_column(5, 5, 15)  # Total
        
        # Write data
        row += 1
        current_partner = None
        partner_total = 0
        
        for line in data['commission_lines']:
            # Check if we need to add a subtotal for grouping
            if self.group_by_partner and current_partner and current_partner != line['partner_name']:
                # Add subtotal row
                worksheet.write(row, 4, f'Subtotal - {current_partner}:', subtotal_format)
                worksheet.write(row, 5, partner_total, currency_format)
                row += 1
                partner_total = 0
            
            current_partner = line['partner_name']
            
            worksheet.write(row, 0, line['partner_name'], text_format)
            worksheet.write(row, 1, line['order_ref'], center_format)
            worksheet.write(row, 2, line['customer_ref'], text_format)
            worksheet.write(row, 3, line['commission_type_display'], center_format)
            
            # Handle rate display
            if line['commission_type'] == 'fixed':
                worksheet.write(row, 4, 'Fixed', center_format)
            else:
                worksheet.write(row, 4, line['rate'] / 100, percentage_format)
            
            worksheet.write(row, 5, line['amount'], currency_format)
            partner_total += line['amount']
            row += 1
        
        # Add final subtotal if grouping
        if self.group_by_partner and current_partner and data['commission_lines']:
            worksheet.write(row, 4, f'Subtotal - {current_partner}:', subtotal_format)
            worksheet.write(row, 5, partner_total, currency_format)
            row += 1
        
        # Add grand total
        if data['commission_lines']:
            worksheet.write(row, 4, 'GRAND TOTAL:', total_format)
            worksheet.write(row, 5, data['total_amount'], total_format)
        
        workbook.close()
        output.seek(0)
        
        # Create attachment
        filename = f"Commission_Statement_{self.date_from}_{self.date_to}.xlsx"
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

    def _prepare_report_data(self):
        """Prepare data for both PDF and Excel reports"""
        domain = self._get_sale_order_domain()
        sale_orders = self.env['sale.order'].search(domain, order='date_order desc')
        
        commission_lines = []
        
        for order in sale_orders:
            lines = self._extract_commission_lines(order)
            commission_lines.extend(lines)
        
        # Sort by partner name if grouping is enabled
        if self.group_by_partner:
            commission_lines.sort(key=lambda x: (x['partner_name'], x['order_ref']))
        else:
            commission_lines.sort(key=lambda x: x['order_ref'])
        
        # Calculate totals by category
        total_external = sum(line['amount'] for line in commission_lines if line['category'] == 'external')
        total_internal = sum(line['amount'] for line in commission_lines if line['category'] == 'internal')
        total_legacy = sum(line['amount'] for line in commission_lines if line['category'] == 'legacy')
        
        return {
            'commission_lines': commission_lines,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'partner_filter': self.partner_id.name if self.partner_id else 'All Partners',
            'commission_type_filter': dict(self._fields['commission_type_filter'].selection)[self.commission_type_filter],
            'total_amount': sum(line['amount'] for line in commission_lines),
            'total_external': total_external,
            'total_internal': total_internal,
            'total_legacy': total_legacy,
            'total_lines': len(commission_lines),
            'report_generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'company_name': self.company_id.name,
            'currency_symbol': self.currency_id.symbol or self.currency_id.name,
            'group_by_partner': self.group_by_partner,
        }

    def _get_sale_order_domain(self):
        """Build domain for sale order search"""
        domain = [
            ('date_order', '>=', self.date_from),
            ('date_order', '<=', self.date_to),
            ('state', 'in', ['sale', 'done'])
        ]
        
        if self.sale_order_id:
            domain.append(('id', '=', self.sale_order_id.id))
        
        return domain

    def _extract_commission_lines(self, order):
        """Extract commission lines from a sale order"""
        lines = []
        
        # Validate that commission_ax fields exist
        required_fields = ['total_commission_amount', 'consultant_id', 'manager_id']
        missing_fields = [f for f in required_fields if not hasattr(order, f)]
        if missing_fields:
            _logger.warning("Missing commission fields on sale.order %s: %s", order.name, missing_fields)
        
        # Method 1: Extract from commission FIELDS on sale order
        lines.extend(self._extract_commission_from_fields(order))
        
        # Method 2: Extract from commission PRODUCT LINES in sale order
        lines.extend(self._extract_commission_from_order_lines(order))
        
        return lines
    
    def _extract_commission_from_fields(self, order):
        """Extract commission data from sale order fields (original method)"""
        lines = []
        
        # Helper function to add commission line
        def add_commission_line(partner, amount, comm_type, rate, category, commission_field_name):
            if not partner or (not self.include_zero_commissions and amount <= 0):
                return
            
            if self.partner_id and partner.id != self.partner_id.id:
                return
            
            # Filter by commission type
            if self.commission_type_filter != 'all':
                if self.commission_type_filter == 'internal' and category != 'internal':
                    return
                elif self.commission_type_filter == 'external' and category != 'external':
                    return
                elif self.commission_type_filter == 'legacy' and category != 'legacy':
                    return
            
            commission_type_display = self._get_commission_type_display(comm_type)
            
            lines.append({
                'partner_name': partner.name,
                'partner_id': partner.id,
                'order_ref': order.name,
                'customer_ref': order.partner_id.name,
                'commission_type': comm_type,
                'commission_type_display': commission_type_display,
                'rate': rate,
                'amount': amount,
                'category': category,
                'sale_order_id': order.id,
                'commission_field': commission_field_name,
                'order_date': order.date_order,
                'order_amount': order.amount_total,
            })
        
        # Legacy commissions
        commission_mappings = [
            # (partner_field, amount_field, type_field, rate_field, category, field_name)
            ('consultant_id', 'salesperson_commission', 'consultant_commission_type', 'consultant_comm_percentage', 'legacy', 'consultant'),
            ('manager_id', 'manager_commission', 'manager_legacy_commission_type', 'manager_comm_percentage', 'legacy', 'manager'),
            ('second_agent_id', 'second_agent_commission', 'second_agent_commission_type', 'second_agent_comm_percentage', 'legacy', 'second_agent'),
            ('director_id', 'director_commission', 'director_legacy_commission_type', 'director_comm_percentage', 'legacy', 'director'),
            
            # External commissions
            ('broker_partner_id', 'broker_amount', 'broker_commission_type', 'broker_rate', 'external', 'broker'),
            ('referrer_partner_id', 'referrer_amount', 'referrer_commission_type', 'referrer_rate', 'external', 'referrer'),
            ('cashback_partner_id', 'cashback_amount', 'cashback_commission_type', 'cashback_rate', 'external', 'cashback'),
            ('other_external_partner_id', 'other_external_amount', 'other_external_commission_type', 'other_external_rate', 'external', 'other_external'),
            
            # Internal commissions
            ('agent1_partner_id', 'agent1_amount', 'agent1_commission_type', 'agent1_rate', 'internal', 'agent1'),
            ('agent2_partner_id', 'agent2_amount', 'agent2_commission_type', 'agent2_rate', 'internal', 'agent2'),
            ('manager_partner_id', 'manager_amount', 'manager_commission_type', 'manager_rate', 'internal', 'manager_partner'),
            ('director_partner_id', 'director_amount', 'director_commission_type', 'director_rate', 'internal', 'director_partner'),
        ]
        
        for partner_field, amount_field, type_field, rate_field, category, field_name in commission_mappings:
            # Check if all required fields exist before processing
            if not all(hasattr(order, field) for field in [partner_field, amount_field, type_field, rate_field]):
                continue
                
            partner = getattr(order, partner_field, None)
            amount = getattr(order, amount_field, 0)
            comm_type = getattr(order, type_field, None)
            rate = getattr(order, rate_field, 0)
            
            if partner:
                add_commission_line(partner, amount, comm_type, rate, category, field_name)
        
        return lines

    def _extract_commission_from_order_lines(self, order):
        """Extract commission data from sale order lines (commission products)"""
        lines = []
        
        # Look for commission products in order lines
        if hasattr(order, 'order_line'):
            for line in order.order_line:
                # Check if this is a commission product line
                if line.product_id and 'commission' in line.product_id.name.lower():
                    # Try to extract partner info from product description or line
                    partner = self._extract_partner_from_commission_line(line, order)
                    role = self._extract_role_from_commission_line(line)
                    
                    if partner and line.price_subtotal > 0:
                        # Convert commission product to commission line format
                        commission_line = {
                            'partner_name': partner.name,
                            'partner_id': partner.id,
                            'order_ref': order.name,
                            'customer_ref': order.partner_id.name,
                            'commission_type': 'fixed',  # Commission products are typically fixed amounts
                            'commission_type_display': 'Product Commission',
                            'rate': 0,  # Not applicable for product-based commissions
                            'amount': line.price_subtotal,
                            'category': 'product',
                            'sale_order_id': order.id,
                            'commission_field': f'product_{line.id}',
                            'order_date': order.date_order,
                            'order_amount': order.amount_total,
                            'product_name': line.product_id.name,
                            'description': line.name,
                            'quantity': line.product_uom_qty,
                            'unit_price': line.price_unit,
                        }
                        
                        # Apply filters
                        if self._should_include_commission_line(commission_line):
                            lines.append(commission_line)
                            _logger.debug("Added commission line from product: partner=%s, amount=%s, product=%s for order %s", 
                                        partner.name, line.price_subtotal, line.product_id.name, order.name)
        
        if not lines:
            _logger.debug("No commission products found in order lines for order %s", order.name)
            
        return lines
    
    def _extract_partner_from_commission_line(self, line, order):
        """Extract partner from commission line based on role or fallback to order fields"""
        # Try to determine partner based on commission type and order fields
        product_name = line.product_id.name.lower()
        
        if 'primary' in product_name or 'consultant' in product_name:
            return getattr(order, 'consultant_id', None)
        elif 'manager' in product_name:
            if 'senior' in product_name:
                return getattr(order, 'senior_manager_id', None)
            elif 'regional' in product_name:
                return getattr(order, 'regional_manager_id', None)
            else:
                return getattr(order, 'manager_id', None)
        elif 'broker' in product_name:
            return getattr(order, 'broker_partner_id', None)
        elif 'director' in product_name:
            return getattr(order, 'director_id', None)
        elif 'agent' in product_name:
            # Try to determine which agent based on description or fallback
            return getattr(order, 'agent1_partner_id', None) or getattr(order, 'agent2_partner_id', None)
        
        # Fallback to consultant if can't determine specific role
        return getattr(order, 'consultant_id', None) or getattr(order, 'manager_id', None)
    
    def _extract_role_from_commission_line(self, line):
        """Extract role from commission product name"""
        product_name = line.product_id.name.lower()
        if 'primary' in product_name or 'consultant' in product_name:
            return 'Consultant'
        elif 'manager' in product_name:
            if 'senior' in product_name:
                return 'Senior Manager'
            elif 'regional' in product_name:
                return 'Regional Manager'
            else:
                return 'Manager'
        elif 'broker' in product_name:
            return 'Broker'
        elif 'director' in product_name:
            return 'Director'
        elif 'agent' in product_name:
            return 'Agent'
        
        # Default fallback
        return 'Commission'
    
    def _should_include_commission_line(self, commission_line):
        """Check if commission line should be included based on filters"""
        # Check zero commission filter
        if not self.include_zero_commissions and commission_line['amount'] <= 0:
            return False
        
        # Check partner filter
        if self.partner_id and commission_line['partner_id'] != self.partner_id.id:
            return False
        
        # Check commission type filter
        if self.commission_type_filter != 'all':
            if self.commission_type_filter == 'internal' and commission_line['category'] != 'internal':
                return False
            elif self.commission_type_filter == 'external' and commission_line['category'] != 'external':
                return False
            elif self.commission_type_filter == 'legacy' and commission_line['category'] != 'legacy':
                return False
            # Allow 'product' category to be included in all filters for now
        
        return True

    def _get_commission_type_display(self, commission_type):
        """Get human-readable commission type"""
        type_mapping = {
            'fixed': 'Fixed Amount',
            'percent_unit_price': 'Unit Price %',
            'percent_untaxed_total': 'Total %'
        }
        return type_mapping.get(commission_type, commission_type or 'Not Set')

    def action_preview_data(self):
        """Preview the data that will be included in the report"""
        data = self._prepare_report_data()
        
        if not data['commission_lines']:
            # Enhanced debugging information (same as other methods)
            domain = self._get_sale_order_domain()
            orders = self.env['sale.order'].search(domain)
            
            debug_info = [
                f"Date range: {self.date_from} to {self.date_to}",
                f"Found {len(orders)} orders in date range",
                f"Order states filter: sale, done",
            ]
            
            if self.partner_id:
                debug_info.append(f"Partner filter: {self.partner_id.name}")
            if self.sale_order_id:
                debug_info.append(f"Order filter: {self.sale_order_id.name}")
                
            # Check if commission_ax module is installed
            commission_module = self.env['ir.module.module'].search([
                ('name', '=', 'commission_ax'),
                ('state', '=', 'installed')
            ])
            
            if not commission_module:
                debug_info.append("⚠️  commission_ax module not installed - commission fields not available")
            else:
                debug_info.append("✓ commission_ax module is installed")
                
            # Check first few orders for commission data
            if orders:
                sample_order = orders[0]
                has_commission_fields = hasattr(sample_order, 'total_commission_amount')
                debug_info.append(f"Commission fields available: {has_commission_fields}")
                
                if has_commission_fields:
                    total_comm = getattr(sample_order, 'total_commission_amount', 0)
                    debug_info.append(f"Sample order {sample_order.name} total commission: {total_comm}")
            
            error_msg = "No commission data found for the selected criteria.\n\nDebugging info:\n" + "\n".join(debug_info)
            raise UserError(error_msg)
        
        # Create a simple tree view to preview the data
        lines = []
        for line_data in data['commission_lines']:
            lines.append((0, 0, {
                'partner_name': line_data['partner_name'],
                'order_ref': line_data['order_ref'],
                'customer_ref': line_data['customer_ref'],
                'commission_type_display': line_data['commission_type_display'],
                'rate': line_data['rate'],
                'amount': line_data['amount'],
                'category': line_data['category'],
                'order_date': line_data['order_date'],
            }))
        
        preview_wizard = self.env['commission.statement.report.preview'].create({
            'line_ids': lines,
            'total_amount': data['total_amount'],
            'total_lines': data['total_lines'],
            'date_from': self.date_from,
            'date_to': self.date_to,
            'partner_filter': data['partner_filter'],
            'commission_type_filter': data['commission_type_filter'],
        })
        
        return {
            'name': 'Commission Statement Preview',
            'type': 'ir.actions.act_window',
            'res_model': 'commission.statement.report.preview',
            'res_id': preview_wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }


class CommissionStatementPreview(models.TransientModel):
    _name = 'commission.statement.report.preview'
    _description = 'Commission Statement Report Preview'

    line_ids = fields.One2many('commission.statement.report.preview.line', 'preview_id', string='Commission Lines')
    total_amount = fields.Float(string='Total Amount')
    total_lines = fields.Integer(string='Total Lines')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    partner_filter = fields.Char(string='Partner Filter')
    commission_type_filter = fields.Char(string='Commission Type Filter')


class CommissionStatementPreviewLine(models.TransientModel):
    _name = 'commission.statement.report.preview.line'
    _description = 'Commission Statement Report Preview Line'

    preview_id = fields.Many2one('commission.statement.report.preview', string='Preview')
    partner_name = fields.Char(string='Commission Name')
    order_ref = fields.Char(string='Order Ref')
    customer_ref = fields.Char(string='Customer Reference')
    commission_type_display = fields.Char(string='Commission Type')
    rate = fields.Float(string='Rate')
    amount = fields.Float(string='Total')
    category = fields.Char(string='Category')
    order_date = fields.Date(string='Order Date')