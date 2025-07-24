# -*- coding: utf-8 -*-
from odoo import models, fields

class CalendarSendInvitationWizard(models.TransientModel):
    _name = 'calendar.send.invitation.wizard'
    _description = 'Send Calendar Invitation Wizard'

    meeting_id = fields.Many2one('calendar.internal.meeting', string='Meeting')
    partner_ids = fields.Many2many('res.partner', string='Additional Attendees')
    
    def action_send_invitation(self):
        self.ensure_one()
        # Add your invitation sending implementation here
        return {'type': 'ir.actions.act_window_close'}
