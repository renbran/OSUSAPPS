from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    # Enhanced fields for OSUS voucher system
    remarks = fields.Text(
        string='Remarks/Memo',
        help="Additional remarks or memo for this payment voucher"
    )
    
    authorized_by = fields.Char(
        string='Authorized By',
        compute='_compute_authorized_by',
        store=True,
        help="Name of the person who approved and posted the payment"
    )
    
    actual_approver_id = fields.Many2one(
        'res.users',
        string='Approved By User',
        help="User who actually approved and posted the payment",
        readonly=True
    )
    
    destination_account_id = fields.Many2one(
        'account.account',
        string='Destination Account',
        domain="[('account_type', 'in', ['asset_receivable', 'liability_payable', 'asset_cash', 'liability_credit_card'])]",
        help="Account where the payment will be posted"
    )
    
    # Enhanced display name for vouchers
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )
    
    @api.depends('name', 'payment_type', 'partner_id', 'amount', 'currency_id')
    def _compute_display_name(self):
        """Compute enhanced display name for vouchers"""
        for record in self:
            if record.name and record.partner_id:
                payment_type_label = 'Payment' if record.payment_type == 'outbound' else 'Receipt'
                record.display_name = f"{payment_type_label} Voucher {record.name} - {record.partner_id.name}"
            else:
                record.display_name = record.name or 'New Payment'
    
    @api.depends('state', 'actual_approver_id', 'write_uid', 'write_date')
    def _compute_authorized_by(self):
        """Compute authorization field showing who approved and posted the payment"""
        for record in self:
            if record.actual_approver_id:
                # Show the actual approver who approved and posted the entry
                record.authorized_by = record.actual_approver_id.name
            elif record.state == 'posted' and record.write_uid:
                # If posted but no specific approver, show who posted it
                record.authorized_by = record.write_uid.name
            else:
                # For draft or other states, show who initiated
                record.authorized_by = record.create_uid.name if record.create_uid else 'System'
    
    @api.model
    def create(self, vals):
        """Enhanced create method with validation"""
        # Add any custom validation here if needed
        if 'remarks' in vals and vals['remarks']:
            # Log the creation with remarks for audit trail
            self.env['mail.message'].create({
                'body': f"Payment voucher created with remarks: {vals['remarks']}",
                'model': 'account.payment',
                'res_id': 0,  # Will be updated after creation
                'message_type': 'comment',
            })
        
        return super(AccountPayment, self).create(vals)
    
    def write(self, vals):
        """Override write to track the approver when payment is posted"""
        # Track state changes for audit
        for record in self:
            if vals.get('state') == 'posted' and record.state != 'posted':
                # Payment is being posted, track who is posting it
                if not record.actual_approver_id:
                    vals['actual_approver_id'] = self.env.user.id
                
                # Log the approval action
                record.message_post(
                    body=f"Payment voucher approved and posted by {self.env.user.name}",
                    subject="Payment Voucher Approved"
                )
        
        return super(AccountPayment, self).write(vals)
    
    def action_print_osus_voucher(self):
        """Print OSUS branded payment voucher"""
        if self.state == 'draft':
            raise UserError(_("Cannot print voucher for draft payments. Please post the payment first."))
        
        return self.env.ref('payment_account_enhanced.action_report_payment_voucher_osus').report_action(self)
    
    def action_print_standard_voucher(self):
        """Print standard payment voucher (fallback)"""
        return self.env.ref('payment_account_enhanced.action_report_payment_voucher').report_action(self)
    
    @api.onchange('journal_id')
    def _onchange_journal_id_destination_account(self):
        """Set default destination account based on journal"""
        if self.journal_id and self.journal_id.default_account_id:
            self.destination_account_id = self.journal_id.default_account_id.id
    
    @api.onchange('partner_id')
    def _onchange_partner_id_enhanced(self):
        """Enhanced partner change logic"""
        if self.partner_id:
            # Auto-populate bank details if available
            partner_banks = self.partner_id.bank_ids
            if partner_banks:
                self.partner_bank_id = partner_banks[0].id
    
    def _get_voucher_data(self):
        """Get formatted data for voucher printing"""
        self.ensure_one()
        
        # Format amount in words (if needed for check printing)
        amount_in_words = ""
        try:
            from num2words import num2words
            amount_in_words = num2words(self.amount, lang='en').title()
        except ImportError:
            # Fallback if num2words is not available
            amount_in_words = "Amount in words not available"
        
        return {
            'voucher_type': 'Payment Voucher' if self.payment_type == 'outbound' else 'Receipt Voucher',
            'amount_in_words': amount_in_words,
            'currency_symbol': self.currency_id.symbol,
            'formatted_date': self.date.strftime('%d %B %Y') if self.date else '',
            'company_logo_url': self.company_id.logo_web if self.company_id.logo_web else '',
            'is_posted': self.state == 'posted',
            'approval_date': self.write_date.strftime('%d/%m/%Y %H:%M') if self.write_date and self.state == 'posted' else '',
        }
    
    def action_validate_and_post(self):
        """Enhanced validation and posting with OSUS specific checks"""
        for record in self:
            # OSUS specific validations
            if not record.partner_id:
                raise UserError(_("Partner is required for OSUS payment vouchers."))
            
            if record.amount <= 0:
                raise UserError(_("Payment amount must be greater than zero."))
            
            # Check if user has approval rights for large amounts
            if record.amount > 10000 and not self.env.user.has_group('account.group_account_manager'):
                raise UserError(_("Payments above AED 10,000 require manager approval."))
        
        # Call standard posting method
        return super(AccountPayment, self).action_post()
    
    @api.model
    def get_osus_branding_data(self):
        """Get OSUS branding data for reports"""
        return {
            'primary_color': '#8B1538',
            'secondary_color': '#D4AF37',
            'company_tagline': 'Luxury Real Estate Excellence',
            'website': 'www.osusproperties.com',
            'logo_url': 'https://osusproperties.com/wp-content/uploads/2025/02/OSUS-logotype-2.png'
        }


class AccountPaymentRegister(models.TransientModel):
    """Enhanced payment registration wizard"""
    _inherit = 'account.payment.register'
    
    remarks = fields.Text(
        string='Remarks/Memo',
        help="Additional remarks for the payment voucher"
    )
    
    def _create_payment_vals_from_wizard(self, batch_result):
        """Override to include remarks in payment creation"""
        payment_vals = super()._create_payment_vals_from_wizard(batch_result)
        
        if self.remarks:
            payment_vals['remarks'] = self.remarks
            
        return payment_vals


class ResCompany(models.Model):
    """Enhanced company model for OSUS branding"""
    _inherit = 'res.company'
    
    voucher_footer_message = fields.Text(
        string='Voucher Footer Message',
        default='Thank you for your business',
        help="Custom message to display in payment voucher footer"
    )
    
    voucher_terms = fields.Text(
        string='Voucher Terms',
        default='This is a computer-generated document. No physical signature or stamp required for system verification.',
        help="Terms and conditions to display in payment voucher"
    )
    
    use_osus_branding = fields.Boolean(
        string='Use OSUS Branding',
        default=True,
        help="Apply OSUS brand guidelines to reports and vouchers"
    )