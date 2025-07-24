from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    # Add joining_date field if it doesn't exist
    joining_date = fields.Date(
        string='Joining Date',
        help="Date when the employee joined the company"
    )
    
    # Helper method to get hire date from multiple possible fields
    @api.depends('joining_date')
    def _get_hire_date(self):
        """Get hire date from available fields in order of priority."""
        return (
            self.joining_date or 
            getattr(self, 'hire_date', False) or
            getattr(self, 'contract_date_start', False)
        )
    
    # Add computed field for years of service
    years_of_service = fields.Integer(
        string='Years of Service',
        compute='_compute_years_of_service',
        store=False
    )
    
    @api.depends('joining_date')
    def _compute_years_of_service(self):
        today = date.today()
        for employee in self:
            hire_date = employee._get_hire_date()
            if hire_date:
                employee.years_of_service = today.year - hire_date.year
                # Adjust if anniversary hasn't occurred this year
                if today.month < hire_date.month or \
                   (today.month == hire_date.month and today.day < hire_date.day):
                    employee.years_of_service -= 1
            else:
                employee.years_of_service = 0
    
    def send_birthday_announcements(self):
        """Send birthday announcements to all employees."""
        today = date.today()
        birthday_employees = self.search([
            ('birthday', '!=', False),
        ])
        
        sent_count = 0
        for employee in birthday_employees:
            if employee.birthday and employee.birthday.month == today.month and employee.birthday.day == today.day:
                # Find the birthday mail template
                template = self.env.ref('automated_employee_announce.mail_template_employee_birthday', raise_if_not_found=False)
                if template and employee.work_email:
                    try:
                        template.send_mail(employee.id, force_send=True)
                        employee.message_post(body=_("Automated: Birthday announcement email sent."))
                        _logger.info(f"Birthday announcement sent for {employee.name}")
                        sent_count += 1
                    except Exception as e:
                        _logger.error(f"Failed to send birthday announcement for {employee.name}: {str(e)}")
        
        return sent_count
    
    def send_anniversary_announcements(self):
        """Send work anniversary announcements to all employees."""
        today = date.today()
        employees_with_hire_date = self.search([
            '|', '|',
            ('joining_date', '!=', False),
            ('hire_date', '!=', False),
            ('contract_date_start', '!=', False),
        ])
        
        sent_count = 0
        for employee in employees_with_hire_date:
            hire_date = employee._get_hire_date()
            if hire_date and hire_date.month == today.month and hire_date.day == today.day:
                # Find the anniversary mail template
                template = self.env.ref('automated_employee_announce.mail_template_employee_anniversary', raise_if_not_found=False)
                if template and employee.work_email:
                    try:
                        template.send_mail(employee.id, force_send=True)
                        employee.message_post(body=_("Automated: Work anniversary announcement email sent."))
                        _logger.info(f"Anniversary announcement sent for {employee.name}")
                        sent_count += 1
                    except Exception as e:
                        _logger.error(f"Failed to send anniversary announcement for {employee.name}: {str(e)}")
        
        return sent_count
    
    @api.model
    def cron_send_birthday_announcements(self):
        """Cron job to send birthday announcements."""
        sent_count = self.send_birthday_announcements()
        _logger.info(f"Birthday cron job completed. Sent {sent_count} emails.")
        return sent_count
        
    @api.model 
    def cron_send_anniversary_announcements(self):
        """Cron job to send anniversary announcements."""
        sent_count = self.send_anniversary_announcements()
        _logger.info(f"Anniversary cron job completed. Sent {sent_count} emails.")
        return sent_count
    
    def action_send_birthday_wish(self):
        """Manual action to send birthday wish."""
        self.ensure_one()
        if not self.birthday:
            raise UserError(_("Employee has no birthday set."))
            
        template = self.env.ref('automated_employee_announce.mail_template_employee_birthday', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
            self.message_post(body=_("Birthday wish sent manually."))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _("Birthday wish sent successfully!"),
                    'type': 'success',
                }
            }
        else:
            raise UserError(_("Birthday email template not found."))
    
    def action_send_anniversary_wish(self):
        """Manual action to send anniversary wish."""
        self.ensure_one()
        hire_date = self._get_hire_date()
        if not hire_date:
            raise UserError(_("Employee has no hire date set."))
            
        template = self.env.ref('automated_employee_announce.mail_template_employee_anniversary', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
            self.message_post(body=_("Anniversary wish sent manually."))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _("Anniversary wish sent successfully!"),
                    'type': 'success',
                }
            }
        else:
            raise UserError(_("Anniversary email template not found."))