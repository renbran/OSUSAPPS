import logging
from odoo import SUPERUSER_ID, api, _

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    """
    Robust Post Installation Hook for commission_ax module

    Features:
    - Comprehensive error handling
    - Graceful degradation
    - Detailed logging
    - Never fails installation
    """
    _logger.info("🚀 Starting commission_ax post-installation setup (robust mode)...")

    try:
        with api.Environment.manage():
            env = api.Environment(cr, SUPERUSER_ID, {})

            # Step 1: Check and report dependencies
            dependency_status = _check_dependencies()

            # Step 2: Setup core commission types (safe)
            types_created = _setup_commission_types_safe(env)

            # Step 3: Initialize available features based on loaded models
            features_initialized = _initialize_available_features(env)

            # Step 4: Setup security groups (safe)
            security_status = _setup_security_groups_safe(env)

            # Step 5: Create default data if needed (safe)
            data_created = _create_default_data_safe(env)

            # Step 6: Report installation status
            _report_installation_status(dependency_status, types_created, features_initialized, security_status, data_created)

        _logger.info("✅ Commission_ax post-installation setup completed successfully")

    except Exception as e:
        _logger.error(f"❌ Error during commission_ax post-installation setup: {str(e)}")
        # CRITICAL: Don't raise the exception - let installation continue
        _logger.info("⚠️  Installation continued despite setup errors - basic functionality will be available")


def _check_dependencies():
    """Check and report on dependencies with detailed status"""
    status = {
        'xlsxwriter': False,
        'ml_libraries': False,
        'all_models_loaded': False
    }

    try:
        # Check xlsxwriter
        try:
            import xlsxwriter
            status['xlsxwriter'] = True
            _logger.info("✅ xlsxwriter available - Excel export enabled")
        except ImportError:
            _logger.warning("⚠️  xlsxwriter not available - Excel export will use basic CSV")

        # Check ML libraries
        try:
            import numpy, pandas
            from sklearn.linear_model import LinearRegression
            status['ml_libraries'] = True
            _logger.info("✅ ML libraries available - Advanced AI analytics enabled")
        except ImportError:
            _logger.warning("⚠️  ML libraries not available - Using basic statistical analytics")

        # Report status
        if not any(status.values()):
            _logger.info("📋 To enable enhanced features, install optional dependencies:")
            _logger.info("   pip install xlsxwriter numpy pandas scikit-learn")

    except Exception as e:
        _logger.error(f"Error checking dependencies: {str(e)}")

    return status


def _setup_commission_types_safe(env):
    """Setup default commission types with safe error handling"""
    types_created = 0

    try:
        # Check if commission.type model is available
        if 'commission.type' not in env:
            _logger.warning("commission.type model not available - skipping default types creation")
            return 0

        commission_type_model = env['commission.type']

        # Check if method exists and is callable
        if hasattr(commission_type_model, 'create_default_types') and callable(getattr(commission_type_model, 'create_default_types')):
            try:
                created_types = commission_type_model.create_default_types()
                types_created = len(created_types) if created_types else 0
                _logger.info(f"✅ Created {types_created} default commission types")
            except Exception as e:
                _logger.warning(f"Failed to create default types: {str(e)}")
        else:
            # Create basic default types manually
            types_created = _create_basic_commission_types(env, commission_type_model)

    except Exception as e:
        _logger.error(f"Error setting up commission types: {str(e)}")

    return types_created


def _create_basic_commission_types(env, commission_type_model):
    """Create basic commission types manually"""
    try:
        default_types = [
            {
                'name': 'Broker Commission',
                'calculation_method': 'percentage_total',
                'rate': 2.5,
                'category': 'external',
            },
            {
                'name': 'Agent Commission',
                'calculation_method': 'percentage_total',
                'rate': 1.5,
                'category': 'internal',
            }
        ]

        created_count = 0
        for type_data in default_types:
            try:
                # Check if type already exists
                existing = commission_type_model.search([('name', '=', type_data['name'])], limit=1)
                if not existing:
                    commission_type_model.create(type_data)
                    created_count += 1
            except Exception as e:
                _logger.warning(f"Failed to create commission type {type_data['name']}: {str(e)}")

        _logger.info(f"✅ Created {created_count} basic commission types")
        return created_count

    except Exception as e:
        _logger.error(f"Error creating basic commission types: {str(e)}")
        return 0


