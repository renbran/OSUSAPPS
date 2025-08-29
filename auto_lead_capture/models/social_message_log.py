from odoo import models, fields, api
import json

class SocialMessageLog(models.Model):
    _name = 'social.message.log'
    _description = 'Social Media Message Log'
    _order = 'create_date desc'

    platform = fields.Selection([
        ('whatsapp', 'WhatsApp'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('telegram', 'Telegram'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter/X'),
    ], required=True)
    
    message_type = fields.Selection([
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
    ], required=True)
    
    contact_name = fields.Char(string='Contact Name')
    phone_number = fields.Char(string='Phone Number')
    email = fields.Char(string='Email')
    username = fields.Char(string='Username/Handle')
    
    message_content = fields.Text(string='Message Content', required=True)
    message_id = fields.Char(string='Platform Message ID')
    thread_id = fields.Char(string='Thread/Conversation ID')
    
    lead_id = fields.Many2one('crm.lead', string='Related Lead')
    lead_created = fields.Boolean(string='Lead Created', default=False)
    
    webhook_data = fields.Text(string='Raw Webhook Data')
    processed = fields.Boolean(string='Processed', default=False)
    error_message = fields.Text(string='Processing Error')
    
    attachment_count = fields.Integer(string='Attachments')
    has_media = fields.Boolean(string='Contains Media')
    
    @api.model
    def create_from_webhook(self, platform, webhook_data):
        """Create message log from webhook data"""
        message_data = self._parse_webhook_data(platform, webhook_data)
        message_log = self.create(message_data)
        
        # Auto-create lead if enabled
        config = self.env['social.config'].search([('platform_name', '=', platform)], limit=1)
        if config and config.auto_create_lead:
            lead = self._create_lead_from_message(message_log, config)
            message_log.lead_id = lead.id if lead else False
            message_log.lead_created = bool(lead)
        
        return message_log
    
    def _parse_webhook_data(self, platform, data):
        """Parse webhook data based on platform"""
        try:
            if platform == 'whatsapp':
                return self._parse_whatsapp_data(data)
            elif platform == 'telegram':
                return self._parse_telegram_data(data)
            # Add parsers for other platforms
        except Exception as e:
            return {
                'platform': platform,
                'message_type': 'incoming',
                'message_content': '',
                'webhook_data': json.dumps(data),
                'error_message': str(e),
            }
        
    def _parse_whatsapp_data(self, data):
        """Parse WhatsApp webhook data"""
        message = data.get('messages', [{}])[0] if data.get('messages') else {}
        
        return {
            'platform': 'whatsapp',
            'message_type': 'incoming',
            'contact_name': message.get('senderName', ''),
            'phone_number': message.get('chatId', '').replace('@c.us', ''),
            'message_content': message.get('body', ''),
            'message_id': message.get('id', ''),
            'thread_id': message.get('chatId', ''),
            'webhook_data': json.dumps(data),
            'has_media': message.get('type') != 'chat',
        }