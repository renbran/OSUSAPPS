from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class CommissionAssignmentMixin(models.AbstractModel):
    """Mixin for models that support commission assignments
    
    This mixin provides a standardized way to add commission assignment 
    support to any model via many2many relationships through the 
    commission.assignment bridge table.
    """
    _name = 'commission.assignment.mixin'
    _description = 'Commission Assignment Mixin'

    # Many2many commission assignments via bridge table
    commission_assignment_ids = fields.Many2many(
        'commission.assignment',
        string='Commission Assignments',
        compute='_compute_commission_assignments',
        help='Commission assignments for this record'
    )

    assigned_commission_line_ids = fields.Many2many(
        'commission.line',
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
            paid_lines = commission_lines.filtered(lambda l: l.state in ['paid', 'partially_paid'])
            record.paid_commission_amount = sum(paid_lines.mapped('commission_amount'))

    def action_view_commission_assignments(self):
        """Action to view commission assignments for this record"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commission Assignments'),
            'res_model': 'commission.assignment',
            'view_mode': 'tree,form',
            'domain': [
                ('source_model', '=', self._name),
                ('source_id', '=', self.id),
            ],
            'context': {
                'default_source_model': self._name,
                'default_source_id': self.id,
            },
            'target': 'current',
        }

    def action_view_commission_lines(self):
        """Action to view commission lines for this record"""
        self.ensure_one()
        commission_line_ids = self.assigned_commission_line_ids.ids
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commission Lines'),
            'res_model': 'commission.line',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', commission_line_ids)],
            'target': 'current',
        }

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

    def unassign_commission_line(self, commission_line_id):
        """Remove commission line assignment from this record"""
        self.ensure_one()
        
        assignment = self.env['commission.assignment'].search([
            ('source_model', '=', self._name),
            ('source_id', '=', self.id),
            ('commission_line_id', '=', commission_line_id),
            ('active', '=', True)
        ])
        
        if assignment:
            assignment.unlink()
            return True
        
        return False

    def bulk_assign_commissions(self, commission_line_ids, assignment_type='manual'):
        """Assign multiple commission lines to this record"""
        self.ensure_one()
        assignments = []
        
        for commission_line_id in commission_line_ids:
            try:
                assignment = self.assign_commission_line(commission_line_id, assignment_type)
                assignments.append(assignment)
            except UserError:
                # Skip if already assigned
                continue
        
        return assignments

    def action_assign_commission_wizard(self):
        """Open wizard to assign new commission lines"""
        self.ensure_one()
        
        # This would open a wizard for selecting commission lines to assign
        # The wizard implementation would be separate
        return {
            'type': 'ir.actions.act_window',
            'name': _('Assign Commission Lines'),
            'res_model': 'commission.assignment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_source_model': self._name,
                'default_source_id': self.id,
            },
        }

    @api.model
    def migrate_legacy_commissions(self):
        """Helper method to migrate legacy commission fields to new assignment structure"""
        # This is a template method that subclasses can override
        # to migrate their specific legacy commission fields
        pass

    def get_commission_summary(self):
        """Get a summary of commission information for this record"""
        self.ensure_one()
        
        commission_lines = self.assigned_commission_line_ids
        
        summary = {
            'total_lines': len(commission_lines),
            'total_amount': sum(commission_lines.mapped('commission_amount')),
            'by_state': {},
            'by_partner': {},
            'by_type': {}
        }
        
        # Group by state
        for state in commission_lines.mapped('state'):
            lines_in_state = commission_lines.filtered(lambda l: l.state == state)
            summary['by_state'][state] = {
                'count': len(lines_in_state),
                'amount': sum(lines_in_state.mapped('commission_amount'))
            }
        
        # Group by partner
        for partner in commission_lines.mapped('partner_id'):
            partner_lines = commission_lines.filtered(lambda l: l.partner_id == partner)
            summary['by_partner'][partner.name] = {
                'count': len(partner_lines),
                'amount': sum(partner_lines.mapped('commission_amount'))
            }
        
        # Group by commission type
        for comm_type in commission_lines.mapped('commission_type_id'):
            type_lines = commission_lines.filtered(lambda l: l.commission_type_id == comm_type)
            summary['by_type'][comm_type.name] = {
                'count': len(type_lines),
                'amount': sum(type_lines.mapped('commission_amount'))
            }
        
        return summary