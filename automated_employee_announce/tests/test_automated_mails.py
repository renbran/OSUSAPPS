from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date, timedelta

class TestAutomatedEmployeeAnnounce(TransactionCase):
    def setUp(self):
        super().setUp()
        self.env = self.env(context=dict(self.env.context, mail_notify_force_send=True))
        self.hr_employee = self.env['hr.employee'].create({
            'name': 'Test Employee',
            'work_email': 'test.employee@example.com',
            'birthday': date.today(),
            'hire_date': date.today() - timedelta(days=365),
        })
        self.partner = self.env['res.partner'].create({'name': 'Test Partner'})
        self.buyer = self.env['res.partner'].create({'name': 'Test Buyer'})
        self.project = self.env['project.project'].create({'name': 'Test Project'})
        self.unit = self.env['product.product'].create({'name': 'Test Unit'})
        self.agent = self.env['res.partner'].create({'name': 'Agent 1', 'email': 'agent1@example.com'})
        self.sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'buyer_id': self.buyer.id if hasattr(self.env['sale.order'], 'buyer_id') else False,
            'project_id': self.project.id if hasattr(self.env['sale.order'], 'project_id') else False,
            'unit_id': self.unit.id if hasattr(self.env['sale.order'], 'unit_id') else False,
            'price_unit': 100000,
            'agent1_partner_id': self.agent.id,
            'booking_date': date.today() - timedelta(days=31),
        })

    def test_birthday_announcement_mail(self):
        rule = self.env['automated.mail.rule'].create({
            'name': 'Birthday Rule',
            'model_id': self.env['ir.model']._get_id('hr.employee'),
            'mail_template_id': self.env.ref('automated_employee_announce.mail_template_employee_birthday').id,
            'rule_type': 'birthday',
        })
        rule.run_rule()
        # Check mail sent in mail.message
        messages = self.hr_employee.message_ids.filtered(lambda m: 'birthday' in (m.subject or '').lower())
        self.assertTrue(messages, 'Birthday announcement mail not sent!')

    def test_saleorder_invoiced_mail(self):
        # Simulate invoice creation
        self.sale_order.state = 'sale'
        self.sale_order._create_invoices()
        messages = self.sale_order.message_ids.filtered(lambda m: 'invoiced' in (m.body or '').lower())
        self.assertTrue(messages, 'Sale order invoiced mail not sent!')

    def test_payment_initiated_mail(self):
        # Simulate payment on invoice
        self.sale_order.state = 'sale'
        invoice = self.sale_order._create_invoices()
        move = invoice and invoice[0] or False
        if move:
            move._message_post_after_payment(None, move)
            messages = self.sale_order.message_ids.filtered(lambda m: 'payment receipt' in (m.body or '').lower())
            self.assertTrue(messages, 'Payment initiated mail not sent!')

    def test_deal_status_reminder_mail(self):
        # Simulate cron job
        self.sale_order.state = 'draft'
        self.env['sale.order'].send_deal_status_reminders()
        messages = self.sale_order.message_ids.filtered(lambda m: 'deal status reminder' in (m.body or '').lower())
        self.assertTrue(messages, 'Deal status reminder mail not sent!')

    def test_work_anniversary_announcement_mail(self):
        """Test work anniversary announcement mail rule."""
        rule = self.env['automated.mail.rule'].create({
            'name': 'Anniversary Rule',
            'model_id': self.env['ir.model']._get_id('hr.employee'),
            'mail_template_id': self.env.ref('automated_employee_announce.mail_template_employee_anniversary').id,
            'rule_type': 'work_anniversary',
        })
        rule.run_rule()
        # Check mail sent in mail.message
        messages = self.hr_employee.message_ids.filtered(lambda m: 'anniversary' in (m.subject or '').lower())
        self.assertTrue(messages, 'Work anniversary announcement mail not sent!')

    def test_automated_mail_rule_constraints(self):
        """Test validation constraints on automated mail rules."""
        # Test negative days_before
        with self.assertRaises(ValidationError):
            self.env['automated.mail.rule'].create({
                'name': 'Invalid Rule',
                'model_id': self.env['ir.model']._get_id('hr.employee'),
                'mail_template_id': self.env.ref('automated_employee_announce.mail_template_employee_birthday').id,
                'rule_type': 'birthday',
                'days_before': -1,
            })

    def test_employee_years_of_service(self):
        """Test years of service computation."""
        # Set a specific joining date
        from datetime import date, timedelta
        self.hr_employee.write({
            'joining_date': date.today() - timedelta(days=730)  # 2 years ago
        })
        self.hr_employee._compute_years_of_service()
        self.assertEqual(self.hr_employee.years_of_service, 2, 'Years of service calculation is incorrect!')

    def test_manual_birthday_wish(self):
        """Test manual birthday wish action."""
        result = self.hr_employee.action_send_birthday_wish()
        self.assertEqual(result.get('type'), 'ir.actions.client', 'Manual birthday wish action failed!')

    def test_manual_anniversary_wish(self):
        """Test manual anniversary wish action."""
        self.hr_employee.joining_date = date.today() - timedelta(days=365)
        result = self.hr_employee.action_send_anniversary_wish()
        self.assertEqual(result.get('type'), 'ir.actions.client', 'Manual anniversary wish action failed!')

    def test_run_all_active_rules(self):
        """Test running all active rules."""
        # Create some rules
        birthday_rule = self.env['automated.mail.rule'].create({
            'name': 'Test Birthday Rule',
            'model_id': self.env['ir.model']._get_id('hr.employee'),
            'mail_template_id': self.env.ref('automated_employee_announce.mail_template_employee_birthday').id,
            'rule_type': 'birthday',
            'active': True,
        })
        
        anniversary_rule = self.env['automated.mail.rule'].create({
            'name': 'Test Anniversary Rule',
            'model_id': self.env['ir.model']._get_id('hr.employee'),
            'mail_template_id': self.env.ref('automated_employee_announce.mail_template_employee_anniversary').id,
            'rule_type': 'work_anniversary',
            'active': True,
        })
        
        # Run all active rules
        total_sent = self.env['automated.mail.rule'].run_all_active_rules()
        self.assertIsInstance(total_sent, int, 'Run all active rules should return an integer!')
        
        # Check that rules were executed
        self.assertIsNotNone(birthday_rule.last_run, 'Birthday rule was not executed!')
        self.assertIsNotNone(anniversary_rule.last_run, 'Anniversary rule was not executed!')
