# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SaleOrderStage(models.Model):
    _name = 'sale.order.stage'
    _description = 'Sale Order Workflow Stages'
    _order = 'sequence, name'

    name = fields.Char(
        string='Stage Name', 
        required=True,
        help="Display name for the workflow stage"
    )
    
    sequence = fields.Integer(
        string='Sequence', 
        default=10,
        help="Sequence order for stage progression"
    )
    
    description = fields.Text(
        string='Description',
        help="Detailed description of what happens in this stage"
    )
    
    fold = fields.Boolean(
        string='Folded in Kanban', 
        default=False,
        help="Fold this stage in kanban view"
    )
    
    stage_code = fields.Selection([
        ('draft', 'Draft'),
        ('documentation', 'Documentation'), 
        ('calculation', 'Calculation'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
    ], string='Stage Code', required=True, help="Internal code for stage identification")
    
    # Enhanced stage configuration
    responsible_group_id = fields.Many2one(
        'res.groups',
        string='Responsible Group',
        help="User group responsible for this stage"
    )
    
    auto_progress = fields.Boolean(
        string='Auto Progress',
        default=False,
        help="Automatically progress to next stage when conditions are met"
    )
    
    progress_conditions = fields.Text(
        string='Progress Conditions',
        help="Description of conditions required to progress from this stage"
    )
    
    is_final_stage = fields.Boolean(
        string='Final Stage',
        compute='_compute_is_final_stage',
        store=True,
        help="True if this is the final stage in the workflow"
    )
    
    color = fields.Integer(
        string='Color',
        default=0,
        help="Color index for kanban view"
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help="Set to false to hide this stage"
    )

    @api.depends('stage_code')
    def _compute_is_final_stage(self):
        """Compute if this is the final stage"""
        for stage in self:
            stage.is_final_stage = stage.stage_code == 'completed'

    @api.model
    def create(self, vals):
        """Ensure proper sequencing for new stages"""
        if 'sequence' not in vals:
            # Auto-assign sequence based on stage_code
            sequence_map = {
                'draft': 10,
                'documentation': 20,
                'calculation': 30,
                'approved': 40,
                'completed': 50
            }
            vals['sequence'] = sequence_map.get(vals.get('stage_code'), 99)
        
        return super().create(vals)

    def name_get(self):
        """Enhanced name display"""
        result = []
        for stage in self:
            name = f"{stage.name}"
            if stage.description:
                name += f" ({stage.description[:30]}...)" if len(stage.description) > 30 else f" ({stage.description})"
            result.append((stage.id, name))
        return result