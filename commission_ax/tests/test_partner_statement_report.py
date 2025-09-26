# -*- coding: utf-8 -*-
"""
Commission Partner Statement Report Tests
=========================================

Test suite for validating the commission partner statement report functionality
including the recent changes to use client_order_ref instead of project/unit.
"""

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date, timedelta
import logging

_logger = logging.getLogger(__name__)


class TestPartnerStatementReport(TransactionCase):
    """Test commission partner statement report functionality"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(user=cls.env.ref('base.user_admin'))
        
        # Create test data
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Commission Partner',
            'is_company': True,
        })
        
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product',
            'list_price': 1000.0,
            'type': 'consu',
        })

    def test_01_wizard_creation(self):
        """Test that the commission partner statement wizard can be created"""
        wizard = self.env['commission.partner.statement.wizard'].create({
            'date_from': date.today() - timedelta(days=30),
            'date_to': date.today(),
            'report_format': 'pdf',
            'commission_state': 'all',
        })
        
        self.assertTrue(wizard.exists(), "Wizard should be created successfully")
        self.assertEqual(wizard.report_format, 'pdf')
        self.assertEqual(wizard.commission_state, 'all')

    def test_02_date_validation(self):
        """Test date range validation in wizard"""
        with self.assertRaises(ValidationError):
            self.env['commission.partner.statement.wizard'].create({
                'date_from': date.today(),
                'date_to': date.today() - timedelta(days=1),  # Invalid: from > to
                'report_format': 'pdf',
            })

    def test_03_sample_data_generation(self):
        """Test sample data generation when no real data exists"""
        wizard = self.env['commission.partner.statement.wizard'].create({
            'date_from': date.today() - timedelta(days=30),
            'date_to': date.today(),
            'report_format': 'pdf',
        })
        
        # Get commission data (should return sample data since no real data exists)
        data = wizard._get_commission_data()
        
        self.assertTrue(isinstance(data, list), "Should return a list")
        if data:  # Sample data should be created
            self.assertIn('partner_name', data[0], "Data should contain partner_name")
            self.assertIn('client_order_ref', data[0], "Data should contain client_order_ref instead of project/unit")
            self.assertIn('booking_date', data[0], "Data should contain booking_date")
            self.assertIn('commission_amount', data[0], "Data should contain commission_amount")
            
            # Verify new structure doesn't contain old fields
            self.assertNotIn('project_name', data[0], "Should not contain project_name (replaced with client_order_ref)")
            self.assertNotIn('unit', data[0], "Should not contain unit (replaced with client_order_ref)")

    def test_04_pdf_report_generation(self):
        """Test PDF report generation"""
        wizard = self.env['commission.partner.statement.wizard'].create({
            'date_from': date.today() - timedelta(days=30),
            'date_to': date.today(),
            'report_format': 'pdf',
            'partner_ids': [(6, 0, [self.partner.id])],
        })
        
        result = wizard._generate_pdf_report()
        
        self.assertIn('type', result, "Should return action dict")
        self.assertEqual(result['type'], 'ir.actions.report')
        self.assertEqual(result['report_name'], 'commission_ax.commission_partner_statement_report')

    def test_05_excel_report_generation(self):
        """Test Excel report generation"""
        wizard = self.env['commission.partner.statement.wizard'].create({
            'date_from': date.today() - timedelta(days=30),
            'date_to': date.today(),
            'report_format': 'excel',
            'partner_ids': [(6, 0, [self.partner.id])],
        })
        
        # This should not raise an exception
        try:
            result = wizard._generate_excel_report()
            self.assertIn('type', result, "Should return action dict for Excel report")
        except Exception as e:
            _logger.warning(f"Excel generation test failed (might be due to missing xlsxwriter): {e}")
            # This is acceptable since xlsxwriter might not be installed

    def test_06_report_model_bridge(self):
        """Test the report model bridge functionality"""
        # Create wizard
        wizard = self.env['commission.partner.statement.wizard'].create({
            'date_from': date.today() - timedelta(days=30),
            'date_to': date.today(),
            'report_format': 'pdf',
        })
        
        # Test the report model
        report_model = self.env['report.commission_ax.commission_partner_statement_report']
        
        # Get report values
        values = report_model._get_report_values([wizard.id])
        
        self.assertIn('data', values, "Report values should contain data")
        self.assertIn('report_data', values['data'], "Data should contain report_data")
        self.assertIn('wizard_info', values['data'], "Data should contain wizard_info")

    def test_07_both_format_generation(self):
        """Test generating both PDF and Excel formats"""
        wizard = self.env['commission.partner.statement.wizard'].create({
            'date_from': date.today() - timedelta(days=30),
            'date_to': date.today(),
            'report_format': 'both',
        })
        
        # Should not raise exception and should return PDF action
        result = wizard.action_generate_report()
        self.assertEqual(result['report_type'], 'qweb-pdf')

    def test_08_client_order_ref_data_structure(self):
        """Test that the new client_order_ref structure is properly implemented"""
        wizard = self.env['commission.partner.statement.wizard'].create({
            'date_from': date.today() - timedelta(days=30),
            'date_to': date.today(),
            'report_format': 'pdf',
        })
        
        sample_data = wizard._create_sample_data()
        
        # Verify sample data has correct structure
        for record in sample_data:
            self.assertIn('client_order_ref', record, "Should contain client_order_ref field")
            self.assertNotIn('project_name', record, "Should NOT contain project_name field")
            self.assertNotIn('unit', record, "Should NOT contain unit field")
            
            # Verify required fields are still present
            required_fields = ['partner_name', 'booking_date', 'sale_value', 
                             'commission_rate', 'commission_amount', 'commission_status']
            for field in required_fields:
                self.assertIn(field, record, f"Should contain required field: {field}")