from . import models
from . import wizards
from . import reports


def post_init_hook(cr, registry):
    """
    Initialize commission dashboard with SQL view creation.
    This hook ensures the dashboard is properly set up after module installation.
    """
    from odoo import api, SUPERUSER_ID
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Create commission dashboard instance
    dashboard = env['commission.dashboard'].create({
        'name': 'System Dashboard',
        'description': 'Auto-created system dashboard for commission analytics'
    })
    
    # Initialize dashboard with SQL views
    dashboard.init()