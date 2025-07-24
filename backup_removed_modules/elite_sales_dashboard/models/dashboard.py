from odoo import models, fields, api, _
from datetime import datetime, timedelta

class AgentType(models.Model):
    _name = 'elite.agent.type'
    _description = 'Agent Type'
    
    name = fields.Char('Type', required=True)
    is_internal = fields.Boolean('Internal', default=True,
        help="Internal agents are employees of the company. External agents are partners.")


class AgentDashboard(models.Model):
    _name = 'elite.agent.dashboard'
    _description = 'Elite Agent Dashboard'
    _rec_name = 'agent_id'
    
    agent_id = fields.Many2one('res.partner', string='Agent', required=True)
    user_id = fields.Many2one('res.users', string='Related User')
    agent_type_id = fields.Many2one('elite.agent.type', string='Agent Type', required=True)
    is_internal = fields.Boolean(related='agent_type_id.is_internal', store=True)
    
    # Performance metrics
    total_sales = fields.Monetary('Total Sales', currency_field='company_currency_id')
    deals_count = fields.Integer('Deals Count')
    in_progress_count = fields.Integer('In Progress Count')
    in_progress_value = fields.Monetary('In Progress Value', currency_field='company_currency_id')
    pending_value = fields.Monetary('Pending Value', currency_field='company_currency_id')
    commission_earned = fields.Monetary('Commission Earned', currency_field='company_currency_id')
    rank = fields.Integer('Rank', default=0)
    previous_rank = fields.Integer('Previous Rank', default=0)
    
    # Reference fields
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    
    _sql_constraints = [
        ('unique_agent', 'UNIQUE(agent_id)', 'An agent can only appear once in the dashboard!')
    ]
    
    @api.model
    def _update_dashboard_data(self):
        """Update dashboard data from sales orders and commission records"""
        self._create_sample_data()
        self._update_rankings()
        return True
    
    @api.model
    def _create_sample_data(self):
        """Create sample data for demo purposes"""
        agent_types = {
            'internal': self.env['elite.agent.type'].create({'name': 'Internal Agent', 'is_internal': True}),
            'external': self.env['elite.agent.type'].create({'name': 'External Partner', 'is_internal': False})
        }
        
        # Sample data
        agents_data = [
            # Internal agents
            {'name': 'Emma Rodriguez', 'type': 'internal', 'total_sales': 2500000, 'deals_count': 48, 'in_progress_count': 7, 'in_progress_value': 320000, 'pending_value': 3200000},
            {'name': 'Michael Chen', 'type': 'internal', 'total_sales': 2100000, 'deals_count': 42, 'in_progress_count': 9, 'in_progress_value': 280000, 'pending_value': 1900000},
            # Add more sample data as needed
        ]
        
        for agent_data in agents_data:
            partner = self.env['res.partner'].search([('name', '=', agent_data['name'])], limit=1)
            if not partner:
                partner = self.env['res.partner'].create({
                    'name': agent_data['name'],
                    'company_type': 'person',
                    'is_company': False,
                })
            
            self.create({
                'agent_id': partner.id,
                'agent_type_id': agent_types[agent_data['type']].id,
                'total_sales': agent_data['total_sales'],
                'deals_count': agent_data['deals_count'],
                'in_progress_count': agent_data['in_progress_count'],
                'in_progress_value': agent_data['in_progress_value'],
                'pending_value': agent_data['pending_value'],
                'commission_earned': agent_data['total_sales'] * 0.03,
            })
    
    def _update_rankings(self):
        """Update agent rankings based on total sales"""
        # Internal agents
        internal_agents = self.search([('is_internal', '=', True)], order='total_sales desc')
        for i, agent in enumerate(internal_agents):
            agent.previous_rank = agent.rank
            agent.rank = i + 1
        
        # External agents
        external_agents = self.search([('is_internal', '=', False)], order='total_sales desc')
        for i, agent in enumerate(external_agents):
            agent.previous_rank = agent.rank
            agent.rank = i + 1
    
    @api.model
    def get_dashboard_data(self, agent_type='internal'):
        """Get dashboard data for the frontend"""
        is_internal = agent_type == 'internal'
        agents = self.search([('is_internal', '=', is_internal)], order='total_sales desc')
        
        # Calculate totals
        total_earnings = sum(agents.mapped('total_sales'))
        completed_deals = sum(agents.mapped('deals_count'))
        in_progress_deals = sum(agents.mapped('in_progress_count'))
        in_progress_value = sum(agents.mapped('in_progress_value'))
        
        # Calculate month-over-month change
        prev_month_earnings = total_earnings * 0.807  # Mock 8.7% increase
        mom_change = ((total_earnings - prev_month_earnings) / prev_month_earnings) * 100 if prev_month_earnings else 0
        
        # Format leaderboard data
        leaderboard = []
        for agent in agents:
            leaderboard.append({
                'id': agent.id,
                'name': agent.agent_id.name,
                'rank': agent.rank,
                'deals_count': agent.deals_count,
                'in_progress_count': agent.in_progress_count,
                'total_sales': agent.total_sales,
                'pending_value': agent.pending_value,
                'rank_change': agent.previous_rank - agent.rank if agent.previous_rank > 0 else 0,
            })
        
        return {
            'total_earnings': total_earnings,
            'completed_deals': completed_deals,
            'agents_count': len(agents),
            'in_progress_deals': in_progress_deals,
            'in_progress_value': in_progress_value,
            'mom_change': mom_change,
            'leaderboard': leaderboard,
            'annual_trend': self._get_annual_trend_data(),
            'avg_per_agent': completed_deals / len(agents) if agents else 0,
        }
    
    @api.model
    def _get_annual_trend_data(self):
        """Get annual sales trend data"""
        return {
            'Jan': 1500000, 'Feb': 1400000, 'Mar': 1700000,
            'Apr': 1800000, 'May': 2000000, 'Jun': 2200000,
            'Jul': 2500000, 'Aug': 2700000, 'Sep': 3000000,
            'Oct': 3300000, 'Nov': 3800000, 'Dec': 4500000,
        }


class DashboardSettings(models.Model):
    _name = 'elite.dashboard.settings'
    _description = 'Dashboard Settings'
    
    name = fields.Char('Setting Name', required=True)
    refresh_interval = fields.Integer('Refresh Interval (seconds)', default=5)
    show_rank_changes = fields.Boolean('Show Rank Changes', default=True)
    
    @api.model
    def get_settings(self):
        """Get dashboard settings"""
        settings = self.search([], limit=1)
        if not settings:
            settings = self.create({'name': 'Default Settings'})
        return {
            'refresh_interval': settings.refresh_interval,
            'show_rank_changes': settings.show_rank_changes,
        }