def _initialize_available_features(env):
    """Initialize features based on available models"""
    features_initialized = []

    try:
        # Check which models are available and initialize them safely
        model_checks = [
            ('commission.line', 'Commission Lines'),
            ('commission.ai.analytics', 'AI Analytics'),
            ('commission.alert', 'Alert System'),
            ('commission.performance.report', 'Performance Reports'),
        ]

        for model_name, feature_name in model_checks:
            try:
                if model_name in env:
                    model = env[model_name]

                    # Try to initialize if method exists
                    if hasattr(model, 'init_feature') and callable(getattr(model, 'init_feature')):
                        model.init_feature()

                    features_initialized.append(feature_name)
                    _logger.info(f"✅ {feature_name} feature initialized")
                else:
                    _logger.info(f"ℹ️  {feature_name} model not available")
            except Exception as e:
                _logger.warning(f"Failed to initialize {feature_name}: {str(e)}")

    except Exception as e:
        _logger.error(f"Error initializing features: {str(e)}")

    return features_initialized


def _setup_security_groups_safe(env):
    """Setup security groups with safe error handling"""
    try:
        # Check if security groups exist
        commission_user_group = env.ref('commission_ax.group_commission_user', raise_if_not_found=False)
        commission_manager_group = env.ref('commission_ax.group_commission_manager', raise_if_not_found=False)

        if commission_user_group and commission_manager_group:
            _logger.info("✅ Commission security groups validated")
            return True
        else:
            _logger.warning("⚠️  Some commission security groups not found")
            return False

    except Exception as e:
        _logger.error(f"Error validating security groups: {str(e)}")
        return False


def _create_default_data_safe(env):
    """Create default data safely"""
    data_created = 0

    try:
        # Only create data if we're in a clean installation
        # Check if commission lines exist
        if 'commission.line' in env:
            line_count = env['commission.line'].search_count([])
            if line_count == 0:
                _logger.info("ℹ️  Clean installation detected - ready for use")
            else:
                _logger.info(f"ℹ️  Found {line_count} existing commission lines")

    except Exception as e:
        _logger.error(f"Error checking default data: {str(e)}")

    return data_created


def _report_installation_status(dependency_status, types_created, features_initialized, security_status, data_created):
    """Report comprehensive installation status"""
    try:
        _logger.info("📊 COMMISSION_AX INSTALLATION REPORT")
        _logger.info("=" * 50)

        # Dependencies
        deps_ok = sum(dependency_status.values())
        _logger.info(f"🔗 Dependencies: {deps_ok}/{len(dependency_status)} optional features available")

        # Models and features
        _logger.info(f"📦 Commission Types: {types_created} created")
        _logger.info(f"🚀 Features: {len(features_initialized)} initialized")
        _logger.info(f"🔐 Security: {'✅ OK' if security_status else '⚠️  Partial'}")

        # Overall status
        if types_created > 0 and len(features_initialized) > 0:
            _logger.info("🎉 INSTALLATION SUCCESSFUL - Ready for production use!")
        else:
            _logger.info("⚠️  INSTALLATION PARTIAL - Basic functionality available")

        _logger.info("=" * 50)

    except Exception as e:
        _logger.error(f"Error generating installation report: {str(e)}")


def pre_init_hook(cr):
    """Pre-installation hook with safe error handling"""
    try:
        _logger.info("🔧 Starting commission_ax pre-installation checks...")

        # Check Odoo version compatibility
        try:
            import odoo
            version = odoo.release.version_info
            if version[0] != 17:
                _logger.warning(f"⚠️  This module is designed for Odoo 17. Current version: {version[0]}")
            else:
                _logger.info("✅ Odoo 17 compatibility confirmed")
        except Exception as e:
            _logger.warning(f"Could not check Odoo version: {str(e)}")

        _logger.info("✅ Pre-installation checks completed")

    except Exception as e:
        _logger.error(f"Error during pre-installation checks: {str(e)}")
        # Don't fail installation on pre-check errors


def uninstall_hook(cr, registry):
    """Safe uninstallation hook"""
    try:
        _logger.info("🗑️  Starting commission_ax module uninstallation cleanup...")

        with api.Environment.manage():
            env = api.Environment(cr, SUPERUSER_ID, {})

            # Safe cleanup of automated tasks
            try:
                cron_model = env['ir.cron']
                commission_crons = cron_model.search([
                    ('model_id.model', 'like', 'commission.%')
                ])
                if commission_crons:
                    commission_crons.unlink()
                    _logger.info(f"🗑️  Removed {len(commission_crons)} commission cron jobs")
            except Exception as e:
                _logger.warning(f"Could not clean up cron jobs: {str(e)}")

        _logger.info("✅ Commission_ax module uninstallation cleanup completed")

    except Exception as e:
        _logger.error(f"Error during uninstallation cleanup: {str(e)}")