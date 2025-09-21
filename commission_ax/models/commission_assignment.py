from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

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