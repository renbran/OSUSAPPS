from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
from datetime import date, timedelta

_logger = logging.getLogger(__name__)

class AutomatedMailRule(models.Model):
    _name = 'automated.mail.rule'
    _description = 'Automated Mail Rule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Rule Name', 
        required=True, 
        index=True, 
        help="Name of the automated mail rule.",
        tracking=True
    )
    model_id = fields.Many2one(
        'ir.model', 
        string='Target Model', 
        required=True, 
        ondelete='cascade', 
        help="Model to apply the rule on.",
        tracking=True
    )
    active = fields.Boolean(
        default=True, 
        string='Active',
        tracking=True
    )
    mail_template_id = fields.Many2one(
        'mail.template', 
        string='Mail Template', 
        required=True, 
        ondelete='cascade', 
        help="Mail template to use.",
        tracking=True
    )
    rule_type = fields.Selection([
        ('birthday', 'Birthday'),
        ('work_anniversary', 'Work Anniversary'),
    ], string='Rule Type', required=True, help="Type of automated mail.", tracking=True)
    
    last_run = fields.Date(string='Last Run', readonly=True, tracking=True)
    last_run_count = fields.Integer(string='Last Run Count', readonly=True, help="Number of emails sent in last run")
    total_sent = fields.Integer(string='Total Emails Sent', readonly=True, default=0)
    
    # Advanced options
    send_to_all_employees = fields.Boolean(
        string='Send to All Employees',
        default=False,
        help="If checked, sends announcement to all employees, not just the celebrant"
    )
    days_before = fields.Integer(
        string='Days Before',
        default=0,
        help="Send notification X days before the event (0 = on the day)"
    )
    
    @api.constrains('days_before')
    def _check_days_before(self):
        for record in self:
            if record.days_before < 0:
                raise ValidationError(_("Days before cannot be negative."))
    
    @api.constrains('model_id', 'rule_type')
    def _check_model_compatibility(self):
        for record in self:
            if record.rule_type in ['birthday', 'work_anniversary'] and record.model_id.model != 'hr.employee':
                raise ValidationError(_("Birthday and Work Anniversary rules can only be applied to HR Employee model."))

    def run_rule(self):
        """Run the automated mail rule for the selected type."""
        self.ensure_one()
        if not self.active:
            _logger.info(f"Rule {self.name} is inactive, skipping")
            return
            
        model = self.env[self.model_id.model]
        today = date.today()
        sent_count = 0
        
        try:
            if self.rule_type == 'birthday':
                sent_count = self._process_birthday_rule(model, today)
            elif self.rule_type == 'work_anniversary':
                sent_count = self._process_anniversary_rule(model, today)
                
            self.last_run = today
            self.last_run_count = sent_count
            self.total_sent += sent_count
            
            self.message_post(
                body=_("Rule executed successfully. Sent %s emails.") % sent_count,
                subject=_("Automated Mail Rule Executed")
            )
            
        except Exception as e:
            _logger.error(f"Failed to run rule {self.name}: {str(e)}")
            self.message_post(
                body=_("Rule execution failed: %s") % str(e),
                subject=_("Automated Mail Rule Failed")
            )
            raise UserError(_("Failed to execute rule: %s") % str(e))
    
    def _process_birthday_rule(self, model, today):
        """Process birthday rule logic."""
        target_date = today + timedelta(days=self.days_before)
        employees = model.search([('birthday', '!=', False)])
        sent_count = 0
        
        for emp in employees:
            if emp.birthday and emp.birthday.month == target_date.month and emp.birthday.day == target_date.day:
                if self.send_to_all_employees:
                    # Send to all employees
                    all_employees = model.search([('work_email', '!=', False)])
                    for recipient in all_employees:
                        self._send_mail_safe(recipient.id, emp)
                        sent_count += 1
                else:
                    # Send only to the birthday person
                    if emp.work_email:
                        self._send_mail_safe(emp.id, emp)
                        sent_count += 1
                        
        return sent_count
    
    def _process_anniversary_rule(self, model, today):
        """Process work anniversary rule logic."""
        target_date = today + timedelta(days=self.days_before)
        # Use multiple possible hire date fields for compatibility
        employees = model.search([
            '|', '|',
            ('joining_date', '!=', False),
            ('hire_date', '!=', False),
            ('contract_date_start', '!=', False),
            ('work_email', '!=', False)
        ])
        sent_count = 0
        
        for emp in employees:
            # Use helper method to get hire date
            anniversary_date = emp._get_hire_date() if hasattr(emp, '_get_hire_date') else (
                emp.joining_date or 
                getattr(emp, 'hire_date', False) or 
                getattr(emp, 'contract_date_start', False)
            )
            
            if anniversary_date and anniversary_date.month == target_date.month and anniversary_date.day == target_date.day:
                if self.send_to_all_employees:
                    # Send to all employees
                    all_employees = model.search([('work_email', '!=', False)])
                    for recipient in all_employees:
                        self._send_mail_safe(recipient.id, emp)
                        sent_count += 1
                else:
                    # Send only to the anniversary person
                    self._send_mail_safe(emp.id, emp)
                    sent_count += 1
                    
        return sent_count
    
    def _send_mail_safe(self, recipient_id, celebrant):
        """Safely send mail with error handling."""
        try:
            # Create context with celebrant info for template
            ctx = dict(self.env.context)
            ctx.update({
                'celebrant_name': celebrant.name,
                'celebrant_id': celebrant.id,
            })
            
            self.mail_template_id.with_context(ctx).send_mail(recipient_id, force_send=True)
            celebrant.message_post(
                body=_("Automated: %s email sent via rule '%s'") % (
                    dict(self._fields['rule_type'].selection).get(self.rule_type),
                    self.name
                )
            )
            _logger.info(f"Mail sent successfully for {celebrant.name} via rule {self.name}")
            
        except Exception as e:
            _logger.error(f"Failed to send mail for {celebrant.name}: {str(e)}")
            raise

    @api.model
    def run_all_active_rules(self):
        """Run all active rules. Called by cron job."""
        rules = self.search([('active', '=', True)])
        total_sent = 0
        
        for rule in rules:
            try:
                rule.run_rule()
                total_sent += rule.last_run_count or 0
            except Exception as e:
                _logger.error(f"AutomatedMailRule {rule.name} failed: {e}")
                continue
                
        _logger.info(f"Automated mail rules completed. Total emails sent: {total_sent}")
        return total_sent
    
    def action_test_rule(self):
        """Test the rule manually."""
        self.ensure_one()
        try:
            self.run_rule()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _("Rule executed successfully! Sent %s emails.") % (self.last_run_count or 0),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _("Rule execution failed: %s") % str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }