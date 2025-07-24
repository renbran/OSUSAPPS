from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class LoanRequest(models.Model):
    """Can create new loan requests and manage records"""
    _name = 'loan.request'
    _inherit = ['mail.thread']
    _description = 'Loan Request'

    name = fields.Char(string='Loan Reference', readonly=True,
                       copy=False, help="Sequence number for loan requests",
                       default=lambda self: 'New')
    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,
                                 help="Company Name",
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, help="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    loan_type_id = fields.Many2one('loan.type', string='Loan Type',
                                   required=True, help="Can choose different loan types suitable")
    loan_amount = fields.Float(string="Loan Amount", help="Total loan amount")
    disbursal_amount = fields.Float(string="Disbursal Amount", help="Total loan amount available to disburse")
    tenure = fields.Integer(string="Tenure", default=1, help="Installment period (months)")
    interest_rate = fields.Float(string="Annual Interest Rate (%)", help="Annual Interest percentage")
    date = fields.Date(string="Date", default=fields.Date.today(), readonly=True, help="Date")
    partner_id = fields.Many2one('res.partner', string="Partner", required=True, help="Partner")
    repayment_lines_ids = fields.One2many('repayment.line', 'loan_id', string="Loan Line", index=True, help="Repayment lines")
    state = fields.Selection([
        ('draft', 'Draft'), ('confirmed', 'Confirmed'), ('waiting', 'Waiting For Approval'),
        ('approved', 'Approved'), ('disbursed', 'Disbursed'), ('rejected', 'Rejected'), ('closed', 'Closed')],
        copy=False, tracking=True, default='draft', help="Loan request states")

    def action_compute_repayment(self):
        """Compute the repayments based on diminishing balance method."""
        self.request = True
        for loan in self:
            loan.repayment_lines_ids.unlink()
            date_start = datetime.strptime(str(loan.date), '%Y-%m-%d') + relativedelta(months=1)
            remaining_principal = loan.loan_amount
            monthly_interest_rate = (loan.interest_rate / 100) / 12  # Convert annual to monthly rate
            partner = loan.partner_id

            # Retrieve account IDs
            try:
                interest_account_id = self.env.ref('advanced_loan_management.loan_management_inrst_accounts').id
            except ValueError:
                raise UserError("Interest account configuration is missing. Please check the configuration.")

            try:
                repayment_account_id = self.env.ref('advanced_loan_management.demo_loan_accounts').id
            except ValueError:
                raise UserError("Repayment account configuration is missing. Please check the configuration.")

            # Compute Equated Monthly Installment (EMI) using diminishing balance method
            if monthly_interest_rate > 0:
                emi = (remaining_principal * monthly_interest_rate * (1 + monthly_interest_rate) ** loan.tenure) / \
                    ((1 + monthly_interest_rate) ** loan.tenure - 1)
            else:
                emi = remaining_principal / loan.tenure

            for installment in range(1, loan.tenure + 1):
                interest_amount = remaining_principal * monthly_interest_rate  # Interest on remaining principal
                principal_amount = emi - interest_amount  # Deduct interest from EMI to get principal
                remaining_principal -= principal_amount  # Reduce principal for next installment

                self.env['repayment.line'].create({
                    'name': f"{loan.name}/{installment}",
                    'partner_id': partner.id,
                    'date': date_start,
                    'amount': principal_amount,
                    'interest_amount': interest_amount,
                    'total_amount': emi,
                    'interest_account_id': interest_account_id,
                    'repayment_account_id': repayment_account_id,
                    'loan_id': loan.id
                })
                date_start += relativedelta(months=1)
        return True