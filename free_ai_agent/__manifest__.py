# -*- encoding: utf-8 -*-
##############################################################################
#
# Free AI Agent for Odoo
# Copyright (C) 2025
#
##############################################################################

{
    'name': "Open Source AI Agent for Odoo",
    'summary': """Complete AI automation platform for Odoo using OpenAI API - No subscriptions, full control""",
    'description': """
        Open Source AI Agent for Odoo - The Complete Business Intelligence Solution
        
        🤖 INTELLIGENT BUSINESS AUTOMATION:
        - Sales Performance Analysis & Forecasting
        - Inventory Optimization & Stock Alerts
        - Customer Relationship Intelligence
        - Financial Analysis & Anomaly Detection
        - Project Management & Risk Assessment
        - HR Analytics & Employee Insights
        
        💰 COST-EFFECTIVE:
        - Uses OpenAI API directly (pay only for what you use)
        - No monthly subscriptions or vendor lock-in
        - Typically costs $5-20/month vs $100+/month for commercial solutions
        
        🔧 ENTERPRISE FEATURES:
        - Multi-agent orchestration
        - Scheduled automation workflows
        - Advanced prompt engineering
        - Complete audit trails
        - Role-based access control
        - Custom business logic integration
        
        🚀 OPEN SOURCE ADVANTAGE:
        - Full source code access
        - Unlimited customization
        - Community-driven development
        - No vendor dependencies
        - Future-proof architecture
    """,
    'author': "Open Source Community",
    'website': "https://github.com/odoo-ai-agents/open-source-ai-agent",
    'support': "https://github.com/odoo-ai-agents/open-source-ai-agent/issues",
    'maintainer': "Odoo AI Agents Community",
    'license': 'LGPL-3',
    'category': 'Tools',
    'version': '17.0.1.0.0',
    'sequence': 1,
    
    # Dependencies
    'depends': ['base', 'web', 'base_setup'],
    
    # Data files
    'data': [
        'security/ir.model.access.csv',
        'data/ai_provider_data.xml',
        'data/ai_agent_cron.xml',
        'views/ai_provider_views.xml',
        'views/ai_agent_views.xml',
        'views/ai_response_history_views.xml',
        'views/openai_business_agent_views.xml',
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