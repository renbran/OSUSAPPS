# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CalendarSendInvitationWizard(models.TransientModel):
    _name = 'calendar.send.invitation.wizard'
    _description = 'Send Invitation Wizard'

    announcement_id = fields.Many2one('calendar.announcement', string='Announcement', required=True)
    
    send_mode = fields.Selection([
        ('now', 'Send Now'),
        ('schedule', 'Schedule for Later')
    ], string='Send Mode', default='now', required=True)
    
    scheduled_date = fields.Datetime(
        string='Scheduled Date',
        help='Date and time to send invitations'
    )
    
    # Preview information
    attendee_count = fields.Integer(
        string='Total Attendees',
        related='announcement_id.attendee_count'
    )
    
    announcement_name = fields.Char(
        string='Meeting Title',
        related='announcement_id.name'
    )
    
    announcement_date = fields.Datetime(
        string='Meeting Date',
        related='announcement_id.start_datetime'
    )
    
    preview_message = fields.Html(string='Invitation Preview', compute='_compute_preview_message')
    
    @api.depends('announcement_id')
    def _compute_preview_message(self):
        for wizard in self:
            if wizard.announcement_id:
                attendees = wizard.announcement_id._get_all_attendees()
                preview = f"""
                <div class="o_mail_thread_message_core">
                    <h4>Meeting Invitation Preview</h4>
                    <p><strong>Meeting:</strong> {wizard.announcement_id.name}</p>
                    <p><strong>Date:</strong> {wizard.announcement_id.start_datetime}</p>
                    <p><strong>Location:</strong> {wizard.announcement_id.location or 'Not specified'}</p>
                    <p><strong>Attendees:</strong> {len(attendees)} people</p>
                    
                    <h5>Attendee List:</h5>
                    <ul>
                """
                
                # Show sample attendees (max 10)
                sample_attendees = attendees[:10]
                for attendee in sample_attendees:
                    preview += f"<li>{attendee.name}</li>"
                
                if len(attendees) > 10:
                    preview += f"<li>... and {len(attendees) - 10} more</li>"
                
                preview += """
                    </ul>
                </div>
                """
                wizard.preview_message = preview
            else:
                wizard.preview_message = "<p>No announcement selected</p>"
    
    @api.onchange('send_mode')
    def _onchange_send_mode(self):
        if self.send_mode == 'now':
            self.scheduled_date = False
    
    @api.constrains('scheduled_date')
    def _check_scheduled_date(self):
        for wizard in self:
            if wizard.send_mode == 'schedule' and wizard.scheduled_date:
                if wizard.scheduled_date <= fields.Datetime.now():
                    raise UserError(_('Scheduled date must be in the future.'))
                
                if (wizard.announcement_id.start_datetime and 
                    wizard.scheduled_date >= wizard.announcement_id.start_datetime):
                    raise UserError(_('Invitations should be sent before the meeting starts.'))
    
    def action_send_invitations(self):
        """Execute the invitation sending"""
        self.ensure_one()
        
        if not self.announcement_id:
            raise UserError(_('No announcement selected.'))
        
        if self.announcement_id.state != 'approved':
            raise UserError(_('Only approved announcements can send invitations.'))
        
        if self.send_mode == 'now':
            # Send immediately
            self.announcement_id._send_invitations()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Invitations sent successfully to %d attendees!') % self.attendee_count,
                    'type': 'success',
                    'sticky': False,
                }
            }
        
        elif self.send_mode == 'schedule':
            if not self.scheduled_date:
                raise UserError(_('Please specify a scheduled date.'))
            
            # Schedule for later
            self.announcement_id.scheduled_send_date = self.scheduled_date
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Invitations scheduled for %s') % self.scheduled_date,
                    'type': 'success',
                    'sticky': False,
                }
            }
    
    def action_preview_attendees(self):
        """Show detailed attendee list"""
        attendees = self.announcement_id._get_all_attendees()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Attendee Preview'),
            'res_model': 'hr.employee',
            'view_mode': 'tree',
            'domain': [('id', 'in', attendees.ids)],
            'context': {'create': False, 'edit': False, 'delete': False}
        }
