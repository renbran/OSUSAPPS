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
from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    """This class inherits the model 'res.config.settings' and adds
     required fields"""
    _inherit = 'res.config.settings'

    def _get_account_manager_ids(self):
        """This function  gets all the records of 'res.users'  and
        it filters the 'res.users' records to select only those users
        who belong to the 'account.group_account_manager' group."""
        user_ids = self.env['res.users'].search([])
        account_manager_ids = user_ids.filtered(
            lambda x: x.has_group('account.group_account_manager'))
        return [('id', 'in', account_manager_ids.ids)]

    payment_approval = fields.Boolean(
        string='Payment Approval',
        config_parameter='account_payment_approval.payment_approval',
        help="Enable/disable payment approval to approve for payment if needed."
    )
    approval_user_id = fields.Many2one(
        'res.users',
        string="Payment Approving Person",
        required=False,
        domain=_get_account_manager_ids,
        config_parameter='account_payment_approval.approval_user_id',
        help="Select the payment approving person."
    )
    approval_user_ids = fields.Many2many(
        'res.users',
        'approval_user_rel',
        'config_id', 
        'user_id',
        string="Payment Approving Persons",
        required=False,
        domain=_get_account_manager_ids,
        help="Select multiple users who can approve payments. If specified, this takes precedence over single approver."
    )

    def set_values(self):
        """Override to properly handle Many2many field storage in config parameters"""
        super(ResConfigSettings, self).set_values()
        
        # Handle the Many2many field storage manually
        if self.approval_user_ids:
            user_ids_str = ','.join(str(uid) for uid in self.approval_user_ids.ids)
            self.env['ir.config_parameter'].sudo().set_param(
                'account_payment_approval.approval_user_ids', 
                user_ids_str
            )
        else:
            self.env['ir.config_parameter'].sudo().set_param(
                'account_payment_approval.approval_user_ids', 
                ''
            )

    @api.model
    def get_values(self):
        """Override to properly handle Many2many field retrieval from config parameters"""
        res = super(ResConfigSettings, self).get_values()
        
        # Handle the Many2many field retrieval manually
        user_ids_str = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.approval_user_ids', ''
        )
        
        if user_ids_str:
            try:
                user_ids = [int(uid.strip()) for uid in user_ids_str.split(',') if uid.strip()]
                res['approval_user_ids'] = [(6, 0, user_ids)]
            except (ValueError, AttributeError):
                res['approval_user_ids'] = [(6, 0, [])]
        else:
            res['approval_user_ids'] = [(6, 0, [])]
            
        return res

    def get_current_approvers(self):
        """Get list of current authorized approvers for display/informational purposes"""
        approval = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.payment_approval')
        
        if not approval:
            return self.env['res.users']
            
        # Check for multiple approvers first
        multiple_approvers_param = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.approval_user_ids')
        
        if multiple_approvers_param:
            try:
                approver_ids = [int(x.strip()) for x in multiple_approvers_param.split(',') if x.strip()]
                return self.env['res.users'].browse(approver_ids)
            except (ValueError, AttributeError):
                pass
        
        # Fall back to single approver
        single_approver_param = self.env['ir.config_parameter'].sudo().get_param(
            'account_payment_approval.approval_user_id')
        if single_approver_param:
            try:
                approver_id = int(single_approver_param)
                return self.env['res.users'].browse(approver_id)
            except (ValueError, TypeError):
                pass
        
        return self.env['res.users']
    approval_amount = fields.Float(
        string='Minimum Amount for Approval',
        config_parameter='account_payment_approval.approval_amount',
        help="Payments exceeding this amount will require approval. If amount is 0.00, All the payments go through approval."
    )
    approval_currency_id = fields.Many2one(
        'res.currency',
        string='Approval Amount Currency',
        config_parameter='account_payment_approval.approval_currency_id',
        default=lambda self: self.env.company.currency_id,
        help="Converts the payment amount to this currency if chosen."
    )
