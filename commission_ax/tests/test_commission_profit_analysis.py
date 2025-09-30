#!/usr/bin/env python3
"""
Commission System Comprehensive Test Script
==========================================

This script tests the enhanced commission calculation logic and profit analysis
features to ensure accurate net profit calculations across all commission categories.
"""

import logging
from datetime import datetime, date
from odoo import fields
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)

@tagged('commission', 'profit_analysis')
class TestCommissionProfitAnalysis(TransactionCase):
    """Test commission calculation logic and profit analysis features"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Create test partners
        cls.broker_partner = cls.env['res.partner'].create({
            'name': 'Test Broker Partner',
            'supplier_rank': 1,
            'email': 'broker@test.com'
        })
        
        cls.agent_partner = cls.env['res.partner'].create({
            'name': 'Test Agent Partner',
            'supplier_rank': 1,
            'email': 'agent@test.com'
        })
        
        cls.customer = cls.env['res.partner'].create({
            'name': 'Test Customer',
            'customer_rank': 1,
            'email': 'customer@test.com'
        })
        
        # Create commission types
        cls.broker_commission_type = cls.env['commission.type'].create({
            'name': 'Broker Commission',
            'code': 'BROKER',
            'calculation_method': 'percentage',
            'default_rate': 3.0,
            'commission_category': 'sales'
        })
        
        cls.agent_commission_type = cls.env['commission.type'].create({
            'name': 'Agent Commission',
            'code': 'AGENT1',
            'calculation_method': 'percentage',
            'default_rate': 2.0,
            'commission_category': 'sales'
        })
        
        # Create test product
        cls.test_product = cls.env['product.product'].create({
            'name': 'Test Service Product',
            'type': 'service',
            'list_price': 1000.00,
            'standard_price': 500.00
        })
        
        # Create test sale order
        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.customer.id,
            'order_line': [(0, 0, {
                'product_id': cls.test_product.id,
                'product_uom_qty': 10,
                'price_unit': 1000.00,
            })]
        })

    def test_commission_calculation_methods(self):
        """Test all commission calculation methods work correctly"""
        _logger.info("Testing commission calculation methods...")
        
        # Test percentage_sales_value method
        commission_line = self.env['commission.line'].create({
            'sale_order_id': self.sale_order.id,
            'partner_id': self.broker_partner.id,
            'commission_type_id': self.broker_commission_type.id,
            'calculation_method': 'percentage_sales_value',
            'rate': 3.0,
            'sales_value': 8000.00,  # Specific sales value
        })
        
        # Force computation
        commission_line._compute_amounts()
        
        # Verify calculation
        expected_commission = 8000.00 * 0.03  # 240.00
        self.assertEqual(commission_line.commission_amount, expected_commission,
                        f"Expected {expected_commission}, got {commission_line.commission_amount}")
        self.assertEqual(commission_line.base_amount, 8000.00)
        
        # Test percentage_total method
        commission_line_2 = self.env['commission.line'].create({
            'sale_order_id': self.sale_order.id,
            'partner_id': self.agent_partner.id,
            'commission_type_id': self.agent_commission_type.id,
            'calculation_method': 'percentage_total',
            'rate': 2.0,
        })
        
        commission_line_2._compute_amounts()
        
        # Verify calculation against order total
        expected_commission_2 = self.sale_order.amount_total * 0.02
        self.assertEqual(commission_line_2.commission_amount, expected_commission_2)
        self.assertEqual(commission_line_2.base_amount, self.sale_order.amount_total)

    def test_commission_categories(self):
        """Test commission categorization for profit analysis"""
        _logger.info("Testing commission categorization...")
        
        # Test external broker commission
        external_commission = self.env['commission.line'].create({
            'sale_order_id': self.sale_order.id,
            'partner_id': self.broker_partner.id,
            'commission_type_id': self.broker_commission_type.id,
            'calculation_method': 'percentage_total',
            'rate': 3.0,
            'commission_category': 'external_broker',
            'is_cost_to_company': True,
        })
        
        external_commission._compute_amounts()
        external_commission._compute_profit_impact()
        
        # Verify category assignment
        self.assertEqual(external_commission.commission_category, 'external_broker')
        self.assertTrue(external_commission.is_cost_to_company)
        
        # Test internal agent commission
        internal_commission = self.env['commission.line'].create({
            'sale_order_id': self.sale_order.id,
            'partner_id': self.agent_partner.id,
            'commission_type_id': self.agent_commission_type.id,
            'calculation_method': 'percentage_total',
            'rate': 2.0,
            'commission_category': 'internal_agent1',
            'is_cost_to_company': True,
        })
        
        internal_commission._compute_amounts()
        internal_commission._compute_profit_impact()
        
        # Verify category assignment
        self.assertEqual(internal_commission.commission_category, 'internal_agent1')
        
        # Test profit impact calculation
        expected_impact = (internal_commission.commission_amount / self.sale_order.amount_total) * 100
        self.assertEqual(internal_commission.profit_impact_percentage, expected_impact)

    def test_tiered_commission_calculation(self):
        """Test tiered commission calculation for advanced profit optimization"""
        _logger.info("Testing tiered commission calculation...")
        
        # Create high-value sale order for tiered testing
        high_value_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'order_line': [(0, 0, {
                'product_id': self.test_product.id,
                'product_uom_qty': 100,
                'price_unit': 2000.00,  # 200,000 total
            })]
        })
        
        # Create tiered commission
        tiered_commission = self.env['commission.line'].create({
            'sale_order_id': high_value_order.id,
            'partner_id': self.broker_partner.id,
            'commission_type_id': self.broker_commission_type.id,
            'calculation_method': 'tiered',
            'rate': 2.0,  # Base rate 2%
        })
        
        # Test tiered calculation
        base_amount = high_value_order.amount_untaxed
        expected_tiered_commission = tiered_commission._calculate_tiered_commission(
            base_amount, 2.0, self.broker_commission_type
        )
        
        tiered_commission._compute_amounts()
        
        # Verify tiered commission is higher than flat percentage
        flat_commission = base_amount * 0.02
        self.assertGreater(tiered_commission.commission_amount, flat_commission,
                          "Tiered commission should be higher than flat percentage for large amounts")

    def test_profit_analysis_wizard(self):
        """Test commission partner statement wizard with profit analysis"""
        _logger.info("Testing profit analysis wizard...")
        
        # Create multiple commission lines for comprehensive testing
        commissions = []
        
        # External broker commission (high profit impact)
        external_comm = self.env['commission.line'].create({
            'sale_order_id': self.sale_order.id,
            'partner_id': self.broker_partner.id,
            'commission_type_id': self.broker_commission_type.id,
            'calculation_method': 'percentage_total',
            'rate': 3.0,
            'commission_category': 'external_broker',
            'is_cost_to_company': True,
            'state': 'confirmed',
        })
        commissions.append(external_comm)
        
        # Internal agent commission (investment)
        internal_comm = self.env['commission.line'].create({
            'sale_order_id': self.sale_order.id,
            'partner_id': self.agent_partner.id,
            'commission_type_id': self.agent_commission_type.id,
            'calculation_method': 'percentage_total',
            'rate': 2.0,
            'commission_category': 'internal_agent1',
            'is_cost_to_company': True,
            'state': 'confirmed',
        })
        commissions.append(internal_comm)
        
        # Force computation
        for comm in commissions:
            comm._compute_amounts()
            comm._compute_profit_impact()
        
        # Create wizard
        wizard = self.env['commission.partner.statement.wizard'].create({
            'date_from': date.today().replace(month=1, day=1),
            'date_to': date.today(),
            'partner_ids': [(6, 0, [self.broker_partner.id, self.agent_partner.id])],
            'commission_state': 'confirmed',
            'report_format': 'pdf',
        })
        
        # Get report data
        report_data = wizard._get_commission_data()
        
        # Verify report includes profit analysis fields
        self.assertGreater(len(report_data), 0, "Report data should not be empty")
        
        for line_data in report_data:
            self.assertIn('commission_category', line_data, "Commission category should be included")
            self.assertIn('is_cost_to_company', line_data, "Cost to company flag should be included")
            self.assertIn('profit_impact_percentage', line_data, "Profit impact should be included")
            self.assertIn('commission_type_name', line_data, "Commission type name should be included")

    def test_negative_commission_prevention(self):
        """Test that negative commissions are prevented"""
        _logger.info("Testing negative commission prevention...")
        
        # Create commission with negative rate (should be corrected)
        commission_line = self.env['commission.line'].create({
            'sale_order_id': self.sale_order.id,
            'partner_id': self.broker_partner.id,
            'commission_type_id': self.broker_commission_type.id,
            'calculation_method': 'percentage_total',
            'rate': -2.0,  # Negative rate
        })
        
        commission_line._compute_amounts()
        
        # Verify commission amount is not negative
        self.assertGreaterEqual(commission_line.commission_amount, 0.0,
                               "Commission amount should not be negative")

    def test_commission_type_auto_categorization(self):
        """Test automatic commission categorization based on commission type"""
        _logger.info("Testing commission type auto-categorization...")
        
        # Create commission line
        commission_line = self.env['commission.line'].create({
            'sale_order_id': self.sale_order.id,
            'partner_id': self.broker_partner.id,
            'commission_type_id': self.broker_commission_type.id,
        })
        
        # Trigger onchange
        commission_line._onchange_commission_type()
        
        # Verify auto-categorization
        self.assertIsNotNone(commission_line.commission_category,
                           "Commission category should be auto-set")

    def test_comprehensive_profit_calculation(self):
        """Test comprehensive profit calculation scenario"""
        _logger.info("Testing comprehensive profit calculation...")
        
        # Create multiple commission types and lines
        total_sales = self.sale_order.amount_total
        total_commission_cost = 0.0
        
        # External commissions (direct cost)
        external_commissions = [
            ('external_broker', self.broker_partner, 3.0),
            ('external_referrer', self.agent_partner, 1.5),
        ]
        
        for category, partner, rate in external_commissions:
            commission = self.env['commission.line'].create({
                'sale_order_id': self.sale_order.id,
                'partner_id': partner.id,
                'commission_type_id': self.broker_commission_type.id,
                'calculation_method': 'percentage_total',
                'rate': rate,
                'commission_category': category,
                'is_cost_to_company': True,
            })
            commission._compute_amounts()
            total_commission_cost += commission.commission_amount
        
        # Internal commissions (investment)
        internal_commissions = [
            ('internal_agent1', self.agent_partner, 2.0),
            ('internal_manager', self.broker_partner, 1.0),
        ]
        
        for category, partner, rate in internal_commissions:
            commission = self.env['commission.line'].create({
                'sale_order_id': self.sale_order.id,
                'partner_id': partner.id,
                'commission_type_id': self.agent_commission_type.id,
                'calculation_method': 'percentage_total',
                'rate': rate,
                'commission_category': category,
                'is_cost_to_company': True,
            })
            commission._compute_amounts()
            total_commission_cost += commission.commission_amount
        
        # Calculate net profit
        net_profit = total_sales - total_commission_cost
        profit_margin = (net_profit / total_sales) * 100 if total_sales > 0 else 0
        
        # Verify calculations
        self.assertGreater(net_profit, 0, "Net profit should be positive")
        self.assertLess(profit_margin, 100, "Profit margin should be less than 100%")
        
        _logger.info(f"Comprehensive test results:")
        _logger.info(f"  Total Sales: ${total_sales:,.2f}")
        _logger.info(f"  Total Commission Cost: ${total_commission_cost:,.2f}")
        _logger.info(f"  Net Profit: ${net_profit:,.2f}")
        _logger.info(f"  Profit Margin: {profit_margin:.2f}%")

if __name__ == '__main__':
    print("Commission System Test - Run this in Odoo test environment")
    print("To run: python -m pytest test_commission_profit_analysis.py -v")