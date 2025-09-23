# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import urllib.parse
from datetime import datetime
import pytz
import logging

_logger = logging.getLogger(__name__)


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    def _get_google_calendar_url(self):
        """Generate enhanced Google Calendar URL with all event details"""
        self.ensure_one()
        
        if not self.start:
            return ''
            
        try:
            # Convert to UTC for Google Calendar
            start_utc = self.start.strftime('%Y%m%dT%H%M%SZ')
            end_utc = self.stop.strftime('%Y%m%dT%H%M%SZ') if self.stop else start_utc
            
            # Prepare event details with proper URL encoding
            title = urllib.parse.quote(self.name or 'Meeting', safe='')
            location = urllib.parse.quote(self.location or '', safe='')
            
            # Create detailed description
            description_parts = []
            if self.description:
                # Clean HTML tags from description for URL
                import re
                clean_description = re.sub('<.*?>', '', str(self.description))
                description_parts.append(clean_description)
                
            if self.user_id and self.user_id.partner_id:
                description_parts.append(f"Organized by: {self.user_id.partner_id.name}")
                
            if self.videocall_location:
                description_parts.append(f"Video call: {self.videocall_location}")
                
            description_parts.append(f"Meeting ID: {self.id}")
            
            description = urllib.parse.quote('\n'.join(description_parts), safe='')
            
            # Build Google Calendar URL
            gcal_params = {
                'action': 'TEMPLATE',
                'text': title,
                'dates': f"{start_utc}/{end_utc}",
                'details': description
            }
            
            if location:
                gcal_params['location'] = location
                
            # Construct URL
            base_url = 'https://calendar.google.com/calendar/render'
            params = urllib.parse.urlencode(gcal_params)
            
            return f"{base_url}?{params}"
            
        except Exception as e:
            _logger.error(f"Error generating Google Calendar URL: {str(e)}")
            return ''

    def _send_mail_to_attendees_with_template(self, template, force_send=False, raise_on_error=True):
        """Override to use custom template and ensure proper data population"""
        if not template:
            template = self.env.ref('calendar.calendar_template_meeting_invitation', raise_if_not_found=False)
            if not template:
                raise UserError(_('No email template found for calendar invitations'))

        # Ensure we have proper timezone context
        tz = self._get_mail_tz() or self.env.context.get('tz') or self.env.user.tz or 'UTC'
        
        for event in self:
            for attendee in event.attendee_ids:
                if attendee.partner_id and attendee.partner_id.email:
                    # Prepare context with attendee-specific data
                    ctx = dict(self.env.context)
                    ctx.update({
                        'attendee_email': attendee.partner_id.email,
                        'attendee_name': attendee.partner_id.name,
                        'mail_tz': tz,
                        'lang': attendee.partner_id.lang or self.env.user.lang,
                        'google_calendar_url': event._get_google_calendar_url(),
                    })
                    
                    try:
                        template.with_context(ctx).send_mail(
                            event.id, 
                            force_send=force_send,
                            raise_exception=raise_on_error,
                            email_values={
                                'email_to': attendee.partner_id.email,
                                'recipient_ids': [(4, attendee.partner_id.id)],
                            }
                        )
                        _logger.info(f"Calendar invitation sent to {attendee.partner_id.email} for event '{event.name}'")
                    except Exception as e:
                        if raise_on_error:
                            raise
                        else:
                            # Log the error instead of raising
                            _logger.error(f'Failed to send invitation to {attendee.partner_id.email}: {str(e)}')
        
        return True

    def action_sendmail(self):
        """Override the send invitations action to use custom template"""
        template = self.env.ref('calendar.calendar_template_meeting_invitation', raise_if_not_found=False)
        if not template:
            raise UserError(_('Calendar invitation template not found. Please check your email templates.'))
        
        # Send invitations using custom template
        self._send_mail_to_attendees_with_template(template, force_send=False)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': _('Invitations Sent'),
                'message': _('Meeting invitations have been sent to all attendees.'),
                'sticky': False,
            }
        }

    @api.model
    def _get_mail_tz(self):
        """Get the proper timezone for email formatting"""
        # Try to get timezone from various sources
        tz = self.env.context.get('tz') or self.env.user.tz
        if not tz and hasattr(self, 'user_id') and self.user_id:
            tz = self.user_id.tz
        return tz or 'UTC'

    def _get_ics_file(self):
        """Enhanced ICS file generation with proper encoding"""
        self.ensure_one()
        
        try:
            # Use the standard ICS generation but ensure proper encoding
            ics_content = super()._get_ics_file()
            
            # Add custom properties if needed
            if self.videocall_location:
                # Add video call URL to ICS
                ics_lines = ics_content.split('\n')
                for i, line in enumerate(ics_lines):
                    if line.startswith('DESCRIPTION:'):
                        # Add video call info to description
                        video_info = f"\\nVideo Call: {self.videocall_location}"
                        ics_lines[i] = line + video_info
                        break
                ics_content = '\n'.join(ics_lines)
            
            return ics_content
        except Exception as e:
            _logger.error(f"Error generating ICS file: {str(e)}")
            return super()._get_ics_file()

    def _compute_display_time(self):
        """Compute display time for templates"""
        for event in self:
            if event.allday:
                event.display_time = _('All Day')
            else:
                # Format time based on user timezone
                tz = event._get_mail_tz()
                if tz:
                    user_tz = pytz.timezone(tz)
                    start_time = pytz.utc.localize(event.start).astimezone(user_tz)
                    event.display_time = start_time.strftime('%I:%M %p')
                else:
                    event.display_time = event.start.strftime('%I:%M %p')

    display_time = fields.Char(compute='_compute_display_time', store=False)


class CalendarAttendee(models.Model):
    _inherit = 'calendar.attendee'

    def _send_mail_to_attendee(self, template, force_send=False):
        """Enhanced attendee mail sending with proper context"""
        if not template:
            return False
            
        # Get timezone for proper formatting
        tz = self.event_id._get_mail_tz()
        
        # Prepare context
        ctx = dict(self.env.context)
        ctx.update({
            'attendee_email': self.partner_id.email,
            'attendee_name': self.partner_id.name,
            'mail_tz': tz,
            'lang': self.partner_id.lang or self.env.user.lang,
            'google_calendar_url': self.event_id._get_google_calendar_url(),
        })
        
        try:
            return template.with_context(ctx).send_mail(
                self.event_id.id,
                force_send=force_send,
                email_values={
                    'email_to': self.partner_id.email,
                    'recipient_ids': [(4, self.partner_id.id)],
                }
            )
        except Exception as e:
            _logger.error(f'Failed to send mail to attendee {self.partner_id.email}: {str(e)}')
            return False