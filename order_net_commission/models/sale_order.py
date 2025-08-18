# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Override state field to add new workflow stages
    state = fields.Selection(
        selection_add=[
            ('documentation', 'Documentation'),
            ('commission', 'Commission Calculation'),
        ],
        ondelete={'documentation': 'cascade', 'commission': 'cascade'}
    )

    # Net commission calculation fields
    net_commission = fields.Monetary(
        string='Net Commission',
        compute='_compute_net_commission',
        store=True,
        readonly=False,
        tracking=True,
        help="Calculated as: Total Amount - (Internal Costs - External Costs)"
    )

    total_internal = fields.Monetary(
        string='Total Internal Costs',
        default=0.0,
        tracking=True,
        help="Internal operational costs for this order"
    )

    total_external = fields.Monetary(
        string='Total External Costs', 
        default=0.0,
        tracking=True,
        help="External vendor costs for this order"
    )

    # Workflow tracking fields
    documentation_date = fields.Datetime(
        string='Documentation Date',
        readonly=True,
        tracking=True
    )

    commission_date = fields.Datetime(
        string='Commission Date',
        readonly=True,
        tracking=True
    )

    documentation_user_id = fields.Many2one(
        'res.users',
        string='Documentation Officer',
        readonly=True,
        tracking=True
    )

    commission_user_id = fields.Many2one(
        'res.users',
        string='Commission Analyst',
        readonly=True,
        tracking=True
    )

    approver_user_id = fields.Many2one(
        'res.users',
        string='Sales Approver',
        readonly=True,
        tracking=True
    )

    # Computed fields for button visibility
    can_set_documentation = fields.Boolean(
        compute='_compute_workflow_permissions',
        string='Can Set Documentation'
    )

    can_set_commission = fields.Boolean(
        compute='_compute_workflow_permissions',
        string='Can Set Commission'
    )

    can_approve_commission = fields.Boolean(
        compute='_compute_workflow_permissions',
        string='Can Approve Commission'
    )

    @api.depends('amount_total', 'total_internal', 'total_external')
    def _compute_net_commission(self):
        """Calculate net commission based on total amount and costs"""
        for order in self:
            if order.amount_total and (order.total_internal or order.total_external):
                order.net_commission = order.amount_total - (order.total_internal - order.total_external)
            else:
                order.net_commission = order.amount_total

    @api.depends('state')
    def _compute_workflow_permissions(self):
        """Compute workflow button visibility based on user groups and order state"""
        for order in self:
            # Check user groups
            user = self.env.user
            is_doc_officer = user.has_group('order_net_commission.group_documentation_officer')
            is_comm_analyst = user.has_group('order_net_commission.group_commission_analyst')
            is_approver = user.has_group('order_net_commission.group_sales_approver')

            # Set permissions based on state and groups
            order.can_set_documentation = (order.state == 'draft' and is_doc_officer)
            order.can_set_commission = (order.state == 'documentation' and is_comm_analyst)
            order.can_approve_commission = (order.state == 'commission' and is_approver)

    def action_set_documentation(self):
        """Move order to documentation stage"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("Only draft orders can be moved to documentation."))
        
        if not self.env.user.has_group('order_net_commission.group_documentation_officer'):
            raise UserError(_("You don't have permission to perform this action."))

        self.write({
            'state': 'documentation',
            'documentation_date': fields.Datetime.now(),
            'documentation_user_id': self.env.user.id,
        })

        # Post message to chatter
        self.message_post(
            body=_("Order moved to Documentation stage by %s") % self.env.user.name,
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )

        # Create activity for commission analyst
        self._create_commission_activity()

        return True

    def action_set_commission(self):
        """Move order to commission calculation stage"""
        self.ensure_one()
        if self.state != 'documentation':
            raise UserError(_("Only documentation orders can be moved to commission calculation."))
        
        if not self.env.user.has_group('order_net_commission.group_commission_analyst'):
            raise UserError(_("You don't have permission to perform this action."))

        # Validate that commission can be calculated
        if not self.order_line:
            raise UserError(_("Cannot calculate commission for an order without lines."))

        self.write({
            'state': 'commission',
            'commission_date': fields.Datetime.now(),
            'commission_user_id': self.env.user.id,
        })

        # Recalculate net commission
        self._compute_net_commission()

        # Post message to chatter
        self.message_post(
            body=_("Order moved to Commission Calculation stage by %s. Net Commission: %s") % (
                self.env.user.name, 
                self.net_commission
            ),
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )

        # Create activity for sales approver
        self._create_approval_activity()

        return True

    def action_approve_commission(self):
        """Final approval - confirm the sales order"""
        self.ensure_one()
        if self.state != 'commission':
            raise UserError(_("Only commission orders can be approved."))
        
        if not self.env.user.has_group('order_net_commission.group_sales_approver'):
            raise UserError(_("You don't have permission to perform this action."))

        # Record approver
        self.write({
            'approver_user_id': self.env.user.id,
        })

        # Post message to chatter before confirmation
        self.message_post(
            body=_("Commission approved by %s. Net Commission: %s. Order confirmed.") % (
                self.env.user.name,
                self.net_commission
            ),
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )

        # Confirm the sales order (moves to 'sale' state)
        return self.action_confirm()

    def _create_commission_activity(self):
        """Create activity for commission analyst"""
        commission_analysts = self.env['res.users'].search([
            ('groups_id', 'in', [self.env.ref('order_net_commission.group_commission_analyst').id])
        ])
        
        if commission_analysts:
            self.activity_schedule(
                'order_net_commission.mail_activity_commission_calculation',
                user_id=commission_analysts[0].id,
                note=_("Please review and calculate commission for order %s") % self.name
            )

    def _create_approval_activity(self):
        """Create activity for sales approver"""
        approvers = self.env['res.users'].search([
            ('groups_id', 'in', [self.env.ref('order_net_commission.group_sales_approver').id])
        ])
        
        if approvers:
            self.activity_schedule(
                'order_net_commission.mail_activity_commission_approval',
                user_id=approvers[0].id,
                note=_("Please review and approve commission for order %s. Net Commission: %s") % (
                    self.name, self.net_commission
                )
            )

    @api.constrains('total_internal', 'total_external', 'amount_total')
    def _check_commission_values(self):
        """Validate commission calculation values"""
        for order in self:
            if order.total_internal < 0:
                raise ValidationError(_("Internal costs cannot be negative."))
            if order.total_external < 0:
                raise ValidationError(_("External costs cannot be negative."))
            if order.state == 'commission' and order.net_commission <= 0:
                raise ValidationError(_("Net commission must be positive for commission calculation."))

    def write(self, vals):
        """Override write to track important field changes"""
        result = super(SaleOrder, self).write(vals)
        
        # Log commission changes
        if 'net_commission' in vals:
            for order in self:
                if order.state in ['commission', 'sale']:
                    order.message_post(
                        body=_("Net commission updated to: %s") % order.net_commission,
                        message_type='notification',
                        subtype_xmlid='mail.mt_note'
                    )
        
        return result

    @api.model
    def create(self, vals):
        """Override create to set default workflow state"""
        # Ensure new orders start in draft state
        if 'state' not in vals:
            vals['state'] = 'draft'
        
        result = super(SaleOrder, self).create(vals)
        
        # Post creation message
        result.message_post(
            body=_("Sales order created. Workflow: Draft → Documentation → Commission → Sale"),
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )
        
        return result
