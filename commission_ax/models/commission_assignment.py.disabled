from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)

class CommissionAssignmentMixin(models.AbstractModel):
    """Mixin for models that support commission assignments"""
    _name = 'commission.assignment.mixin'
    _description = 'Commission Assignment Mixin'

    # Many2many commission assignments via bridge table
    commission_assignment_ids = fields.Many2many(
        'commission.assignment',
        relation='commission_assignment_mixin_rel',
        column1='source_id',
        column2='assignment_id',
        string='Commission Assignments',
        compute='_compute_commission_assignments',
        help='Commission assignments for this record'
    )

    assigned_commission_line_ids = fields.Many2many(
        'commission.line',
        relation='commission_line_mixin_rel',
        column1='source_id',
        column2='line_id',
        string='Assigned Commission Lines',
        compute='_compute_commission_lines',
        help='Commission lines assigned to this record via assignments'
    )

    # Commission statistics
    commission_count = fields.Integer(
        string='Commission Lines Count',
        compute='_compute_commission_stats',
        help='Number of commission lines assigned to this record'
    )

    total_commission_amount = fields.Float(
        string='Total Commission Amount',
        compute='_compute_commission_stats',
        help='Total amount of all commissions assigned to this record'
    )

    pending_commission_amount = fields.Float(
        string='Pending Commission Amount',
        compute='_compute_commission_stats',
        help='Total amount of pending commissions assigned to this record'
    )

    paid_commission_amount = fields.Float(
        string='Paid Commission Amount',
        compute='_compute_commission_stats',
        help='Total amount of paid commissions assigned to this record'
    )

    def _compute_commission_assignments(self):
        """Compute commission assignments for this record"""
        for record in self:
            model_name = record._name
            record_id = record.id

            if model_name and record_id:
                assignments = self.env['commission.assignment'].search([
                    ('source_model', '=', model_name),
                    ('source_id', '=', record_id),
                    ('active', '=', True)
                ])
                record.commission_assignment_ids = assignments
            else:
                record.commission_assignment_ids = self.env['commission.assignment']

    def _compute_commission_lines(self):
        """Compute commission lines for this record"""
        for record in self:
            record.assigned_commission_line_ids = record.commission_assignment_ids.mapped('commission_line_id')

    def _compute_commission_stats(self):
        """Compute commission statistics"""
        for record in self:
            commission_lines = record.assigned_commission_line_ids

            record.commission_count = len(commission_lines)
            record.total_commission_amount = sum(commission_lines.mapped('commission_amount'))

            # Calculate pending commissions
            pending_lines = commission_lines.filtered(lambda l: l.state in ['draft', 'calculated', 'confirmed'])
            record.pending_commission_amount = sum(pending_lines.mapped('commission_amount'))

            # Calculate paid commissions
            paid_lines = commission_lines.filtered(lambda l: l.state in ['paid'])
            record.paid_commission_amount = sum(paid_lines.mapped('commission_amount'))

    def assign_commission_line(self, commission_line_id, assignment_type='manual'):
        """Assign a commission line to this record"""
        self.ensure_one()

        # Check if assignment already exists
        existing = self.env['commission.assignment'].search([
            ('source_model', '=', self._name),
            ('source_id', '=', self.id),
            ('commission_line_id', '=', commission_line_id),
            ('active', '=', True)
        ])

        if existing:
            raise UserError(_("This commission line is already assigned to this record."))

        # Create new assignment
        assignment = self.env['commission.assignment'].create({
            'source_model': self._name,
            'source_id': self.id,
            'commission_line_id': commission_line_id,
            'assignment_type': assignment_type,
        })

        return assignment

