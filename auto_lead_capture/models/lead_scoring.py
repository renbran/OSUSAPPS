from odoo import models, fields, api

class SocialLeadScoring(models.Model):
    _name = 'social.lead.scoring'
    _description = 'Social Media Lead Scoring Rules'
    
    name = fields.Char(string='Rule Name', required=True)
    platform = fields.Selection([
        ('whatsapp', 'WhatsApp'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('telegram', 'Telegram'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter/X'),
    ])
    
    condition_type = fields.Selection([
        ('keyword', 'Contains Keyword'),
        ('message_count', 'Message Count'),
        ('response_time', 'Response Time'),
        ('profile_complete', 'Profile Complete'),
        ('followers_count', 'Followers Count'),
        ('time_of_day', 'Time of Day'),
    ], required=True)
    
    condition_value = fields.Char(string='Condition Value')
    score_points = fields.Integer(string='Score Points', required=True)
    active = fields.Boolean(string='Active', default=True)
    
    @api.model
    def calculate_lead_score(self, lead_id):
        """Calculate total score for a lead based on scoring rules"""
        lead = self.env['crm.lead'].browse(lead_id)
        total_score = 0
        
        # Get all active scoring rules for the platform
        rules = self.search([
            ('active', '=', True),
            '|',
            ('platform', '=', lead.social_platform),
            ('platform', '=', False)  # Global rules
        ])
        
        for rule in rules:
            score = self._apply_scoring_rule(rule, lead)
            total_score += score
            
        lead.social_engagement_score = total_score
        return total_score
    
    def _apply_scoring_rule(self, rule, lead):
        """Apply individual scoring rule to lead"""
        if rule.condition_type == 'keyword':
            if rule.condition_value.lower() in (lead.description or '').lower():
                return rule.score_points
                
        elif rule.condition_type == 'message_count':
            message_count = lead.social_messages_count
            threshold = int(rule.condition_value or 0)
            if message_count >= threshold:
                return rule.score_points
                
        elif rule.condition_type == 'followers_count':
            followers = lead.platform_followers or 0
            threshold = int(rule.condition_value or 0)
            if followers >= threshold:
                return rule.score_points
                
        # Add more scoring conditions as needed
        return 0
