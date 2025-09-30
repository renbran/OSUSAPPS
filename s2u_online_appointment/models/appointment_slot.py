# -*- coding: utf-8 -*-

from odoo.addons.s2u_online_appointment.helpers import functions
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AppointmentSlot(models.Model):
    _name = 's2u.appointment.slot'
    _order = 'videographer_id, user_id, day, slot'
    _description = "Availability Slot"

    @api.model
    def _get_week_days(self):
        return [
            ('0', _('Monday')),
            ('1', _('Tuesday')),
            ('2', _('Wednesday')),
            ('3', _('Thursday')),
            ('4', _('Friday')),
            ('5', _('Saturday')),
            ('6', _('Sunday'))
        ]

    # Core Fields
    videographer_id = fields.Many2one('s2u.videographer.profile', string='Videographer',
                                      ondelete='cascade', index=True)
    user_id = fields.Many2one('res.users', string='User', required=True, ondelete='cascade')
    day = fields.Selection(selection=_get_week_days, default='0', string="Day", required=True)
    slot = fields.Float('Time Slot', required=True, help='Start time in hours (e.g., 9.5 for 9:30 AM)')

    # Additional Features
    active = fields.Boolean(default=True, string='Active')
    slot_type = fields.Selection([
        ('regular', 'Regular Availability'),
        ('temporary', 'Temporary Availability'),
        ('blocked', 'Blocked/Unavailable')
    ], string='Type', default='regular', required=True)

    # Date Range for Temporary Slots
    date_from = fields.Date(string='From Date', help='For temporary availability')
    date_to = fields.Date(string='To Date', help='For temporary availability')

    # Notes
    notes = fields.Char(string='Notes', help='Internal notes about this slot')

    @api.constrains('slot')
    def _slot_validation(self):
        for record in self:
            if functions.float_to_time(record.slot) < '00:00' or functions.float_to_time(record.slot) > '23:59':
                raise ValidationError(_('The slot value must be between 0:00 and 23:59!'))

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to and record.date_from > record.date_to:
                raise ValidationError(_('End date must be after start date.'))
