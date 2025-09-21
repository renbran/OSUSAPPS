# -*- coding: utf-8 -*-
#############################################################################
#
#    Unified Commission Management System - Sale Order Integration
#
#############################################################################

import logging
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    """Enhanced Sale Order with Unified Commission Management"""
    _inherit = 'sale.order'

    # Commission Lines Relationship
    commission_ids = fields.One2many('commission.lines', 'sale_order_id', string='Commission Lines')

    # Commission Status and Workflow
    commission_status = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('approved', 'Approved'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
    ], string="Commission Status", default='draft', tracking=True, copy=False)

    commission_processed = fields.Boolean(string="Commissions Processed", default=False, copy=False)
    commission_auto_calculate = fields.Boolean(string="Auto Calculate", default=True,
                                               help="Automatically calculate commissions on order confirmation")

    # Commission Summary Fields (computed from commission.lines)
    total_commission_amount = fields.Monetary(string="Total Commission Amount",
                                              compute="_compute_commission_totals", store=True)
    total_external_commission = fields.Monetary(string="Total External Commissions",
                                                compute="_compute_commission_totals", store=True)
    total_internal_commission = fields.Monetary(string="Total Internal Commissions",
                                                compute="_compute_commission_totals", store=True)
    total_legacy_commission = fields.Monetary(string="Total Legacy Commissions",
                                              compute="_compute_commission_totals", store=True)
    total_rule_commission = fields.Monetary(string="Total Rule-based Commissions",
                                            compute="_compute_commission_totals", store=True)

    # Company Financial Impact
    company_share = fields.Monetary(string="Company Share", compute="_compute_commission_totals", store=True)
    net_company_share = fields.Monetary(string="Net Company Share", compute="_compute_commission_totals", store=True)
    commission_percentage = fields.Float(string="Commission %", compute="_compute_commission_totals", store=True)

    # Commission Counts for UI
    commission_count = fields.Integer(string="Commission Count", compute="_compute_commission_counts")
    pending_commission_count = fields.Integer(string="Pending Commissions", compute="_compute_commission_counts")
    paid_commission_count = fields.Integer(string="Paid Commissions", compute="_compute_commission_counts")

    # External Commission Partners (from commission_ax)
    broker_partner_id = fields.Many2one('res.partner', string="Broker")
    referrer_partner_id = fields.Many2one('res.partner', string="Referrer")
    cashback_partner_id = fields.Many2one('res.partner', string="Cashback Partner")
    other_external_partner_id = fields.Many2one('res.partner', string="Other External Partner")

    # Internal Commission Partners (from commission_ax)
    agent1_partner_id = fields.Many2one('res.partner', string="Agent 1")
    agent2_partner_id = fields.Many2one('res.partner', string="Agent 2")
    manager_partner_id = fields.Many2one('res.partner', string="Manager")
    director_partner_id = fields.Many2one('res.partner', string="Director")

    # Legacy Commission Partners (from commission_ax - backward compatibility)
    consultant_id = fields.Many2one('res.partner', string="Consultant")
    manager_id = fields.Many2one('res.partner', string="Manager (Legacy)")
    second_agent_id = fields.Many2one('res.partner', string="Second Agent")
    director_id = fields.Many2one('res.partner', string="Director (Legacy)")

    # Commission Rules (from sales_commission_users)
    commission_rules_ids = fields.Many2many('commission.rules', string='Applied Commission Rules')

    # Payment Processing
    commission_payment_method = fields.Selection([
        ('invoice', 'Customer Invoices'),
        ('purchase_order', 'Purchase Orders'),
        ('journal_entry', 'Journal Entries'),
        ('auto', 'Auto (Use System Default)'),
    ], string="Commission Payment Method", default='auto')

    # Approval Requirements
    commission_requires_approval = fields.Boolean(string="Requires Approval", default=False)
    commission_approved_by = fields.Many2one('res.users', string='Commission Approved By', readonly=True)
    commission_approved_date = fields.Datetime(string='Commission Approved Date', readonly=True)

    @api.depends('commission_ids.commission_amount', 'commission_ids.status', 'commission_ids.commission_group')
    def _compute_commission_totals(self):
        """Compute all commission total fields"""
        for order in self:
            commission_lines = order.commission_ids.filtered(lambda l: l.status != 'cancelled')

            # Total amounts by group
            order.total_external_commission = sum(
                commission_lines.filtered(lambda l: l.commission_group == 'external').mapped('commission_amount')
            )
            order.total_internal_commission = sum(
                commission_lines.filtered(lambda l: l.commission_group == 'internal').mapped('commission_amount')
            )
            order.total_legacy_commission = sum(
                commission_lines.filtered(lambda l: l.commission_group == 'legacy').mapped('commission_amount')
            )
            order.total_rule_commission = sum(
                commission_lines.filtered(lambda l: l.commission_group == 'rule_based').mapped('commission_amount')
            )

            # Overall totals
            order.total_commission_amount = sum(commission_lines.mapped('commission_amount'))

            # Company share calculations
            order.company_share = order.amount_total - order.total_commission_amount
            order.net_company_share = order.company_share - order.amount_tax

            # Commission percentage
            if order.amount_total > 0:
                order.commission_percentage = (order.total_commission_amount / order.amount_total) * 100
            else:
                order.commission_percentage = 0.0

    @api.depends('commission_ids')
    def _compute_commission_counts(self):
        """Compute commission counts for UI"""
        for order in self:
            commission_lines = order.commission_ids
            order.commission_count = len(commission_lines)
            order.pending_commission_count = len(commission_lines.filtered(
                lambda l: l.status in ['draft', 'calculated', 'approved', 'confirmed']
            ))
            order.paid_commission_count = len(commission_lines.filtered(lambda l: l.status == 'paid'))

    def action_confirm(self):
        """Override to handle commission calculation on order confirmation"""
        result = super(SaleOrder, self).action_confirm()

        for order in self:
            if order.commission_auto_calculate:
                try:
                    order._auto_calculate_commissions()
                except Exception as e:
                    _logger.warning(f"Auto commission calculation failed for {order.name}: {str(e)}")
                    # Don't block order confirmation if commission calculation fails
                    order.message_post(
                        body=f"Warning: Commission auto-calculation failed: {str(e)}. "
                             f"Please calculate commissions manually.",
                        message_type='comment'
                    )

        return result

    def _auto_calculate_commissions(self):
        """Automatically calculate commissions based on configuration"""
        self.ensure_one()

        if self.commission_processed:
            _logger.info(f"Commissions already processed for order {self.name}")
            return

        _logger.info(f"Auto-calculating commissions for order {self.name}")

        # Use the unified commission calculator
        calculator = self.env['commission.calculator']
        commission_data = calculator.calculate_all_commissions(self)

        if commission_data:
            # Create commission lines
            for comm_data in commission_data:
                self.env['commission.lines'].create(comm_data)

            self.commission_status = 'calculated'
            self.commission_processed = True

            self.message_post(
                body=f"Commissions automatically calculated: {len(commission_data)} commission lines created.",
                message_type='notification'
            )

            _logger.info(f"Created {len(commission_data)} commission lines for order {self.name}")
        else:
            _logger.info(f"No commissions calculated for order {self.name}")

    def action_calculate_commissions(self):
        """Manual action to calculate commissions"""
        for order in self:
            if order.commission_processed and order.commission_status != 'draft':
                raise UserError(_("Commissions have already been processed for this order. "
                                  "Use 'Reset Commissions' to recalculate."))

            # Clear existing draft commission lines
            order.commission_ids.filtered(lambda l: l.status == 'draft').unlink()

            # Calculate new commissions
            calculator = self.env['commission.calculator']
            commission_data = calculator.calculate_all_commissions(order)

            if commission_data:
                # Create commission lines
                created_lines = []
                for comm_data in commission_data:
                    line = self.env['commission.lines'].create(comm_data)
                    created_lines.append(line)

                # Auto-calculate amounts
                for line in created_lines:
                    line.action_calculate()

                order.commission_status = 'calculated'
                order.commission_processed = True

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': f"{len(commission_data)} commission lines calculated successfully.",
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(_("No commissions found to calculate. Please check commission configuration."))

    def action_approve_commissions(self):
        """Approve all calculated commissions"""
        for order in self:
            calculated_lines = order.commission_ids.filtered(lambda l: l.status == 'calculated')

            if not calculated_lines:
                raise UserError(_("No calculated commissions found to approve."))

            # Check if approval is required
            require_approval = self.env['ir.config_parameter'].sudo().get_param(
                'commission.require_approval', 'False'
            ).lower() == 'true'

            if require_approval:
                # Check user permissions
                if not self.env.user.has_group('commission_unified.group_commission_manager'):
                    raise UserError(_("Only Commission Managers can approve commissions."))

            # Approve all calculated lines
            for line in calculated_lines:
                line.action_approve()

            order.commission_status = 'approved'
            order.commission_approved_by = self.env.user
            order.commission_approved_date = fields.Datetime.now()

            order.message_post(
                body=f"Commissions approved by {self.env.user.name}",
                message_type='notification'
            )

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': f"{len(calculated_lines)} commissions approved successfully.",
                    'type': 'success',
                    'sticky': False,
                }
            }

    def action_confirm_commissions(self):
        """Confirm approved commissions"""
        for order in self:
            approved_lines = order.commission_ids.filtered(lambda l: l.status == 'approved')

            if not approved_lines:
                raise UserError(_("No approved commissions found to confirm."))

            # Confirm all approved lines
            for line in approved_lines:
                line.action_confirm()

            order.commission_status = 'confirmed'

            order.message_post(
                body=f"Commissions confirmed by {self.env.user.name}",
                message_type='notification'
            )

    def action_process_commission_payments(self):
        """Process commission payments"""
        for order in self:
            confirmed_lines = order.commission_ids.filtered(lambda l: l.status in ['confirmed', 'approved'])

            if not confirmed_lines:
                raise UserError(_("No confirmed commissions found to process."))

            # Set payment method for lines that don't have one
            default_method = order.commission_payment_method
            if default_method == 'auto':
                default_method = self.env['ir.config_parameter'].sudo().get_param(
                    'commission.default_payment_method', 'invoice'
                )

            for line in confirmed_lines:
                if not line.payment_method:
                    line.payment_method = default_method
                line.action_process_payment()

            order.commission_status = 'paid'

            order.message_post(
                body=f"Commission payments processed: {len(confirmed_lines)} payments created",
                message_type='notification'
            )

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': f"{len(confirmed_lines)} commission payments processed successfully.",
                    'type': 'success',
                    'sticky': False,
                }
            }

    def action_reset_commissions(self):
        """Reset commission status and allow recalculation"""
        for order in self:
            # Check if any commissions are already paid
            paid_lines = order.commission_ids.filtered(lambda l: l.status == 'paid')
            if paid_lines:
                raise UserError(_(
                    "Cannot reset commissions because some are already paid. "
                    "Please handle paid commissions separately."
                ))

            # Reset all commission lines to draft
            draft_lines = order.commission_ids.filtered(lambda l: l.status != 'paid')
            for line in draft_lines:
                line.action_reset_to_draft()

            # Reset order commission status
            order.commission_status = 'draft'
            order.commission_processed = False
            order.commission_approved_by = False
            order.commission_approved_date = False

            order.message_post(
                body="Commission status reset to draft. Commissions can now be recalculated.",
                message_type='notification'
            )

    def action_view_commissions(self):
        """Open commission lines view"""
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("commission_unified.action_commission_lines")
        action['domain'] = [('sale_order_id', '=', self.id)]
        action['context'] = {'default_sale_order_id': self.id}
        return action

    def action_commission_report(self):
        """Generate commission report"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Commission Report',
            'res_model': 'commission.report.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sale_order_id': self.id}
        }

    @api.constrains('commission_ids')
    def _check_commission_totals(self):
        """Validate commission totals don't exceed reasonable limits"""
        max_percentage = float(self.env['ir.config_parameter'].sudo().get_param(
            'commission.max_commission_percentage', '50.0'
        ))

        for order in self:
            if order.amount_total > 0 and order.commission_percentage > max_percentage:
                raise ValidationError(_(
                    "Total commission percentage (%.2f%%) exceeds maximum allowed (%.2f%%). "
                    "Please review commission configuration."
                ) % (order.commission_percentage, max_percentage))

    def write(self, vals):
        """Override write to handle commission field changes"""
        result = super(SaleOrder, self).write(vals)

        # Reset commission processing if commission-related fields change
        commission_fields = [
            'broker_partner_id', 'referrer_partner_id', 'cashback_partner_id', 'other_external_partner_id',
            'agent1_partner_id', 'agent2_partner_id', 'manager_partner_id', 'director_partner_id',
            'consultant_id', 'manager_id', 'second_agent_id', 'director_id',
            'commission_rules_ids', 'order_line'
        ]

        if any(field in vals for field in commission_fields):
            for order in self:
                if order.commission_processed and order.commission_status not in ['draft', 'paid']:
                    order.message_post(
                        body="Commission-related fields changed. Please recalculate commissions if needed.",
                        message_type='comment'
                    )

        return result

    @api.model
    def _cron_auto_process_commissions(self):
        """Scheduled action to auto-process commissions for invoiced orders"""
        auto_process = self.env['ir.config_parameter'].sudo().get_param(
            'commission.auto_process_invoiced', 'False'
        ).lower() == 'true'

        if not auto_process:
            return

        orders = self.search([
            ('state', 'in', ['sale', 'done']),
            ('commission_processed', '=', False),
            ('invoice_status', '=', 'invoiced')
        ])

        for order in orders:
            posted_invoices = order.invoice_ids.filtered(lambda inv: inv.state == 'posted')
            if posted_invoices:
                try:
                    order._auto_calculate_commissions()
                    _logger.info(f"Auto-processed commissions for invoiced order {order.name}")
                except Exception as e:
                    _logger.error(f"Failed to auto-process commissions for {order.name}: {str(e)}")

    def unlink(self):
        """Override unlink to handle commission lines"""
        for order in self:
            paid_commissions = order.commission_ids.filtered(lambda l: l.status == 'paid')
            if paid_commissions:
                raise UserError(_(
                    "Cannot delete sale order %s because it has paid commission lines. "
                    "Please handle the commissions first."
                ) % order.name)

            # Delete associated commission lines
            order.commission_ids.unlink()

        return super(SaleOrder, self).unlink()