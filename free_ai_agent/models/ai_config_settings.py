# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Default AI Provider
    default_ai_provider_id = fields.Many2one(
        'ai.provider', 
        string='Default AI Provider',
        config_parameter='free_ai_agent.default_provider_id'
    )
    
    # General Settings
    ai_agent_enabled = fields.Boolean(
        string='Enable AI Agents',
        config_parameter='free_ai_agent.enabled',
        default=True
    )
    
    # Auto-cleanup settings
    auto_cleanup_enabled = fields.Boolean(
        string='Auto Cleanup Old Records',
        config_parameter='free_ai_agent.auto_cleanup_enabled',
        default=True
    )
    
    cleanup_days = fields.Integer(
        string='Keep Records for (days)',
        config_parameter='free_ai_agent.cleanup_days',
        default=30,
        help='Number of days to keep response history records'
    )
    
    # Rate limiting
    max_requests_per_hour = fields.Integer(
        string='Max Requests per Hour',
        config_parameter='free_ai_agent.max_requests_per_hour',
        default=100,
        help='Maximum number of AI requests per hour per user'
    )
    
    # Token limits
    max_tokens_per_request = fields.Integer(
        string='Max Tokens per Request',
        config_parameter='free_ai_agent.max_tokens_per_request',
        default=4000,
        help='Maximum tokens allowed per AI request'
    )
    
    # Security
    allowed_user_ids = fields.Many2many(
        'res.users',
        string='Allowed Users',
        help='Users allowed to create and run AI agents. Leave empty to allow all users.'
    )
    
    # Notification settings
    notify_on_agent_failure = fields.Boolean(
        string='Notify on Agent Failure',
        config_parameter='free_ai_agent.notify_on_failure',
        default=True
    )
    
    failure_notification_user_ids = fields.Many2many(
        'res.users',
        'free_ai_agent_failure_notification_rel',
        string='Failure Notification Recipients',
        help='Users to notify when agents fail'
    )
    
    @api.onchange('default_ai_provider_id')
    def _onchange_default_ai_provider(self):
        """Validate default AI provider"""
        if self.default_ai_provider_id and not self.default_ai_provider_id.active:
            return {
                'warning': {
                    'title': _('Warning'),
                    'message': _('The selected AI provider is not active.')
                }
            }
    
    def test_default_provider(self):
        """Test connection to default AI provider"""
        if not self.default_ai_provider_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _('No default AI provider configured'),
                }
            }
        
        return self.default_ai_provider_id.test_connection()
    
    def cleanup_old_records_now(self):
        """Manually trigger cleanup of old records"""
        if not self.cleanup_days:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _('Please set the number of days to keep records'),
                }
            }
        
        count = self.env['free.ai.response.history'].cleanup_old_records(self.cleanup_days)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': _('Cleaned up %d old records') % count,
            }
        }
    
    def create_sample_agents(self):
        """Create sample AI agents for demonstration"""
        ai_provider = self.default_ai_provider_id
        if not ai_provider:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _('Please configure a default AI provider first'),
                }
            }
        
        # Sample agents data
        sample_agents = [
            {
                'name': 'Sales Performance Analyzer',
                'agent_type': 'sales',
                'description': 'Analyzes sales performance and identifies opportunities',
                'execution_mode': 'scheduled',
                'execute_every': 1,
                'execute_unit': 'days',
            },
            {
                'name': 'Inventory Stock Monitor',
                'agent_type': 'inventory',
                'description': 'Monitors inventory levels and suggests reordering',
                'execution_mode': 'scheduled',
                'execute_every': 12,
                'execute_unit': 'hours',
            },
            {
                'name': 'Customer Relationship Assistant',
                'agent_type': 'crm',
                'description': 'Analyzes customer interactions and suggests follow-ups',
                'execution_mode': 'manual',
            },
        ]
        
        created_count = 0
        for agent_data in sample_agents:
            # Check if agent already exists
            existing = self.env['free.ai.agent'].search([('name', '=', agent_data['name'])], limit=1)
            if not existing:
                agent_data.update({
                    'ai_provider_id': ai_provider.id,
                    'status': 'active',
                })
                self.env['free.ai.agent'].create(agent_data)
                created_count += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': _('Created %d sample agents') % created_count,
            }
        }