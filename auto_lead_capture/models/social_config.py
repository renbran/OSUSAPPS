from odoo import models, fields, api
import requests
import json

class SocialConfig(models.Model):
    _name = 'social.config'
    _description = 'Social Media Configuration'
    _rec_name = 'platform_name'

    platform_name = fields.Selection([
        ('whatsapp', 'WhatsApp Business'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('telegram', 'Telegram'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter/X'),
    ], string='Platform', required=True)
    
    active = fields.Boolean(default=True)
    api_token = fields.Char(string='API Token/Key')
    webhook_url = fields.Char(string='Webhook URL', readonly=True, compute='_compute_webhook_url')
    webhook_secret = fields.Char(string='Webhook Secret')
    instance_id = fields.Char(string='Instance ID (WhatsApp/Telegram)')
    phone_number = fields.Char(string='Business Phone Number')
    
    # Facebook specific
    page_id = fields.Char(string='Facebook Page ID')
    app_id = fields.Char(string='Facebook App ID')
    app_secret = fields.Char(string='Facebook App Secret')
    
    # Lead generation settings
    auto_create_lead = fields.Boolean(string='Auto Create Leads', default=True)
    lead_source_id = fields.Many2one('utm.source', string='Lead Source')
    default_user_id = fields.Many2one('res.users', string='Default Salesperson')
    lead_scoring_enabled = fields.Boolean(string='Enable Lead Scoring', default=True)
    
    # Response automation
    auto_response_enabled = fields.Boolean(string='Enable Auto Response')
    welcome_message = fields.Text(string='Welcome Message Template')
    response_delay = fields.Integer(string='Response Delay (seconds)', default=30)

    @api.depends('platform_name')
    def _compute_webhook_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.platform_name:
                record.webhook_url = f"{base_url}/social/{record.platform_name}/webhook"
            else:
                record.webhook_url = False

    def test_connection(self):
        """Test API connection for each platform"""
        if self.platform_name == 'whatsapp':
            return self._test_whatsapp_connection()
        elif self.platform_name == 'telegram':
            return self._test_telegram_connection()
        # Add other platform tests
        
    def _test_whatsapp_connection(self):
        if not self.api_token or not self.instance_id:
            raise UserError("WhatsApp API Token and Instance ID are required")
        
        url = f"https://api.chat-api.com/instance{self.instance_id}/status"
        headers = {'Authorization': f'Bearer {self.api_token}'}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return {'type': 'ir.actions.client', 'tag': 'display_notification',
                       'params': {'message': 'WhatsApp connection successful!', 'type': 'success'}}
            else:
                raise UserError(f"Connection failed: {response.text}")
        except Exception as e:
            raise UserError(f"Connection error: {str(e)}")