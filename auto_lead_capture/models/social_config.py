from odoo import models, fields, api

class SocialConfig(models.Model):
    _name = 'social.config'
    _description = 'Social Media Configuration'
    
    name = fields.Char(string='Configuration Name', required=True)
    platform_name = fields.Selection([
        ('whatsapp', 'WhatsApp Business'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('telegram', 'Telegram'),
    ], string='Platform', required=True)
    
    active = fields.Boolean(string='Active', default=True)
    api_token = fields.Char(string='API Token')
    instance_id = fields.Char(string='Instance ID')
    webhook_secret = fields.Char(string='Webhook Secret')
    webhook_url = fields.Char(string='Webhook URL', compute='_compute_webhook_url', store=True)
    
    # Auto-response settings
    auto_response_enabled = fields.Boolean(string='Auto Response Enabled', default=False)
    welcome_message = fields.Text(string='Welcome Message')
    
    # Lead creation settings
    auto_create_lead = fields.Boolean(string='Auto Create Leads', default=True)
    default_user_id = fields.Many2one('res.users', string='Default Assigned User')
    default_team_id = fields.Many2one('crm.team', string='Default Sales Team')
    
    @api.depends('platform_name')
    def _compute_webhook_url(self):
        for record in self:
            if record.platform_name:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                record.webhook_url = f"{base_url}/social/{record.platform_name}/webhook"
            else:
                record.webhook_url = False