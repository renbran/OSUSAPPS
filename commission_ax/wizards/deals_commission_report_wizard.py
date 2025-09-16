from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging
import io
import xlsxwriter
import base64

_logger = logging.getLogger(__name__)

class DealsCommissionReportWizard(models.TransientModel):
    _name = 'deals.commission.report.wizard'
    _description = 'Comprehensive Deals Commission Report Wizard'

    # Filter fields
    date_from = fields.Date(string='Booking Date From', required=True, default=fields.Date.today)
    date_to = fields.Date(string='Booking Date To', required=True, default=fields.Date.today)
    partner_id = fields.Many2one('res.partner', string='Commission Partner', help='Leave empty to include all partners')
    project_id = fields.Many2one('project.project', string='Project', help='Leave empty to include all projects')
    sale_order_id = fields.Many2one('sale.order', string='Specific Deal/Sale Order', help='Generate report for specific deal only')
    
    # Report options
    include_zero_commissions = fields.Boolean(string='Include Zero Commissions', default=False)
    include_draft_orders = fields.Boolean(string='Include Draft Orders', default=False)
    group_by_project = fields.Boolean(string='Group by Project', default=True)
    show_payment_details = fields.Boolean(string='Show Payment Details', default=True)
    
    # Status filters
    commission_status_filter = fields.Selection([
        ('all', 'All Statuses'),
        ('eligible', 'Eligible Only'),
        ('processed', 'Processed Only'),
        ('paid', 'Paid Only'),
        ('pending', 'Pending Only')
    ], string='Commission Status Filter', default='all')

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for wizard in self:
            if wizard.date_from > wizard.date_to:
                raise ValidationError("Date From cannot be later than Date To")

    def _get_deals_data(self):
        """Get comprehensive deals data with commission information"""
        domain = [
            ('date_order', '>=', self.date_from),
            ('date_order', '<=', self.date_to),
        ]
        
        if self.partner_id:
            domain.extend([
                '|', '|', '|',
                ('consultant_id', '=', self.partner_id.id),
                ('manager_id', '=', self.partner_id.id),
                ('director_id', '=', self.partner_id.id),
                ('commission_partner_ids', 'in', [self.partner_id.id])
            ])
            
        if self.project_id:
            domain.append(('project_id', '=', self.project_id.id))
            
        if self.sale_order_id:
            domain.append(('id', '=', self.sale_order_id.id))
            
        if not self.include_draft_orders:
            domain.append(('state', 'not in', ['draft', 'cancel']))

        sale_orders = self.env['sale.order'].search(domain, order='date_order desc, name')
        
        deals_data = []
        
        for order in sale_orders:
            # Get all commission partners for this order
            commission_partners = self._get_commission_partners_for_order(order)
            
            for partner_data in commission_partners:
                # Get payment/invoice information
                payment_info = self._get_payment_info_for_order(order)
                
                deal_data = {
                    'order_id': order.id,
                    'order_name': order.name,
                    'customer_name': order.partner_id.name,
                    'booking_date': order.date_order,
                    'project_name': order.project_id.name if order.project_id else 'No Project',
                    'unit_reference': self._get_unit_reference(order),
                    'order_amount': order.amount_total,
                    'order_untaxed_amount': order.amount_untaxed,
                    'currency_id': order.currency_id.id,
                    'currency_symbol': order.currency_id.symbol,
                    'state': order.state,
                    'state_display': dict(order._fields['state'].selection).get(order.state),
                    
                    # Commission partner information
                    'partner_id': partner_data['partner_id'],
                    'partner_name': partner_data['partner_name'],
                    'commission_type': partner_data['commission_type'],
                    'commission_role': partner_data['role'],
                    'commission_rate': partner_data['rate'],
                    'eligible_amount': partner_data['eligible_amount'],
                    'commission_status': partner_data['status'],
                    
                    # Payment information
                    'total_invoiced': payment_info['total_invoiced'],
                    'total_paid': payment_info['total_paid'],
                    'commission_processed': partner_data.get('processed_amount', 0.0),
                    'commission_paid': partner_data.get('paid_amount', 0.0),
                    'commission_pending': partner_data['eligible_amount'] - partner_data.get('paid_amount', 0.0),
                    
                    # Additional details
                    'purchase_orders': self._get_purchase_orders_info(order),
                    'invoice_count': len(order.invoice_ids),
                    'payment_count': self._get_payment_count(order),
                }
                
                # Apply commission status filter
                if self.commission_status_filter != 'all':
                    if not self._matches_status_filter(deal_data):
                        continue
                
                # Apply zero commission filter
                if not self.include_zero_commissions and deal_data['eligible_amount'] == 0:
                    continue
                    
                deals_data.append(deal_data)
        
        return deals_data

    def _get_commission_partners_for_order(self, order):
        """Get all commission partners and their details for an order"""
        partners = []
        
        # Legacy commission partners
        if order.consultant_id:
            partners.append({
                'partner_id': order.consultant_id.id,
                'partner_name': order.consultant_id.name,
                'role': 'Consultant',
                'commission_type': order.consultant_commission_type,
                'rate': order.consultant_comm_percentage,
                'eligible_amount': order.salesperson_commission,
                'status': self._get_commission_status(order, 'consultant'),
                'processed_amount': self._get_processed_amount(order, order.consultant_id),
                'paid_amount': self._get_paid_amount(order, order.consultant_id),
            })
            
        if order.manager_id:
            partners.append({
                'partner_id': order.manager_id.id,
                'partner_name': order.manager_id.name,
                'role': 'Manager',
                'commission_type': order.manager_legacy_commission_type,
                'rate': order.manager_comm_percentage,
                'eligible_amount': order.manager_commission,
                'status': self._get_commission_status(order, 'manager'),
                'processed_amount': self._get_processed_amount(order, order.manager_id),
                'paid_amount': self._get_paid_amount(order, order.manager_id),
            })
            
        if order.director_id:
            partners.append({
                'partner_id': order.director_id.id,
                'partner_name': order.director_id.name,
                'role': 'Director',
                'commission_type': order.director_legacy_commission_type,
                'rate': order.director_comm_percentage,
                'eligible_amount': order.director_commission,
                'status': self._get_commission_status(order, 'director'),
                'processed_amount': self._get_processed_amount(order, order.director_id),
                'paid_amount': self._get_paid_amount(order, order.director_id),
            })

        # Add other commission partners if they exist
        if hasattr(order, 'commission_partner_ids'):
            for partner in order.commission_partner_ids:
                if partner.id not in [p['partner_id'] for p in partners]:
                    partners.append({
                        'partner_id': partner.id,
                        'partner_name': partner.name,
                        'role': 'Commission Partner',
                        'commission_type': 'External',
                        'rate': 0.0,  # Would need to get from commission setup
                        'eligible_amount': 0.0,  # Would need calculation
                        'status': 'Pending',
                        'processed_amount': 0.0,
                        'paid_amount': 0.0,
                    })
        
        return partners

    def _get_commission_status(self, order, role):
        """Determine commission status based on order state and payments"""
        if order.state in ['draft', 'sent']:
            return 'Pending'
        elif order.state == 'cancel':
            return 'Cancelled'
        elif order.state in ['sale', 'done']:
            # Check if commission has been processed/paid
            # Role parameter can be used for role-specific status logic
            _logger.debug("Checking commission status for order %s and role %s", order.name, role)
            return 'Eligible'
        return 'Unknown'

    def _get_processed_amount(self, order, partner):
        """Get processed commission amount for partner - placeholder for actual logic"""
        # This should be implemented based on your commission processing system
        # Using parameters for future enhancement
        _logger.debug("Getting processed amount for order %s and partner %s", order.name, partner.name)
        return 0.0

    def _get_paid_amount(self, order, partner):
        """Get paid commission amount for partner - placeholder for actual logic"""
        # This should be implemented based on your commission payment system  
        # Using parameters for future enhancement
        _logger.debug("Getting paid amount for order %s and partner %s", order.name, partner.name)
        return 0.0

    def _get_unit_reference(self, order):
        """Get unit reference from order lines or related data"""
        unit_refs = []
        for line in order.order_line:
            if line.product_id and line.product_id.default_code:
                unit_refs.append(line.product_id.default_code)
        return ', '.join(unit_refs) if unit_refs else 'N/A'

    def _get_payment_info_for_order(self, order):
        """Get payment and invoice information for order"""
        total_invoiced = sum(order.invoice_ids.filtered(lambda inv: inv.state == 'posted').mapped('amount_total'))
        
        # Get total paid amount from invoice payments
        total_paid = 0.0
        for invoice in order.invoice_ids.filtered(lambda inv: inv.state == 'posted'):
            total_paid += invoice.amount_total - invoice.amount_residual
            
        return {
            'total_invoiced': total_invoiced,
            'total_paid': total_paid,
        }

    def _get_purchase_orders_info(self, order):
        """Get related purchase orders information"""
        # This depends on how purchase orders are linked to sale orders in your system
        pos = []
        if hasattr(order, 'purchase_order_ids'):
            for po in order.purchase_order_ids:
                pos.append({
                    'name': po.name,
                    'amount': po.amount_total,
                    'state': po.state,
                })
        return pos

    def _get_payment_count(self, order):
        """Get count of payments related to order"""
        payment_count = 0
        for invoice in order.invoice_ids:
            payment_count += len(invoice.payment_ids)
        return payment_count

    def _matches_status_filter(self, deal_data):
        """Check if deal matches the status filter"""
        if self.commission_status_filter == 'eligible':
            return deal_data['eligible_amount'] > 0
        elif self.commission_status_filter == 'processed':
            return deal_data['commission_processed'] > 0
        elif self.commission_status_filter == 'paid':
            return deal_data['commission_paid'] > 0
        elif self.commission_status_filter == 'pending':
            return deal_data['commission_pending'] > 0
        return True

    def action_generate_pdf_report(self):
        """Generate PDF deals commission report"""
        self.ensure_one()
        deals_data = self._get_deals_data()
        
        if not deals_data:
            raise UserError("No deals found for the selected criteria.")
        
        data = {
            'wizard_id': self.id,
            'deals_data': deals_data,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'partner_filter': self.partner_id.name if self.partner_id else 'All Partners',
            'project_filter': self.project_id.name if self.project_id else 'All Projects',
            'total_deals': len(deals_data),
            'total_eligible_amount': sum(d['eligible_amount'] for d in deals_data),
            'total_processed_amount': sum(d['commission_processed'] for d in deals_data),
            'total_paid_amount': sum(d['commission_paid'] for d in deals_data),
        }
        
        return self.env.ref('commission_ax.action_report_deals_commission').report_action(self, data=data)

    def action_generate_excel_report(self):
        """Generate Excel deals commission report"""
        self.ensure_one()
        deals_data = self._get_deals_data()
        
        if not deals_data:
            raise UserError("No deals found for the selected criteria.")
        
        # Create Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Deals Commission Report')
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#800020',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        data_format = workbook.add_format({
            'font_size': 10,
            'border': 1,
            'align': 'left',
            'valign': 'vcenter'
        })
        
        currency_format = workbook.add_format({
            'font_size': 10,
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'num_format': '#,##0.00'
        })
        
        # Write headers
        headers = [
            'Deal/Order', 'Customer', 'Booking Date', 'Project', 'Unit/Reference',
            'Order Amount', 'Partner', 'Role', 'Commission Type', 'Rate (%)',
            'Eligible Amount', 'Processed Amount', 'Paid Amount', 'Pending Amount',
            'Status', 'Total Invoiced', 'Total Paid', 'Order State'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Write data
        row = 1
        for deal in deals_data:
            worksheet.write(row, 0, deal['order_name'], data_format)
            worksheet.write(row, 1, deal['customer_name'], data_format)
            worksheet.write(row, 2, deal['booking_date'].strftime('%Y-%m-%d') if deal['booking_date'] else '', data_format)
            worksheet.write(row, 3, deal['project_name'], data_format)
            worksheet.write(row, 4, deal['unit_reference'], data_format)
            worksheet.write(row, 5, deal['order_amount'], currency_format)
            worksheet.write(row, 6, deal['partner_name'], data_format)
            worksheet.write(row, 7, deal['commission_role'], data_format)
            worksheet.write(row, 8, deal['commission_type'], data_format)
            worksheet.write(row, 9, deal['commission_rate'], data_format)
            worksheet.write(row, 10, deal['eligible_amount'], currency_format)
            worksheet.write(row, 11, deal['commission_processed'], currency_format)
            worksheet.write(row, 12, deal['commission_paid'], currency_format)
            worksheet.write(row, 13, deal['commission_pending'], currency_format)
            worksheet.write(row, 14, deal['commission_status'], data_format)
            worksheet.write(row, 15, deal['total_invoiced'], currency_format)
            worksheet.write(row, 16, deal['total_paid'], currency_format)
            worksheet.write(row, 17, deal['state_display'], data_format)
            row += 1
        
        # Auto-adjust column widths
        for col in range(len(headers)):
            worksheet.set_column(col, col, 15)
        
        workbook.close()
        
        # Create attachment
        report_data = base64.b64encode(output.getvalue())
        filename = f"Deals_Commission_Report_{self.date_from}_{self.date_to}.xlsx"
        
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': report_data,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }
