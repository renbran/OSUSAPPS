# -*- coding: utf-8 -*-

from odoo.addons.online_appointment.helpers import functions
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OnlineAppointmentSlot(models.Model):
    """
    Appointment Time Slot Model
    
    Defines available time slots for each user on specific days of the week.
    Used to determine when appointments can be booked.
    """
    _name = 'online_appointment.slot'
    _description = 'Online Appointment Time Slot'
    _order = 'user_id, day, slot_time'
    _rec_name = 'display_name'
    
    @api.model
    def _get_week_days(self):
        """Get list of weekdays for selection field"""
        return [
            ('0', _('Monday')),
            ('1', _('Tuesday')),
            ('2', _('Wednesday')),
            ('3', _('Thursday')),
            ('4', _('Friday')),
            ('5', _('Saturday')),
            ('6', _('Sunday'))
        ]

    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        ondelete='cascade',
        help="User who will be available during this time slot"
    )
    day = fields.Selection(
        selection=_get_week_days,
        default='0',
        string="Day of Week",
        required=True,
        help="Day of the week for this time slot"
    )
    slot_time = fields.Float(
        string='Time Slot',
        required=True,
        help="Time in 24-hour format (e.g., 9.5 for 9:30 AM)"
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help="Uncheck to temporarily disable this time slot"
    )
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
        help="Human-readable representation of the slot"
    )

    # Legacy field for backwards compatibility
    slot = fields.Float(
        string='Slot (Legacy)',
        related='slot_time',
        help="Legacy field for backwards compatibility"
    )

    @api.depends('user_id', 'day', 'slot_time')
    def _compute_display_name(self):
        """Compute human-readable display name"""
        day_mapping = dict(self._get_week_days())
        for slot in self:
            if slot.user_id and slot.day:
                time_str = functions.float_to_time(slot.slot_time)
                day_name = day_mapping.get(slot.day, slot.day)
                slot.display_name = f"{slot.user_id.name} - {day_name} {time_str}"
            else:
                slot.display_name = _("Incomplete Slot")

    @api.constrains('slot_time')
    def _check_slot_time_range(self):
        """Validate that slot time is within valid 24-hour range"""
        for slot in self:
            if slot.slot_time < 0.0 or slot.slot_time >= 24.0:
                raise ValidationError(
                    _('Time slot must be between 00:00 and 23:59. Got: %s') %
                    functions.float_to_time(slot.slot_time)
                )

    @api.constrains('user_id', 'day', 'slot_time')
    def _check_unique_slot(self):
        """Ensure no duplicate slots for the same user, day, and time"""
        for slot in self:
            duplicate = self.search([
                ('user_id', '=', slot.user_id.id),
                ('day', '=', slot.day),
                ('slot_time', '=', slot.slot_time),
                ('id', '!=', slot.id),
                ('active', '=', True)
            ])
            if duplicate:
                time_str = functions.float_to_time(slot.slot_time)
                day_name = dict(self._get_week_days())[slot.day]
                raise ValidationError(
                    _('Duplicate time slot detected for %s on %s at %s') %
                    (slot.user_id.name, day_name, time_str)
                )

    def name_get(self):
        """Enhanced name display"""
        result = []
        day_mapping = dict(self._get_week_days())
        for slot in self:
            time_str = functions.float_to_time(slot.slot_time)
            day_name = day_mapping.get(slot.day, slot.day)
            name = f"{slot.user_id.name} - {day_name} {time_str}"
            result.append((slot.id, name))
        return result

    @api.model
    def get_available_slots(self, user_id, day, exclude_booked=True):
        """
        Get available time slots for a specific user and day
        
        :param user_id: ID of the user
        :param day: Day of week (0-6)
        :param exclude_booked: Whether to exclude already booked slots
        :return: List of available slot records
        """
        domain = [
            ('user_id', '=', user_id),
            ('day', '=', str(day)),
            ('active', '=', True)
        ]
        
        slots = self.search(domain, order='slot_time')
        
        if exclude_booked:
            # TODO: Add logic to exclude slots that have existing appointments
            pass
            
        return slots
