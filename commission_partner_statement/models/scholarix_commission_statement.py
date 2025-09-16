# -*- coding: utf-8 -*-
import json
from datetime import datetime

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class ScholarixCommissionStatement(models.Model):
    """SCHOLARIX Commission Statement Model for consolidated reporting"""
    _name = 'scholarix.commission.statement'
    _description = 'SCHOLARIX Commission Statement'
    _order = 'period_start desc, agent_id'
    _rec_name = 'display_name'

    # Core identification fields
    display_name = fields.Char(
        string='Statement Name',
        compute='_compute_display_name',
        store=True
    )
    
    # Period and agent information
    agent_id = fields.Many2one(
        'res.partner',
        string='Agent',
        required=True,
        domain=[('is_company', '=', False)],
        help='Commission agent/partner'
    )
    period_start = fields.Date(
        string='Period Start',
        required=True,
        help='Start date for commission period'
    )
    period_end = fields.Date(
        string='Period End', 
        required=True,
        help='End date for commission period'
    )
    
    # Commission calculation fields
    total_sales = fields.Monetary(
        string='Total Sales',
        help='Total sales amount for the period'
    )
    commission_rate = fields.Float(
        string='Average Commission Rate (%)',
        digits=(16, 2),
        help='Average commission rate for the period'
    )
    gross_commission = fields.Monetary(
        string='Gross Commission',
        help='Total commission before deductions'
    )
    deductions = fields.Monetary(
        string='Deductions',
        default=0.0,
        help='Deductions applied to commission'
    )
    net_commission = fields.Monetary(
        string='Net Commission',
        compute='_compute_net_commission',
        store=True,
        help='Final commission after deductions'
    )
    
    # Commission type breakdown
    direct_sales_commission = fields.Monetary(
        string='Direct Sales Commission (5%)',
        help='Commission from direct sales at 5%'
    )
    referral_bonus = fields.Monetary(
        string='Referral Bonus (2%)',
        help='Commission from referrals at 2%'
    )
    team_override = fields.Monetary(
        string='Team Override (1%)',
        help='Team override commission at 1%'
    )
    
    # Status and workflow
    payment_status = fields.Selection([
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Payment Status', default='pending', required=True)
    
    statement_status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('sent', 'Sent'),
        ('closed', 'Closed')
    ], string='Statement Status', default='draft', required=True)
    
    # System fields
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id.id,
        required=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    create_date = fields.Datetime(
        string='Created On',
        readonly=True
    )
    
    # Related order information
    commission_line_ids = fields.One2many(
        'scholarix.commission.line',
        'statement_id',
        string='Commission Lines',
        help='Detailed commission lines for this statement'
    )
    order_count = fields.Integer(
        string='Number of Orders',
        compute='_compute_order_count',
        help='Total number of orders in this statement'
    )
    
    # Agent information
    agent_email = fields.Char(
        related='agent_id.email',
        string='Agent Email',
        readonly=True
    )
    agent_phone = fields.Char(
        related='agent_id.phone',
        string='Agent Phone',
        readonly=True
    )
    
    @api.depends('agent_id', 'period_start', 'period_end')
    def _compute_display_name(self):
        """Generate display name for statement"""
        for statement in self:
            if statement.agent_id and statement.period_start and statement.period_end:
                statement.display_name = f"{statement.agent_id.name} - {statement.period_start} to {statement.period_end}"
            else:
                statement.display_name = "New Commission Statement"
    
    @api.depends('gross_commission', 'deductions')
    def _compute_net_commission(self):
        """Calculate net commission after deductions"""
        for statement in self:
            statement.net_commission = statement.gross_commission - statement.deductions
    
    @api.depends('commission_line_ids')
    def _compute_order_count(self):
        """Count number of orders in statement"""
        for statement in self:
            statement.order_count = len(statement.commission_line_ids)
    
    @api.constrains('period_start', 'period_end')
    def _check_period_dates(self):
        """Validate period dates"""
        for statement in self:
            if statement.period_start and statement.period_end:
                if statement.period_start > statement.period_end:
                    raise ValidationError(_("Period start date must be before end date."))
    
    def generate_commission_data(self):
        """Generate commission data for the specified period and agent"""
        self.ensure_one()
        
        # Clear existing lines
        self.commission_line_ids.unlink()
        
        # Get commission orders for this agent and period
        orders = self._get_commission_orders()
        
        # Process each order
        commission_lines = []
        total_sales = 0.0
        total_commission = 0.0
        direct_sales_total = 0.0
        referral_total = 0.0
        team_override_total = 0.0
        
        for order in orders:
            commission_details = self.agent_id._get_partner_commission_details_from_order(order)
            order_commission = self.agent_id._get_partner_commission_from_order(order)
            
            if order_commission > 0:
                # Categorize commission types
                direct_sales_amount = 0.0
                referral_amount = 0.0
                team_amount = 0.0
                
                for detail in commission_details:
                    if detail.get('category') in ['Broker', 'Agent1', 'Agent2']:
                        direct_sales_amount += detail.get('amount', 0.0)
                    elif detail.get('category') in ['Referrer', 'Cashback']:
                        referral_amount += detail.get('amount', 0.0)
                    elif detail.get('category') in ['Manager', 'Director']:
                        team_amount += detail.get('amount', 0.0)
                
                # Create commission line
                line_vals = {
                    'statement_id': self.id,
                    'order_id': order.id,
                    'order_reference': order.name,
                    'order_date': order.date_order,
                    'customer_id': order.partner_id.id,
                    'order_amount': order.amount_total,
                    'commission_amount': order_commission,
                    'direct_sales_commission': direct_sales_amount,
                    'referral_commission': referral_amount,
                    'team_commission': team_amount,
                    'commission_details': json.dumps(commission_details),
                }
                commission_lines.append((0, 0, line_vals))
                
                # Update totals
                total_sales += order.amount_total
                total_commission += order_commission
                direct_sales_total += direct_sales_amount
                referral_total += referral_amount
                team_override_total += team_amount
        
        # Update statement totals
        self.write({
            'commission_line_ids': commission_lines,
            'total_sales': total_sales,
            'gross_commission': total_commission,
            'direct_sales_commission': direct_sales_total,
            'referral_bonus': referral_total,
            'team_override': team_override_total,
            'commission_rate': (total_commission / total_sales * 100) if total_sales > 0 else 0.0,
        })
    
    def _get_commission_orders(self):
        """Get commission orders for this agent and period"""
        domain = [
            ('date_order', '>=', self.period_start),
            ('date_order', '<=', self.period_end),
            ('state', 'in', ['sale', 'done']),
            '|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|',
            # External commissions
            ('broker_partner_id', '=', self.agent_id.id),
            ('referrer_partner_id', '=', self.agent_id.id),
            ('cashback_partner_id', '=', self.agent_id.id),
            ('other_external_partner_id', '=', self.agent_id.id),
            # Internal commissions
            ('agent1_partner_id', '=', self.agent_id.id),
            ('agent2_partner_id', '=', self.agent_id.id),
            ('manager_partner_id', '=', self.agent_id.id),
            ('director_partner_id', '=', self.agent_id.id),
            # Legacy commissions
            ('consultant_id', '=', self.agent_id.id),
            ('manager_id', '=', self.agent_id.id),
            ('second_agent_id', '=', self.agent_id.id),
            ('director_id', '=', self.agent_id.id),
        ]
        
        return self.env['sale.order'].search(domain, order='date_order desc')
    
    @api.model
    def generate_consolidated_report(self, period_start, period_end, agent_ids=None):
        """
        Generate consolidated commission report for all or selected agents
        
        Args:
            period_start (date): Start date for commission period
            period_end (date): End date for commission period  
            agent_ids (list, optional): Specific agents to include
            
        Returns:
            dict: Report data structure for rendering
        """
        # Get agents with commissions in the period
        if agent_ids:
            agents = self.env['res.partner'].browse(agent_ids)
        else:
            # Find all agents with commissions in the period
            order_domain = [
                ('date_order', '>=', period_start),
                ('date_order', '<=', period_end),
                ('state', 'in', ['sale', 'done']),
            ]
            orders = self.env['sale.order'].search(order_domain)
            
            agent_ids = set()
            for order in orders:
                # Collect all agents from commission fields
                for field_name in ['broker_partner_id', 'referrer_partner_id', 'cashback_partner_id',
                                 'other_external_partner_id', 'agent1_partner_id', 'agent2_partner_id',
                                 'manager_partner_id', 'director_partner_id', 'consultant_id',
                                 'manager_id', 'second_agent_id', 'director_id']:
                    if hasattr(order, field_name):
                        agent = getattr(order, field_name)
                        if agent:
                            agent_ids.add(agent.id)
            
            agents = self.env['res.partner'].browse(list(agent_ids))
        
        # Generate or update statements for each agent
        statements = []
        total_agents = len(agents)
        total_sales = 0.0
        total_commission = 0.0
        
        for agent in agents:
            # Find or create statement for this period
            existing_statement = self.search([
                ('agent_id', '=', agent.id),
                ('period_start', '=', period_start),
                ('period_end', '=', period_end)
            ], limit=1)
            
            if existing_statement:
                statement = existing_statement
            else:
                statement = self.create({
                    'agent_id': agent.id,
                    'period_start': period_start,
                    'period_end': period_end,
                })
            
            # Generate commission data
            statement.generate_commission_data()
            statements.append(statement)
            
            total_sales += statement.total_sales
            total_commission += statement.gross_commission
        
        # Prepare consolidated report data
        report_data = {
            'period_start': period_start,
            'period_end': period_end,
            'total_agents': total_agents,
            'total_sales': total_sales,
            'total_commission': total_commission,
            'average_commission_per_agent': total_commission / total_agents if total_agents > 0 else 0.0,
            'statements': statements,
            'generation_date': datetime.now(),
        }
        
        return report_data
    
    def action_confirm_statement(self):
        """Confirm the commission statement"""
        self.write({'statement_status': 'confirmed'})
    
    def action_send_statement(self):
        """Send commission statement to agent"""
        if not self.agent_email:
            raise UserError(_("Agent email is required to send statement."))
        
        # Generate PDF and send email
        # Implementation would use mail template
        self.write({'statement_status': 'sent'})
    
    def action_mark_paid(self):
        """Mark commission as paid"""
        self.write({'payment_status': 'paid'})


