# -*- coding: utf-8 -*-
"""
Odoo 17 Test: commission_ax
Basic functional tests for commission wizard and sale order commission logic.
"""
from odoo.tests.common import TransactionCase
from odoo import fields

class TestCommissionAx(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test Agent',
        })
        self.sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'date_order': fields.Date.today(),
            'state': 'draft',
        })

    def test_commission_statement_wizard(self):
        wizard = self.env['commission.partner.statement.wizard'].create({
            'partner_id': self.partner.id,
            'sale_order_id': self.sale_order.id,
            'date_from': fields.Date.today(),
            'date_to': fields.Date.today(),
            'output_format': 'pdf',
        })
        self.assertEqual(wizard.partner_id, self.partner)
        self.assertEqual(wizard.sale_order_id, self.sale_order)
        self.assertEqual(wizard.output_format, 'pdf')

    def test_commission_cancel_wizard(self):
        wizard = self.env['commission.cancel.wizard'].create({
            'sale_order_ids': [(6, 0, [self.sale_order.id])],
        })
        self.assertIn(self.sale_order, wizard.sale_order_ids)

    def test_commission_report_wizard(self):
        wizard = self.env['commission.report.wizard'].create({
            'sale_order_id': self.sale_order.id,
            'agent_id': self.partner.id,
            'format': 'pdf',
        })
        self.assertEqual(wizard.sale_order_id, self.sale_order)
        self.assertEqual(wizard.agent_id, self.partner)
        self.assertEqual(wizard.format, 'pdf')

    def test_commission_draft_wizard(self):
        wizard = self.env['commission.draft.wizard'].create({
            'sale_order_id': self.sale_order.id,
        })
        self.assertEqual(wizard.sale_order_id, self.sale_order)
