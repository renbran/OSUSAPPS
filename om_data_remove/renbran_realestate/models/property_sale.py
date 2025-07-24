from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime


class PropertySale(models.Model):
    _name = 'property.sale'
    _description = 'Property Sale'

    name = fields.Char(string='Sale Name', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('invoiced', 'Invoiced'),
        ('cancelled', 'Cancelled')
    ], string='State', default='draft')
    sale_price = fields.Float(string='Sale Price', compute='_compute_sale_price', store=True)
    down_payment_percentage = fields.Float(string='Down Payment (%)', default=20)
    down_payment = fields.Float(string='Down Payment', compute='_compute_down_payment', store=True)
    dld_fee = fields.Float(string='DLD Fee', compute='_compute_dld_fee', store=True)
    remaining_balance = fields.Float(string='Remaining Balance', compute='_compute_remaining_balance', store=True)
    no_of_installments = fields.Integer(string='No. of Installments', default=1)
    amount_per_installment = fields.Float(string='Amount Per Installment', compute='_compute_amount_per_installment',
                                          store=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    property_id = fields.Many2one('property.property', string='Property', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)
    desired_years = fields.Integer(string='Desired Years')
    property_sale_line_ids = fields.One2many('property.sale.line', 'property_sale_id', string='Installment Lines')
    start_date = fields.Date(string='Start Date', required=True)

    @api.depends('property_id')
    def _compute_sale_price(self):
        for record in self:
            if record.property_id:
                record.sale_price = record.property_id.property_price
            else:
                record.sale_price = 0.0

    @api.depends('sale_price', 'down_payment_percentage')
    def _compute_down_payment(self):
        for record in self:
            record.down_payment = (record.down_payment_percentage / 100) * record.sale_price

    @api.depends('sale_price')
    def _compute_dld_fee(self):
        for record in self:
            # DLD fee fixed at 4%
            record.dld_fee = 0.04 * record.sale_price

    @api.depends('sale_price', 'down_payment', 'dld_fee')
    def _compute_remaining_balance(self):
        for record in self:
            record.remaining_balance = record.sale_price - record.down_payment - record.dld_fee

    @api.depends('remaining_balance', 'no_of_installments')
    def _compute_amount_per_installment(self):
        for record in self:
            if record.no_of_installments > 0:
                record.amount_per_installment = record.remaining_balance / record.no_of_installments
            else:
                record.amount_per_installment = 0.0

    def action_confirm(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Only draft sales can be confirmed.'))

            # Create EMI lines
            self._create_emi_lines()
            record.state = 'confirm'

    def _create_emi_lines(self):
        self.ensure_one()
        if not self.start_date:
            raise UserError(_('Start date is required to create EMI lines.'))

        # Clear existing lines
        self.property_sale_line_ids.unlink()

        # Calculate the EMI dates dynamically
        start_date = fields.Date.from_string(self.start_date)

        # Create downpayment line
        self.env['property.sale.line'].create({
            'property_sale_id': self.id,
            'serial_number': 0,
            'capital_repayment': self.down_payment,
            'remaining_capital': self.down_payment,
            'collection_date': start_date,
            'line_type': 'downpayment'
        })

        # Create DLD fee line
        self.env['property.sale.line'].create({
            'property_sale_id': self.id,
            'serial_number': 0,
            'capital_repayment': self.dld_fee,
            'remaining_capital': self.dld_fee,
            'collection_date': start_date,
            'line_type': 'dld_fee'
        })

        # Create EMI lines
        for i in range(self.no_of_installments):
            due_date = self._calculate_due_date(start_date, i + 1)  # +1 to start EMIs after downpayment
            self.env['property.sale.line'].create({
                'property_sale_id': self.id,
                'serial_number': i + 1,
                'capital_repayment': self.amount_per_installment,
                'remaining_capital': self.amount_per_installment,
                'collection_date': due_date,
                'line_type': 'emi'
            })

    def _calculate_due_date(self, start_date, installment_number):
        try:
            due_date = start_date + relativedelta(months=installment_number)
            if due_date.month != (start_date + relativedelta(months=installment_number)).month:
                due_date = (start_date + relativedelta(months=installment_number)).replace(day=1) - relativedelta(
                    days=1)
            return due_date
        except Exception as e:
            raise UserError(_('Error calculating due date: %s') % str(e))

    def action_draft(self):
        """
        Set the record state to 'draft'.
        """
        self.ensure_one()  # Ensure single record operation
        if self.state == 'cancelled':
            self.state = 'draft'
        else:
            raise UserError("Only cancelled records can be reset to draft.")

    def action_cancel(self):
        """Cancel the property sale and remove associated records."""
        for record in self:
            if record.state == 'cancelled':
                raise UserError(_('This sale is already canceled.'))
            if record.state == 'invoiced':
                raise UserError(_('Cannot cancel a sale that has been invoiced.'))
            # Remove related EMI lines
            record.property_sale_line_ids.unlink()
            record.state = 'cancelled'

    def action_view_invoices(self):
        """View all invoices related to the property sale."""
        self.ensure_one()
        invoice_ids = self.property_sale_line_ids.mapped('invoice_id')
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoice_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': invoice_ids.id,
                'target': 'current',
            })
        else:
            action.update({
                'domain': [('id', 'in', invoice_ids.ids)],
                'view_mode': 'tree,form',
            })
        return action


class PropertySaleLine(models.Model):
    _name = 'property.sale.line'
    _description = 'Installment Line'

    property_sale_id = fields.Many2one('property.sale', string='Property Sale')
    serial_number = fields.Integer(string='Installment Number')
    capital_repayment = fields.Monetary(string='Capital Repayment')
    remaining_capital = fields.Monetary(string='Remaining Capital')
    collection_date = fields.Date(string='Collection Date')
    collection_status = fields.Selection(
        [('unpaid', 'Unpaid'), ('paid', 'Paid')],
        string='Collection Status',
        default='unpaid'
    )
    line_type = fields.Selection([
        ('downpayment', 'Down Payment'),
        ('dld_fee', 'DLD Fee'),
        ('emi', 'EMI')
    ], string='Line Type', required=True, default='emi')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    currency_id = fields.Many2one(related='property_sale_id.currency_id', store=True, readonly=True)

    def action_create_pay_invoice(self):
        self.ensure_one()
        if self.collection_status == 'paid':
            raise UserError(_('This installment is already paid.'))
        if self.invoice_id:
            raise UserError(_('Invoice already exists for this installment.'))

        # Create invoice for this specific line
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.property_sale_id.partner_id.id,
            'currency_id': self.property_sale_id.currency_id.id,
            'invoice_date': fields.Date.context_today(self),
            'invoice_line_ids': [(0, 0, {
                'name': f'{self.line_type.title()} - {self.serial_number}',
                'quantity': 1,
                'price_unit': self.capital_repayment,
            })],
        })

        self.write({
            'invoice_id': invoice.id,
            'collection_status': 'paid'
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Customer Invoice'),
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current',
        }