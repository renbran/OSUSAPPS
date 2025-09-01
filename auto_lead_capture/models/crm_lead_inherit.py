from odoo import models, fields, api

class CrmLeadInherit(models.Model):
    _inherit = 'crm.lead'
    
    # Social media fields
    social_platform = fields.Selection([
        ('whatsapp', 'WhatsApp'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('telegram', 'Telegram'),
    ], string='Social Platform')
    
    social_message_ids = fields.One2many('social.message.log', 'lead_id', string='Social Messages')
    social_message_count = fields.Integer(string='Messages Count', compute='_compute_social_message_count')
    social_engagement_score = fields.Float(string='Social Engagement Score', default=0.0)
    
    @api.depends('social_message_ids')
    def _compute_social_message_count(self):
        for lead in self:
            lead.social_message_count = len(lead.social_message_ids)
    
    def action_view_social_messages(self):
        """Open social messages for this lead"""
        return {
            'name': 'Social Messages',
            'type': 'ir.actions.act_window',
            'res_model': 'social.message.log',
            'view_mode': 'tree,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id},
        }
    
    @api.model
    def update_social_engagement_scores(self):
        """Update engagement scores for all social leads (called by cron)"""
        social_leads = self.search([('social_platform', '!=', False)])
        for lead in social_leads:
            # Simple scoring based on message count and recency
            message_count = len(lead.social_message_ids)
            recent_messages = lead.social_message_ids.filtered(
                lambda m: (fields.Datetime.now() - m.create_date).days <= 7
            )
            
            # Base score from message count
            score = message_count * 10
            
            # Bonus for recent activity
            score += len(recent_messages) * 20
            
            # Bonus for response speed (if any outgoing messages)
            outgoing_messages = lead.social_message_ids.filtered(lambda m: m.message_type == 'outgoing')
            if outgoing_messages:
                score += 50
            
            lead.social_engagement_score = score