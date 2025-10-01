# -*- encoding: utf-8 -*-
##############################################################################
#
# Free AI Agent for Odoo
# Copyright (C) 2025
#
##############################################################################

{
    'name': "Free AI Agent",
    'summary': """Free AI assistant for Odoo with customizable agents using open-source AI APIs""",
    'description': """
        Free AI Agent provides intelligent assistance within Odoo using:
        - OpenAI API (pay-per-use, no subscription)
        - Anthropic Claude API
        - Local AI models (Ollama, OpenAI-compatible endpoints)
        - Google Gemini API (free tier)
        
        Features:
        - Agent dashboard with customizable AI agents
        - Response history and tracking
        - Integration with all Odoo models
        - Scheduled agent execution
        - Multi-step AI workflows
        - No external subscription fees
    """,
    'author': "Open Source Community",
    'website': "https://github.com/your-repo/free-ai-agent",
    'license': 'LGPL-3',
    'category': 'Tools',
    'version': '18.0.1.0.0',
    'sequence': 1,
    
    # Dependencies
    'depends': ['base', 'web', 'base_setup'],
    
    # Data files
    'data': [
        'security/ir.model.access.csv',
        'data/ai_agent_cron.xml',
        'views/ai_agent_views.xml',
        'views/ai_response_history_views.xml',
        'views/ai_config_settings_views.xml',
        'views/main_menu.xml',
    ],
    
    # Assets
    'assets': {
        'web.assets_backend': [
            'free_ai_agent/static/src/css/ai_agent.scss',
            'free_ai_agent/static/src/js/ai_agent_dashboard.js',
            'free_ai_agent/static/src/xml/ai_agent_dashboard.xml',
        ],
    },
    
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}