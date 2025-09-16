# -*- coding: utf-8 -*-
"""
Date/period utilities for commission modules
This module provides standardized date range functionality
"""

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

def get_date_range(period_type, base_date=None):
    """
    Get standardized date ranges based on period type
    
    Args:
        period_type (str): Type of period (current_month, last_month, etc.)
        base_date (datetime.date, optional): Reference date, defaults to today
        
    Returns:
        tuple: (start_date, end_date)
    """
    today = base_date or date.today()
    
    # Standard date range calculations
    if period_type == 'current_month':
        return (
            today.replace(day=1),
            (today.replace(day=1) + relativedelta(months=1) - timedelta(days=1))
        )
    elif period_type == 'last_month':
        first_day_last_month = (today.replace(day=1) - relativedelta(months=1))
        return (
            first_day_last_month,
            (today.replace(day=1) - timedelta(days=1))
        )
    elif period_type == 'current_quarter':
        quarter_start = today.replace(month=((today.month - 1) // 3) * 3 + 1, day=1)
        return (
            quarter_start,
            (quarter_start + relativedelta(months=3) - timedelta(days=1))
        )
    elif period_type == 'last_quarter':
        current_quarter_start = today.replace(month=((today.month - 1) // 3) * 3 + 1, day=1)
        last_quarter_start = current_quarter_start - relativedelta(months=3)
        return (
            last_quarter_start,
            (current_quarter_start - timedelta(days=1))
        )
    elif period_type == 'current_year':
        return (
            today.replace(month=1, day=1),
            today.replace(month=12, day=31)
        )
    elif period_type == 'last_year':
        last_year = today.year - 1
        return (
            date(last_year, 1, 1),
            date(last_year, 12, 31)
        )
    elif period_type == 'last_30_days':
        return (
            today - timedelta(days=30),
            today
        )
    elif period_type == 'last_90_days':
        return (
            today - timedelta(days=90),
            today
        )
    elif period_type == 'last_365_days':
        return (
            today - timedelta(days=365),
            today
        )
    elif period_type == 'ytd':  # Year to date
        return (
            date(today.year, 1, 1),
            today
        )
    elif period_type == 'all_time':
        return (None, None)  # Special case for no date filtering
    
    # Default to current month if period type not recognized
    return (
        today.replace(day=1),
        (today.replace(day=1) + relativedelta(months=1) - timedelta(days=1))
    )

def get_period_name(period_type, start_date=None, end_date=None):
    """
    Get a human-readable period name based on period type or dates
    
    Args:
        period_type (str): Type of period
        start_date (datetime.date, optional): Start date if custom period
        end_date (datetime.date, optional): End date if custom period
        
    Returns:
        str: Human-readable period name
    """
    if period_type == 'custom' and start_date and end_date:
        return f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"
    
    period_names = {
        'current_month': f"Current Month ({date.today().strftime('%B %Y')})",
        'last_month': f"Last Month ({(date.today().replace(day=1) - timedelta(days=1)).strftime('%B %Y')})",
        'current_quarter': f"Current Quarter (Q{((date.today().month - 1) // 3) + 1} {date.today().year})",
        'last_quarter': "Last Quarter",
        'current_year': f"Current Year ({date.today().year})",
        'last_year': f"Last Year ({date.today().year - 1})",
        'last_30_days': "Last 30 Days",
        'last_90_days': "Last 90 Days",
        'last_365_days': "Last 365 Days",
        'ytd': f"Year to Date ({date.today().year})",
        'all_time': "All Time",
    }
    
    return period_names.get(period_type, "Custom Period")