# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError, UserError


@tagged('post_install', '-at_install')
class TestOrderNetCommissionWorkflow(TransactionCase):
    """Test Order Net Commission Workflow"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Get security groups
        cls.doc_officer_group = cls.env.ref('order_net_commission.group_documentation_officer')
        cls.comm_analyst_group = cls.env.ref('order_net_commission.group_commission_analyst')
        cls.approver_group = cls.env.ref('order_net_commission.group_sales_approver')
        
        # Create test users
        cls.doc_officer = cls.env['res.users'].create({
            'name': 'Documentation Officer',
            'login': 'doc_officer',
            'email': 'doc@osus.test',
            'groups_id': [(4, cls.doc_officer_group.id)]
        })
        
        cls.comm_analyst = cls.env['res.users'].create({
            'name': 'Commission Analyst',
            'login': 'comm_analyst',
            'email': 'analyst@osus.test',
            'groups_id': [(4, cls.comm_analyst_group.id)]
        })
        
        cls.approver = cls.env['res.users'].create({
            'name': 'Sales Approver',
            'login': 'approver',
            'email': 'approver@osus.test',
            'groups_id': [(4, cls.approver_group.id)]
        })
        
        # Create test partner and product
        cls.partner = cls.env['res.partner'].create({
            'name': 'OSUS Test Customer',
            'email': 'customer@osus.test'
        })
        
        cls.product = cls.env['product.product'].create({
            'name': 'OSUS Test Product',
            'type': 'service',
            'list_price': 1000.0,
        })

    def _create_test_order(self):
        """Create a test sales order"""
        return self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 1000,
            })],
            'total_internal': 400,
            'total_external': 200,
        })

    def test_01_net_commission_calculation(self):
        """Test net commission calculation"""
        order = self._create_test_order()
        
        # Test commission calculation: 1000 - (400 - 200) = 800
        self.assertEqual(order.net_commission, 800)
        
        # Update costs and verify recalculation
        order.write({
            'total_internal': 500,
            'total_external': 100
        })
        self.assertEqual(order.net_commission, 600)

    def test_02_workflow_documentation_stage(self):
        """Test documentation stage workflow"""
        order = self._create_test_order()
        self.assertEqual(order.state, 'draft')
        
        # Test with documentation officer
        order.with_user(self.doc_officer).action_set_documentation()
        self.assertEqual(order.state, 'documentation')
        self.assertEqual(order.documentation_user_id, self.doc_officer)
        self.assertTrue(order.documentation_date)
        
        # Test unauthorized access
        order2 = self._create_test_order()
        with self.assertRaises(UserError):
            order2.with_user(self.comm_analyst).action_set_documentation()

    def test_03_workflow_commission_stage(self):
        """Test commission stage workflow"""
        order = self._create_test_order()
        
        # Move to documentation first
        order.with_user(self.doc_officer).action_set_documentation()
        
        # Test with commission analyst
        order.with_user(self.comm_analyst).action_set_commission()
        self.assertEqual(order.state, 'commission')
        self.assertEqual(order.commission_user_id, self.comm_analyst)
        self.assertTrue(order.commission_date)
        
        # Test unauthorized access
        order2 = self._create_test_order()
        order2.with_user(self.doc_officer).action_set_documentation()
        with self.assertRaises(UserError):
            order2.with_user(self.doc_officer).action_set_commission()

    def test_04_workflow_approval_stage(self):
        """Test final approval stage"""
        order = self._create_test_order()
        
        # Move through all stages
        order.with_user(self.doc_officer).action_set_documentation()
        order.with_user(self.comm_analyst).action_set_commission()
        
        # Test final approval
        order.with_user(self.approver).action_approve_commission()
        self.assertEqual(order.state, 'sale')
        self.assertEqual(order.approver_user_id, self.approver)

    def test_05_workflow_permissions(self):
        """Test workflow button permissions"""
        order = self._create_test_order()
        
        # Test permission computation for documentation officer
        order_doc = order.with_user(self.doc_officer)
        self.assertTrue(order_doc.can_set_documentation)
        self.assertFalse(order_doc.can_set_commission)
        self.assertFalse(order_doc.can_approve_commission)
        
        # Move to documentation stage
        order.with_user(self.doc_officer).action_set_documentation()
        
        # Test permission computation for commission analyst
        order_comm = order.with_user(self.comm_analyst)
        self.assertFalse(order_comm.can_set_documentation)
        self.assertTrue(order_comm.can_set_commission)
        self.assertFalse(order_comm.can_approve_commission)
        
        # Move to commission stage
        order.with_user(self.comm_analyst).action_set_commission()
        
        # Test permission computation for approver
        order_app = order.with_user(self.approver)
        self.assertFalse(order_app.can_set_documentation)
        self.assertFalse(order_app.can_set_commission)
        self.assertTrue(order_app.can_approve_commission)

    def test_06_validation_constraints(self):
        """Test validation constraints"""
        order = self._create_test_order()
        
        # Test negative internal costs
        with self.assertRaises(ValidationError):
            order.write({'total_internal': -100})
        
        # Test negative external costs
        with self.assertRaises(ValidationError):
            order.write({'total_external': -50})

    def test_07_wrong_state_transitions(self):
        """Test invalid state transitions"""
        order = self._create_test_order()
        
        # Try to skip documentation stage
        with self.assertRaises(UserError):
            order.with_user(self.comm_analyst).action_set_commission()
        
        # Try to skip commission stage
        order.with_user(self.doc_officer).action_set_documentation()
        with self.assertRaises(UserError):
            order.with_user(self.approver).action_approve_commission()

    def test_08_workflow_tracking(self):
        """Test workflow tracking information"""
        order = self._create_test_order()
        
        # Initial state
        self.assertFalse(order.documentation_date)
        self.assertFalse(order.commission_date)
        self.assertFalse(order.documentation_user_id)
        self.assertFalse(order.commission_user_id)
        self.assertFalse(order.approver_user_id)
        
        # Documentation stage
        order.with_user(self.doc_officer).action_set_documentation()
        self.assertTrue(order.documentation_date)
        self.assertEqual(order.documentation_user_id, self.doc_officer)
        
        # Commission stage
        order.with_user(self.comm_analyst).action_set_commission()
        self.assertTrue(order.commission_date)
        self.assertEqual(order.commission_user_id, self.comm_analyst)
        
        # Approval stage
        order.with_user(self.approver).action_approve_commission()
        self.assertEqual(order.approver_user_id, self.approver)

    def test_09_full_workflow_integration(self):
        """Test complete workflow integration"""
        order = self._create_test_order()
        
        # Verify initial state and commission
        self.assertEqual(order.state, 'draft')
        self.assertEqual(order.net_commission, 800)
        
        # Complete workflow
        order.with_user(self.doc_officer).action_set_documentation()
        self.assertEqual(order.state, 'documentation')
        
        order.with_user(self.comm_analyst).action_set_commission()
        self.assertEqual(order.state, 'commission')
        
        order.with_user(self.approver).action_approve_commission()
        self.assertEqual(order.state, 'sale')
        
        # Verify all tracking information is recorded
        self.assertTrue(order.documentation_date)
        self.assertTrue(order.commission_date)
        self.assertEqual(order.documentation_user_id, self.doc_officer)
        self.assertEqual(order.commission_user_id, self.comm_analyst)
        self.assertEqual(order.approver_user_id, self.approver)

    def test_10_commission_with_zero_costs(self):
        """Test commission calculation with zero costs"""
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 1000,
            })],
            'total_internal': 0,
            'total_external': 0,
        })
        
        # Commission should equal total amount when no costs
        self.assertEqual(order.net_commission, 1000)

    def test_11_multiple_orders_workflow(self):
        """Test multiple orders in different workflow stages"""
        orders = []
        
        # Create multiple orders
        for i in range(3):
            order = self._create_test_order()
            orders.append(order)
        
        # Put orders in different stages
        orders[0].with_user(self.doc_officer).action_set_documentation()
        
        orders[1].with_user(self.doc_officer).action_set_documentation()
        orders[1].with_user(self.comm_analyst).action_set_commission()
        
        orders[2].with_user(self.doc_officer).action_set_documentation()
        orders[2].with_user(self.comm_analyst).action_set_commission()
        orders[2].with_user(self.approver).action_approve_commission()
        
        # Verify states
        self.assertEqual(orders[0].state, 'documentation')
        self.assertEqual(orders[1].state, 'commission')
        self.assertEqual(orders[2].state, 'sale')

    def test_12_commission_calculation_edge_cases(self):
        """Test commission calculation edge cases"""
        # Case 1: External costs higher than internal
        order1 = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 1000,
            })],
            'total_internal': 200,
            'total_external': 400,
        })
        # Commission = 1000 - (200 - 400) = 1000 + 200 = 1200
        self.assertEqual(order1.net_commission, 1200)
        
        # Case 2: High internal costs
        order2 = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 1000,
            })],
            'total_internal': 800,
            'total_external': 100,
        })
        # Commission = 1000 - (800 - 100) = 1000 - 700 = 300
        self.assertEqual(order2.net_commission, 300)
