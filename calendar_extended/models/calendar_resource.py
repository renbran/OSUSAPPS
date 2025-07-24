# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CalendarResource(models.Model):
    _name = 'calendar.resource'
    _description = 'Calendar Resource'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    
    description = fields.Text(string='Description')
    
    resource_type = fields.Selection([
        ('room', 'Meeting Room'),
        ('equipment', 'Equipment'),
        ('vehicle', 'Vehicle'),
        ('other', 'Other')
    ], string='Resource Type', required=True, default='room')
    
    capacity = fields.Integer(string='Capacity', help='Maximum capacity of the resource')
    
    location = fields.Char(string='Location')
    
    active = fields.Boolean(string='Active', default=True)
    
    color = fields.Integer(string='Color', default=0)
    
    image = fields.Binary(string='Image')
    
    availability_calendar = fields.Text(
        string='Availability Calendar',
        help='JSON data for availability calendar'
    )
    
    booking_rules = fields.Text(
        string='Booking Rules',
        help='Rules for booking this resource'
    )
    
    hourly_rate = fields.Monetary(
        string='Hourly Rate',
        currency_field='currency_id',
        help='Cost per hour for using this resource'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        help='User responsible for this resource'
    )
    
    equipment_ids = fields.One2many(
        'calendar.resource.equipment',
        'resource_id',
        string='Equipment'
    )
    
    booking_ids = fields.One2many(
        'calendar.event',
        compute='_compute_booking_ids',
        string='Bookings'
    )
    
    booking_count = fields.Integer(
        string='Booking Count',
        compute='_compute_booking_count'
    )
    
    utilization_rate = fields.Float(
        string='Utilization Rate (%)',
        compute='_compute_utilization_rate',
        help='Percentage of time this resource is booked'
    )
    
    @api.depends()
    def _compute_booking_ids(self):
        for resource in self:
            resource.booking_ids = self.env['calendar.event'].search([
                ('resource_ids', 'in', resource.id)
            ])
    
    @api.depends('booking_ids')
    def _compute_booking_count(self):
        for resource in self:
            resource.booking_count = len(resource.booking_ids)
    
    @api.depends('booking_ids')
    def _compute_utilization_rate(self):
        for resource in self:
            # Calculate utilization rate based on bookings
            # This is a simplified calculation
            total_hours = 24 * 7  # Hours in a week
            booked_hours = sum(
                (booking.stop - booking.start).total_seconds() / 3600
                for booking in resource.booking_ids
                if booking.start and booking.stop
            )
            resource.utilization_rate = (booked_hours / total_hours) * 100 if total_hours > 0 else 0.0
    
    def check_availability(self, start_date, end_date):
        """Check if resource is available for the given period"""
        conflicting_events = self.env['calendar.event'].search([
            ('resource_ids', 'in', self.id),
            ('start', '<', end_date),
            ('stop', '>', start_date),
            ('status', 'not in', ['cancelled', 'postponed'])
        ])
        return len(conflicting_events) == 0
    
    def book_resource(self, event_id):
        """Book the resource for an event"""
        event = self.env['calendar.event'].browse(event_id)
        if self.check_availability(event.start, event.stop):
            event.resource_ids = [(4, self.id)]
            return True
        return False
    
    def action_view_bookings(self):
        """View bookings for this resource"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Resource Bookings'),
            'res_model': 'calendar.event',
            'view_mode': 'calendar,tree,form',
            'domain': [('resource_ids', 'in', self.id)],
            'context': {'default_resource_ids': [(6, 0, [self.id])]}
        }


class CalendarResourceEquipment(models.Model):
    _name = 'calendar.resource.equipment'
    _description = 'Calendar Resource Equipment'

    name = fields.Char(string='Equipment Name', required=True)
    
    description = fields.Text(string='Description')
    
    resource_id = fields.Many2one(
        'calendar.resource',
        string='Resource',
        required=True,
        ondelete='cascade'
    )
    
    quantity = fields.Integer(string='Quantity', default=1)
    
    is_available = fields.Boolean(string='Available', default=True)
