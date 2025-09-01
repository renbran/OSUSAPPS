from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging


class SocialAutomation(models.Model):
    _name = 'social.automation'
    _description = 'Social Media Automation Rules'
    
    name = fields.Char(string='Automation Name', required=True)
    platform = fields.Selection([
        ('whatsapp', 'WhatsApp'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('telegram', 'Telegram'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter/X'),
    ])
    
    trigger_type = fields.Selection([
        ('new_message', 'New Message Received'),
        ('keyword_match', 'Keyword Match'),
        ('business_hours', 'Outside Business Hours'),
        ('first_contact', 'First Time Contact'),
        ('follow_up', 'Follow-up Required'),
    ], required=True)
    
    trigger_value = fields.Char(string='Trigger Value (keywords, etc.)')
    
    action_type = fields.Selection([
        ('send_message', 'Send Message'),
        ('create_lead', 'Create Lead'),
        ('assign_user', 'Assign to User'),
        ('add_tag', 'Add Tag'),
        ('schedule_activity', 'Schedule Activity'),
    ], required=True)
    
    action_value = fields.Text(string='Action Configuration (JSON)')
    delay_minutes = fields.Integer(string='Delay (minutes)', default=0)
    active = fields.Boolean(string='Active', default=True)
    
    @api.model
    def process_message_automation(self, message_log):
        """Process automation rules for incoming message"""
        automations = self.search([
            ('active', '=', True),
            '|',
            ('platform', '=', message_log.platform),
            ('platform', '=', False)  # Global automations
        ])
        
        for automation in automations:
            if self._should_trigger(automation, message_log):
                self._execute_automation(automation, message_log)
    
    def _should_trigger(self, automation, message_log):
        """Check if automation should be triggered"""
        if automation.trigger_type == 'new_message':
            return True
            
        elif automation.trigger_type == 'keyword_match':
            keywords = automation.trigger_value.split(',') if automation.trigger_value else []
            message_content = (message_log.message_content or '').lower()
            return any(keyword.strip().lower() in message_content for keyword in keywords)
            
        elif automation.trigger_type == 'first_contact':
            # Check if this is the first message from this contact
            previous_messages = self.env['social.message.log'].search([
                ('phone_number', '=', message_log.phone_number),
                ('platform', '=', message_log.platform),
                ('id', '!=', message_log.id)
            ])
            return len(previous_messages) == 0
            
        return False
    
    def _execute_automation(self, automation, message_log):
        """Execute the automation action"""
        try:
            if automation.action_type == 'send_message':
                self._send_auto_message(automation, message_log)
            elif automation.action_type == 'create_lead':
                self._create_auto_lead(automation, message_log)
            elif automation.action_type == 'schedule_activity':
                self._schedule_auto_activity(automation, message_log)
                
        except Exception as e:
            _logger.error(f"Automation execution error: {str(e)}")

# 4. models/social_analytics.py - Analytics and Reporting
class SocialAnalytics(models.Model):
    _name = 'social.analytics'
    _description = 'Social Media Analytics'
    _auto = False
    
    platform = fields.Selection([
        ('whatsapp', 'WhatsApp'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('telegram', 'Telegram'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter/X'),
    ])
    
    date = fields.Date(string='Date')
    message_count = fields.Integer(string='Messages Count')
    lead_count = fields.Integer(string='Leads Created')
    conversion_rate = fields.Float(string='Conversion Rate %')
    avg_response_time = fields.Float(string='Avg Response Time (hours)')
    
    def init(self):
        """Create SQL view for analytics"""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    row_number() OVER () AS id,
                    sml.platform,
                    DATE(sml.create_date) as date,
                    COUNT(sml.id) as message_count,
                    COUNT(CASE WHEN sml.lead_created = true THEN 1 END) as lead_count,
                    CASE 
                        WHEN COUNT(sml.id) > 0 THEN 
                            (COUNT(CASE WHEN sml.lead_created = true THEN 1 END) * 100.0 / COUNT(sml.id))
                        ELSE 0 
                    END as conversion_rate,
                    AVG(EXTRACT(EPOCH FROM (sml.write_date - sml.create_date))/3600) as avg_response_time
                FROM social_message_log sml
                WHERE sml.message_type = 'incoming'
                GROUP BY sml.platform, DATE(sml.create_date)
            )
        """ % self._table)