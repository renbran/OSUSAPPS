from odoo import models, fields, api
import logging

class SocialPlatform(models.Model):
    _name = 'social.platform'
    _description = 'Social Media Platform'
    
    name = fields.Char(string='Platform Name', required=True)
    code = fields.Char(string='Platform Code', required=True)
    api_base_url = fields.Char(string='API Base URL')
    webhook_verification_required = fields.Boolean(string='Webhook Verification Required')
    supports_media = fields.Boolean(string='Supports Media Messages', default=True)
    supports_groups = fields.Boolean(string='Supports Group Messages', default=False)
    
    # Platform-specific settings
    rate_limit_per_minute = fields.Integer(string='Rate Limit (per minute)', default=100)
    max_message_length = fields.Integer(string='Max Message Length', default=4096)
    
    # Configuration template
    config_template = fields.Text(string='Configuration Template (JSON)')
    
    @api.model
    def get_platform_by_code(self, code):
        return self.search([('code', '=', code)], limit=1)