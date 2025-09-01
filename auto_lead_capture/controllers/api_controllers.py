from odoo import http
from odoo.http import request
import json

class SocialAPIController(http.Controller):
    
    @http.route('/api/social/platforms', type='json', auth='user', methods=['GET'])
    def get_platforms(self):
        """Get configured social platforms"""
        platforms = request.env['social.config'].search([('active', '=', True)])
        return [{
            'platform': p.platform_name,
            'webhook_url': p.webhook_url,
            'auto_create_lead': p.auto_create_lead,
        } for p in platforms]
    
    @http.route('/api/social/send_message', type='json', auth='user', methods=['POST'])
    def send_message(self, platform, phone_number, message):
        """Send message via API"""
        try:
            config = request.env['social.config'].search([
                ('platform_name', '=', platform),
                ('active', '=', True)
            ], limit=1)
            
            if not config:
                return {'error': f'Platform {platform} not configured'}
            
            # Platform-specific sending logic
            if platform == 'whatsapp':
                return self._send_whatsapp_message(config, phone_number, message)
            elif platform == 'telegram':
                return self._send_telegram_message(config, phone_number, message)
            else:
                return {'error': f'Sending not implemented for {platform}'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _send_whatsapp_message(self, config, phone_number, message):
        """Send WhatsApp message via Chat-API"""
        url = f"https://api.chat-api.com/instance{config.instance_id}/sendMessage"
        headers = {'Authorization': f'Bearer {config.api_token}'}
        data = {
            'chatId': f"{phone_number}@c.us",
            'body': message
        }
        
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            # Log outgoing message
            request.env['social.message.log'].create({
                'platform': 'whatsapp',
                'message_type': 'outgoing',
                'phone_number': phone_number,
                'message_content': message,
                'processed': True,
            })
            return {'success': True, 'message_id': response.json().get('id')}
        else:
            return {'error': f'Failed to send message: {response.text}'}
