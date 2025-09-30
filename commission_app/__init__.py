# -*- coding: utf-8 -*-

from . import models
from . import wizards
from . import reports

def post_init_hook(cr, registry):
    """Post-installation hook to set up initial data."""
    pass

def uninstall_hook(cr, registry):
    """Pre-uninstallation hook to clean up data."""
    pass