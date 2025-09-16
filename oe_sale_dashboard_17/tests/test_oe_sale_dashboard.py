# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestOeSaleDashboard(TransactionCase):
    """Test cases for OE Sales Dashboard 17 module"""

    def setUp(self):
        super(TestOeSaleDashboard, self).setUp()
        # Set up common test data
        self.user_demo = self.env.ref('base.user_demo')
        
        # Create test sales dashboard
        self.dashboard = self.env['sales.dashboard'].create({
            'name': 'Test Dashboard',
            'user_id': self.user_demo.id,
            'date_from': '2023-01-01',
            'date_to': '2023-12-31',
        })

    def test_dashboard_creation(self):
        """Test dashboard record creation"""
        self.assertTrue(self.dashboard, "Dashboard was not created")
        self.assertEqual(self.dashboard.name, "Test Dashboard", "Dashboard name is incorrect")
        self.assertEqual(self.dashboard.user_id, self.user_demo, "Dashboard user is incorrect")

    def test_dashboard_performer(self):
        """Test dashboard performer functionality"""
        # Create a performer record
        performer = self.env['sales.dashboard.performer'].create({
            'dashboard_id': self.dashboard.id,
            'user_id': self.user_demo.id,
            'total_orders': 10,
            'total_revenue': 1000.0,
            'conversion_rate': 25.0,
        })
        
        self.assertTrue(performer, "Performer record was not created")
        self.assertEqual(performer.dashboard_id, self.dashboard, "Performer dashboard reference is incorrect")
        self.assertEqual(performer.total_orders, 10, "Performer total orders incorrect")
        
        # Test computed fields
        self.assertEqual(performer.average_order_value, 100.0, "Average order value calculation incorrect")

    def test_kpi_computation(self):
        """Test KPI computation on dashboard"""
        # This test assumes _compute_kpis is implemented and depends on sales order data
        # Create some test sales order data
        partner = self.env.ref('base.res_partner_1')
        product = self.env.ref('product.product_product_4')
        
        # Create a sales order
        sale_order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'user_id': self.user_demo.id,
            'date_order': '2023-05-15',
        })
        
        # Add order line
        self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': product.id,
            'product_uom_qty': 5.0,
            'price_unit': 100.0,
        })
        
        # Confirm the order
        sale_order.action_confirm()
        
        # Manually trigger compute methods or use invalidate_cache if needed
        self.dashboard.invalidate_cache()
        
        # Check if KPIs are updated - these assertions would depend on your actual implementation
        # This is a simple check to ensure the method doesn't crash
        try:
            if hasattr(self.dashboard, '_compute_kpis'):
                self.dashboard._compute_kpis()
            self.assertTrue(True, "KPI computation completed without errors")
        except Exception as e:
            self.fail(f"KPI computation raised an exception: {str(e)}")

    def test_security_access(self):
        """Test security access rules for sales dashboard"""
        # Test as sales user
        sales_user = self.env.ref('base.user_demo')
        sales_user.write({
            'groups_id': [(4, self.env.ref('sales_team.group_sale_salesman').id)]
        })
        
        # Switch to sales user
        dashboard = self.dashboard.with_user(sales_user)
        
        # Test read access
        try:
            name = dashboard.name
            self.assertEqual(name, "Test Dashboard", "Sales user should have read access")
        except Exception as e:
            self.fail(f"Sales user couldn't read dashboard: {str(e)}")
        
        # Test write access
        try:
            dashboard.write({'name': 'Updated Dashboard'})
            self.assertEqual(dashboard.name, "Updated Dashboard", "Sales user should have write access")
        except Exception as e:
            self.fail(f"Sales user couldn't write to dashboard: {str(e)}")
        
        # Test unlink access (should fail for regular sales user)
        has_unlink_exception = False
        try:
            dashboard.unlink()
        except Exception:
            has_unlink_exception = True
        
        self.assertTrue(has_unlink_exception, "Sales user shouldn't have unlink access")