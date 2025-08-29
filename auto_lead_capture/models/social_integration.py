class SocialIntegration(models.Model):
    _name = 'social.integration'
    _description = 'Third-party Social Integrations'
    
    name = fields.Char(string='Integration Name', required=True)
    integration_type = fields.Selection([
        ('zapier', 'Zapier'),
        ('make', 'Make.com (Integromat)'),
        ('direct_api', 'Direct API'),
        ('webhook', 'Webhook'),
    ], required=True)
    
    platform = fields.Selection([
        ('whatsapp', 'WhatsApp'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('telegram', 'Telegram'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter/X'),
    ])
    
    api_endpoint = fields.Char(string='API Endpoint')
    api_key = fields.Char(string='API Key')
    webhook_url = fields.Char(string='Webhook URL')
    
    field_mapping = fields.Text(string='Field Mapping (JSON)', help="Map external fields to Odoo fields")
    active = fields.Boolean(string='Active', default=True)
    
    test_data = fields.Text(string='Test Data (JSON)', help="Sample data for testing integration")
    
    def test_integration(self):
        """Test the integration with sample data"""
        if self.integration_type == 'webhook' and self.test_data:
            try:
                test_data = json.loads(self.test_data)
                # Process test data through webhook handler
                result = self._process_webhook_data(test_data)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': f'Integration test successful: {result}',
                        'type': 'success'
                    }
                }
            except Exception as e:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': f'Integration test failed: {str(e)}',
                        'type': 'danger'
                    }
                }

# 7. Additional methods for existing models

# Extend social_message_log.py with additional methods
class SocialMessageLogExtended(models.Model):
    _inherit = 'social.message.log'
    
    @api.model
    def process_unprocessed_messages(self):
        """Process messages that haven't been processed yet (cron job)"""
        unprocessed = self.search([('processed', '=', False)])
        for message in unprocessed:
            try:
                if message.platform and not message.lead_id:
                    self._create_lead_from_message(message)
                    
                # Run automation rules
                automations = self.env['social.automation']
                automations.process_message_automation(message)
                
                message.processed = True
                
            except Exception as e:
                message.error_message = str(e)
                _logger.error(f"Error processing message {message.id}: {str(e)}")
    
    def _create_lead_from_message(self, message):
        """Create lead from message log"""
        config = self.env['social.config'].search([
            ('platform_name', '=', message.platform)
        ], limit=1)
        
        if not config or not config.auto_create_lead:
            return False
            
        lead_vals = {
            'name': message.contact_name or f'{message.platform.title()} Lead',
            'phone': message.phone_number,
            'email': message.email,
            'description': message.message_content,
            'social_platform': message.platform,
            'social_username': message.username,
            'message_thread_id': message.thread_id,
            'source_id': config.lead_source_id.id if config.lead_source_id else False,
            'user_id': config.default_user_id.id if config.default_user_id else False,
            'medium_id': self.env.ref('utm.utm_medium_social').id,
        }
        
        lead = self.env['crm.lead'].create(lead_vals)
        message.lead_id = lead.id
        message.lead_created = True
        
        # Calculate initial lead score
        scoring = self.env['social.lead.scoring']
        scoring.calculate_lead_score(lead.id)
        
        return lead

# Extend crm_lead_inherit.py with additional methods
class CrmLeadExtendedMethods(models.Model):
    _inherit = 'crm.lead'
    
    @api.model
    def update_social_engagement_scores(self):
        """Update engagement scores for all social leads (cron job)"""
        social_leads = self.search([('social_platform', '!=', False)])
        scoring = self.env['social.lead.scoring']
        
        for lead in social_leads:
            scoring.calculate_lead_score(lead.id)
    
    def action_send_whatsapp_template(self):
        """Open wizard to send WhatsApp template message"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send WhatsApp Message',
            'res_model': 'social.message.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_lead_id': self.id,
                'default_platform': 'whatsapp',
                'default_phone_number': self.phone,
            }
        }