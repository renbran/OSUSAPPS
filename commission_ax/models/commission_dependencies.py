# -*- coding: utf-8 -*-
"""
Commission Dependencies Manager
===============================

World-class dependency management for commission module:
- External library validation
- Graceful degradation
- Feature availability checking
- Installation guidance
"""

import logging

_logger = logging.getLogger(__name__)

# External dependencies status
DEPENDENCIES_STATUS = {
    'xlsxwriter': False,
    'numpy': False,
    'pandas': False,
    'scikit-learn': False,
}

# Check xlsxwriter
try:
    import xlsxwriter
    DEPENDENCIES_STATUS['xlsxwriter'] = True
    _logger.info("xlsxwriter library available - Excel export enabled")
except ImportError:
    _logger.warning("xlsxwriter not available - Excel export will be disabled")

# Check machine learning libraries
try:
    import numpy as np
    DEPENDENCIES_STATUS['numpy'] = True
except ImportError:
    _logger.warning("numpy not available - AI analytics will use basic calculations")

try:
    import pandas as pd
    DEPENDENCIES_STATUS['pandas'] = True
except ImportError:
    _logger.warning("pandas not available - Advanced data processing disabled")

try:
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    DEPENDENCIES_STATUS['scikit-learn'] = True
except ImportError:
    _logger.warning("scikit-learn not available - ML features disabled")


def check_dependency(dependency_name):
    """Check if a specific dependency is available"""
    return DEPENDENCIES_STATUS.get(dependency_name, False)


def get_missing_dependencies():
    """Get list of missing dependencies"""
    return [dep for dep, available in DEPENDENCIES_STATUS.items() if not available]


def get_available_features():
    """Get list of available features based on dependencies"""
    features = ['basic_commission_management']

    if DEPENDENCIES_STATUS['xlsxwriter']:
        features.append('excel_export')

    if DEPENDENCIES_STATUS['numpy']:
        features.append('advanced_calculations')

    if DEPENDENCIES_STATUS['pandas']:
        features.append('data_analysis')

    if DEPENDENCIES_STATUS['scikit-learn']:
        features.append('machine_learning')
        features.append('predictive_analytics')
        features.append('anomaly_detection')

    return features


def get_installation_guide():
    """Get installation guide for missing dependencies"""
    missing = get_missing_dependencies()
    if not missing:
        return "All dependencies are installed!"

    guide = "Missing dependencies installation guide:\n\n"

    if 'xlsxwriter' in missing:
        guide += "For Excel export functionality:\n"
        guide += "  pip install xlsxwriter\n\n"

    if any(dep in missing for dep in ['numpy', 'pandas', 'scikit-learn']):
        guide += "For AI and advanced analytics:\n"
        guide += "  pip install numpy pandas scikit-learn\n\n"

    guide += "Note: These are optional dependencies. The module will work without them,\n"
    guide += "but some advanced features will be disabled.\n"

    return guide


def validate_for_feature(feature_name):
    """Validate dependencies for a specific feature"""
    feature_deps = {
        'excel_export': ['xlsxwriter'],
        'machine_learning': ['numpy', 'pandas', 'scikit-learn'],
        'ai_analytics': ['numpy', 'pandas', 'scikit-learn'],
        'predictive_analytics': ['numpy', 'scikit-learn'],
        'anomaly_detection': ['numpy', 'scikit-learn'],
        'data_analysis': ['pandas'],
    }

    required_deps = feature_deps.get(feature_name, [])
    missing_deps = [dep for dep in required_deps if not DEPENDENCIES_STATUS.get(dep, False)]

    return len(missing_deps) == 0, missing_deps