# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)

class CustomSalesOrder(models.Model):
    _name = 'custom.sales.order'
    _description = 'Custom Sales Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'
    
    # Core fields
    name = fields.Char(
        string='Order Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('custom.sales.order') or 'New'
    )
    
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Related Sale Order',
        ondelete='cascade',
        index=True,
        help="Link to the original sale order"
    )
    
    # Custom fields with indexes for performance
    custom_field_1 = fields.Char(
        string='Custom Field 1',
        help='Additional custom field for business-specific data',
        tracking=True,
        index=True  # Added for search performance
    )
    
    custom_field_2 = fields.Integer(
        string='Custom Field 2',
        help='Numeric custom field for calculations',
        tracking=True,
        index=True  # Added for filtering performance
    )
    
    custom_field_3 = fields.Many2one(
        'res.partner',
        string='Custom Partner',
        help='Additional partner reference',
        index=True,  # Foreign key index
        tracking=True
    )
    
    # Enhanced fields
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Very High'),
    ], string='Priority', default='1', tracking=True)
    
    sales_team_id = fields.Many2one(
        'crm.team',
        string='Sales Team',
        tracking=True
    )
    
    sales_person_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        default=lambda self: self.env.user,
        tracking=True
    )
    
    customer_type = fields.Selection([
        ('new', 'New Customer'),
        ('existing', 'Existing Customer'),
        ('vip', 'VIP Customer'),
        ('corporate', 'Corporate Customer'),
    ], string='Customer Type', tracking=True)
    
    # Financial fields
    estimated_revenue = fields.Monetary(
        string='Estimated Revenue',
        currency_field='currency_id',
        tracking=True
    )
    
    actual_revenue = fields.Monetary(
        string='Actual Revenue',
        currency_field='currency_id',
        compute='_compute_actual_revenue',
        store=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    # Status and workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Quotation Sent'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('delivered', 'Delivered'),
        ('invoiced', 'Invoiced'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    # Dates
    order_date = fields.Datetime(
        string='Order Date',
        default=fields.Datetime.now,
        tracking=True
    )
    
    expected_delivery_date = fields.Date(
        string='Expected Delivery Date',
        tracking=True
    )
    
    actual_delivery_date = fields.Date(
        string='Actual Delivery Date',
        tracking=True
    )
    
    # Analytics fields
    profit_margin = fields.Float(
        string='Profit Margin (%)',
        compute='_compute_profit_margin',
        store=True
    )
    
    customer_satisfaction = fields.Selection([
        ('1', 'Very Poor'),
        ('2', 'Poor'),
        ('3', 'Average'),
        ('4', 'Good'),
        ('5', 'Excellent'),
    ], string='Customer Satisfaction')
    
    # Notes and additional info
    internal_notes = fields.Text(string='Internal Notes')
    customer_notes = fields.Text(string='Customer Notes')
    
    # Computed fields
    days_to_delivery = fields.Integer(
        string='Days to Delivery',
        compute='_compute_days_to_delivery'
    )
    
    is_overdue = fields.Boolean(
        string='Is Overdue',
        compute='_compute_is_overdue'
    )
    
    @api.depends('sale_order_id.amount_total')
    def _compute_actual_revenue(self):
        for record in self:
            if record.sale_order_id:
                record.actual_revenue = record.sale_order_id.amount_total
            else:
                record.actual_revenue = 0
    
    @api.depends('estimated_revenue', 'actual_revenue')
    def _compute_profit_margin(self):
        for record in self:
            if record.estimated_revenue and record.actual_revenue:
                record.profit_margin = ((record.actual_revenue - record.estimated_revenue) / record.estimated_revenue) * 100
            else:
                record.profit_margin = 0
    
    @api.depends('expected_delivery_date')
    def _compute_days_to_delivery(self):
        today = fields.Date.today()
        for record in self:
            if record.expected_delivery_date:
                delta = record.expected_delivery_date - today
                record.days_to_delivery = delta.days
            else:
                record.days_to_delivery = 0
    
    @api.depends('expected_delivery_date', 'state')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for record in self:
            if (record.expected_delivery_date and 
                record.expected_delivery_date < today and 
                record.state not in ['delivered', 'invoiced', 'paid', 'cancelled']):
                record.is_overdue = True
            else:
                record.is_overdue = False
    
    # Constraints
    @api.constrains('custom_field_2')
    def _check_custom_field_2(self):
        for record in self:
            if record.custom_field_2 < 0:
                raise ValidationError("Custom Field 2 must be positive")
    
    @api.constrains('estimated_revenue')
    def _check_estimated_revenue(self):
        for record in self:
            if record.estimated_revenue < 0:
                raise ValidationError("Estimated revenue must be positive")
    
    # CRUD overrides
    @api.model
    def create(self, vals):
        # Custom logic for custom_field_1
        if 'custom_field_1' in vals:
            vals['custom_field_1'] = self._process_custom_field_1(vals['custom_field_1'])
        
        # Auto-generate name if not provided
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('custom.sales.order') or 'New'
        
        result = super().create(vals)
        
        # Log creation
        _logger.info(f"Custom sales order created: {result.name}")
        
        return result
    
    def write(self, vals):
        # Custom logic for custom_field_1
        if 'custom_field_1' in vals:
            vals['custom_field_1'] = self._process_custom_field_1(vals['custom_field_1'])
        
        # Track state changes
        if 'state' in vals:
            for record in self:
                if record.state != vals['state']:
                    record.message_post(
                        body=f"Status changed from {dict(record._fields['state'].selection)[record.state]} to {dict(record._fields['state'].selection)[vals['state']]}"
                    )
        
        return super().write(vals)
    
    def unlink(self):
        for record in self:
            if record.state not in ['draft', 'cancelled']:
                raise UserError("You can only delete draft or cancelled orders.")
        return super().unlink()
    
    # Custom methods
    def _process_custom_field_1(self, value):
        """Process custom_field_1 with business logic"""
        if value:
            # Example: Convert to uppercase and add prefix
            return f"CUST-{value.upper()}"
        return value
    
    def action_confirm(self):
        """Confirm the custom sales order"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError("Only draft orders can be confirmed.")
        
        self.write({'state': 'confirmed'})
        
        # Create or link to sale order if needed
        if not self.sale_order_id:
            self._create_sale_order()
        
        return True
    
    def action_send_quotation(self):
        """Send quotation to customer"""
        self.ensure_one()
        if self.state not in ['draft', 'sent']:
            raise UserError("Only draft or sent orders can be sent again.")
        
        self.write({'state': 'sent'})
        
        # Here you could add email sending logic
        return True
    
    def action_cancel(self):
        """Cancel the order"""
        self.ensure_one()
        if self.state in ['delivered', 'invoiced', 'paid']:
            raise UserError("Cannot cancel orders that are delivered, invoiced, or paid.")
        
        self.write({'state': 'cancelled'})
        return True
    
    def _create_sale_order(self):
        """Create a related sale order"""
        self.ensure_one()
        
        sale_order_vals = {
            'partner_id': self.custom_field_3.id if self.custom_field_3 else False,
            'user_id': self.sales_person_id.id,
            'team_id': self.sales_team_id.id,
            'note': self.customer_notes,
        }
        
        sale_order = self.env['sale.order'].create(sale_order_vals)
        self.write({'sale_order_id': sale_order.id})
        
        return sale_order
    
    def get_dashboard_data(self):
        """Get data for dashboard visualization"""
        self.ensure_one()
        
        return {
            'name': self.name,
            'state': self.state,
            'estimated_revenue': self.estimated_revenue,
            'actual_revenue': self.actual_revenue,
            'profit_margin': self.profit_margin,
            'customer_type': self.customer_type,
            'priority': self.priority,
            'days_to_delivery': self.days_to_delivery,
            'is_overdue': self.is_overdue,
        }


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
    custom_sales_order_ids = fields.One2many(
        'custom.sales.order',
        'sale_order_id',
        string='Custom Sales Orders'
    )
    
    custom_order_count = fields.Integer(
        string='Custom Orders Count',
        compute='_compute_custom_order_count'
    )
    
    @api.depends('custom_sales_order_ids')
    def _compute_custom_order_count(self):
        for record in self:
            record.custom_order_count = len(record.custom_sales_order_ids)
    
    def action_view_custom_orders(self):
        """Open custom sales orders related to this sale order"""
        self.ensure_one()
        
        action = self.env.ref('custom_sales.action_custom_sales_order').read()[0]
        action['domain'] = [('sale_order_id', '=', self.id)]
        action['context'] = {'default_sale_order_id': self.id}
        
        return action
