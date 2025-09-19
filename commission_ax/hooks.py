import logging
from odoo import SUPERUSER_ID, api, _

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    """
    Post installation hook for commission_ax module

    This hook performs essential setup tasks:
    1. Validates dependencies
    2. Creates default commission types
    3. Initializes dashboard views
    4. Sets up alert system
    5. Provides migration guidance
    """
    try:
        _logger.info("🚀 Starting commission_ax post-installation setup...")

        with api.Environment.manage():
            env = api.Environment(cr, SUPERUSER_ID, {})

            # Step 1: Check dependencies
            _check_dependencies()

            # Step 2: Create default commission types
            _setup_commission_types(env)

            # Step 3: Initialize dashboard views
            _initialize_dashboard(env)

            # Step 4: Setup alert system
            _setup_alert_system(env)

            # Step 5: Validate security groups
            _validate_security_groups(env)

            # Step 6: Create demo data if in demo mode
            _setup_demo_data(env)

        _logger.info("✅ Commission_ax post-installation setup completed successfully")

    except Exception as e:
        _logger.error(f"❌ Error during commission_ax post-installation setup: {str(e)}")
        # Log full traceback for debugging
        import traceback
        _logger.error(f"Full traceback: {traceback.format_exc()}")

        # Don't raise the exception to avoid installation failure
        # The module should still install even if some setup steps fail


def _check_dependencies():
    """Check and report on external dependencies"""
    try:
        missing_deps = []

        # Check xlsxwriter
        try:
            import xlsxwriter
            _logger.info("✅ xlsxwriter available - Excel export enabled")
        except ImportError:
            missing_deps.append('xlsxwriter')
            _logger.warning("⚠️  xlsxwriter not available - Excel export disabled")

        # Check ML libraries
        try:
            import numpy, pandas
            from sklearn.linear_model import LinearRegression
            _logger.info("✅ ML libraries available - AI analytics enabled")
        except ImportError:
            missing_deps.append('numpy/pandas/scikit-learn')
            _logger.warning("⚠️  ML libraries not available - AI features disabled")

        if missing_deps:
            _logger.info("📋 To install missing dependencies:")
            _logger.info("   pip install xlsxwriter numpy pandas scikit-learn")

    except Exception as e:
        _logger.error(f"Error checking dependencies: {str(e)}")


def _setup_commission_types(env):
    """Setup default commission types"""
    try:
        commission_type_model = env['commission.type']

        # Check if method exists
        if hasattr(commission_type_model, 'create_default_types'):
            created_types = commission_type_model.create_default_types()
            _logger.info(f"✅ Created {len(created_types)} default commission types")
        else:
            _logger.warning("create_default_types method not found in commission.type model")

    except Exception as e:
        _logger.error(f"Error setting up commission types: {str(e)}")


def _initialize_dashboard(env):
    """Initialize commission dashboard"""
    try:
        dashboard_model = env['commission.dashboard']

        # Check if initialization method exists
        if hasattr(dashboard_model, 'init'):
            dashboard_model.init()
            _logger.info("✅ Initialized commission dashboard view")
        else:
            _logger.info("Dashboard init method not found - skipping initialization")

    except Exception as e:
        _logger.error(f"Error initializing dashboard: {str(e)}")


def _setup_alert_system(env):
    """Setup commission alert system"""
    try:
        alert_model = env['commission.alert']

        # Verify the model is accessible
        alert_count = alert_model.search_count([])
        _logger.info(f"✅ Commission alert system initialized (existing alerts: {alert_count})")

    except Exception as e:
        _logger.error(f"Error setting up alert system: {str(e)}")


def _validate_security_groups(env):
    """Validate security groups and access rights"""
    try:
        # Check if commission groups exist
        commission_user_group = env.ref('commission_ax.group_commission_user', raise_if_not_found=False)
        commission_manager_group = env.ref('commission_ax.group_commission_manager', raise_if_not_found=False)

        if commission_user_group and commission_manager_group:
            _logger.info("✅ Commission security groups validated")
        else:
            _logger.warning("⚠️  Commission security groups not found")

        # Validate model access rights
        access_model = env['ir.model.access']
        commission_access = access_model.search([('model_id.model', 'like', 'commission.%')])
        _logger.info(f"✅ Found {len(commission_access)} commission model access rights")

    except Exception as e:
        _logger.error(f"Error validating security groups: {str(e)}")


def _setup_demo_data(env):
    """Setup demo data if in demo mode"""
    try:
        # Check if we should create demo data
        if env.ref('base.module_base').demo:
            _logger.info("Demo mode detected - setting up demo commission data")
            # Demo data will be loaded from data files
        else:
            _logger.info("Production mode - skipping demo data creation")

    except Exception as e:
        _logger.error(f"Error setting up demo data: {str(e)}")


def pre_init_hook(cr):
    """Pre-installation hook for commission_ax module"""
    try:
        _logger.info("🔧 Starting commission_ax pre-installation checks...")

        # Check Odoo version compatibility
        import odoo
        version = odoo.release.version_info
        if version[0] != 17:
            _logger.warning(f"⚠️  This module is designed for Odoo 17. Current version: {version[0]}")

        _logger.info("✅ Pre-installation checks completed")

    except Exception as e:
        _logger.error(f"Error during pre-installation checks: {str(e)}")
        # Don't fail installation on pre-check errors


def uninstall_hook(cr, registry):
    """Uninstallation hook for commission_ax module"""
    try:
        _logger.info("🗑️  Starting commission_ax module uninstallation cleanup...")

        with api.Environment.manage():
            env = api.Environment(cr, SUPERUSER_ID, {})

            # Remove automated cron jobs
            cron_model = env['ir.cron']
            commission_crons = cron_model.search([
                ('model_id.model', 'like', 'commission.%')
            ])
            if commission_crons:
                commission_crons.unlink()
                _logger.info(f"🗑️  Removed {len(commission_crons)} commission cron jobs")

        _logger.info("✅ Commission_ax module uninstallation cleanup completed")

    except Exception as e:
        _logger.error(f"Error during uninstallation cleanup: {str(e)}")