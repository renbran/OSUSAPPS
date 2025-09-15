# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Jumana Haseen (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    """This class inherits "account.move" and add state for approval """
    _inherit = "account.move"

    state = fields.Selection(
        selection_add=[('submit_review', 'Submit for Review'),
                       ('waiting_approval', 'Waiting For Approval'),
                       ('approved', 'Approved'),
                       ('rejected', 'Rejected')],
        ondelete={'submit_review': 'set default', 'waiting_approval': 'set default', 'approved': 'set default',
                  'rejected': 'set default'}, help="States of approval.")
    
    journal_restrict_mode = fields.Boolean(
        string="Journal Restrict Mode",
        related="journal_id.restrict_mode_hash_table",
        help="Indicates if the journal has strict mode enabled"
    )

    def _check_journal_hash_restriction(self):
        """Check if journal has strict mode enabled and provide helpful error message"""
        for record in self:
            if record.journal_id.restrict_mode_hash_table and record.state == 'posted':
                raise UserError(_(
                    "Cannot modify posted entry from journal '%s' because it is in strict mode.\n\n"
                    "Solutions:\n"
                    "1. Create a Credit Note/Reverse Entry instead of modifying the original entry\n"
                    "2. Ask your Administrator to temporarily disable 'Lock Posted Entries with Hash' in the journal settings\n"
                    "3. Use the 'Reset to Draft' button before making changes (if available)\n\n"
                    "This restriction exists to maintain data integrity and compliance requirements."
                ) % record.journal_id.name)

    def _is_user_authorized_approver_move(self, user_id=None):
        """Helper method to check if a user is authorized to approve vendor bills.
        Uses the same approval configuration as payments.
        
        Args:
            user_id (int): User ID to check. If None, uses current user.
            
        Returns:
            bool: True if user is authorized to approve vendor bills
        """
        if user_id is None:
            user_id = self.env.user.id
            
        approval = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.payment_approval')
        
        if not approval:
            return False
            
        # Check for multiple approvers first (takes precedence)
        multiple_approvers_param = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.approval_user_ids', '')
        
        if multiple_approvers_param:
            try:
                # Parse the comma-separated string of user IDs
                approver_ids = [int(x.strip()) for x in multiple_approvers_param.split(',') if x.strip()]
                if approver_ids:  # Only use if we actually have IDs
                    return user_id in approver_ids
            except (ValueError, AttributeError):
                # If parsing fails, fall back to single approver
                pass
        
        # Fall back to single approver configuration
        single_approver_param = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.approval_user_id', '')
        if single_approver_param:
            try:
                approver_id = int(single_approver_param)
                return user_id == approver_id
            except (ValueError, TypeError):
                return False
        
        return False

    def action_submit_review(self):
        """Submit vendor bills for review"""
        for record in self:
            if record.move_type in ['in_invoice', 'in_refund'] and record.state == 'draft':
                record.state = 'waiting_approval'

    def approve_transfer(self):
        """Approve vendor bills - only for authorized users"""
        for record in self:
            if (record.move_type in ['in_invoice', 'in_refund'] and 
                record.state == 'waiting_approval' and 
                record._is_user_authorized_approver_move()):
                record.state = 'approved'

    def reject_transfer(self):
        """Reject vendor bills - only for authorized users"""
        for record in self:
            if (record.move_type in ['in_invoice', 'in_refund'] and 
                record.state == 'waiting_approval' and 
                record._is_user_authorized_approver_move()):
                record.state = 'rejected'

    def button_cancel(self):
        """Override button_cancel to handle strict mode journals properly"""
        for record in self:
            # Check for strict mode before attempting to cancel
            if record.state == 'posted' and record.journal_id.restrict_mode_hash_table:
                raise UserError(_(
                    "Cannot cancel posted entry from journal '%s' because it is in strict mode.\n\n"
                    "To cancel this entry:\n"
                    "1. Create a Credit Note/Reverse Entry using the 'Credit Note' button instead\n"
                    "2. Or ask your Administrator to temporarily disable 'Lock Posted Entries with Hash' in journal settings\n\n"
                    "This restriction protects the integrity of your accounting records."
                ) % record.journal_id.name)
            
            # Allow cancellation from new approval states for vendor bills
            if (record.move_type in ['in_invoice', 'in_refund'] and 
                record.state in ['waiting_approval', 'approved', 'rejected']):
                # Set to cancel state directly for vendor bills
                record.state = 'cancel'
                return True
        
        # Call parent method for other cases
        return super(AccountMove, self).button_cancel()

    def button_draft(self):
        """Override button_draft to handle strict mode journals properly"""
        for record in self:
            # Check for strict mode before attempting to reset to draft
            if record.state == 'posted' and record.journal_id.restrict_mode_hash_table:
                raise UserError(_(
                    "Cannot reset posted entry from journal '%s' to draft because it is in strict mode.\n\n"
                    "To modify this entry:\n"
                    "1. Create a Credit Note/Reverse Entry to cancel the original entry\n"
                    "2. Create a new entry with the correct information\n"
                    "3. Or ask your Administrator to temporarily disable 'Lock Posted Entries with Hash' in journal settings\n\n"
                    "This restriction maintains audit compliance and data integrity."
                ) % record.journal_id.name)
            
            # Allow setting to draft from rejected state for vendor bills
            if (record.move_type in ['in_invoice', 'in_refund'] and 
                record.state == 'rejected'):
                record.state = 'draft'
                return True
        
        # Call parent method for other cases
        return super(AccountMove, self).button_draft()

    def action_post(self):
        """Override action_post to allow posting from approved state for vendor bills"""
        for record in self:
            # Allow posting from approved state for vendor bills
            if (record.move_type in ['in_invoice', 'in_refund'] and 
                record.state == 'approved'):
                # Set to draft temporarily to allow normal posting
                record.state = 'draft'
        
        # Call parent method
        result = super(AccountMove, self).action_post()
        return result