class ScholarixCommissionLine(models.Model):
    """Individual commission line items"""
    _name = 'scholarix.commission.line'
    _description = 'SCHOLARIX Commission Line'
    _order = 'order_date desc'

    statement_id = fields.Many2one(
        'scholarix.commission.statement',
        string='Commission Statement',
        required=True,
        ondelete='cascade'
    )
    
    # Order information
    order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        required=True
    )
    order_reference = fields.Char(
        string='Order Reference',
        required=True
    )
    order_date = fields.Date(
        string='Order Date',
        required=True
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True
    )
    
    # Commission details
    order_amount = fields.Monetary(
        string='Order Amount',
        currency_field='currency_id'
    )
    commission_amount = fields.Monetary(
        string='Total Commission',
        currency_field='currency_id'
    )
    
    # Commission type breakdown
    direct_sales_commission = fields.Monetary(
        string='Direct Sales (5%)',
        currency_field='currency_id'
    )
    referral_commission = fields.Monetary(
        string='Referral Bonus (2%)',
        currency_field='currency_id'
    )
    team_commission = fields.Monetary(
        string='Team Override (1%)',
        currency_field='currency_id'
    )
    
    # Technical fields
    currency_id = fields.Many2one(
        related='statement_id.currency_id',
        string='Currency',
        readonly=True
    )
    commission_details = fields.Text(
        string='Commission Details JSON',
        help='Detailed commission breakdown in JSON format'
    )
    
    # Status
    order_status = fields.Selection(
        related='order_id.state',
        string='Order Status',
        readonly=True
    )
    
    @api.depends('commission_amount', 'order_amount')
    def _compute_commission_rate(self):
        """Calculate commission rate for this line"""
        for line in self:
            if line.order_amount > 0:
                line.commission_rate = (line.commission_amount / line.order_amount) * 100
            else:
                line.commission_rate = 0.0
    
    commission_rate = fields.Float(
        string='Commission Rate (%)',
        compute='_compute_commission_rate',
        digits=(16, 2)
    )
