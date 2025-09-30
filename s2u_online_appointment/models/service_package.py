# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ServicePackage(models.Model):
    _name = 's2u.service.package'
    _description = 'Service Package'
    _inherit = ['mail.thread', 'image.mixin']
    _order = 'sequence, name'

    # Basic Information
    name = fields.Char(string='Package Name', required=True, tracking=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(default=True, tracking=True)

    # Package Details
    description = fields.Html(string='Description', sanitize=True, translate=True)
    short_description = fields.Char(string='Short Description', size=256, translate=True)

    category = fields.Selection([
        ('wedding', 'Wedding Package'),
        ('corporate', 'Corporate Package'),
        ('event', 'Event Coverage'),
        ('commercial', 'Commercial/Advertisement'),
        ('real_estate', 'Real Estate'),
        ('music_video', 'Music Video'),
        ('custom', 'Custom Package')
    ], string='Category', default='custom', required=True, tracking=True)

    # Pricing
    currency_id = fields.Many2one('res.currency', string='Currency',
                                   default=lambda self: self.env.company.currency_id)
    base_price = fields.Monetary(string='Base Price', currency_field='currency_id',
                                  required=True, tracking=True)
    deposit_percentage = fields.Float(string='Deposit %', default=30.0,
                                      help='Deposit percentage required to confirm booking')
    deposit_amount = fields.Monetary(string='Deposit Amount', compute='_compute_deposit_amount',
                                     currency_field='currency_id', store=True)

    # Duration & Resources
    duration_hours = fields.Float(string='Duration (Hours)', required=True, default=4.0)
    videographer_count = fields.Integer(string='Videographers Required', default=1)
    editor_hours = fields.Float(string='Editing Hours', default=0.0)

    # Features & Deliverables
    feature_ids = fields.Many2many(
        's2u.package.feature',
        's2u_package_feature_rel',
        'package_id',
        'feature_id',
        string='Features Included'
    )
    deliverable_ids = fields.One2many('s2u.package.deliverable', 'package_id', string='Deliverables')

    # Availability
    videographer_ids = fields.Many2many(
        's2u.videographer.profile',
        's2u_package_videographer_rel',
        'package_id',
        'videographer_id',
        string='Available Videographers',
        help='Leave empty to make available for all videographers'
    )
    is_public = fields.Boolean(string='Show on Website', default=True)
    popular = fields.Boolean(string='Popular Package', default=False)

    # Add-ons
    addon_ids = fields.Many2many(
        's2u.package.addon',
        's2u_package_addon_rel',
        'package_id',
        'addon_id',
        string='Available Add-ons'
    )

    # Statistics
    booking_count = fields.Integer(compute='_compute_booking_count', string='Total Bookings')

    @api.depends('base_price', 'deposit_percentage')
    def _compute_deposit_amount(self):
        for record in self:
            record.deposit_amount = record.base_price * (record.deposit_percentage / 100.0)

    def _compute_booking_count(self):
        for record in self:
            record.booking_count = self.env['s2u.appointment.registration'].search_count([
                ('package_id', '=', record.id)
            ])

    @api.constrains('deposit_percentage')
    def _check_deposit_percentage(self):
        for record in self:
            if not 0 <= record.deposit_percentage <= 100:
                raise ValidationError(_('Deposit percentage must be between 0 and 100.'))

    @api.constrains('duration_hours')
    def _check_duration(self):
        for record in self:
            if record.duration_hours <= 0:
                raise ValidationError(_('Duration must be greater than 0.'))

    def action_view_bookings(self):
        self.ensure_one()
        return {
            'name': _('Bookings'),
            'type': 'ir.actions.act_window',
            'res_model': 's2u.appointment.registration',
            'view_mode': 'tree,form,calendar',
            'domain': [('package_id', '=', self.id)],
            'context': {'default_package_id': self.id}
        }


class PackageFeature(models.Model):
    _name = 's2u.package.feature'
    _description = 'Package Feature'
    _order = 'sequence, name'

    name = fields.Char(string='Feature', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Text(string='Description', translate=True)
    icon = fields.Char(string='Icon Class', help='Font Awesome icon class')
    active = fields.Boolean(default=True)


class PackageDeliverable(models.Model):
    _name = 's2u.package.deliverable'
    _description = 'Package Deliverable'
    _order = 'sequence'

    package_id = fields.Many2one('s2u.service.package', string='Package',
                                  required=True, ondelete='cascade')
    name = fields.Char(string='Deliverable', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    quantity = fields.Integer(string='Quantity', default=1)
    description = fields.Text(string='Description', translate=True)
    delivery_days = fields.Integer(string='Delivery Time (Days)', default=14,
                                    help='Expected days after event to deliver')


class PackageAddon(models.Model):
    _name = 's2u.package.addon'
    _description = 'Package Add-on'
    _order = 'name'

    name = fields.Char(string='Add-on Name', required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    active = fields.Boolean(default=True)

    currency_id = fields.Many2one('res.currency', string='Currency',
                                   default=lambda self: self.env.company.currency_id)
    price = fields.Monetary(string='Price', currency_field='currency_id', required=True)

    addon_type = fields.Selection([
        ('extra_hour', 'Extra Hour'),
        ('extra_videographer', 'Additional Videographer'),
        ('drone', 'Drone Footage'),
        ('raw_footage', 'Raw Footage'),
        ('rush_delivery', 'Rush Delivery'),
        ('social_media', 'Social Media Edits'),
        ('other', 'Other')
    ], string='Type', default='other', required=True)

    duration_hours = fields.Float(string='Duration (Hours)', default=0.0)
    icon = fields.Char(string='Icon Class')


class BookingAddon(models.Model):
    _name = 's2u.booking.addon'
    _description = 'Booking Add-on'

    booking_id = fields.Many2one('s2u.appointment.registration', string='Booking',
                                  required=True, ondelete='cascade')
    addon_id = fields.Many2one('s2u.package.addon', string='Add-on', required=True, ondelete='restrict')

    name = fields.Char(string='Add-on', related='addon_id.name', readonly=True)
    quantity = fields.Integer(string='Quantity', default=1, required=True)

    currency_id = fields.Many2one('res.currency', string='Currency',
                                   related='booking_id.currency_id', readonly=True)
    unit_price = fields.Monetary(string='Unit Price', currency_field='currency_id', required=True)
    subtotal = fields.Monetary(string='Subtotal', compute='_compute_subtotal',
                                currency_field='currency_id', store=True)

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.quantity * record.unit_price

    @api.onchange('addon_id')
    def _onchange_addon_id(self):
        if self.addon_id:
            self.unit_price = self.addon_id.price