from odoo import models, fields, api, _

class SocialWebhook(models.Model):
    _name = 'social.webhook'
    _description = 'Social Webhook'

    platform = fields.Selection([
        ('whatsapp', 'WhatsApp'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('telegram', 'Telegram'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter/X'),
    ], string='Platform', required=True)
    webhook_url = fields.Char(string='Webhook URL', required=True)
    secret = fields.Char(string='Secret')
    active = fields.Boolean(string='Active', default=True)
