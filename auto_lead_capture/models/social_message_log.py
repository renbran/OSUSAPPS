from odoo import models, fields, api
import json
import logging

class SocialMessageLog(models.Model):
    _name = 'social.message.log'
    _description = 'Social Media Message Log'
    _order = 'create_date desc'
    
    name = fields.Char(string='Message Reference', compute='_compute_name', store=True)
    platform = fields.Selection([
        ('whatsapp', 'WhatsApp'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('telegram', 'Telegram'),
    ], string='Platform', required=True)
    
    message_type = fields.Selection([
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
    ], string='Type', default='incoming')
    
    phone_number = fields.Char(string='Phone Number')
    contact_name = fields.Char(string='Contact Name')
    message_content = fields.Text(string='Message Content')
    
    # Webhook data
    webhook_data = fields.Text(string='Raw Webhook Data')
    message_id = fields.Char(string='External Message ID')
    
    # Processing status
    processed = fields.Boolean(string='Processed', default=False)
    lead_id = fields.Many2one('crm.lead', string='Related Lead')
    error_message = fields.Text(string='Error Message')
    
    @api.depends('platform', 'contact_name', 'phone_number')
    def _compute_name(self):
        for record in self:
            if record.contact_name:
                record.name = f"{record.platform.title()} - {record.contact_name}"
            elif record.phone_number:
                record.name = f"{record.platform.title()} - {record.phone_number}"
            else:
                record.name = f"{record.platform.title()} - {record.id}"
    
    @api.model
    def create_from_webhook(self, platform, webhook_data):
        """Create message log from webhook data"""
        try:
            # Parse webhook data based on platform
            if platform == 'whatsapp':
                message_data = self._parse_whatsapp_webhook(webhook_data)
            elif platform == 'telegram':
                message_data = self._parse_telegram_webhook(webhook_data)
            elif platform == 'facebook':
                message_data = self._parse_facebook_webhook(webhook_data)
            else:
                message_data = {'error': f'Unsupported platform: {platform}'}
            
            if 'error' in message_data:
                _logger.error(f"Error parsing {platform} webhook: {message_data['error']}")
                return False
                
            # Create message log
            message_log = self.create({
                'platform': platform,
                'phone_number': message_data.get('phone_number'),
                'contact_name': message_data.get('contact_name'),
                'message_content': message_data.get('message_content'),
                'webhook_data': json.dumps(webhook_data),
                'message_id': message_data.get('message_id'),
            })
            
            # Auto-create lead if enabled
            config = self.env['social.config'].search([('platform_name', '=', platform)], limit=1)
            if config and config.auto_create_lead:
                message_log._create_lead_from_message()
                
            return message_log
            
        except Exception as e:
            _logger.error(f"Error creating message log from {platform} webhook: {str(e)}")
            return False
    
    def _parse_whatsapp_webhook(self, data):
        """Parse WhatsApp webhook data"""
        # Implement WhatsApp-specific parsing
        return {
            'phone_number': data.get('author', '').replace('@c.us', ''),
            'contact_name': data.get('senderName', ''),
            'message_content': data.get('body', ''),
            'message_id': data.get('id', ''),
        }
    
    def _parse_telegram_webhook(self, data):
        """Parse Telegram webhook data"""
        # Implement Telegram-specific parsing
        message = data.get('message', {})
        return {
            'phone_number': str(message.get('from', {}).get('id', '')),
            'contact_name': message.get('from', {}).get('first_name', ''),
            'message_content': message.get('text', ''),
            'message_id': str(message.get('message_id', '')),
        }
    
    def _parse_facebook_webhook(self, data):
        """Parse Facebook webhook data"""
        # Implement Facebook-specific parsing
        # This is a simplified version
        return {
            'phone_number': '',
            'contact_name': '',
            'message_content': '',
            'message_id': '',
        }
    
    def _create_lead_from_message(self):
        """Create a CRM lead from the message"""
        if self.lead_id:
            return self.lead_id
            
        # Check if lead already exists for this contact
        domain = []
        if self.phone_number:
            domain.append(('phone', '=', self.phone_number))
        if self.contact_name:
            domain.append(('contact_name', '=', self.contact_name))
            
        if domain:
            existing_lead = self.env['crm.lead'].search(domain, limit=1)
            if existing_lead:
                self.lead_id = existing_lead
                existing_lead.message_post(
                    body=f"New {self.platform} message: {self.message_content}"
                )
                return existing_lead
        
        # Create new lead
        lead_vals = {
            'name': f"{self.platform.title()} Lead - {self.contact_name or self.phone_number}",
            'contact_name': self.contact_name,
            'phone': self.phone_number,
            'description': self.message_content,
            'social_platform': self.platform,
            'source_id': self._get_utm_source().id,
            'medium_id': self.env.ref('auto_lead_capture.utm_medium_social_message').id,
        }
        
        # Set default user/team from config
        config = self.env['social.config'].search([('platform_name', '=', self.platform)], limit=1)
        if config:
            if config.default_user_id:
                lead_vals['user_id'] = config.default_user_id.id
            if config.default_team_id:
                lead_vals['team_id'] = config.default_team_id.id
        
        lead = self.env['crm.lead'].create(lead_vals)
        self.lead_id = lead
        self.processed = True
        
        return lead
    
    def _get_utm_source(self):
        """Get UTM source for the platform"""
        source_mapping = {
            'whatsapp': 'auto_lead_capture.utm_source_whatsapp',
            'facebook': 'auto_lead_capture.utm_source_facebook',
            'instagram': 'auto_lead_capture.utm_source_instagram',
            'telegram': 'auto_lead_capture.utm_source_telegram',
        }
        
        source_ref = source_mapping.get(self.platform)
        if source_ref:
            return self.env.ref(source_ref)
        return self.env['utm.source']
    
    @api.model
    def process_unprocessed_messages(self):
        """Process unprocessed messages (called by cron)"""
        unprocessed = self.search([('processed', '=', False), ('error_message', '=', False)])
        for message in unprocessed:
            try:
                message._create_lead_from_message()
            except Exception as e:
                message.error_message = str(e)
                _logger.error(f"Error processing message {message.id}: {str(e)}")