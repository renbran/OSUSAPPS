# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StatementConfigAlias(models.Model):
    """Alias model for statement.config references"""
    _name = 'statement.config'
    _description = 'Statement Configuration (Alias)'
    _order = 'name, id'

    name = fields.Char(string='Configuration Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', 
                                default=lambda self: self.env.company)
    
    # Basic statement settings
    include_zero_balance = fields.Boolean(string='Include Zero Balance', default=False)
    aging_bucket_ids = fields.One2many('statement.ageing.period', 'config_id', 
                                     string='Aging Buckets')
    
    # Additional fields that might be referenced
    statement_format = fields.Selection([
        ('standard', 'Standard'),
        ('detailed', 'Detailed'),
        ('summary', 'Summary')
    ], string='Statement Format', default='standard')
    
    show_aging = fields.Boolean(string='Show Aging Analysis', default=True)
    show_payments = fields.Boolean(string='Show Payments', default=True)

class StatementAgeingPeriodConfig(models.Model):
    """Enhanced ageing period with config reference"""
    _inherit = 'statement.ageing.period'
    
    config_id = fields.Many2one('statement.config', string='Configuration', 
                               ondelete='cascade')

class FollowupHistoryAlias(models.Model):
    """Alias model for followup.history references"""
    _name = 'followup.history'
    _description = 'Follow-up History (Alias)'
    _order = 'date desc, id desc'

    name = fields.Char(string='Reference', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    date = fields.Date(string='Follow-up Date', required=True)
    level_id = fields.Many2one('followup.level', string='Follow-up Level')
    user_id = fields.Many2one('res.users', string='Responsible User')
    description = fields.Text(string='Notes')
    email_sent = fields.Boolean(string='Email Sent', default=False)
    letter_printed = fields.Boolean(string='Letter Printed', default=False)
    company_id = fields.Many2one('res.company', string='Company', 
                                default=lambda self: self.env.company)

class BatchFollowupConfig(models.Model):
    """Model for batch.followup.config references"""
    _name = 'batch.followup.config'
    _description = 'Batch Follow-up Configuration'

    name = fields.Char(string='Configuration Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    schedule_type = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ], string='Schedule Type', default='weekly')
    company_id = fields.Many2one('res.company', string='Company', 
                                default=lambda self: self.env.company)

class ReportConfig(models.Model):
    """Model for report.config references"""
    _name = 'report.config'
    _description = 'Report Configuration'

    name = fields.Char(string='Configuration Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    report_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly')
    ], string='Report Type', default='monthly')
    company_id = fields.Many2one('res.company', string='Company', 
                                default=lambda self: self.env.company)
