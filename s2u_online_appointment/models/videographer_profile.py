# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VideographerProfile(models.Model):
    _name = 's2u.videographer.profile'
    _description = 'Videographer Profile'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _order = 'name'

    # Basic Information
    name = fields.Char(string='Name', required=True, tracking=True)
    user_id = fields.Many2one('res.users', string='User Account', required=True, ondelete='cascade', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Contact', related='user_id.partner_id', store=True, readonly=True)

    active = fields.Boolean(default=True, tracking=True)

    # Professional Details
    bio = fields.Html(string='Biography', sanitize=True, sanitize_overridable=True)
    years_experience = fields.Integer(string='Years of Experience', tracking=True)
    specialization_ids = fields.Many2many(
        's2u.videographer.specialization',
        's2u_videographer_specialization_rel',
        'videographer_id',
        'specialization_id',
        string='Specializations'
    )

    # Contact & Social
    phone = fields.Char(string='Phone', related='user_id.phone', readonly=False)
    mobile = fields.Char(string='Mobile', related='user_id.mobile', readonly=False)
    email = fields.Char(string='Email', related='user_id.email', readonly=False)
    website = fields.Char(string='Website')
    instagram = fields.Char(string='Instagram')
    youtube = fields.Char(string='YouTube Channel')
    facebook = fields.Char(string='Facebook')

    # Service Areas
    service_location_ids = fields.Many2many(
        'res.country.state',
        's2u_videographer_location_rel',
        'videographer_id',
        'state_id',
        string='Service Locations'
    )
    travel_radius = fields.Integer(string='Travel Radius (km)', default=50)
    travel_fee_per_km = fields.Monetary(string='Travel Fee per KM', currency_field='currency_id')

    # Pricing
    currency_id = fields.Many2one('res.currency', string='Currency',
                                   default=lambda self: self.env.company.currency_id)
    hourly_rate = fields.Monetary(string='Base Hourly Rate', currency_field='currency_id', tracking=True)
    min_booking_hours = fields.Float(string='Minimum Booking Hours', default=2.0)

    # Availability Settings
    buffer_time_before = fields.Float(string='Buffer Before (hours)', default=0.5,
                                       help='Time needed before appointment for preparation')
    buffer_time_after = fields.Float(string='Buffer After (hours)', default=0.5,
                                      help='Time needed after appointment for pack-up')
    max_bookings_per_day = fields.Integer(string='Max Bookings Per Day', default=2)
    advance_booking_days = fields.Integer(string='Advance Booking Days', default=7,
                                          help='Minimum days in advance for booking')

    # Equipment
    equipment_ids = fields.Many2many(
        's2u.videographer.equipment',
        's2u_videographer_equipment_rel',
        'videographer_id',
        'equipment_id',
        string='Equipment'
    )
    equipment_notes = fields.Text(string='Equipment Notes')

    # Portfolio
    portfolio_ids = fields.One2many('s2u.videographer.portfolio', 'videographer_id', string='Portfolio Items')
    portfolio_count = fields.Integer(compute='_compute_portfolio_count', string='Portfolio Items')

    # Statistics
    total_bookings = fields.Integer(compute='_compute_statistics', string='Total Bookings', store=True)
    completed_bookings = fields.Integer(compute='_compute_statistics', string='Completed Bookings', store=True)
    average_rating = fields.Float(compute='_compute_rating', string='Average Rating', digits=(3, 2), store=True)
    review_count = fields.Integer(compute='_compute_rating', string='Reviews', store=True)

    # Relations
    booking_ids = fields.One2many('s2u.appointment.registration', 'videographer_id', string='Bookings')
    slot_ids = fields.One2many('s2u.appointment.slot', 'videographer_id', string='Availability Slots')
    review_ids = fields.One2many('s2u.videographer.review', 'videographer_id', string='Reviews')

    @api.depends('portfolio_ids')
    def _compute_portfolio_count(self):
        for record in self:
            record.portfolio_count = len(record.portfolio_ids)

    @api.depends('booking_ids', 'booking_ids.state')
    def _compute_statistics(self):
        for record in self:
            record.total_bookings = len(record.booking_ids)
            record.completed_bookings = len(record.booking_ids.filtered(lambda b: b.state == 'completed'))

    @api.depends('review_ids', 'review_ids.rating')
    def _compute_rating(self):
        for record in self:
            reviews = record.review_ids.filtered(lambda r: r.rating > 0)
            record.review_count = len(reviews)
            record.average_rating = sum(reviews.mapped('rating')) / len(reviews) if reviews else 0.0

    @api.constrains('hourly_rate')
    def _check_hourly_rate(self):
        for record in self:
            if record.hourly_rate < 0:
                raise ValidationError(_('Hourly rate cannot be negative.'))

    @api.constrains('min_booking_hours')
    def _check_min_booking_hours(self):
        for record in self:
            if record.min_booking_hours < 0.5:
                raise ValidationError(_('Minimum booking hours must be at least 0.5 hours.'))

    def action_view_bookings(self):
        self.ensure_one()
        return {
            'name': _('Bookings'),
            'type': 'ir.actions.act_window',
            'res_model': 's2u.appointment.registration',
            'view_mode': 'tree,form,calendar',
            'domain': [('videographer_id', '=', self.id)],
            'context': {'default_videographer_id': self.id}
        }

    def action_view_portfolio(self):
        self.ensure_one()
        return {
            'name': _('Portfolio'),
            'type': 'ir.actions.act_window',
            'res_model': 's2u.videographer.portfolio',
            'view_mode': 'kanban,tree,form',
            'domain': [('videographer_id', '=', self.id)],
            'context': {'default_videographer_id': self.id}
        }


class VideographerSpecialization(models.Model):
    _name = 's2u.videographer.specialization'
    _description = 'Videographer Specialization'
    _order = 'name'

    name = fields.Char(string='Specialization', required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    icon = fields.Char(string='Icon Class', help='Font Awesome icon class (e.g., fa-video)')
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color Index')


class VideographerEquipment(models.Model):
    _name = 's2u.videographer.equipment'
    _description = 'Videographer Equipment'
    _order = 'category_id, name'

    name = fields.Char(string='Equipment Name', required=True)
    category_id = fields.Many2one('s2u.equipment.category', string='Category', required=True)
    description = fields.Text(string='Description')
    brand = fields.Char(string='Brand')
    model = fields.Char(string='Model')
    active = fields.Boolean(default=True)


class EquipmentCategory(models.Model):
    _name = 's2u.equipment.category'
    _description = 'Equipment Category'
    _order = 'sequence, name'

    name = fields.Char(string='Category', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    icon = fields.Char(string='Icon Class')
    active = fields.Boolean(default=True)


class VideographerPortfolio(models.Model):
    _name = 's2u.videographer.portfolio'
    _description = 'Videographer Portfolio Item'
    _inherit = ['image.mixin']
    _order = 'sequence, create_date desc'

    name = fields.Char(string='Title', required=True)
    videographer_id = fields.Many2one('s2u.videographer.profile', string='Videographer',
                                      required=True, ondelete='cascade', index=True)
    sequence = fields.Integer(string='Sequence', default=10)

    description = fields.Html(string='Description', sanitize=True)
    video_url = fields.Char(string='Video URL', help='YouTube, Vimeo, or direct video link')
    thumbnail_url = fields.Char(string='Thumbnail URL')

    category = fields.Selection([
        ('wedding', 'Wedding'),
        ('corporate', 'Corporate'),
        ('event', 'Event'),
        ('commercial', 'Commercial'),
        ('music_video', 'Music Video'),
        ('documentary', 'Documentary'),
        ('real_estate', 'Real Estate'),
        ('other', 'Other')
    ], string='Category', default='other', required=True)

    date_recorded = fields.Date(string='Date Recorded')
    views = fields.Integer(string='Views', default=0)
    featured = fields.Boolean(string='Featured', default=False)
    active = fields.Boolean(default=True)


class VideographerReview(models.Model):
    _name = 's2u.videographer.review'
    _description = 'Videographer Review'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    videographer_id = fields.Many2one('s2u.videographer.profile', string='Videographer',
                                      required=True, ondelete='cascade', index=True)
    booking_id = fields.Many2one('s2u.appointment.registration', string='Booking', ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Reviewer', required=True, ondelete='cascade')

    rating = fields.Integer(string='Rating', required=True, help='Rating from 1 to 5')
    title = fields.Char(string='Review Title')
    comment = fields.Text(string='Comment', required=True)

    state = fields.Selection([
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='pending', required=True, tracking=True)

    helpful_count = fields.Integer(string='Helpful Count', default=0)

    @api.constrains('rating')
    def _check_rating(self):
        for record in self:
            if not 1 <= record.rating <= 5:
                raise ValidationError(_('Rating must be between 1 and 5.'))

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})