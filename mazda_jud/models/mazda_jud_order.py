from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MazdaJudOrder(models.Model):
    _name = 'mazda.jud.order'
    _description = 'Mazda Jud Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # Basic Information
    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, default='New')
    description = fields.Text(string='Description')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('documentation', 'Documentation'),
        ('review', 'Review'),
        ('approve', 'Approve'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    assigned_doc_user_id = fields.Many2one('res.users', string='Documentation User', tracking=True)
    assigned_review_user_id = fields.Many2one('res.users', string='Review User', tracking=True)
    assigned_approve_user_id = fields.Many2one('res.users', string='Approve User', tracking=True)
    assigned_post_user_id = fields.Many2one('res.users', string='Posted User', tracking=True)

    can_doc = fields.Boolean(compute='_compute_can_doc', string='Can Document', store=False)
    can_review = fields.Boolean(compute='_compute_can_review', string='Can Review', store=False)
    can_approve = fields.Boolean(compute='_compute_can_approve', string='Can Approve', store=False)
    can_post = fields.Boolean(compute='_compute_can_post', string='Can Post', store=False)

    @api.depends('assigned_doc_user_id')
    def _compute_can_doc(self):
        user = self.env.user
        for rec in self:
            rec.can_doc = rec.assigned_doc_user_id and rec.assigned_doc_user_id.id == user.id and rec.state == 'draft'

    @api.depends('assigned_review_user_id')
    def _compute_can_review(self):
        user = self.env.user
        for rec in self:
            rec.can_review = rec.assigned_review_user_id and rec.assigned_review_user_id.id == user.id and rec.state == 'documentation'

    @api.depends('assigned_approve_user_id')
    def _compute_can_approve(self):
        user = self.env.user
        for rec in self:
            rec.can_approve = rec.assigned_approve_user_id and rec.assigned_approve_user_id.id == user.id and rec.state == 'review'

    @api.depends('assigned_post_user_id')
    def _compute_can_post(self):
        user = self.env.user
        for rec in self:
            rec.can_post = rec.assigned_post_user_id and rec.assigned_post_user_id.id == user.id and rec.state == 'approve'

    def action_to_documentation(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Order must be draft to send to Documentation.'))
            rec.state = 'documentation'
            rec.message_post(body=_('Moved to Documentation stage.'))

    def action_to_review(self):
        for rec in self:
            if rec.state != 'documentation':
                raise UserError(_('Order must be in Documentation to send to Review.'))
            rec.state = 'review'
            rec.message_post(body=_('Moved to Review stage.'))

    def action_to_approve(self):
        for rec in self:
            if rec.state != 'review':
                raise UserError(_('Order must be in Review to send to Approve.'))
            rec.state = 'approve'
            rec.message_post(body=_('Moved to Approve stage.'))

    def action_post_stage(self):
        for rec in self:
            if rec.state != 'approve':
                raise UserError(_('Order must be in Approve to post.'))
            rec.state = 'posted'
            rec.message_post(body=_('Order posted.'))

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('mazda.jud.order') or 'New'
        return super(MazdaJudOrder, self).create(vals)
