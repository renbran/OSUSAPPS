# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class AppointmentRegistration(models.Model):
    """
    Booking Registration Management.
    
    Manages videography booking registrations including client information,
    appointment scheduling, payment tracking, and service delivery. Integrates
    with portal access for client self-service and includes workflow states
    for professional booking management.
    """
    _name = 's2u.appointment.registration'
    _description = 'Booking Registration'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'mail.activity.mixin']
    _order = 'appointment_begin desc'
    _rec_names_search = ['name', 'partner_id.name', 'videographer_id.name', 'package_id.name']

    # Core Fields
    name = fields.Char(string='Booking Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'), tracking=True)
    event_id = fields.Many2one('calendar.event', string='Calendar Event', ondelete='cascade', tracking=True)

    # Parties
    partner_id = fields.Many2one('res.partner', string='Customer', required=True,
                                  ondelete='cascade', tracking=True)
    videographer_id = fields.Many2one('s2u.videographer.profile', string='Videographer',
                                      required=True, ondelete='restrict', tracking=True)
    appointee_id = fields.Many2one('res.partner', string='Videographer Contact',
                                   related='videographer_id.partner_id', store=True, readonly=True)

    # Service Details
    package_id = fields.Many2one('s2u.service.package', string='Package', tracking=True)
    option_id = fields.Many2one('s2u.appointment.option', string='Service Option', tracking=True)

    # Dates & Duration
    appointment_begin = fields.Datetime(string="Start Date & Time", required=True,
                                        tracking=True, index=True)
    appointment_end = fields.Datetime(string="End Date & Time", required=True, tracking=True)
    duration_hours = fields.Float(string='Duration (Hours)', compute='_compute_duration',
                                   store=True, readonly=True)

    # Location
    event_location = fields.Char(string='Event Location', tracking=True)
    event_address = fields.Text(string='Full Address')
    travel_distance = fields.Float(string='Travel Distance (km)')
    travel_fee = fields.Monetary(string='Travel Fee', currency_field='currency_id')

    # Pricing
    currency_id = fields.Many2one('res.currency', string='Currency',
                                   default=lambda self: self.env.company.currency_id,
                                   required=True)
    base_price = fields.Monetary(string='Base Price', currency_field='currency_id',
                                  tracking=True, required=True)
    addon_ids = fields.One2many('s2u.booking.addon', 'booking_id', string='Add-ons')
    addon_total = fields.Monetary(string='Add-ons Total', compute='_compute_totals',
                                   currency_field='currency_id', store=True)
    subtotal = fields.Monetary(string='Subtotal', compute='_compute_totals',
                                currency_field='currency_id', store=True)
    discount_percentage = fields.Float(string='Discount %', default=0.0, tracking=True)
    discount_amount = fields.Monetary(string='Discount Amount', compute='_compute_totals',
                                       currency_field='currency_id', store=True)
    total_amount = fields.Monetary(string='Total Amount', compute='_compute_totals',
                                    currency_field='currency_id', store=True, tracking=True)

    # Payment
    deposit_percentage = fields.Float(string='Deposit %', default=30.0)
    deposit_amount = fields.Monetary(string='Deposit Amount', compute='_compute_totals',
                                      currency_field='currency_id', store=True)
    paid_amount = fields.Monetary(string='Paid Amount', currency_field='currency_id',
                                   default=0.0, tracking=True)
    balance_due = fields.Monetary(string='Balance Due', compute='_compute_payment_status',
                                   currency_field='currency_id', store=True)
    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('deposit_paid', 'Deposit Paid'),
        ('partially_paid', 'Partially Paid'),
        ('fully_paid', 'Fully Paid')
    ], string='Payment Status', compute='_compute_payment_status', store=True, tracking=True)

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], required=True, default='draft', string='Status', copy=False, tracking=True)

    # Additional Information
    customer_notes = fields.Text(string='Customer Notes', tracking=True)
    internal_notes = fields.Text(string='Internal Notes')
    special_requirements = fields.Text(string='Special Requirements')

    # Communication
    appointee_interaction = fields.Boolean(string='Videographer Interaction', default=True)

    # Review
    review_id = fields.Many2one('s2u.videographer.review', string='Review', readonly=True)
    reviewed = fields.Boolean(string='Reviewed', default=False)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('s2u.booking') or _('New')
        return super(AppointmentRegistration, self).create(vals)

    @api.depends('appointment_begin', 'appointment_end')
    def _compute_duration(self):
        for record in self:
            if record.appointment_begin and record.appointment_end:
                delta = record.appointment_end - record.appointment_begin
                record.duration_hours = delta.total_seconds() / 3600.0
            else:
                record.duration_hours = 0.0

    @api.depends('base_price', 'addon_ids', 'addon_ids.subtotal', 'travel_fee',
                 'discount_percentage', 'deposit_percentage')
    def _compute_totals(self):
        for record in self:
            addon_total = sum(record.addon_ids.mapped('subtotal'))
            subtotal = record.base_price + addon_total + (record.travel_fee or 0.0)
            discount = subtotal * (record.discount_percentage / 100.0)
            total = subtotal - discount

            record.addon_total = addon_total
            record.subtotal = subtotal
            record.discount_amount = discount
            record.total_amount = total
            record.deposit_amount = total * (record.deposit_percentage / 100.0)

    @api.depends('total_amount', 'paid_amount')
    def _compute_payment_status(self):
        for record in self:
            record.balance_due = record.total_amount - record.paid_amount

            if record.paid_amount <= 0:
                record.payment_status = 'unpaid'
            elif record.paid_amount >= record.total_amount:
                record.payment_status = 'fully_paid'
            elif record.paid_amount >= record.deposit_amount:
                record.payment_status = 'partially_paid'
            else:
                record.payment_status = 'deposit_paid'

    @api.onchange('package_id')
    def _onchange_package(self):
        if self.package_id:
            self.base_price = self.package_id.base_price
            self.deposit_percentage = self.package_id.deposit_percentage
            if self.package_id.duration_hours and self.appointment_begin:
                self.appointment_end = fields.Datetime.add(
                    self.appointment_begin,
                    hours=self.package_id.duration_hours
                )

    @api.constrains('appointment_begin', 'appointment_end')
    def _check_dates(self):
        for record in self:
            if record.appointment_begin and record.appointment_end:
                if record.appointment_end <= record.appointment_begin:
                    raise ValidationError(_('End date must be after start date.'))

    @api.constrains('discount_percentage')
    def _check_discount(self):
        for record in self:
            if not 0 <= record.discount_percentage <= 100:
                raise ValidationError(_('Discount percentage must be between 0 and 100.'))

    def action_confirm(self):
        for record in self:
            if record.state == 'draft':
                record.write({'state': 'pending'})
        return True

    def action_approve(self):
        for record in self:
            if record.state == 'pending':
                record.write({'state': 'confirmed'})
                # Create or update calendar event
                record._sync_calendar_event()
        return True

    def action_start(self):
        for record in self:
            if record.state == 'confirmed':
                record.write({'state': 'in_progress'})
        return True

    def action_complete(self):
        for record in self:
            if record.state in ['confirmed', 'in_progress']:
                record.write({'state': 'completed'})
        return True

    def action_cancel(self):
        for record in self:
            if record.state not in ['completed', 'cancelled']:
                record.write({'state': 'cancelled'})
                if record.event_id:
                    record.event_id.write({'active': False})
        return True

    def cancel_appointment(self):
        """Legacy method for backward compatibility"""
        return self.action_cancel()

    def confirm_appointment(self):
        """Legacy method for backward compatibility"""
        return self.action_approve()

    def _sync_calendar_event(self):
        """Create or update calendar event"""
        for record in self:
            partner_ids = [record.partner_id.id, record.appointee_id.id]
            event_vals = {
                'name': record.name or record.package_id.name,
                'description': record.customer_notes or '',
                'start': record.appointment_begin,
                'stop': record.appointment_end,
                'location': record.event_location or '',
                'partner_ids': [(6, 0, partner_ids)]
            }

            if record.event_id:
                record.event_id.with_context(detaching=True).write(event_vals)
            else:
                event = self.env['calendar.event'].with_context(detaching=True).create(event_vals)
                record.event_id = event.id
                # Set attendees to accepted
                event.attendee_ids.write({'state': 'accepted'})

    def action_view_calendar_event(self):
        self.ensure_one()
        return {
            'name': _('Calendar Event'),
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'view_mode': 'form',
            'res_id': self.event_id.id,
            'target': 'current'
        }

    def action_send_confirmation_email(self):
        """Send booking confirmation email to customer"""
        self.ensure_one()
        template = self.env.ref('s2u_online_appointment.email_template_booking_confirmation', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
        return True

    def action_request_review(self):
        """Request review from customer after completion"""
        self.ensure_one()
        if self.state == 'completed' and not self.reviewed:
            # Create review request notification
            self.message_post(
                body=_('Review request sent to customer for completed booking.'),
                message_type='notification'
            )
            return True
        return False
