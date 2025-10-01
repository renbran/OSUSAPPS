# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class NewAppModel(models.Model):
    _name = 'new.app.model'
    _description = 'New App Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
        help='Enter the name'
    )

    description = fields.Text(
        string='Description',
        tracking=True,
    )

    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True,
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)

    date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
        tracking=True,
    )

    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        tracking=True,
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        tracking=True,
    )

    amount = fields.Float(
        string='Amount',
        digits='Product Price',
        tracking=True,
    )

    notes = fields.Html(
        string='Notes',
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )

    # Computed fields
    display_name_custom = fields.Char(
        string='Display Name',
        compute='_compute_display_name_custom',
        store=True,
    )

    @api.depends('name', 'date')
    def _compute_display_name_custom(self):
        for record in self:
            if record.date:
                record.display_name_custom = f"{record.name} - {record.date}"
            else:
                record.display_name_custom = record.name

    # Constraints
    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount < 0:
                raise ValidationError("Amount cannot be negative!")

    # CRUD Methods
    @api.model
    def create(self, vals):
        # Add custom logic before create
        record = super(NewAppModel, self).create(vals)
        return record

    def write(self, vals):
        # Add custom logic before write
        result = super(NewAppModel, self).write(vals)
        return result

    def unlink(self):
        # Add custom logic before delete
        return super(NewAppModel, self).unlink()

    # Action Methods
    def action_confirm(self):
        self.write({'state': 'confirmed'})
        return True

    def action_done(self):
        self.write({'state': 'done'})
        return True

    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    def action_cancel(self):
        self.write({'state': 'cancelled'})
        return True
