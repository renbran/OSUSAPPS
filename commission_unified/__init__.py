# -*- coding: utf-8 -*-
#############################################################################
#
#    Unified Commission Management System
#
#    Copyright (C) 2025-TODAY Commission Unified Team
#
#############################################################################

from . import models
from . import wizard
from . import report


def post_init_hook(cr, registry):
    """Post installation hook"""
    import logging
    _logger = logging.getLogger(__name__)

    _logger.info("Unified Commission Management System installed successfully")
    _logger.info("Starting post-installation configuration...")

    # Initialize commission sequences
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Create default commission sequence if not exists
    sequence = env['ir.sequence'].search([('code', '=', 'commission.lines.unified')], limit=1)
    if not sequence:
        env['ir.sequence'].create({
            'name': 'Commission Lines Sequence',
            'code': 'commission.lines.unified',
            'prefix': 'COMM-',
            'padding': 6,
            'number_next': 1,
        })
        _logger.info("Created default commission sequence")

    # Set default configuration parameters
    config_params = [
        ('commission.auto_calculate_on_confirm', 'True'),
        ('commission.default_payment_method', 'invoice'),
        ('commission.require_approval', 'False'),
        ('commission.max_commission_percentage', '50.0'),
        ('commission.enable_audit_log', 'True'),
    ]

    for key, value in config_params:
        existing = env['ir.config_parameter'].sudo().get_param(key)
        if not existing:
            env['ir.config_parameter'].sudo().set_param(key, value)
            _logger.info(f"Set configuration parameter: {key} = {value}")

    _logger.info("Post-installation configuration completed")


def uninstall_hook(cr, registry):
    """Uninstall hook"""
    import logging
    _logger = logging.getLogger(__name__)

    _logger.info("Unified Commission Management System uninstall hook executed")
    _logger.warning("Please ensure you have backed up all commission data before uninstalling")