# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class OnlineAppointmentRegistration(models.Model):
    """
    Appointment Registration Model
    
    Manages the relationship between website visitors and their booked appointments.
    Integrates with calendar events and provides portal access.
    """
    _name = 'online_appointment.registration'
    _description = 'Online Appointment Registration'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'appointment_begin desc'
    _rec_name = 'display_name'

    # Core fields
    event_id = fields.Many2one(
        'calendar.event',
        string='Calendar Event',
        required=True,
        ondelete='cascade',
        help="Associated calendar event"
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        ondelete='cascade',
        tracking=True,
        help="Customer who booked the appointment"
    )
    appointee_id = fields.Many2one(
        'res.partner',
        string='Service Provider',
        ondelete='cascade',
        tracking=True,
        help="Partner record of the user providing the service"
    )
    appointee_user_id = fields.Many2one(
        'res.users',
        string='Service Provider User',
        tracking=True,
        help="User providing the appointment service"
    )
    appointment_option_id = fields.Many2one(
        'online_appointment.option',
        string='Appointment Type',
        tracking=True,
        help="Type of appointment booked"
    )

    # Related fields from calendar event
    appointment_begin = fields.Datetime(
        string="Start Date",
        related='event_id.start',
        readonly=True,
        store=True,
        help="Appointment start date and time"
    )
    appointment_end = fields.Datetime(
        string="End Date",
        related='event_id.stop',
        readonly=True,
        store=True,
        help="Appointment end date and time"
    )
    name = fields.Char(
        string='Subject',
        related='event_id.name',
        readonly=True,
        store=True,
        help="Appointment subject/title"
    )

    # Status and workflow
    state = fields.Selection([
        ('draft', _('Draft')),
        ('pending', _('Pending Confirmation')),
        ('confirmed', _('Confirmed')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('no_show', _('No Show')),
    ], 
        required=True,
        default='confirmed',
        string='Status',
        copy=False,
        tracking=True,
        help="Current status of the appointment"
    )

    # Customer information
    customer_name = fields.Char(
        string='Customer Name',
        required=True,
        tracking=True,
        help="Name of the person booking the appointment"
    )
    customer_email = fields.Char(
        string='Customer Email',
        required=True,
        tracking=True,
        help="Email address for appointment notifications"
    )
    customer_phone = fields.Char(
        string='Customer Phone',
        tracking=True,
        help="Phone number of the customer"
    )
    notes = fields.Text(
        string='Customer Notes',
        help="Additional notes or requirements from the customer"
    )

    # System fields
    booking_date = fields.Datetime(
        string='Booking Date',
        default=fields.Datetime.now,
        readonly=True,
        help="When this appointment was booked"
    )
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )
    duration_hours = fields.Float(
        string='Duration (Hours)',
        compute='_compute_duration',
        store=True,
        help="Duration of the appointment in hours"
    )

    # Legacy fields for backwards compatibility
    appointee_interaction = fields.Boolean(
        string='Appointee Interaction (Legacy)',
        default=False,
        help="Legacy field for backwards compatibility"
    )

    @api.depends('customer_name', 'appointment_begin', 'appointment_option_id')
    def _compute_display_name(self):
        """Compute human-readable display name"""
        for registration in self:
            parts = []
            if registration.customer_name:
                parts.append(registration.customer_name)
            if registration.appointment_option_id:
                parts.append(registration.appointment_option_id.name)
            if registration.appointment_begin:
                parts.append(registration.appointment_begin.strftime('%Y-%m-%d %H:%M'))
            registration.display_name = ' - '.join(parts) if parts else _('New Appointment')

    @api.depends('appointment_begin', 'appointment_end')
    def _compute_duration(self):
        """Compute appointment duration in hours"""
        for registration in self:
            if registration.appointment_begin and registration.appointment_end:
                delta = registration.appointment_end - registration.appointment_begin
                registration.duration_hours = delta.total_seconds() / 3600.0
            else:
                registration.duration_hours = 0.0

    @api.constrains('appointment_begin', 'appointment_end')
    def _check_appointment_dates(self):
        """Validate appointment dates"""
        for registration in self:
            if registration.appointment_begin and registration.appointment_end:
                if registration.appointment_begin >= registration.appointment_end:
                    raise ValidationError(_('Appointment start time must be before end time.'))
                
                # Check if appointment is in the past (allow some grace period)
                now = datetime.now()
                if registration.appointment_begin < now - timedelta(minutes=5):
                    raise ValidationError(_('Cannot book appointments in the past.'))

    @api.constrains('customer_email')
    def _check_customer_email(self):
        """Validate customer email format"""
        from odoo.addons.online_appointment.helpers.functions import valid_email
        for registration in self:
            if registration.customer_email and not valid_email(registration.customer_email):
                raise ValidationError(_('Please provide a valid email address.'))

    def action_cancel_appointment(self):
        """Cancel the appointment"""
        self.ensure_one()
        if self.state in ['cancelled', 'completed']:
            raise UserError(_('Cannot cancel an appointment that is already %s.') % self.state)
        
        # Deactivate the calendar event
        if self.event_id:
            self.event_id.sudo().write({'active': False})
        
        # Update status
        self.write({'state': 'cancelled'})
        
        # Send notification email
        self._send_cancellation_email()
        
        return True

    def action_confirm_appointment(self):
        """Confirm a pending appointment"""
        self.ensure_one()
        if self.state != 'pending':
            raise UserError(_('Only pending appointments can be confirmed.'))
        
        self.write({'state': 'confirmed'})
        
        # Send confirmation email
        self._send_confirmation_email()
        
        return True

    def action_mark_completed(self):
        """Mark appointment as completed"""
        self.ensure_one()
        if self.state not in ['confirmed']:
            raise UserError(_('Only confirmed appointments can be marked as completed.'))
        
        self.write({'state': 'completed'})
        return True

    def action_mark_no_show(self):
        """Mark appointment as no show"""
        self.ensure_one()
        if self.state not in ['confirmed']:
            raise UserError(_('Only confirmed appointments can be marked as no show.'))
        
        self.write({'state': 'no_show'})
        return True

    def _send_confirmation_email(self):
        """Send appointment confirmation email to customer"""
        # Email template implementation will be added in future version
        return True

    def _send_cancellation_email(self):
        """Send appointment cancellation email to customer"""
        # Email template implementation will be added in future version
        return True

    def send_reminder_email(self):
        """Send appointment reminder email to customer - public method"""
        # Email template implementation will be added in future version
        return True

    @api.model
    def cron_send_reminders(self):
        """Cron job to send appointment reminders"""
        # Send reminders 24 hours before appointment
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)
        
        appointments = self.search([
            ('state', '=', 'confirmed'),
            ('appointment_begin', '>=', start_time),
            ('appointment_begin', '<', end_time),
        ])
        
        for appointment in appointments:
            appointment.send_reminder_email()

    # Legacy methods for backwards compatibility
    def cancel_appointment(self):
        """Legacy method - use action_cancel_appointment instead"""
        return self.action_cancel_appointment()

    def confirm_appointment(self):
        """Legacy method - use action_confirm_appointment instead"""
        return self.action_confirm_appointment()
