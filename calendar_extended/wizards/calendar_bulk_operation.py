# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CalendarBulkOperation(models.TransientModel):
    _name = 'calendar.bulk.operation'
    _description = 'Calendar Bulk Operations Wizard'

    operation_type = fields.Selection([
        ('update_status', 'Update Status'),
        ('change_type', 'Change Event Type'),
        ('add_attendees', 'Add Attendees'),
        ('remove_attendees', 'Remove Attendees'),
        ('update_location', 'Update Location'),
        ('reschedule', 'Reschedule Events'),
        ('duplicate', 'Duplicate Events'),
        ('delete', 'Delete Events'),
    ], string='Operation Type', required=True)
    
    event_ids = fields.Many2many(
        'calendar.event',
        string='Events',
        required=True
    )
    
    # Fields for different operations
    new_status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('postponed', 'Postponed')
    ], string='New Status')
    
    new_event_type_id = fields.Many2one(
        'calendar.event.type',
        string='New Event Type'
    )
    
    attendees_to_add = fields.Many2many(
        'res.partner',
        'calendar_bulk_add_attendees_rel',
        string='Attendees to Add'
    )
    
    attendees_to_remove = fields.Many2many(
        'res.partner',
        'calendar_bulk_remove_attendees_rel',
        string='Attendees to Remove'
    )
    
    new_location = fields.Char(string='New Location')
    
    reschedule_type = fields.Selection([
        ('days', 'Days'),
        ('hours', 'Hours'),
        ('specific_date', 'Specific Date')
    ], string='Reschedule Type')
    
    reschedule_value = fields.Integer(string='Reschedule Value')
    
    new_start_date = fields.Datetime(string='New Start Date')
    
    duplicate_count = fields.Integer(string='Number of Duplicates', default=1)
    
    duplicate_interval = fields.Integer(string='Interval (Days)', default=7)
    
    confirm_operation = fields.Boolean(string='Confirm Operation')
    
    @api.model
    def default_get(self, fields_list):
        """Set default event_ids from context"""
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])
        if active_ids:
            res['event_ids'] = [(6, 0, active_ids)]
        return res
    
    def action_execute_operation(self):
        """Execute the bulk operation"""
        self.ensure_one()
        
        if not self.confirm_operation:
            raise ValidationError(_('Please confirm the operation before executing.'))
        
        if self.operation_type == 'update_status':
            self._update_status()
        elif self.operation_type == 'change_type':
            self._change_event_type()
        elif self.operation_type == 'add_attendees':
            self._add_attendees()
        elif self.operation_type == 'remove_attendees':
            self._remove_attendees()
        elif self.operation_type == 'update_location':
            self._update_location()
        elif self.operation_type == 'reschedule':
            self._reschedule_events()
        elif self.operation_type == 'duplicate':
            self._duplicate_events()
        elif self.operation_type == 'delete':
            self._delete_events()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Bulk operation completed successfully.'),
                'type': 'success',
            }
        }
    
    def _update_status(self):
        """Update status of selected events"""
        if not self.new_status:
            raise ValidationError(_('Please select a new status.'))
        
        for event in self.event_ids:
            event.status = self.new_status
    
    def _change_event_type(self):
        """Change event type of selected events"""
        if not self.new_event_type_id:
            raise ValidationError(_('Please select a new event type.'))
        
        for event in self.event_ids:
            event.event_type_id = self.new_event_type_id
    
    def _add_attendees(self):
        """Add attendees to selected events"""
        if not self.attendees_to_add:
            raise ValidationError(_('Please select attendees to add.'))
        
        for event in self.event_ids:
            event.partner_ids = [(4, partner.id) for partner in self.attendees_to_add]
    
    def _remove_attendees(self):
        """Remove attendees from selected events"""
        if not self.attendees_to_remove:
            raise ValidationError(_('Please select attendees to remove.'))
        
        for event in self.event_ids:
            event.partner_ids = [(3, partner.id) for partner in self.attendees_to_remove]
    
    def _update_location(self):
        """Update location of selected events"""
        if not self.new_location:
            raise ValidationError(_('Please enter a new location.'))
        
        for event in self.event_ids:
            event.location = self.new_location
    
    def _reschedule_events(self):
        """Reschedule selected events"""
        if self.reschedule_type == 'specific_date':
            if not self.new_start_date:
                raise ValidationError(_('Please select a new start date.'))
            
            for event in self.event_ids:
                duration = event.stop - event.start
                event.start = self.new_start_date
                event.stop = self.new_start_date + duration
        else:
            if not self.reschedule_value:
                raise ValidationError(_('Please enter a reschedule value.'))
            
            for event in self.event_ids:
                if self.reschedule_type == 'days':
                    delta = timedelta(days=self.reschedule_value)
                elif self.reschedule_type == 'hours':
                    delta = timedelta(hours=self.reschedule_value)
                
                event.start += delta
                event.stop += delta
    
    def _duplicate_events(self):
        """Duplicate selected events"""
        if self.duplicate_count <= 0:
            raise ValidationError(_('Number of duplicates must be greater than 0.'))
        
        for event in self.event_ids:
            for i in range(self.duplicate_count):
                new_date = event.start + timedelta(days=self.duplicate_interval * (i + 1))
                event.duplicate_event(new_date)
    
    def _delete_events(self):
        """Delete selected events"""
        self.event_ids.unlink()
