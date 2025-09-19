from . import models
from . import wizards
from . import reports


def post_init_hook(cr, registry):
    """
    Simple post-init hook for commission module.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Commission AX module installed successfully")