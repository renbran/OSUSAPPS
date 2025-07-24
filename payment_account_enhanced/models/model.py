from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    # Additional fields for voucher
    destination_account_id = fields.Many2one(
        'account.account',
        string='Destination Account',
        domain="[('account_type', 'in', ['asset_receivable', 'liability_payable', 'asset_cash', 'liability_credit_card'])]",
        help="Account where the payment will be posted"
    )
    
    # Override the name field to have a better label for voucher context
    name = fields.Char(
        string='Number',
        readonly=True,
        copy=False,
        help="Payment reference number"
    )
    
    received_by = fields.Char(
        string='Received By',
        help="Person who received the payment (manually filled)"
    )
    
    # Authorization fields with computed logic
    authorized_by = fields.Char(
        string='Authorized By',
        compute='_compute_authorized_by',
        store=True,
        help="Shows the name of the person who approved and posted the payment"
    )
    
    # Field to store actual approver user
    actual_approver_id = fields.Many2one(
        'res.users',
        string='Approved By',
        help="User who actually approved and posted the payment",
        readonly=True
    )
    
    remarks = fields.Text(
        string='Remarks/Memo',
        help="Additional remarks or memo for the payment"
    )
    
    # One2many field for journal items
    line_ids = fields.One2many(
        'account.move.line', 
        'move_id', 
        string='Journal Items',
        related='move_id.line_ids',
        readonly=True,
        help="Journal entries created by this payment"
    )
    
    @api.depends('state', 'actual_approver_id', 'write_uid', 'write_date')
    def _compute_authorized_by(self):
        """Compute authorization field showing who approved and posted the payment"""
        for record in self:
            if record.actual_approver_id:
                # Show the actual approver who approved and posted the entry
                record.authorized_by = record.actual_approver_id.name
            elif record.state in ['posted'] and record.write_uid:
                # If posted but no specific approver, show who posted it
                record.authorized_by = record.write_uid.name
            else:
                # For draft or other states, show who initiated
                record.authorized_by = record.create_uid.name if record.create_uid else 'System'
    
    @api.model
    def create(self, vals):
        # The standard name field will be handled by the parent class
        return super(AccountPayment, self).create(vals)
    
    def action_print_voucher(self):
        """Print payment voucher"""
        return self.env.ref('payment_account_enhanced.action_report_payment_voucher').report_action(self)
    
    def write(self, vals):
        """Override write to track the approver when payment is posted"""
        # If state is being changed to 'posted', track who is posting it
        if vals.get('state') == 'posted' and not self.actual_approver_id:
            vals['actual_approver_id'] = self.env.user.id
        return super(AccountPayment, self).write(vals)
    
    @api.onchange('journal_id')
    def _onchange_journal_id_destination_account(self):
        """Set default destination account based on journal"""
        if self.journal_id:
            if self.journal_id.default_account_id:
                self.destination_account_id = self.journal_id.default_account_id.id
