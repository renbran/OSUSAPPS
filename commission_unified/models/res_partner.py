# -*- coding: utf-8 -*-
#############################################################################
#
#    Unified Commission Management System - Partner Extensions
#
#############################################################################

from odoo import fields, models


class ResPartner(models.Model):
    """Enhanced Partner model with commission-related fields"""
    _inherit = 'res.partner'

    # Commission-related fields
    affiliated = fields.Boolean(string='Affiliated Partner',
                                help='Indicates if this partner is affiliated for commission calculations')

    commission_rate = fields.Float(string='Default Commission Rate (%)',
                                   help='Default commission rate for this partner')

    commission_payment_method = fields.Selection([
        ('invoice', 'Customer Invoice'),
        ('purchase_order', 'Purchase Order'),
        ('journal_entry', 'Journal Entry'),
    ], string='Preferred Payment Method',
       help='Preferred method for commission payments to this partner')

    # Commission statistics
    total_commissions_received = fields.Monetary(string='Total Commissions Received',
                                                  compute='_compute_commission_stats', store=True)
    commission_count = fields.Integer(string='Commission Count',
                                      compute='_compute_commission_stats', store=True)

    def _compute_commission_stats(self):
        """Compute commission statistics for partners"""
        for partner in self:
            commission_lines = self.env['commission.lines'].search([
                ('partner_id', '=', partner.id),
                ('status', '!=', 'cancelled')
            ])

            partner.total_commissions_received = sum(commission_lines.mapped('commission_amount'))
            partner.commission_count = len(commission_lines)

    def action_view_commissions(self):
        """View commissions for this partner"""
        self.ensure_one()

        action = self.env["ir.actions.actions"]._for_xml_id("commission_unified.action_commission_lines")
        action['domain'] = [('partner_id', '=', self.id)]
        action['context'] = {'default_partner_id': self.id}

        return action