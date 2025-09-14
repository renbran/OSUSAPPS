# -*- coding: utf-8 -*-

import base64
import io
import json
import xlsxwriter
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import date_utils


class Partner(models.Model):
    """Extended Partner with Commission Statement capabilities"""
    _inherit = 'res.partner'

    # Commission-related computed fields
    commission_sale_order_ids = fields.Many2many(
        'sale.order',
        compute='_compute_commission_sale_orders',
        store=True,
        help='Sale Orders where this partner receives commission'
    )
    total_commission_amount = fields.Monetary(
        string='Total Commission Amount',
        compute='_compute_commission_totals',
        store=True,
        help='Total commission amount from all orders'
    )
    commission_order_count = fields.Integer(
        string='Commission Orders Count',
        compute='_compute_commission_totals',
        store=True,
        help='Number of orders with commission for this partner'
    )
    last_commission_date = fields.Date(
        string='Last Commission Date',
        compute='_compute_commission_totals',
        store=True,
        help='Date of last commission order'
    )
    
    # Report configuration fields
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id.id,
        help="Currency for commission calculations"
    )
    enable_auto_commission_statement = fields.Boolean(
        string='Auto Commission Statement',
        default=False,
        help='Enable automatic monthly commission statement generation'
    )

    @api.depends('name')
    def _compute_commission_sale_orders(self):
        """Compute sale orders where this partner receives commission"""
        for partner in self:
            # DEFENSIVE FIX: Ensure partner.id is always an integer, never a list
            partner_id = partner.id
            if isinstance(partner_id, (list, tuple)):
                # If somehow partner.id is a list, take the first element
                partner_id = partner_id[0] if partner_id else False
                # Log this as it should not happen
                import logging
                _logger = logging.getLogger(__name__)
                _logger.warning("Partner ID was unexpectedly a list: %s. Using %s", partner.id, partner_id)
            
            if not partner_id:
                partner.commission_sale_order_ids = self.env['sale.order']
                continue
                
            commission_orders = self.env['sale.order'].search([
                '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|',
                # External commissions
                ('broker_partner_id', '=', partner_id),
                ('referrer_partner_id', '=', partner_id),
                ('cashback_partner_id', '=', partner_id),
                ('other_external_partner_id', '=', partner_id),
                # Internal commissions
                ('agent1_partner_id', '=', partner_id),
                ('agent2_partner_id', '=', partner_id),
                ('manager_partner_id', '=', partner_id),
                ('director_partner_id', '=', partner_id),
                # Legacy commissions
                ('consultant_id', '=', partner_id),
                ('manager_id', '=', partner_id),
                ('second_agent_id', '=', partner_id),
                ('director_id', '=', partner_id),
            ])
            partner.commission_sale_order_ids = commission_orders

    @api.depends('commission_sale_order_ids', 'commission_sale_order_ids.broker_amount',
                 'commission_sale_order_ids.referrer_amount', 'commission_sale_order_ids.cashback_amount',
                 'commission_sale_order_ids.other_external_amount', 'commission_sale_order_ids.agent1_amount',
                 'commission_sale_order_ids.agent2_amount', 'commission_sale_order_ids.manager_amount',
                 'commission_sale_order_ids.director_amount', 'commission_sale_order_ids.salesperson_commission',
                 'commission_sale_order_ids.manager_commission', 'commission_sale_order_ids.second_agent_commission',
                 'commission_sale_order_ids.director_commission', 'commission_sale_order_ids.date_order')
    def _compute_commission_totals(self):
        """Compute commission totals and statistics"""
        for partner in self:
            orders = partner.commission_sale_order_ids
            total_amount = 0.0
            last_date = False
            
            for order in orders:
                # Calculate partner's commission from this order
                commission_amount = partner._get_partner_commission_from_order(order)
                total_amount += commission_amount
                
                if order.date_order:
                    order_date = order.date_order.date()
                    if not last_date or order_date > last_date:
                        last_date = order_date
            
            partner.total_commission_amount = total_amount
            partner.commission_order_count = len(orders)
            partner.last_commission_date = last_date

    def _get_partner_commission_from_order(self, order):
        """Get commission amount for this partner from a specific order"""
        commission_amount = 0.0
        
        # External commissions
        if hasattr(order, 'broker_partner_id') and order.broker_partner_id.id == self.id:
            commission_amount += getattr(order, 'broker_amount', 0.0) or 0.0
        if hasattr(order, 'referrer_partner_id') and order.referrer_partner_id.id == self.id:
            commission_amount += getattr(order, 'referrer_amount', 0.0) or 0.0
        if hasattr(order, 'cashback_partner_id') and order.cashback_partner_id.id == self.id:
            commission_amount += getattr(order, 'cashback_amount', 0.0) or 0.0
        if hasattr(order, 'other_external_partner_id') and order.other_external_partner_id.id == self.id:
            commission_amount += getattr(order, 'other_external_amount', 0.0) or 0.0
            
        # Internal commissions
        if hasattr(order, 'agent1_partner_id') and order.agent1_partner_id.id == self.id:
            commission_amount += getattr(order, 'agent1_amount', 0.0) or 0.0
        if hasattr(order, 'agent2_partner_id') and order.agent2_partner_id.id == self.id:
            commission_amount += getattr(order, 'agent2_amount', 0.0) or 0.0
        if hasattr(order, 'manager_partner_id') and order.manager_partner_id.id == self.id:
            commission_amount += getattr(order, 'manager_amount', 0.0) or 0.0
        if hasattr(order, 'director_partner_id') and order.director_partner_id.id == self.id:
            commission_amount += getattr(order, 'director_amount', 0.0) or 0.0
            
        # Legacy commissions
        if hasattr(order, 'consultant_id') and order.consultant_id.id == self.id:
            commission_amount += getattr(order, 'salesperson_commission', 0.0) or 0.0
        if hasattr(order, 'manager_id') and order.manager_id.id == self.id:
            commission_amount += getattr(order, 'manager_commission', 0.0) or 0.0
        if hasattr(order, 'second_agent_id') and order.second_agent_id.id == self.id:
            commission_amount += getattr(order, 'second_agent_commission', 0.0) or 0.0
        if hasattr(order, 'director_id') and order.director_id.id == self.id:
            commission_amount += getattr(order, 'director_commission', 0.0) or 0.0
            
        return commission_amount

    def _get_partner_commission_details_from_order(self, order):
        """Get detailed commission information for this partner from an order"""
        details = []
        
        # External commissions
        if hasattr(order, 'broker_partner_id') and order.broker_partner_id.id == self.id and getattr(order, 'broker_amount', 0) > 0:
            details.append({
                'type': 'External',
                'category': 'Broker',
                'rate': getattr(order, 'broker_rate', 0),
                'commission_type': getattr(order, 'broker_commission_type', 'fixed'),
                'amount': getattr(order, 'broker_amount', 0),
            })
        if hasattr(order, 'referrer_partner_id') and order.referrer_partner_id.id == self.id and getattr(order, 'referrer_amount', 0) > 0:
            details.append({
                'type': 'External',
                'category': 'Referrer',
                'rate': getattr(order, 'referrer_rate', 0),
                'commission_type': getattr(order, 'referrer_commission_type', 'fixed'),
                'amount': getattr(order, 'referrer_amount', 0),
            })
        if hasattr(order, 'cashback_partner_id') and order.cashback_partner_id.id == self.id and getattr(order, 'cashback_amount', 0) > 0:
            details.append({
                'type': 'External',
                'category': 'Cashback',
                'rate': getattr(order, 'cashback_rate', 0),
                'commission_type': getattr(order, 'cashback_commission_type', 'fixed'),
                'amount': getattr(order, 'cashback_amount', 0),
            })
        if hasattr(order, 'other_external_partner_id') and order.other_external_partner_id.id == self.id and getattr(order, 'other_external_amount', 0) > 0:
            details.append({
                'type': 'External',
                'category': 'Other External',
                'rate': getattr(order, 'other_external_rate', 0),
                'commission_type': getattr(order, 'other_external_commission_type', 'fixed'),
                'amount': getattr(order, 'other_external_amount', 0),
            })
            
        # Internal commissions
        if hasattr(order, 'agent1_partner_id') and order.agent1_partner_id.id == self.id and getattr(order, 'agent1_amount', 0) > 0:
            details.append({
                'type': 'Internal',
                'category': 'Agent 1',
                'rate': getattr(order, 'agent1_rate', 0),
                'commission_type': getattr(order, 'agent1_commission_type', 'fixed'),
                'amount': getattr(order, 'agent1_amount', 0),
            })
        if hasattr(order, 'agent2_partner_id') and order.agent2_partner_id.id == self.id and getattr(order, 'agent2_amount', 0) > 0:
            details.append({
                'type': 'Internal',
                'category': 'Agent 2',
                'rate': getattr(order, 'agent2_rate', 0),
                'commission_type': getattr(order, 'agent2_commission_type', 'fixed'),
                'amount': getattr(order, 'agent2_amount', 0),
            })
        if hasattr(order, 'manager_partner_id') and order.manager_partner_id.id == self.id and getattr(order, 'manager_amount', 0) > 0:
            details.append({
                'type': 'Internal',
                'category': 'Manager',
                'rate': getattr(order, 'manager_rate', 0),
                'commission_type': getattr(order, 'manager_commission_type', 'fixed'),
                'amount': getattr(order, 'manager_amount', 0),
            })
        if hasattr(order, 'director_partner_id') and order.director_partner_id.id == self.id and getattr(order, 'director_amount', 0) > 0:
            details.append({
                'type': 'Internal',
                'category': 'Director',
                'rate': getattr(order, 'director_rate', 0),
                'commission_type': getattr(order, 'director_commission_type', 'fixed'),
                'amount': getattr(order, 'director_amount', 0),
            })
            
        # Legacy commissions
        if hasattr(order, 'consultant_id') and order.consultant_id.id == self.id and getattr(order, 'salesperson_commission', 0) > 0:
            details.append({
                'type': 'Legacy',
                'category': 'Consultant',
                'rate': getattr(order, 'consultant_comm_percentage', 0),
                'commission_type': getattr(order, 'consultant_commission_type', 'fixed'),
                'amount': getattr(order, 'salesperson_commission', 0),
            })
        if hasattr(order, 'manager_id') and order.manager_id.id == self.id and getattr(order, 'manager_commission', 0) > 0:
            details.append({
                'type': 'Legacy',
                'category': 'Manager',
                'rate': getattr(order, 'manager_comm_percentage', 0),
                'commission_type': getattr(order, 'manager_legacy_commission_type', 'fixed'),
                'amount': getattr(order, 'manager_commission', 0),
            })
        if hasattr(order, 'second_agent_id') and order.second_agent_id.id == self.id and getattr(order, 'second_agent_commission', 0) > 0:
            details.append({
                'type': 'Legacy',
                'category': 'Second Agent',
                'rate': getattr(order, 'second_agent_comm_percentage', 0),
                'commission_type': getattr(order, 'second_agent_commission_type', 'fixed'),
                'amount': getattr(order, 'second_agent_commission', 0),
            })
        if hasattr(order, 'director_id') and order.director_id.id == self.id and getattr(order, 'director_commission', 0) > 0:
            details.append({
                'type': 'Legacy',
                'category': 'Director',
                'rate': getattr(order, 'director_comm_percentage', 0),
                'commission_type': getattr(order, 'director_legacy_commission_type', 'fixed'),
                'amount': getattr(order, 'director_commission', 0),
            })
            
        return details

    def commission_statement_query(self, date_from=None, date_to=None):
        """Return commission statement data for this partner"""
        if not date_from:
            date_from = date.today().replace(day=1)  # First day of current month
        if not date_to:
            date_to = date.today()
        
        # DEFENSIVE FIX: Ensure self.id is always an integer, never a list
        partner_id = self.id
        if isinstance(partner_id, (list, tuple)):
            partner_id = partner_id[0] if partner_id else False
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning("Partner ID was unexpectedly a list in commission_statement_query: %s. Using %s", self.id, partner_id)
        
        if not partner_id:
            return {
                'partner': self,
                'date_from': date_from,
                'date_to': date_to,
                'statement_lines': [],
                'total_amount': 0.0,
                'orders_count': 0,
                'currency': self.currency_id,
            }
            
        domain = [
            '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|',
            # External commissions
            ('broker_partner_id', '=', partner_id),
            ('referrer_partner_id', '=', partner_id),
            ('cashback_partner_id', '=', partner_id),
            ('other_external_partner_id', '=', partner_id),
            # Internal commissions
            ('agent1_partner_id', '=', partner_id),
            ('agent2_partner_id', '=', partner_id),
            ('manager_partner_id', '=', partner_id),
            ('director_partner_id', '=', partner_id),
            # Legacy commissions
            ('consultant_id', '=', partner_id),
            ('manager_id', '=', partner_id),
            ('second_agent_id', '=', partner_id),
            ('director_id', '=', partner_id),
        ]
        
        # Add date range filter
        domain.extend([
            ('date_order', '>=', date_from),
            ('date_order', '<=', date_to),
            ('state', 'in', ['sale', 'done']),  # Only confirmed orders
        ])
        
        orders = self.env['sale.order'].search(domain, order='date_order desc')
        
        statement_lines = []
        total_amount = 0.0
        
        for order in orders:
            commission_details = self._get_partner_commission_details_from_order(order)
            
            for detail in commission_details:
                statement_lines.append({
                    'order_ref': order.name,
                    'order_date': order.date_order,
                    'customer_name': order.partner_id.name,
                    'customer_ref': getattr(order, 'client_order_ref', '') or '',
                    'commission_type': detail['type'],
                    'commission_category': detail['category'],
                    'commission_type_display': detail['commission_type'].title(),
                    'rate': detail['rate'],
                    'amount': detail['amount'],
                    'order_total': order.amount_total,
                    'order_state': order.state,
                    'commission_status': getattr(order, 'commission_status', 'draft'),
                })
                total_amount += detail['amount']
        
        return {
            'partner': self,
            'date_from': date_from,
            'date_to': date_to,
            'statement_lines': statement_lines,
            'total_amount': total_amount,
            'orders_count': len(orders),
            'currency': self.currency_id,
        }

    def action_view_commission_orders(self):
        """Action to view commission sale orders"""
        self.ensure_one()
        action = self.env.ref('sale.action_orders').read()[0]
        action['domain'] = [('id', 'in', self.commission_sale_order_ids.ids)]
        action['context'] = {'search_default_partner_id': self.id}
        return action

    def action_generate_commission_statement_pdf(self):
        """Generate PDF commission statement report"""
        self.ensure_one()
        if not self.commission_sale_order_ids:
            raise UserError(_("No commission orders found for partner %s") % self.name)
            
        # Get date range (current month by default)
        date_from = date.today().replace(day=1)
        date_to = date.today()
        
        try:
            # Get the report reference
            report_ref = 'commission_partner_statement.action_commission_partner_statement_pdf'
            report_action = self.env.ref(report_ref)
            
            # Generate the report
            return report_action.report_action(self)
        except Exception as e:
            # Fallback to direct PDF generation
            report_obj = self.env['ir.actions.report']
            template_name = 'commission_partner_statement.commission_partner_statement_template'
            
            # Prepare data for the report
            data = {
                'date_from': date_from.strftime('%Y-%m-%d'),
                'date_to': date_to.strftime('%Y-%m-%d'),
            }
            
            try:
                # Generate PDF directly using the template
                pdf_content, content_type = report_obj._render_qweb_pdf(template_name, self.ids, data=data)
                
                # Return as file download
                return {
                    'type': 'ir.actions.act_url',
                    'url': '/web/content/?model=res.partner&id=%s&field=commission_statement_pdf&filename=Commission_Statement_%s.pdf' % (self.id, self.name.replace(' ', '_')),
                    'target': 'self',
                }
            except Exception as pdf_error:
                raise UserError(_("Error generating commission statement: %s") % str(pdf_error))

    def action_generate_commission_statement_excel(self):
        """Generate Excel commission statement report"""
        self.ensure_one()
        data = self.commission_statement_query()
        
        if not data['statement_lines']:
            raise UserError(_("No commission data found for the selected period."))
        
        return {
            'type': 'ir.actions.act_url',
            'url': '/commission_partner_statement/excel_report/%s' % self.id,
            'target': 'new',
        }

    def action_share_commission_statement(self):
        """Share commission statement via email"""
        self.ensure_one()
        if not self.email:
            raise UserError(_("Partner %s has no email address configured.") % self.name)
            
        # Create email template context
        template = self.env.ref('commission_partner_statement.email_template_commission_statement', False)
        if template:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'mail.compose.message',
                'view_mode': 'form',
                'view_id': self.env.ref('mail.email_compose_message_wizard_form').id,
                'target': 'new',
                'context': {
                    'default_model': 'res.partner',
                    'default_res_id': self.id,
                    'default_template_id': template.id,
                    'default_composition_mode': 'comment',
                }
            }

    @api.model
    def _cron_generate_monthly_commission_statements(self):
        """Cron job to generate monthly commission statements"""
        # Get partners with auto statement enabled
        partners = self.search([
            ('enable_auto_commission_statement', '=', True),
            ('email', '!=', False),
        ])
        
        # Get last month date range
        today = date.today()
        first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day_last_month = today.replace(day=1) - timedelta(days=1)
        
        for partner in partners:
            try:
                data = partner.commission_statement_query(first_day_last_month, last_day_last_month)
                if data['statement_lines']:
                    # Send commission statement email
                    partner._send_commission_statement_email(data)
                    self.env.cr.commit()  # Commit after each partner
            except Exception as e:
                self.env.cr.rollback()
                continue

    def _send_commission_statement_email(self, data):
        """Send commission statement email to partner"""
        template = self.env.ref('commission_partner_statement.email_template_commission_statement', False)
        if template:
            template.with_context(commission_data=data).send_mail(self.id, force_send=True)

    # SCHOLARIX-specific methods
    def action_view_scholarix_statements(self):
        """View SCHOLARIX commission statements for this partner"""
        statements = self.env['scholarix.commission.statement'].search([
            ('agent_id', '=', self.id)
        ])
        
        return {
            'name': f'SCHOLARIX Statements - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'scholarix.commission.statement',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', statements.ids)],
            'context': {
                'default_agent_id': self.id,
                'search_default_group_by_payment_status': 1,
            }
        }
    
    def action_generate_scholarix_statement(self):
        """Generate SCHOLARIX statement for this partner"""
        # Get last month as default period
        today = date.today()
        first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day_last_month = today.replace(day=1) - timedelta(days=1)
        
        # Check if statement already exists
        existing = self.env['scholarix.commission.statement'].search([
            ('agent_id', '=', self.id),
            ('period_start', '=', first_day_last_month),
            ('period_end', '=', last_day_last_month)
        ], limit=1)
        
        if existing:
            statement = existing
            statement.generate_commission_data()
        else:
            statement = self.env['scholarix.commission.statement'].create({
                'agent_id': self.id,
                'period_start': first_day_last_month,
                'period_end': last_day_last_month,
            })
            statement.generate_commission_data()
        
        return {
            'name': f'SCHOLARIX Statement - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'scholarix.commission.statement',
            'res_id': statement.id,
            'view_mode': 'form',
            'target': 'current',
        }
