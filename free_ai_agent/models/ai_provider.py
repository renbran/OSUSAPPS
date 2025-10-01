# -*- coding: utf-8 -*-

import json
import logging
import requests
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class AIProvider(models.Model):
    _name = 'ai.provider'
    _description = 'AI Provider Configuration'
    _order = 'sequence, name'

    name = fields.Char('Provider Name', required=True)
    provider_type = fields.Selection([
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic Claude'),
        ('google', 'Google Gemini'),
        ('ollama', 'Ollama (Local)'),
        ('openai_compatible', 'OpenAI Compatible'),
    ], string='Provider Type', required=True)
    
    api_key = fields.Char('API Key', help="API key for the provider (not needed for local models)")
    api_base_url = fields.Char('Base URL', help="Custom base URL for the API")
    model_name = fields.Char('Model Name', required=True, 
                            help="e.g., gpt-3.5-turbo, claude-3-sonnet, gemini-pro, llama2")
    
    max_tokens = fields.Integer('Max Tokens', default=2000)
    temperature = fields.Float('Temperature', default=0.7, help="Creativity level (0.0 to 2.0)")
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence', default=10)
    
    # Usage tracking
    total_requests = fields.Integer('Total Requests', readonly=True, default=0)
    total_tokens_used = fields.Integer('Total Tokens Used', readonly=True, default=0)
    last_used = fields.Datetime('Last Used', readonly=True)
    
    # Rate limiting
    requests_per_minute = fields.Integer('Requests per Minute', default=60)
    
    def _get_default_headers(self):
        """Get default headers for API requests"""
        headers = {'Content-Type': 'application/json'}
        
        if self.provider_type == 'openai':
            headers['Authorization'] = f'Bearer {self.api_key}'
        elif self.provider_type == 'anthropic':
            headers['x-api-key'] = self.api_key
            headers['anthropic-version'] = '2023-06-01'
        elif self.provider_type == 'google':
            # Google uses API key in URL parameter
            pass
        elif self.provider_type == 'openai_compatible':
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                
        return headers
    
    def _get_api_url(self):
        """Get the API endpoint URL"""
        if self.api_base_url:
            base_url = self.api_base_url.rstrip('/')
        else:
            if self.provider_type == 'openai':
                base_url = 'https://api.openai.com/v1'
            elif self.provider_type == 'anthropic':
                base_url = 'https://api.anthropic.com/v1'
            elif self.provider_type == 'google':
                base_url = 'https://generativelanguage.googleapis.com/v1'
            elif self.provider_type == 'ollama':
                base_url = 'http://localhost:11434/api'
            else:
                base_url = self.api_base_url or 'http://localhost:8000/v1'
        
        if self.provider_type in ['openai', 'openai_compatible']:
            return f'{base_url}/chat/completions'
        elif self.provider_type == 'anthropic':
            return f'{base_url}/messages'
        elif self.provider_type == 'google':
            return f'{base_url}/models/{self.model_name}:generateContent?key={self.api_key}'
        elif self.provider_type == 'ollama':
            return f'{base_url}/chat'
        
        return base_url
    
    def _format_messages_for_provider(self, messages):
        """Format messages according to provider requirements"""
        if self.provider_type in ['openai', 'openai_compatible', 'ollama']:
            return messages  # Standard OpenAI format
        elif self.provider_type == 'anthropic':
            # Convert to Anthropic format
            formatted_messages = []
            for msg in messages:
                if msg['role'] == 'system':
                    # Anthropic handles system messages differently
                    continue
                formatted_messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
            return formatted_messages
        elif self.provider_type == 'google':
            # Convert to Google Gemini format
            parts = []
            for msg in messages:
                if msg['role'] != 'system':
                    parts.append({'text': f"{msg['role']}: {msg['content']}"})
            return {'contents': [{'parts': parts}]}
        
        return messages
    
    def _prepare_request_data(self, messages, **kwargs):
        """Prepare request data according to provider format"""
        formatted_messages = self._format_messages_for_provider(messages)
        
        if self.provider_type in ['openai', 'openai_compatible']:
            return {
                'model': self.model_name,
                'messages': formatted_messages,
                'max_tokens': kwargs.get('max_tokens', self.max_tokens),
                'temperature': kwargs.get('temperature', self.temperature),
            }
        elif self.provider_type == 'anthropic':
            system_msg = next((msg['content'] for msg in messages if msg['role'] == 'system'), '')
            return {
                'model': self.model_name,
                'max_tokens': kwargs.get('max_tokens', self.max_tokens),
                'temperature': kwargs.get('temperature', self.temperature),
                'system': system_msg,
                'messages': formatted_messages,
            }
        elif self.provider_type == 'google':
            return formatted_messages
        elif self.provider_type == 'ollama':
            return {
                'model': self.model_name,
                'messages': formatted_messages,
                'stream': False,
                'options': {
                    'temperature': kwargs.get('temperature', self.temperature),
                    'num_predict': kwargs.get('max_tokens', self.max_tokens),
                }
            }
        
        return {'messages': formatted_messages}
    
    def send_request(self, messages, **kwargs):
        """Send request to AI provider and return response"""
        if not self.active:
            raise ValidationError(_('AI Provider %s is not active') % self.name)
        
        if self.provider_type != 'ollama' and not self.api_key:
            raise ValidationError(_('AI Provider %s requires an API key') % self.name)
        
        try:
            url = self._get_api_url()
            headers = self._get_default_headers()
            data = self._prepare_request_data(messages, **kwargs)
            
            _logger.info(f"Sending request to {self.name} ({self.provider_type})")
            
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code != 200:
                _logger.error(f"API Error {response.status_code}: {response.text}")
                raise ValidationError(f"API Error {response.status_code}: {response.text}")
            
            result = response.json()
            
            # Update usage statistics
            self.sudo().write({
                'total_requests': self.total_requests + 1,
                'last_used': fields.Datetime.now(),
            })
            
            # Extract response content based on provider
            content = self._extract_response_content(result)
            
            return {
                'content': content,
                'raw_response': result,
                'provider': self.name,
                'model': self.model_name,
                'tokens_used': self._extract_token_usage(result),
            }
            
        except requests.exceptions.RequestException as e:
            _logger.error(f"Request failed for {self.name}: {str(e)}")
            raise ValidationError(_('Request failed: %s') % str(e))
        except Exception as e:
            _logger.error(f"Unexpected error with {self.name}: {str(e)}")
            raise ValidationError(_('Unexpected error: %s') % str(e))
    
    def _extract_response_content(self, result):
        """Extract content from API response"""
        if self.provider_type in ['openai', 'openai_compatible']:
            return result['choices'][0]['message']['content']
        elif self.provider_type == 'anthropic':
            return result['content'][0]['text']
        elif self.provider_type == 'google':
            return result['candidates'][0]['content']['parts'][0]['text']
        elif self.provider_type == 'ollama':
            return result['message']['content']
        
        return str(result)
    
    def _extract_token_usage(self, result):
        """Extract token usage from API response"""
        if self.provider_type in ['openai', 'openai_compatible']:
            usage = result.get('usage', {})
            return usage.get('total_tokens', 0)
        elif self.provider_type == 'anthropic':
            usage = result.get('usage', {})
            return usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
        
        return 0
    
    def test_connection(self):
        """Test connection to AI provider"""
        try:
            test_messages = [
                {'role': 'user', 'content': 'Hello, this is a test message. Please respond with "Connection successful".'}
            ]
            
            response = self.send_request(test_messages)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'message': f'Connection to {self.name} successful! Response: {response["content"][:100]}...',
                }
            }
            
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'danger',
                    'message': f'Connection to {self.name} failed: {str(e)}',
                }
            }
    
    @api.model
    def get_default_provider(self):
        """Get the default active provider"""
        return self.search([('active', '=', True)], limit=1, order='sequence')