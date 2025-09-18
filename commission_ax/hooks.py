import logging
from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    """Post installation hook for commission_ax module"""
    try:
        _logger.info("Starting commission_ax post-installation setup...")

        with api.Environment.manage():
            env = api.Environment(cr, SUPERUSER_ID, {})

            # Create default commission types
            commission_type_model = env['commission.type']
            created_types = commission_type_model.create_default_types()
            _logger.info(f"Created {len(created_types)} default commission types")

            # Initialize commission dashboard view
            dashboard_model = env['commission.dashboard']
            if hasattr(dashboard_model, 'init'):
                dashboard_model.init()
                _logger.info("Initialized commission dashboard view")

            # Create initial alert categories if needed
            alert_model = env['commission.alert']
            # We don't create initial alerts, just ensure the model is accessible
            _logger.info("Commission alert system initialized")

            # Optional: Auto-migrate existing commission data
            # Uncomment the following lines if you want automatic migration
            # _logger.info("Starting automatic migration of existing commission data...")
            # commission_line_model = env['commission.line']
            # migrated_count = commission_line_model.migrate_legacy_commissions()
            # _logger.info(f"Migrated {migrated_count} sale orders to commission lines structure")

        _logger.info("Commission_ax post-installation setup completed successfully")

    except Exception as e:
        _logger.error(f"Error during commission_ax post-installation setup: {str(e)}")
        # Don't raise the exception to avoid installation failure
        # The module should still install even if some setup steps fail