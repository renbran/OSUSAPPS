from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CommissionLine(models.Model):
    _name = 'commission.line'
    _description = 'Commission Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'
    _rec_name = 'display_name'

    # Basic Information
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)
    date = fields.Date(string='Commission Date', required=True, default=fields.Date.context_today, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    # Commission Details
    commission_type = fields.Selection([
        ('sale', 'Sales Commission'),
        ('referral', 'Referral Commission'),
        ('target', 'Target Achievement'),
        ('bonus', 'Bonus Commission')
    ], string='Commission Type', required=True, default='sale')
    
    # Financial Information
    base_amount = fields.Monetary(string='Base Amount', required=True, currency_field='currency_id', tracking=True)
    commission_rate = fields.Float(string='Commission Rate (%)', digits=(5, 2), tracking=True)
    commission_amount = fields.Monetary(string='Commission Amount', required=True, currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, 
                                  default=lambda self: self.env.company.currency_id)

    # Related Records
    partner_id = fields.Many2one('res.partner', string='Commission Partner', required=True, 
                                 domain=[('is_company', '=', False)], tracking=True)
    salesperson_id = fields.Many2one('res.users', string='Salesperson', required=True, tracking=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    client_order_ref = fields.Char(related='sale_order_id.client_order_ref', string='Customer Reference', store=True, readonly=True)
    invoice_id = fields.Many2one('account.move', string='Invoice')
    
    # Company and User Information
    company_id = fields.Many2one('res.company', string='Company', required=True, 
                                 default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Created by', default=lambda self: self.env.user)

    # Computed Fields
    is_paid = fields.Boolean(string='Is Paid', compute='_compute_is_paid', store=True)
    partner_name = fields.Char(string='Partner Name', related='partner_id.name', store=True)
    salesperson_name = fields.Char(string='Salesperson Name', related='salesperson_id.name', store=True)

    # Description and Notes
    description = fields.Text(string='Description')
    notes = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('commission.line') or 'New'
        return super(CommissionLine, self).create(vals)

    @api.depends('name', 'partner_id', 'commission_amount', 'date')
    def _compute_display_name(self):
        for record in self:
            if record.partner_id:
                record.display_name = f"{record.name} - {record.partner_id.name} - {record.commission_amount}"
            else:
                record.display_name = record.name or 'New'

    @api.depends('state')
    def _compute_is_paid(self):
        for record in self:
            record.is_paid = record.state == 'paid'

    @api.onchange('base_amount', 'commission_rate')
    def _onchange_commission_calculation(self):
        if self.base_amount and self.commission_rate:
            self.commission_amount = self.base_amount * (self.commission_rate / 100)

    @api.constrains('commission_rate')
    def _check_commission_rate(self):
        for record in self:
            if record.commission_rate < 0 or record.commission_rate > 100:
                raise ValidationError("Commission rate must be between 0 and 100 percent.")

    @api.constrains('commission_amount', 'base_amount')
    def _check_amounts(self):
        for record in self:
            if record.commission_amount < 0:
                raise ValidationError("Commission amount cannot be negative.")
            if record.base_amount < 0:
                raise ValidationError("Base amount cannot be negative.")

    def action_confirm(self):
        """Confirm the commission line"""
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError("Only draft commission lines can be confirmed.")
        self.state = 'confirmed'
        self.message_post(body="Commission line has been confirmed.")

    def action_mark_paid(self):
        """Mark the commission line as paid"""
        self.ensure_one()
        if self.state not in ['confirmed']:
            raise ValidationError("Only confirmed commission lines can be marked as paid.")
        self.state = 'paid'
        self.message_post(body="Commission line has been marked as paid.")

    def action_cancel(self):
        """Cancel the commission line"""
        self.ensure_one()
        if self.state == 'paid':
            raise ValidationError("Paid commission lines cannot be cancelled.")
        self.state = 'cancelled'
        self.message_post(body="Commission line has been cancelled.")

    def action_reset_to_draft(self):
        """Reset to draft state"""
        self.ensure_one()
        if self.state == 'paid':
            raise ValidationError("Paid commission lines cannot be reset to draft.")
        self.state = 'draft'
        self.message_post(body="Commission line has been reset to draft.")

    @api.model
    def create_from_sale_order(self, sale_order, commission_rate=None):
        """Create commission line from sale order"""
        if not commission_rate:
            # Get default commission rate from partner or system parameter
            commission_rate = sale_order.partner_id.commission_rate or 5.0
        
        vals = {
            'sale_order_id': sale_order.id,
            'partner_id': sale_order.user_id.partner_id.id,
            'salesperson_id': sale_order.user_id.id,
            'base_amount': sale_order.amount_total,
            'commission_rate': commission_rate,
            'commission_type': 'sale',
            'date': sale_order.date_order.date() if sale_order.date_order else fields.Date.today(),
            'description': f"Commission for sale order {sale_order.name}",
        }
        
        commission_line = self.create(vals)
        commission_line.message_post(
            body=f"Commission line created automatically from sale order {sale_order.name}"
        )
        
        return commission_line