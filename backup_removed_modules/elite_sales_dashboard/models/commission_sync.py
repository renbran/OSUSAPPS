from odoo import models, fields, api
import logging
import requests
import json
from datetime import datetime

_logger = logging.getLogger(__name__)

class CommissionSync(models.Model):
    _name = 'elite.commission.sync'
    _description = 'Commission Sync'
    
    name = fields.Char('Name', default='Commission Sync')
    last_sync = fields.Datetime('Last Sync')
    api_endpoint = fields.Char('API Endpoint')
    api_key = fields.Char('API Key')
    sync_interval = fields.Integer('Sync Interval (minutes)', default=60)
    is_active = fields.Boolean('Active', default=True)
    
    def _sync_commissions(self):
        """Sync commissions from external system"""
        if not self.is_active or not self.api_endpoint or not self.api_key:
            return False
            
        try:
            # This is a placeholder for the actual API call
            # In a real implementation, you would make HTTP requests to your commission system
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Get internal agents data
            internal_response = requests.get(
                f'{self.api_endpoint}/api/commissions/internal',
                headers=headers
            )
            internal_data = internal_response.json()
            
            # Get external agents data
            external_response = requests.get(
                f'{self.api_endpoint}/api/commissions/external',
                headers=headers
            )
            external_data = external_response.json()
            
            # Process the data and update agent performance
            self._process_commission_data(internal_data, external_data)
            
            # Update last sync timestamp
            self.last_sync = fields.Datetime.now()
            return True
            
        except Exception as e:
            _logger.error(f"Error syncing commission data: {e}")
            return False
    
    def _process_commission_data(self, internal_data, external_data):
        """Process commission data and update agent performance"""
        AgentDashboard = self.env['elite.agent.dashboard']
        
        # Process internal agents
        for agent_data in internal_data:
            agent = AgentDashboard.search([
                ('agent_id.name', '=', agent_data.get('agent_name')),
                ('is_internal', '=', True)
            ], limit=1)
            
            if agent:
                agent.write({
                    'total_sales': agent_data.get('total_sales', 0),
                    'deals_count': agent_data.get('deals_count', 0),
                    'in_progress_count': agent_data.get('in_progress_count', 0),
                    'in_progress_value': agent_data.get('in_progress_value', 0),
                    'pending_value': agent_data.get('pending_value', 0),
                    'commission_earned': agent_data.get('commission_earned', 0),
                })
                
        # Process external agents
        for agent_data in external_data:
            agent = AgentDashboard.search([
                ('agent_id.name', '=', agent_data.get('agent_name')),
                ('is_internal', '=', False)
            ], limit=1)
            
            if agent:
                agent.write({
                    'total_sales': agent_data.get('total_sales', 0),
                    'deals_count': agent_data.get('deals_count', 0),
                    'in_progress_count': agent_data.get('in_progress_count', 0),
                    'in_progress_value': agent_data.get('in_progress_value', 0),
                    'pending_value': agent_data.get('pending_value', 0),
                    'commission_earned': agent_data.get('commission_earned', 0),
                })
                
        # Update rankings
        AgentDashboard._update_rankings()
        
        return True
    
    @api.model
    def _cron_sync_commissions(self):
        """Cron job to sync commissions from external system"""
        sync_config = self.search([], limit=1)
        if not sync_config:
            sync_config = self.create({
                'name': 'Commission Sync',
                'api_endpoint': 'https://api.yourcommissionsystem.com',
                'sync_interval': 60,
            })
        
        return sync_config._sync_commissions()