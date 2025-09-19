import logging
from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    """Safe post installation hook - minimal operations only"""
    try:
        _logger.info("Commission AX: Safe mode installation completed")
    except Exception as e:
        _logger.error(f"Commission AX: Installation error: {str(e)}")
        # Don't raise to avoid blocking installation