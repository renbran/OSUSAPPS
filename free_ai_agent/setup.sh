#!/bin/bash

# Free AI Agent - Quick Setup Script
# This script helps you get started with the Free AI Agent module

echo "🤖 Free AI Agent - Quick Setup"
echo "================================"

echo ""
echo "Choose your AI provider setup:"
echo "1. Ollama (Free, Local, Private)"
echo "2. OpenAI (Pay-per-use, Cloud)"
echo "3. Google Gemini (Free tier + Pay-per-use, Cloud)"
echo "4. Skip provider setup"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Setting up Ollama (Local AI)..."
        echo "1. Installing Ollama..."
        
        # Check if ollama is already installed
        if command -v ollama &> /dev/null; then
            echo "   ✅ Ollama is already installed"
        else
            echo "   📥 Downloading and installing Ollama..."
            curl -fsSL https://ollama.ai/install.sh | sh
        fi
        
        echo ""
        echo "2. Pulling recommended AI model..."
        echo "   📥 Downloading Llama 2 (this may take a few minutes)..."
        ollama pull llama2:7b-chat
        
        echo ""
        echo "3. Starting Ollama service..."
        ollama serve &
        
        echo ""
        echo "✅ Ollama setup complete!"
        echo "   - No API key required"
        echo "   - Completely free and private"
        echo "   - Model: llama2:7b-chat"
        echo "   - URL: http://localhost:11434"
        ;;
        
    2)
        echo ""
        echo "Setting up OpenAI..."
        echo "1. Get your API key from: https://platform.openai.com/api-keys"
        echo "2. Add credits to your account (typically $5-20 lasts months)"
        echo "3. In Odoo, go to Free AI Agents > Configuration > AI Providers"
        echo "4. Edit 'OpenAI GPT-3.5' and enter your API key"
        echo ""
        echo "💰 Cost: ~$0.002 per 1K tokens (very affordable for most use cases)"
        ;;
        
    3)
        echo ""
        echo "Setting up Google Gemini..."
        echo "1. Get your API key from: https://aistudio.google.com/app/apikey"
        echo "2. Free tier includes generous limits"
        echo "3. In Odoo, go to Free AI Agents > Configuration > AI Providers"
        echo "4. Edit 'Google Gemini Pro' and enter your API key"
        echo ""
        echo "💰 Cost: Free tier available, then pay-per-use"
        ;;
        
    4)
        echo ""
        echo "Skipping provider setup..."
        echo "You can configure AI providers later in Odoo:"
        echo "Free AI Agents > Configuration > AI Providers"
        ;;
        
    *)
        echo "Invalid choice. Exiting..."
        exit 1
        ;;
esac

echo ""
echo "📋 Next Steps:"
echo "1. Install the 'Free AI Agent' module in Odoo"
echo "2. Go to Free AI Agents > Configuration > Settings"
echo "3. Set your default AI provider"
echo "4. Click 'Create Sample Agents' for quick start"
echo "5. Visit Free AI Agents > Dashboard to see your agents"
echo ""
echo "📖 Need help? Check the README.md file for detailed instructions"
echo ""
echo "🎉 Happy automating with AI!"