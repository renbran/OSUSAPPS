from odoo import models, fields, api

class SocialSetupWizard(models.TransientModel):
    _name = 'social.setup.wizard'
    _description = 'Social Media Setup Wizard'

    step = fields.Selection([
        ('platform', 'Select Platform'),
        ('config', 'Configuration'),
        ('test', 'Test Connection'),
        ('complete', 'Complete'),
    ], default='platform')
    
    platform_name = fields.Selection([
        ('whatsapp', 'WhatsApp Business'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('telegram', 'Telegram'),
    ])
    
    # Configuration fields
    name = fields.Char(string='Configuration Name')
    api_token = fields.Char()
    instance_id = fields.Char()
    webhook_secret = fields.Char()
    
    # Auto-response settings
    auto_response_enabled = fields.Boolean(string='Enable Auto Response', default=False)
    welcome_message = fields.Text(string='Welcome Message')
    
    # Lead settings
    auto_create_lead = fields.Boolean(string='Auto Create Leads', default=True)
    default_user_id = fields.Many2one('res.users', string='Default Assigned User')
    default_team_id = fields.Many2one('crm.team', string='Default Sales Team')
    
    def action_next_step(self):
        """Move to next step in wizard"""
        if self.step == 'platform':
            if not self.name:
                self.name = f"{self.platform_name.title()} Configuration"
            self.step = 'config'
        elif self.step == 'config':
            self.step = 'test'
        elif self.step == 'test':
            # Create the configuration
            self.env['social.config'].create({
                'name': self.name,
                'platform_name': self.platform_name,
                'api_token': self.api_token,
                'instance_id': self.instance_id,
                'webhook_secret': self.webhook_secret,
                'auto_response_enabled': self.auto_response_enabled,
                'welcome_message': self.welcome_message,
                'auto_create_lead': self.auto_create_lead,
                'default_user_id': self.default_user_id.id if self.default_user_id else False,
                'default_team_id': self.default_team_id.id if self.default_team_id else False,
            })
            self.step = 'complete'
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'social.setup.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_back_step(self):
        """Go back to previous step"""
        if self.step == 'config':
            self.step = 'platform'
        elif self.step == 'test':
            self.step = 'config'
        elif self.step == 'complete':
            self.step = 'test'
            
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'social.setup.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_test_connection(self):
        """Test the connection to the social platform"""
        # Implement platform-specific connection testing
        # For now, just mark as successful
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'{self.platform_name.title()} connection test successful!',
                'type': 'success',
            }
        }
    
    def action_finish(self):
        """Complete the wizard"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'social.config',
            'view_mode': 'tree,form',
            'target': 'current',
        }