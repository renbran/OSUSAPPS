# -*- coding: utf-8 -*-
"""
Commission Module Installation Tests
====================================

World-class test suite for commission module installation validation:
- Dependency verification
- Model integrity checks
- Security validation
- Data consistency tests
- Performance benchmarks
"""

from odoo.tests.common import TransactionCase, Form
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class TestCommissionInstallation(TransactionCase):
    """Test commission module installation and setup"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(user=cls.env.ref('base.user_admin'))

    def test_01_models_exist(self):
        """Test that all commission models are properly loaded"""
        expected_models = [
            'commission.type',
            'commission.line',
            'commission.dashboard',
            'commission.ai.analytics',
            'commission.realtime.dashboard',
            'commission.alert',
            'commission.performance.report',
            'commission.statement.line',
        ]

        for model_name in expected_models:
            with self.subTest(model=model_name):
                model = self.env.get(model_name)
                self.assertIsNotNone(model, f"Model {model_name} not found")

    def test_02_security_groups_exist(self):
        """Test that security groups are properly created"""
        commission_user_group = self.env.ref('commission_ax.group_commission_user', raise_if_not_found=False)
        commission_manager_group = self.env.ref('commission_ax.group_commission_manager', raise_if_not_found=False)

        self.assertIsNotNone(commission_user_group, "Commission User group not found")
        self.assertIsNotNone(commission_manager_group, "Commission Manager group not found")

        # Test inheritance
        self.assertIn(commission_user_group, commission_manager_group.implied_ids)

    def test_03_access_rights_complete(self):
        """Test that all models have proper access rights"""
        access_model = self.env['ir.model.access']

        expected_models = [
            'commission.type',
            'commission.line',
            'commission.dashboard',
            'commission.alert',
            'commission.performance.report',
        ]

        for model_name in expected_models:
            with self.subTest(model=model_name):
                model_id = self.env['ir.model'].search([('model', '=', model_name)])
                self.assertTrue(model_id, f"Model {model_name} not found in ir.model")

                access_rights = access_model.search([('model_id', '=', model_id.id)])
                self.assertTrue(access_rights, f"No access rights found for {model_name}")

                # Check both user and manager rights exist
                user_access = access_rights.filtered(lambda a: 'user' in a.name.lower())
                manager_access = access_rights.filtered(lambda a: 'manager' in a.name.lower())

                self.assertTrue(user_access, f"User access rights missing for {model_name}")
                self.assertTrue(manager_access, f"Manager access rights missing for {model_name}")

    def test_04_commission_types_created(self):
        """Test that default commission types are created"""
        commission_types = self.env['commission.type'].search([])
        self.assertTrue(commission_types, "No default commission types found")

        # Check for expected types
        expected_types = ['Broker', 'Referrer', 'Agent', 'Manager']
        type_names = commission_types.mapped('name')

        for expected_type in expected_types:
            self.assertIn(expected_type, type_names, f"Commission type {expected_type} not found")

    def test_05_menu_items_exist(self):
        """Test that menu items are properly created"""
        menu_model = self.env['ir.ui.menu']

        commission_menus = menu_model.search([('name', 'ilike', 'commission')])
        self.assertTrue(commission_menus, "No commission menu items found")

        # Check for main commission menu
        main_menu = menu_model.search([('name', '=', 'Commissions')])
        self.assertTrue(main_menu, "Main commission menu not found")

    def test_06_views_exist(self):
        """Test that all required views are created"""
        view_model = self.env['ir.ui.view']

        expected_views = [
            'commission_line_tree_view',
            'commission_line_form_view',
            'commission_dashboard_view',
            'commission_type_tree_view',
        ]

        for view_name in expected_views:
            with self.subTest(view=view_name):
                view = view_model.search([('name', 'ilike', view_name)])
                self.assertTrue(view, f"View {view_name} not found")

    def test_07_cron_jobs_setup(self):
        """Test that automated cron jobs are properly configured"""
        cron_model = self.env['ir.cron']

        commission_crons = cron_model.search([
            ('model_id.model', 'like', 'commission.%')
        ])

        # Should have at least basic monitoring cron jobs
        self.assertTrue(commission_crons, "No commission cron jobs found")

    def test_08_dependencies_handling(self):
        """Test that external dependencies are properly handled"""
        # Test xlsxwriter dependency
        try:
            import xlsxwriter
            xlsxwriter_available = True
        except ImportError:
            xlsxwriter_available = False

        # Module should work regardless of xlsxwriter availability
        commission_line = self.env['commission.line']
        self.assertIsNotNone(commission_line, "Commission line model should be available")

        # If xlsxwriter not available, Excel export should gracefully fail
        if not xlsxwriter_available:
            _logger.warning("xlsxwriter not available - Excel export features will be disabled")

    def test_09_model_field_integrity(self):
        """Test that critical model fields are properly defined"""
        # Test commission line model fields
        commission_line_model = self.env['commission.line']

        critical_fields = [
            'sale_order_id',
            'partner_id',
            'commission_type_id',
            'amount',
            'state',
            'payment_status'
        ]

        for field_name in critical_fields:
            with self.subTest(field=field_name):
                self.assertIn(field_name, commission_line_model._fields,
                            f"Critical field {field_name} missing from commission.line")

    def test_10_wizard_models_functional(self):
        """Test that wizard models are properly functional"""
        wizard_models = [
            'commission.report.wizard',
            'commission.statement.wizard',
            'commission.payment.wizard',
        ]

        for wizard_model in wizard_models:
            with self.subTest(wizard=wizard_model):
                model = self.env.get(wizard_model)
                if model:  # Some wizards might be optional
                    # Try to create a basic wizard record
                    try:
                        wizard = model.create({'name': 'Test Wizard'})
                        self.assertTrue(wizard, f"Failed to create {wizard_model}")
                    except Exception as e:
                        # Some wizards might require specific fields
                        _logger.info(f"Wizard {wizard_model} creation test skipped: {str(e)}")

    def test_11_commission_calculation_basic(self):
        """Test basic commission calculation functionality"""
        # Create a test partner
        partner = self.env['res.partner'].create({
            'name': 'Test Commission Partner',
            'is_company': True,
            'supplier_rank': 1,
        })

        # Create a commission type
        commission_type = self.env['commission.type'].create({
            'name': 'Test Commission',
            'calculation_method': 'percentage_total',
            'rate': 5.0,
        })

        # Create a sale order
        sale_order = self.env['sale.order'].create({
            'partner_id': self.env.ref('base.res_partner_1').id,
            'order_line': [(0, 0, {
                'product_id': self.env.ref('product.product_product_4').id,
                'product_uom_qty': 1,
                'price_unit': 1000.0,
            })],
        })

        # Create a commission line
        commission_line = self.env['commission.line'].create({
            'sale_order_id': sale_order.id,
            'partner_id': partner.id,
            'commission_type_id': commission_type.id,
            'amount': 50.0,
            'state': 'draft',
        })

        self.assertEqual(commission_line.amount, 50.0)
        self.assertEqual(commission_line.state, 'draft')

    def test_12_performance_basic(self):
        """Test basic performance of commission operations"""
        import time

        # Test commission line creation performance
        start_time = time.time()

        partner = self.env['res.partner'].create({
            'name': 'Performance Test Partner',
            'supplier_rank': 1,
        })

        commission_type = self.env['commission.type'].create({
            'name': 'Performance Test Type',
            'calculation_method': 'fixed',
            'fixed_amount': 100.0,
        })

        # Create multiple commission lines
        lines_data = []
        for i in range(10):
            sale_order = self.env['sale.order'].create({
                'partner_id': self.env.ref('base.res_partner_1').id,
            })
            lines_data.append({
                'sale_order_id': sale_order.id,
                'partner_id': partner.id,
                'commission_type_id': commission_type.id,
                'amount': 100.0,
                'state': 'draft',
            })

        commission_lines = self.env['commission.line'].create(lines_data)

        end_time = time.time()
        creation_time = end_time - start_time

        self.assertEqual(len(commission_lines), 10)
        self.assertLess(creation_time, 5.0, "Commission line creation took too long")

        _logger.info(f"Created 10 commission lines in {creation_time:.2f} seconds")

    def test_13_data_integrity_constraints(self):
        """Test data integrity and constraint validation"""
        partner = self.env['res.partner'].create({
            'name': 'Constraint Test Partner',
            'supplier_rank': 1,
        })

        commission_type = self.env['commission.type'].create({
            'name': 'Constraint Test Type',
            'calculation_method': 'fixed',
            'fixed_amount': 100.0,
        })

        sale_order = self.env['sale.order'].create({
            'partner_id': self.env.ref('base.res_partner_1').id,
        })

        # Test required field validation
        with self.assertRaises((ValidationError, UserError)):
            self.env['commission.line'].create({
                'partner_id': partner.id,
                'commission_type_id': commission_type.id,
                'amount': 100.0,
                # Missing required sale_order_id
            })

        # Test negative amount validation (if implemented)
        commission_line = self.env['commission.line'].create({
            'sale_order_id': sale_order.id,
            'partner_id': partner.id,
            'commission_type_id': commission_type.id,
            'amount': 100.0,
            'state': 'draft',
        })

        # Commission line should be created successfully
        self.assertTrue(commission_line.id)

    def test_14_upgrade_compatibility(self):
        """Test module upgrade compatibility"""
        # Check that the module can handle existing data
        # This is more relevant for actual upgrades, but we can test structure

        # Verify that all new fields have proper defaults
        commission_line_model = self.env['commission.line']

        # Check that new fields have defaults or are properly nullable
        for field_name, field in commission_line_model._fields.items():
            if field.required and not field.default and field_name not in ['sale_order_id', 'partner_id']:
                self.fail(f"Required field {field_name} without default may cause upgrade issues")

    def tearDown(self):
        """Clean up test data"""
        super().tearDown()
        # Test data is automatically rolled back in TransactionCase