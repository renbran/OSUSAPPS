# 🤖 Open Source AI Agent for Odoo

**The Complete Business Intelligence Platform - Powered by OpenAI**

Transform your Odoo system into an intelligent business platform with AI-powered analysis, insights, and automation. No subscriptions, no vendor lock-in, complete control.

## Features

- 🤖 **Multiple AI Provider Support**: OpenAI, Anthropic Claude, Google Gemini, Ollama (local), and OpenAI-compatible APIs
- 💰 **Cost-Effective**: Use pay-per-use APIs or completely free local models
- 🎯 **Specialized Agents**: Pre-configured agents for Sales, Inventory, Accounting, CRM, Projects, and HR
- ⏰ **Scheduled Execution**: Automatic agent execution based on custom schedules
- 📊 **Response History**: Track all AI interactions and responses
- 🔧 **Customizable**: Create custom agents with personalized prompts and behaviors
- 🔒 **Secure**: No data sent to third-party services (when using local models)

## Installation

1. Copy the `free_ai_agent` folder to your Odoo addons directory
2. Update your apps list in Odoo
3. Install the "Free AI Agent" module

## Setup Guide

### Option 1: Free Local AI (Recommended for Privacy)

1. **Install Ollama** (completely free and runs locally):
   ```bash
   # Install Ollama from https://ollama.ai/
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull a model (e.g., Llama 2)
   ollama pull llama2
   
   # Or try a smaller, faster model
   ollama pull llama2:7b-chat
   ```

2. **Configure in Odoo**:
   - Go to Free AI Agents > Configuration > AI Providers
   - Edit the "Ollama Llama2 (Local)" provider
   - Set it as active
   - Test the connection

### Option 2: OpenAI (Pay-per-use)

1. **Get API Key**:
   - Visit [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create an account and generate an API key
   - Add credits to your account (typically $5-20 lasts months for small usage)

2. **Configure in Odoo**:
   - Go to Free AI Agents > Configuration > AI Providers
   - Edit the "OpenAI GPT-3.5" provider
   - Enter your API key
   - Set it as active
   - Test the connection

### Option 3: Google Gemini (Free Tier Available)

1. **Get API Key**:
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a Google account if needed
   - Generate an API key (free tier includes generous limits)

2. **Configure in Odoo**:
   - Go to Free AI Agents > Configuration > AI Providers
   - Edit the "Google Gemini Pro" provider
   - Enter your API key
   - Set it as active
   - Test the connection

### Option 4: Anthropic Claude (Pay-per-use)

1. **Get API Key**:
   - Visit [Anthropic Console](https://console.anthropic.com/)
   - Create an account and generate an API key
   - Add credits to your account

2. **Configure in Odoo**:
   - Go to Free AI Agents > Configuration > AI Providers
   - Edit the "Anthropic Claude" provider
   - Enter your API key
   - Set it as active

## Usage

### Creating Your First Agent

1. Go to **Free AI Agents > AI Agents > Create Agent**
2. Choose an agent type (Sales, Inventory, CRM, etc.)
3. Select your configured AI provider
4. Customize the system prompt if needed
5. Set execution mode (Manual or Scheduled)
6. Save and run the agent

### Sample Agents

Use the quick setup feature:
1. Go to **Free AI Agents > Configuration > Settings**
2. Click "Create Sample Agents"
3. This creates ready-to-use agents for different business functions

### Running Agents

- **Manual**: Click the "Run Agent" button on any agent
- **Scheduled**: Agents run automatically based on their schedule
- **Dashboard**: View all agents and their status from the dashboard

## Cost Comparison

| Provider | Cost | Free Tier | Local |
|----------|------|-----------|-------|
| Ollama | Free | ✅ Unlimited | ✅ Yes |
| Google Gemini | Free tier + pay-per-use | ✅ Generous limits | ❌ No |
| OpenAI | Pay-per-use | ❌ No | ❌ No |
| Anthropic | Pay-per-use | ❌ No | ❌ No |

**Recommendation**: Start with Ollama for complete privacy and zero cost, or Google Gemini for cloud-based AI with free tier.

## Privacy & Security

- **Local Models (Ollama)**: Complete privacy, no data leaves your server
- **Cloud APIs**: Data sent to respective AI providers (check their privacy policies)
- **No Third-party Tracking**: This module doesn't send any data to external analytics services

## Customization

### Creating Custom Agents

1. Define clear system prompts that specify:
   - The agent's role and expertise
   - What data they should analyze
   - Expected output format
   - Specific instructions

2. Example system prompt for a custom inventory agent:
   ```
   You are an Inventory Optimization Specialist for an Odoo ERP system. 
   Analyze current stock levels, sales trends, and supplier performance.
   Provide specific recommendations for:
   - Products to reorder immediately
   - Overstock situations to address
   - Supplier performance issues
   Always include specific product names and quantities in your recommendations.
   ```

### Advanced Configuration

- **Model Access**: Grant agents access to specific Odoo models
- **Context Data**: Provide additional context or constraints
- **Token Limits**: Control AI response length and costs
- **Temperature**: Adjust creativity vs. consistency (0.0 = deterministic, 1.0 = creative)

## Troubleshooting

### Common Issues

1. **"Connection failed"**:
   - Check API key is correct
   - Verify internet connection
   - For Ollama: ensure service is running (`ollama serve`)

2. **"No AI provider configured"**:
   - Set up at least one AI provider
   - Mark it as active
   - Set as default in settings

3. **"Agent execution failed"**:
   - Check agent has access to required models
   - Verify system prompt is clear and specific
   - Check token limits aren't too restrictive

4. **High costs with paid APIs**:
   - Reduce max_tokens setting
   - Use less expensive models (GPT-3.5 vs GPT-4)
   - Consider switching to Ollama for cost savings

### Support

- Create issues on GitHub for bugs or feature requests
- Check Odoo logs for detailed error messages
- Test AI provider connections individually

## Contributing

This is an open-source project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

LGPL-3 (same as Odoo)

## Comparison with Commercial Alternatives

| Feature | Free AI Agent | Commercial Module |
|---------|---------------|-------------------|
| Cost | Free | $X/month subscription |
| AI Providers | Multiple choices | Locked to one service |
| Local AI Support | ✅ Yes | ❌ No |
| Privacy | ✅ Full control | ❌ Data sent to third party |
| Customization | ✅ Full source code | ❌ Limited |
| Vendor Lock-in | ❌ No | ✅ Yes |

---

**Get started today and bring AI to your Odoo system without breaking the bank!**