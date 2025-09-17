# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CommissionType(models.Model):
    """Commission Type configuration model for commission_lines compatibility"""
    _name = 'commission.type'
    _description = 'Commission Type'
    _order = 'sequence, name'
    _rec_name = 'name'

    # Basic fields
    sequence = fields.Integer(string='Sequence', default=10, help='Used to order commission types')
    name = fields.Char(string='Name', required=True, help='Commission type name')
    code = fields.Char(string='Code', required=True, help='Unique code for commission type')
    
    # Additional fields for comprehensive commission type management
    active = fields.Boolean(string='Active', default=True)
    description = fields.Text(string='Description', help='Detailed description of commission type')
    
    # Commission calculation fields
    calculation_method = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage'),
        ('tiered', 'Tiered Percentage'),
    ], string='Calculation Method', default='percentage', required=True)
    
    default_rate = fields.Float(
        string='Default Rate', 
        digits=(16, 4),
        help='Default commission rate for this type'
    )
    
    # Commission type category
    commission_category = fields.Selection([
        ('sales', 'Sales Commission'),
        ('referral', 'Referral Commission'),
        ('management', 'Management Override'),
        ('bonus', 'Bonus Commission'),
        ('other', 'Other'),
    ], string='Category', default='sales', required=True)
    
    # Integration fields
    account_id = fields.Many2one(
        'account.account',
        string='Commission Expense Account',
        help='Default account for commission expenses'
    )
    
    # Constraints and rules
    min_amount = fields.Monetary(
        string='Minimum Amount',
        currency_field='currency_id',
        help='Minimum commission amount'
    )
    
    max_amount = fields.Monetary(
        string='Maximum Amount', 
        currency_field='currency_id',
        help='Maximum commission amount (0 = no limit)'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    # SQL constraints
    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Commission type code must be unique!'),
        ('check_rates', 'CHECK(default_rate >= 0)', 'Commission rate must be positive!'),
        ('check_amounts', 'CHECK(max_amount = 0 OR max_amount >= min_amount)', 
         'Maximum amount must be greater than minimum amount!'),
    ]

    @api.constrains('code')
    def _check_code_format(self):
        """Validate commission type code format"""
        for record in self:
            if record.code:
                if not record.code.replace('_', '').replace('-', '').isalnum():
                    raise ValidationError(
                        "Commission type code can only contain letters, numbers, "
                        "hyphens and underscores."
                    )
                if len(record.code) > 20:
                    raise ValidationError("Commission type code cannot exceed 20 characters.")

    @api.constrains('default_rate', 'calculation_method')
    def _check_rate_consistency(self):
        """Validate rate based on calculation method"""
        for record in self:
            if record.calculation_method == 'percentage' and record.default_rate > 100:
                raise ValidationError(
                    "Percentage-based commission rate cannot exceed 100%."
                )

    def name_get(self):
        """Custom name display with code"""
        result = []
        for record in self:
            name = f"[{record.code}] {record.name}"
            result.append((record.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """Enhanced search by code or name"""
        args = args or []
        if name:
            # Search by code or name
            commission_types = self.search([
                '|',
                ('code', operator, name),
                ('name', operator, name)
            ] + args, limit=limit)
            if commission_types:
                return commission_types.name_get()
        return super(CommissionType, self)._name_search(
            name, args, operator, limit, name_get_uid
        )

    @api.model
    def create_default_types(self):
        """Create default commission types for initial setup"""
        default_types = [
            {
                'sequence': 10,
                'name': 'Sales Commission',
                'code': 'SALES',
                'calculation_method': 'percentage',
                'default_rate': 5.0,
                'commission_category': 'sales',
                'description': 'Standard sales commission for direct sales'
            },
            {
                'sequence': 20,
                'name': 'Referral Commission',
                'code': 'REFERRAL',
                'calculation_method': 'percentage',
                'default_rate': 2.0,
                'commission_category': 'referral',
                'description': 'Commission for customer referrals'
            },
            {
                'sequence': 30,
                'name': 'Management Override',
                'code': 'MGMT_OVERRIDE',
                'calculation_method': 'percentage',
                'default_rate': 1.0,
                'commission_category': 'management',
                'description': 'Management override commission'
            },
            {
                'sequence': 40,
                'name': 'Director Commission',
                'code': 'DIRECTOR',
                'calculation_method': 'percentage',
                'default_rate': 1.5,
                'commission_category': 'management',
                'description': 'Director level commission'
            },
            {
                'sequence': 50,
                'name': 'Broker Commission',
                'code': 'BROKER',
                'calculation_method': 'percentage',
                'default_rate': 3.0,
                'commission_category': 'sales',
                'description': 'External broker commission'
            }
        ]
        
        created_types = []
        for type_data in default_types:
            # Check if type already exists
            existing = self.search([('code', '=', type_data['code'])])
            if not existing:
                commission_type = self.create(type_data)
                created_types.append(commission_type)
        
        return created_types

    def action_view_commissions(self):
        """View commissions using this type"""
        self.ensure_one()
        # This action would show related commission records
        # Implementation depends on your commission line model structure
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Commission Type',
                'message': f'Commission type: {self.name} ({self.code})',
                'type': 'info',
            }
        }