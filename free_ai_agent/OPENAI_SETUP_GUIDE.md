# OpenAI API Configuration Guide

## SECURITY WARNING
The API key shared in chat has been exposed and should be regenerated immediately.

## Steps to Configure OpenAI API Securely

### 1. Generate New API Key
- Go to: https://platform.openai.com/api-keys
- Delete the exposed key
- Create a new API key
- Copy it securely (don't share in chat)

### 2. Configure in Odoo
1. Install the Free AI Agent module
2. Go to: Free AI Agents > Configuration > AI Providers
3. Edit "OpenAI GPT-3.5" provider
4. Paste your NEW API key in the "API Key" field
5. Set Active = True
6. Click "Test Connection"

### 3. Set as Default
1. Go to: Free AI Agents > Configuration > Settings
2. Set "Default AI Provider" to your OpenAI provider
3. Save settings

### 4. Create Sample Agents
1. In settings, click "Create Sample Agents"
2. This creates ready-to-use business agents

### 5. Test Your Setup
1. Go to: Free AI Agents > Dashboard
2. Click "Run Agent" on any agent
3. Verify OpenAI responds correctly

## Security Best Practices
- Never share API keys in chat/email
- Regularly rotate API keys
- Monitor usage in OpenAI dashboard
- Set usage limits in OpenAI account

## Cost Management
- Start with GPT-3.5-turbo (~$0.002/1K tokens)
- Set reasonable token limits (1000-2000)
- Monitor usage regularly
- Typical cost: $2-10/month for moderate usage

## Support
If you need help with configuration, ask questions without sharing sensitive information.