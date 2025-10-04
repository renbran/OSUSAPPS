# -*- coding: utf-8 -*-

from odoo.addons.online_appointment.helpers import functions
from odoo.exceptions import ValidationError
from odoo import api, fields, models, _


class OnlineAppointmentOption(models.Model):
    """
    Appointment Option Model
    
    Defines different types of appointment services available for booking.
    Each option has a duration and can be restricted to specific users.
    """
    _name = 'online_appointment.option'
    _description = 'Online Appointment Option'
    _order = 'sequence, name'
    _rec_name = 'name'

    name = fields.Char(
        string='Appointment Option',
        required=True,
        translate=True,
        help="Name of the appointment service (e.g., 'Consultation', 'Checkup')"
    )
    description = fields.Text(
        string='Description',
        translate=True,
        help="Detailed description of the appointment option"
    )
    duration = fields.Float(
        string='Duration (Hours)',
        required=True,
        default=1.0,
        help="Duration of the appointment in hours (e.g., 0.5 for 30 minutes)"
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Order of appearance in selection lists"
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help="Uncheck to hide this option from booking forms"
    )
    user_specific = fields.Boolean(
        string='User Specific',
        default=False,
        help="If checked, only allowed users can provide this service"
    )
    users_allowed = fields.Many2many(
        'res.users',
        'online_appointment_option_user_rel',
        'option_id',
        'user_id',
        string='Allowed Users',
        help="Users who can provide this appointment service"
    )
    color = fields.Integer(
        string='Color',
        default=0,
        help="Color for calendar display"
    )
    price = fields.Monetary(
        string='Price',
        currency_field='currency_id',
        help="Optional price for this appointment type"
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    @api.constrains('duration')
    def _check_duration_range(self):
        """Validate that duration is within acceptable limits"""
        for option in self:
            if option.duration <= 0:
                raise ValidationError(_('Duration must be greater than 0 hours.'))
            if option.duration > 8.0:
                raise ValidationError(_('Duration cannot exceed 8 hours.'))
            
            # Convert to time format for additional validation
            time_str = functions.float_to_time(option.duration)
            if time_str < '00:05':
                raise ValidationError(_('Minimum duration is 5 minutes (0:05).'))

    @api.constrains('users_allowed', 'user_specific')
    def _check_user_specific_consistency(self):
        """Ensure user-specific options have at least one allowed user"""
        for option in self:
            if option.user_specific and not option.users_allowed:
                raise ValidationError(
                    _('User-specific appointment options must have at least one allowed user.')
                )

    def name_get(self):
        """Enhanced name display including duration"""
        result = []
        for option in self:
            duration_str = functions.float_to_time(option.duration)
            name = f"{option.name} ({duration_str})"
            if option.price > 0:
                name += f" - {option.currency_id.symbol}{option.price}"
            result.append((option.id, name))
        return result