class CommissionAssignment(models.Model):
    """Commission Assignment Bridge Model
    
    This model acts as a bridge between any source model and commission lines,
    allowing flexible many2many relationships instead of individual commission fields.
    """
    _name = 'commission.assignment'
    _description = 'Commission Assignment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'source_model, source_id, sequence, id'
    _rec_name = 'display_name'

    # Bridge fields for generic assignment
    source_model = fields.Char(
        string='Source Model',
        required=True,
        index=True,
        help='The model name this assignment relates to (e.g., sale.order, purchase.order)'
    )
    source_id = fields.Integer(
        string='Source Record ID',
        required=True,
        index=True,
        help='The ID of the record in the source model'
    )
    
    # Commission relationship
    commission_line_id = fields.Many2one(
        'commission.line',
        string='Commission Line',
        required=True,
        ondelete='cascade',
        index=True,
        help='The commission line assigned to this record'
    )
    
    # Assignment metadata
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of commission assignments'
    )
    
    assignment_type = fields.Selection([
        ('automatic', 'Automatic'),
        ('manual', 'Manual'),
        ('imported', 'Imported'),
        ('migrated', 'Migrated from Legacy')
    ], string='Assignment Type', default='manual', help='How this assignment was created')
    
    # Display and relationship fields
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )
    
    # Computed fields from commission line
    partner_id = fields.Many2one(
        'res.partner',
        string='Commission Partner',
        related='commission_line_id.partner_id',
        store=True,
        readonly=True
    )
    
    commission_type_id = fields.Many2one(
        'commission.type',
        string='Commission Type',
        related='commission_line_id.commission_type_id',
        store=True,
        readonly=True
    )
    
    commission_amount = fields.Monetary(
        string='Commission Amount',
        related='commission_line_id.commission_amount',
        store=True,
        readonly=True,
        currency_field='currency_id'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        related='commission_line_id.currency_id',
        store=True,
        readonly=True
    )
    
    state = fields.Selection(
        related='commission_line_id.state',
        store=True,
        readonly=True
    )
    
    # Active flag
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Uncheck to archive this assignment'
    )
    
    # Audit fields
    created_date = fields.Datetime(
        string='Created Date',
        default=fields.Datetime.now,
        readonly=True
    )
    
    assigned_by = fields.Many2one(
        'res.users',
        string='Assigned By',
        default=lambda self: self.env.user,
        readonly=True
    )

    @api.depends('source_model', 'source_id', 'commission_line_id.display_name')
    def _compute_display_name(self):
        """Compute display name from source model and commission line"""
        for assignment in self:
            if assignment.source_model and assignment.source_id and assignment.commission_line_id:
                try:
                    # Try to get the source record name
                    source_record = self.env[assignment.source_model].browse(assignment.source_id)
                    if source_record.exists():
                        source_name = source_record.display_name or f"ID: {assignment.source_id}"
                    else:
                        source_name = f"ID: {assignment.source_id} (deleted)"
                    
                    assignment.display_name = f"{assignment.source_model}: {source_name} → {assignment.commission_line_id.display_name}"
                except Exception as e:
                    assignment.display_name = f"{assignment.source_model}({assignment.source_id}) → {assignment.commission_line_id.display_name}"
            else:
                assignment.display_name = "Commission Assignment"

    @api.constrains('source_model', 'source_id', 'commission_line_id')
    def _check_unique_assignment(self):
        """Ensure no duplicate assignments for the same source record and commission line"""
        for assignment in self:
            duplicate = self.search([
                ('source_model', '=', assignment.source_model),
                ('source_id', '=', assignment.source_id),
                ('commission_line_id', '=', assignment.commission_line_id.id),
                ('id', '!=', assignment.id),
                ('active', '=', True)
            ])
            if duplicate:
                raise ValidationError(_(
                    "This commission line is already assigned to this record. "
                    "Please use a different commission line or modify the existing assignment."
                ))

    @api.constrains('source_model')
    def _check_valid_source_model(self):
        """Validate that source_model is a valid Odoo model"""
        for assignment in self:
            if assignment.source_model:
                try:
                    # Check if model exists
                    if assignment.source_model not in self.env:
                        raise ValidationError(_(
                            "Invalid source model: %s. Please use a valid Odoo model name."
                        ) % assignment.source_model)
                except Exception:
                    raise ValidationError(_(
                        "Invalid source model: %s. Please use a valid Odoo model name."
                    ) % assignment.source_model)

    def get_source_record(self):
        """Get the source record for this assignment"""
        self.ensure_one()
        if self.source_model and self.source_id:
            try:
                return self.env[self.source_model].browse(self.source_id)
            except Exception as e:
                _logger.warning(f"Could not access source record {self.source_model}({self.source_id}): {e}")
                return self.env[self.source_model]
        return None

    def action_view_source_record(self):
        """Action to view the source record"""
        self.ensure_one()
        source_record = self.get_source_record()
        if not source_record or not source_record.exists():
            raise ValidationError(_("Source record not found or has been deleted."))
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Source Record: {source_record.display_name}',
            'res_model': self.source_model,
            'res_id': self.source_id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_commission_line(self):
        """Action to view the commission line"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Commission Line: {self.commission_line_id.display_name}',
            'res_model': 'commission.line',
            'res_id': self.commission_line_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model
    def create_assignment(self, source_model, source_id, commission_line_id, assignment_type='manual'):
        """Helper method to create commission assignments"""
        return self.create({
            'source_model': source_model,
            'source_id': source_id,
            'commission_line_id': commission_line_id,
            'assignment_type': assignment_type,
        })

    @api.model
    def get_assignments_for_record(self, source_model, source_id):
        """Get all commission assignments for a specific record"""
        return self.search([
            ('source_model', '=', source_model),
            ('source_id', '=', source_id),
            ('active', '=', True)
        ])

    def unlink(self):
        """Override unlink to add logging"""
        for assignment in self:
            _logger.info(f"Deleting commission assignment: {assignment.display_name}")
        return super().unlink()