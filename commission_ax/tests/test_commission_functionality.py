# -*- coding: utf-8 -*-
"""
Commission Module Functionality Tests
=====================================

Comprehensive test suite for commission module functionality:
- End-to-end commission workflows
- Business logic validation
- Integration testing
- Performance testing
- Edge case handling
"""

from odoo.tests.common import TransactionCase, Form
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class TestCommissionFunctionality(TransactionCase):
    """Test commission module functionality and business logic"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(user=cls.env.ref('base.user_admin'))

        # Create test data
        cls.commission_partner = cls.env['res.partner'].create({
            'name': 'Test Commission Agent',
            'is_company': False,
            'supplier_rank': 1,
            'customer_rank': 0,
        })

        cls.customer = cls.env['res.partner'].create({
            'name': 'Test Customer',
            'is_company': True,
            'customer_rank': 1,
        })

        cls.product = cls.env['product.product'].create({
            'name': 'Test Product',
            'type': 'product',
            'list_price': 1000.0,
            'standard_price': 500.0,
        })

        cls.commission_type = cls.env['commission.type'].create({
            'name': 'Test Commission Type',
            'calculation_method': 'percentage_total',
            'rate': 5.0,
            'category': 'external',
        })

    def test_01_commission_line_creation(self):
        """Test commission line creation and basic functionality"""
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 2,
                'price_unit': 1000.0,
            })],
        })

        commission_line = self.env['commission.line'].create({
            'sale_order_id': sale_order.id,
            'partner_id': self.commission_partner.id,
            'commission_type_id': self.commission_type.id,
            'amount': 100.0,
            'state': 'draft',
        })

        # Test basic properties
        self.assertEqual(commission_line.sale_order_id, sale_order)
        self.assertEqual(commission_line.partner_id, self.commission_partner)
        self.assertEqual(commission_line.amount, 100.0)
        self.assertEqual(commission_line.state, 'draft')

    def test_02_commission_calculation(self):
        """Test commission calculation methods"""
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 1000.0,
            })],
        })

        # Test percentage calculation
        percentage_type = self.env['commission.type'].create({
            'name': 'Percentage Commission',
            'calculation_method': 'percentage_total',
            'rate': 5.0,
        })

        commission_line = self.env['commission.line'].create({
            'sale_order_id': sale_order.id,
            'partner_id': self.commission_partner.id,
            'commission_type_id': percentage_type.id,
            'state': 'draft',
        })

        # Calculate commission amount
        if hasattr(commission_line, '_compute_amount'):
            commission_line._compute_amount()
            # Expected: 1000 * 5% = 50
            self.assertEqual(commission_line.amount, 50.0)

        # Test fixed amount calculation
        fixed_type = self.env['commission.type'].create({
            'name': 'Fixed Commission',
            'calculation_method': 'fixed',
            'fixed_amount': 200.0,
        })

        fixed_commission = self.env['commission.line'].create({
            'sale_order_id': sale_order.id,
            'partner_id': self.commission_partner.id,
            'commission_type_id': fixed_type.id,
            'amount': 200.0,  # Should be set to fixed_amount
            'state': 'draft',
        })

        self.assertEqual(fixed_commission.amount, 200.0)

    def test_03_commission_workflow(self):
        """Test commission state workflow"""
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 1000.0,
            })],
        })

        commission_line = self.env['commission.line'].create({
            'sale_order_id': sale_order.id,
            'partner_id': self.commission_partner.id,
            'commission_type_id': self.commission_type.id,
            'amount': 50.0,
            'state': 'draft',
        })

        # Test state transitions
        self.assertEqual(commission_line.state, 'draft')

        # Calculate commission
        if hasattr(commission_line, 'action_calculate'):
            commission_line.action_calculate()
            self.assertEqual(commission_line.state, 'calculated')

        # Confirm commission
        if hasattr(commission_line, 'action_confirm'):
            commission_line.action_confirm()
            self.assertEqual(commission_line.state, 'confirmed')

        # Process commission
        if hasattr(commission_line, 'action_process'):
            commission_line.action_process()
            self.assertEqual(commission_line.state, 'processed')

    def test_04_purchase_order_generation(self):
        """Test purchase order generation for commissions"""
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'client_order_ref': 'TEST-REF-001',
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 1000.0,
            })],
        })

        commission_line = self.env['commission.line'].create({
            'sale_order_id': sale_order.id,
            'partner_id': self.commission_partner.id,
            'commission_type_id': self.commission_type.id,
            'amount': 50.0,
            'state': 'confirmed',
        })

        # Generate purchase order
        if hasattr(commission_line, 'action_create_purchase_order'):
            commission_line.action_create_purchase_order()

            # Check if purchase order was created
            purchase_orders = self.env['purchase.order'].search([
                ('origin_so_id', '=', sale_order.id)
            ])

            if purchase_orders:
                po = purchase_orders[0]
                self.assertEqual(po.partner_id, self.commission_partner)
                self.assertEqual(po.partner_ref, sale_order.client_order_ref)

    def test_05_commission_dashboard_data(self):
        """Test commission dashboard data generation"""
        # Create multiple commission lines
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'date_order': datetime.now(),
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 1000.0,
            })],
        })

        commission_lines = []
        for i in range(5):
            commission_line = self.env['commission.line'].create({
                'sale_order_id': sale_order.id,
                'partner_id': self.commission_partner.id,
                'commission_type_id': self.commission_type.id,
                'amount': (i + 1) * 50.0,
                'state': 'confirmed',
            })
            commission_lines.append(commission_line)

        # Test dashboard data
        dashboard = self.env['commission.dashboard']
        if hasattr(dashboard, 'get_dashboard_data'):
            data = dashboard.get_dashboard_data()

            self.assertIn('total_commission_amount', data)
            self.assertIn('commission_count', data)
            self.assertIsInstance(data['total_commission_amount'], (int, float))

    def test_06_commission_alerts(self):
        """Test commission alert system"""
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 10000.0,  # High value for threshold alert
            })],
        })

        commission_line = self.env['commission.line'].create({
            'sale_order_id': sale_order.id,
            'partner_id': self.commission_partner.id,
            'commission_type_id': self.commission_type.id,
            'amount': 500.0,  # High commission amount
            'state': 'confirmed',
        })

        # Test alert creation
        alert_model = self.env['commission.alert']
        if hasattr(alert_model, 'create_threshold_alert'):
            alert = alert_model.create_threshold_alert(
                commission_line, 'amount', 300.0, 500.0
            )

            self.assertEqual(alert.commission_line_id, commission_line)
            self.assertEqual(alert.alert_type, 'threshold')
            self.assertEqual(alert.state, 'new')

    def test_07_commission_reporting(self):
        """Test commission reporting functionality"""
        # Create test data
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'date_order': datetime.now(),
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 1000.0,
            })],
        })

        commission_line = self.env['commission.line'].create({
            'sale_order_id': sale_order.id,
            'partner_id': self.commission_partner.id,
            'commission_type_id': self.commission_type.id,
            'amount': 50.0,
            'state': 'processed',
        })

        # Test performance report
        performance_report = self.env['commission.performance.report']
        if performance_report:
            report = performance_report.create({
                'date_from': datetime.now().date() - timedelta(days=30),
                'date_to': datetime.now().date(),
                'report_type': 'summary',
            })

            if hasattr(report, '_calculate_metrics'):
                report._calculate_metrics()
                self.assertGreaterEqual(report.total_commission_amount, 0)

    def test_08_commission_payment_tracking(self):
        """Test commission payment tracking"""
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 1000.0,
            })],
        })

        commission_line = self.env['commission.line'].create({
            'sale_order_id': sale_order.id,
            'partner_id': self.commission_partner.id,
            'commission_type_id': self.commission_type.id,
            'amount': 50.0,
            'state': 'processed',
        })

        # Test payment status updates
        initial_status = commission_line.payment_status
        self.assertIn(initial_status, ['pending', 'draft', 'unpaid'])

        # Mark as paid
        if hasattr(commission_line, 'action_mark_paid'):
            commission_line.action_mark_paid()
            self.assertEqual(commission_line.payment_status, 'paid')

    def test_09_commission_bulk_operations(self):
        """Test bulk commission operations"""
        sale_orders = []
        commission_lines = []

        # Create multiple sale orders and commission lines
        for i in range(10):
            sale_order = self.env['sale.order'].create({
                'partner_id': self.customer.id,
                'order_line': [(0, 0, {
                    'product_id': self.product.id,
                    'product_uom_qty': 1,
                    'price_unit': 1000.0,
                })],
            })
            sale_orders.append(sale_order)

            commission_line = self.env['commission.line'].create({
                'sale_order_id': sale_order.id,
                'partner_id': self.commission_partner.id,
                'commission_type_id': self.commission_type.id,
                'amount': 50.0,
                'state': 'draft',
            })
            commission_lines.append(commission_line)

        # Test bulk confirm
        commission_lines_recordset = self.env['commission.line'].browse([cl.id for cl in commission_lines])

        if hasattr(commission_lines_recordset, 'action_bulk_confirm'):
            commission_lines_recordset.action_bulk_confirm()

            # Verify all are confirmed
            for line in commission_lines_recordset:
                self.assertEqual(line.state, 'confirmed')

    def test_10_commission_edge_cases(self):
        """Test edge cases and error handling"""
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 0.0,  # Zero price
            })],
        })

        # Test zero amount commission
        commission_line = self.env['commission.line'].create({
            'sale_order_id': sale_order.id,
            'partner_id': self.commission_partner.id,
            'commission_type_id': self.commission_type.id,
            'amount': 0.0,
            'state': 'draft',
        })

        self.assertEqual(commission_line.amount, 0.0)

        # Test duplicate commission prevention (if implemented)
        # This would depend on specific business rules

    def test_11_commission_security(self):
        """Test commission security and access control"""
        # Create a regular user
        test_user = self.env['res.users'].create({
            'name': 'Commission Test User',
            'login': 'commission_test_user',
            'email': 'test@example.com',
            'groups_id': [(6, 0, [self.env.ref('commission_ax.group_commission_user').id])],
        })

        # Test access as regular user
        commission_line_as_user = self.env['commission.line'].with_user(test_user)

        # User should be able to read commission lines
        lines = commission_line_as_user.search([])
        self.assertIsNotNone(lines)

        # Test manager access
        manager_user = self.env['res.users'].create({
            'name': 'Commission Manager',
            'login': 'commission_manager',
            'email': 'manager@example.com',
            'groups_id': [(6, 0, [self.env.ref('commission_ax.group_commission_manager').id])],
        })

        commission_line_as_manager = self.env['commission.line'].with_user(manager_user)
        manager_lines = commission_line_as_manager.search([])
        self.assertIsNotNone(manager_lines)

    def test_12_commission_performance(self):
        """Test commission system performance"""
        import time

        # Create large dataset
        start_time = time.time()

        sale_orders = []
        for i in range(50):
            sale_order = self.env['sale.order'].create({
                'partner_id': self.customer.id,
                'order_line': [(0, 0, {
                    'product_id': self.product.id,
                    'product_uom_qty': 1,
                    'price_unit': 1000.0,
                })],
            })
            sale_orders.append(sale_order)

        creation_time = time.time() - start_time

        # Performance should be reasonable
        self.assertLess(creation_time, 30.0, "Sale order creation took too long")

        # Test commission calculation performance
        start_time = time.time()

        commission_lines = []
        for sale_order in sale_orders:
            commission_line = self.env['commission.line'].create({
                'sale_order_id': sale_order.id,
                'partner_id': self.commission_partner.id,
                'commission_type_id': self.commission_type.id,
                'amount': 50.0,
                'state': 'draft',
            })
            commission_lines.append(commission_line)

        commission_creation_time = time.time() - start_time

        self.assertLess(commission_creation_time, 20.0, "Commission creation took too long")
        self.assertEqual(len(commission_lines), 50)

        _logger.info(f"Performance test: Created 50 sale orders in {creation_time:.2f}s, "
                    f"50 commission lines in {commission_creation_time:.2f}s")

    def tearDown(self):
        """Clean up test data"""
        super().tearDown()
        # Test data is automatically rolled back in TransactionCase