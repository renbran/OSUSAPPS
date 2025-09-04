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
        help='Sale Orders where this partner receives commission'
    )
    total_commission_amount = fields.Monetary(
        string='Total Commission Amount',
        compute='_compute_commission_totals',
        help='Total commission amount from all orders'
    )
    commission_order_count = fields.Integer(
        string='Commission Orders Count',
        compute='_compute_commission_totals',
        help='Number of orders with commission for this partner'
    )
    last_commission_date = fields.Date(
        string='Last Commission Date',
        compute='_compute_commission_totals',
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
            commission_orders = self.env['sale.order'].search([
                '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|',
                # External commissions
                ('broker_partner_id', '=', partner.id),
                ('referrer_partner_id', '=', partner.id),
                ('cashback_partner_id', '=', partner.id),
                ('other_external_partner_id', '=', partner.id),
                # Internal commissions
                ('agent1_partner_id', '=', partner.id),
                ('agent2_partner_id', '=', partner.id),
                ('manager_partner_id', '=', partner.id),
                ('director_partner_id', '=', partner.id),
                # Legacy commissions
                ('consultant_id', '=', partner.id),
                ('manager_id', '=', partner.id),
                ('second_agent_id', '=', partner.id),
                ('director_id', '=', partner.id),
            ])
            partner.commission_sale_order_ids = commission_orders

    @api.depends('commission_sale_order_ids')
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
            
        domain = [
            '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|',
            # External commissions
            ('broker_partner_id', '=', self.id),
            ('referrer_partner_id', '=', self.id),
            ('cashback_partner_id', '=', self.id),
            ('other_external_partner_id', '=', self.id),
            # Internal commissions
            ('agent1_partner_id', '=', self.id),
            ('agent2_partner_id', '=', self.id),
            ('manager_partner_id', '=', self.id),
            ('director_partner_id', '=', self.id),
            # Legacy commissions
            ('consultant_id', '=', self.id),
            ('manager_id', '=', self.id),
            ('second_agent_id', '=', self.id),
            ('director_id', '=', self.id),
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
        
        data = self.commission_statement_query(date_from, date_to)
        
        return self.env.ref('commission_partner_statement.action_commission_partner_statement_pdf').report_action(
            self, data=data
        )

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
