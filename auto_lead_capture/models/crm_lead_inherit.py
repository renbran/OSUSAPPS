from odoo import models, fields, api

class CrmLeadInherit(models.Model):
    _inherit = 'crm.lead'

    # Social media specific fields
    social_platform = fields.Selection([
        ('whatsapp', 'WhatsApp'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('telegram', 'Telegram'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter/X'),
    ], string='Social Platform')
    
    social_username = fields.Char(string='Social Media Username')
    message_thread_id = fields.Char(string='Message Thread ID')
    social_profile_url = fields.Char(string='Social Profile URL')
    
    # Engagement tracking
    social_messages_count = fields.Integer(string='Messages Count', compute='_compute_social_stats')
    last_message_date = fields.Datetime(string='Last Message', compute='_compute_social_stats')
    response_time_avg = fields.Float(string='Avg Response Time (hours)', compute='_compute_social_stats')
    
    # Lead scoring from social interactions
    social_engagement_score = fields.Integer(string='Social Engagement Score', default=0)
    platform_followers = fields.Integer(string='Followers Count')
    
    @api.depends('message_ids')
    def _compute_social_stats(self):
        for lead in self:
            social_messages = self.env['social.message.log'].search([('lead_id', '=', lead.id)])
            lead.social_messages_count = len(social_messages)
            lead.last_message_date = social_messages[0].create_date if social_messages else False
            
            # Calculate average response time
            if social_messages:
                # Logic for response time calculation
                pass

    def action_view_social_messages(self):
        """Open social messages related to this lead"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Social Messages',
            'res_model': 'social.message.log',
            'view_mode': 'tree,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id}
        }
    
    def send_whatsapp_message(self, message):
        """Send WhatsApp message to lead"""
        if not self.phone or self.social_platform != 'whatsapp':
            return False
            
        config = self.env['social.config'].search([('platform_name', '=', 'whatsapp')], limit=1)
        if not config:
            return False
            
        # WhatsApp API call logic here
        return self._send_whatsapp_via_api(config, message)
