# -*- coding: utf-8 -*-
#############################################################################
#
#    Unified Commission Management System - Payment Processor
#    Handles all commission payment methods: Invoices, Purchase Orders, Journal Entries
#
#############################################################################

import logging
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class CommissionPaymentProcessor(models.Model):
    """
    Unified Commission Payment Processor
    Supports multiple payment methods for commission processing
    """
    _name = 'commission.payment.processor'
    _description = 'Commission Payment Processor'

    name = fields.Char(string="Processor Name", default="Unified Payment Processor")
    active = fields.Boolean(string="Active", default=True)

    def process_commission_payment(self, commission_line, payment_method=None):
        """
        Main method to process commission payment based on specified method
        """
        self.ensure_one()

        if not commission_line:
            raise UserError(_("Commission line is required for payment processing"))

        if commission_line.status not in ['approved', 'confirmed']:
            raise UserError(_("Commission must be approved or confirmed before payment processing"))

        if not payment_method:
            payment_method = commission_line.payment_method or 'invoice'

        _logger.info(f"Processing commission payment for {commission_line.name} using method: {payment_method}")

        try:
            if payment_method == 'invoice':
                return self._create_commission_invoice(commission_line)
            elif payment_method == 'purchase_order':
                return self._create_commission_purchase_order(commission_line)
            elif payment_method == 'journal_entry':
                return self._create_commission_journal_entry(commission_line)
            else:
                raise UserError(_("Unsupported payment method: %s") % payment_method)

        except Exception as e:
            _logger.error(f"Payment processing failed for {commission_line.name}: {str(e)}")
            raise UserError(_("Payment processing failed: %s") % str(e))

    def _create_commission_invoice(self, commission_line):
        """
        Create customer invoice for commission payment (sales_commission_users approach)
        """
        _logger.info(f"Creating commission invoice for {commission_line.name}")

        # Validate partner has invoicing setup
        partner = commission_line.partner_id
        if not partner:
            raise UserError(_("Partner is required for invoice creation"))

        # Get or create commission product
        commission_product = self._get_or_create_commission_product('Commission Payment')

        # Prepare invoice values
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': fields.Date.today(),
            'payment_reference': f"Commission - {commission_line.sale_order_id.name}",
            'ref': f"Commission payment for {commission_line.description}",
            'company_id': commission_line.company_id.id,
            'currency_id': commission_line.currency_id.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': commission_product.id,
                'name': commission_line.description,
                'quantity': 1.0,
                'price_unit': commission_line.commission_amount,
                'account_id': commission_product.property_account_income_id.id or
                             commission_product.categ_id.property_account_income_categ_id.id,
            })]
        }

        # Create invoice
        invoice = self.env['account.move'].create(invoice_vals)

        # Update commission line
        commission_line.write({
            'invoice_id': invoice.id,
            'status': 'paid',
            'date_paid': fields.Datetime.now(),
        })

        _logger.info(f"Commission invoice created: {invoice.name} for {commission_line.name}")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Commission Invoice',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'target': 'current',
        }

    def _create_commission_purchase_order(self, commission_line):
        """
        Create purchase order for commission payment (commission_ax approach)
        """
        _logger.info(f"Creating commission purchase order for {commission_line.name}")

        # Validate partner is a vendor
        partner = commission_line.partner_id
        if not partner:
            raise UserError(_("Partner is required for purchase order creation"))

        if not partner.is_company and not partner.supplier_rank:
            partner.supplier_rank = 1  # Make partner a vendor

        # Get or create commission product
        commission_product = self._get_or_create_commission_product('Commission Service')

        # Prepare purchase order values
        po_vals = {
            'partner_id': partner.id,
            'origin': commission_line.sale_order_id.name,
            'date_order': fields.Datetime.now(),
            'company_id': commission_line.company_id.id,
            'currency_id': commission_line.currency_id.id,
            'order_line': [(0, 0, {
                'product_id': commission_product.id,
                'name': commission_line.description,
                'product_qty': 1.0,
                'product_uom': commission_product.uom_po_id.id,
                'price_unit': commission_line.commission_amount,
                'date_planned': fields.Datetime.now(),
                'account_analytic_id': False,  # Can be set based on business rules
            })]
        }

        # Create purchase order
        purchase_order = self.env['purchase.order'].create(po_vals)

        # Update commission line
        commission_line.write({
            'purchase_order_id': purchase_order.id,
            'status': 'paid',
            'date_paid': fields.Datetime.now(),
        })

        _logger.info(f"Commission purchase order created: {purchase_order.name} for {commission_line.name}")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Commission Purchase Order',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'res_id': purchase_order.id,
            'target': 'current',
        }

    def _create_commission_journal_entry(self, commission_line):
        """
        Create journal entry for commission payment (new unified approach)
        """
        _logger.info(f"Creating commission journal entry for {commission_line.name}")

        # Get commission accounts from configuration or defaults
        commission_expense_account = self._get_commission_expense_account()
        commission_payable_account = self._get_commission_payable_account()

        if not commission_expense_account or not commission_payable_account:
            raise UserError(_("Commission accounting configuration is incomplete. Please configure commission accounts."))

        # Prepare journal entry values
        journal = self.env['account.journal'].search([
            ('type', '=', 'general'),
            ('company_id', '=', commission_line.company_id.id)
        ], limit=1)

        if not journal:
            raise UserError(_("No general journal found for journal entry creation"))

        move_vals = {
            'move_type': 'entry',
            'journal_id': journal.id,
            'date': fields.Date.today(),
            'ref': f"Commission payment - {commission_line.description}",
            'company_id': commission_line.company_id.id,
            'currency_id': commission_line.currency_id.id,
            'line_ids': [
                # Debit Commission Expense
                (0, 0, {
                    'name': f"Commission Expense - {commission_line.description}",
                    'account_id': commission_expense_account.id,
                    'partner_id': commission_line.partner_id.id,
                    'debit': commission_line.commission_amount,
                    'credit': 0.0,
                    'analytic_account_id': False,  # Can be set based on business rules
                }),
                # Credit Commission Payable
                (0, 0, {
                    'name': f"Commission Payable - {commission_line.partner_id.name}",
                    'account_id': commission_payable_account.id,
                    'partner_id': commission_line.partner_id.id,
                    'debit': 0.0,
                    'credit': commission_line.commission_amount,
                })
            ]
        }

        # Create journal entry
        journal_entry = self.env['account.move'].create(move_vals)

        # Auto-post if configured
        auto_post = self.env['ir.config_parameter'].sudo().get_param(
            'commission.auto_post_journal_entries', 'False'
        ).lower() == 'true'

        if auto_post:
            journal_entry.action_post()

        # Update commission line
        commission_line.write({
            'journal_entry_id': journal_entry.id,
            'status': 'paid',
            'date_paid': fields.Datetime.now(),
        })

        _logger.info(f"Commission journal entry created: {journal_entry.name} for {commission_line.name}")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Commission Journal Entry',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': journal_entry.id,
            'target': 'current',
        }

    def _get_or_create_commission_product(self, product_name):
        """
        Get or create commission product for transactions
        """
        product = self.env['product.product'].search([
            ('name', '=', product_name),
            ('type', '=', 'service'),
            ('company_id', 'in', [False, self.env.company.id])
        ], limit=1)

        if not product:
            # Create commission product
            product_category = self.env['product.category'].search([
                ('name', 'ilike', 'service')
            ], limit=1)

            if not product_category:
                product_category = self.env.ref('product.product_category_all')

            product = self.env['product.product'].create({
                'name': product_name,
                'type': 'service',
                'categ_id': product_category.id,
                'list_price': 0.0,
                'standard_price': 0.0,
                'sale_ok': True,
                'purchase_ok': True,
                'detailed_type': 'service',
                'taxes_id': [(6, 0, [])],  # No taxes by default
                'supplier_taxes_id': [(6, 0, [])],  # No taxes by default
            })

            _logger.info(f"Created commission product: {product_name}")

        return product

    def _get_commission_expense_account(self):
        """
        Get commission expense account from configuration
        """
        account_code = self.env['ir.config_parameter'].sudo().get_param(
            'commission.expense_account_code', '6220'
        )

        account = self.env['account.account'].search([
            ('code', '=like', f"{account_code}%"),
            ('company_id', '=', self.env.company.id),
            ('account_type', 'in', ['expense', 'other'])
        ], limit=1)

        if not account:
            # Try to find any expense account
            account = self.env['account.account'].search([
                ('account_type', '=', 'expense'),
                ('company_id', '=', self.env.company.id)
            ], limit=1)

        return account

    def _get_commission_payable_account(self):
        """
        Get commission payable account from configuration
        """
        account_code = self.env['ir.config_parameter'].sudo().get_param(
            'commission.payable_account_code', '2010'
        )

        account = self.env['account.account'].search([
            ('code', '=like', f"{account_code}%"),
            ('company_id', '=', self.env.company.id),
            ('account_type', 'in', ['liability_payable', 'liability_current'])
        ], limit=1)

        if not account:
            # Try to find any payable account
            account = self.env['account.account'].search([
                ('account_type', '=', 'liability_payable'),
                ('company_id', '=', self.env.company.id)
            ], limit=1)

        return account

    @api.model
    def bulk_process_payments(self, commission_line_ids, payment_method='auto'):
        """
        Bulk process payments for multiple commission lines
        """
        if not commission_line_ids:
            return []

        commission_lines = self.env['commission.lines'].browse(commission_line_ids)

        # Filter lines that can be processed
        processable_lines = commission_lines.filtered(
            lambda l: l.status in ['approved', 'confirmed'] and not l.invoice_id and
                     not l.purchase_order_id and not l.journal_entry_id
        )

        if not processable_lines:
            raise UserError(_("No commission lines found that can be processed"))

        _logger.info(f"Bulk processing {len(processable_lines)} commission payments")

        results = []
        errors = []

        for line in processable_lines:
            try:
                # Determine payment method
                method = payment_method
                if method == 'auto':
                    method = line.payment_method or self.env['ir.config_parameter'].sudo().get_param(
                        'commission.default_payment_method', 'invoice'
                    )

                result = self.process_commission_payment(line, method)
                results.append({
                    'commission_line_id': line.id,
                    'success': True,
                    'result': result
                })

            except Exception as e:
                error_msg = str(e)
                errors.append({
                    'commission_line_id': line.id,
                    'success': False,
                    'error': error_msg
                })
                _logger.error(f"Failed to process payment for {line.name}: {error_msg}")

        _logger.info(f"Bulk payment processing completed: {len(results)} successful, {len(errors)} failed")

        return {
            'successful': results,
            'failed': errors,
            'summary': {
                'total_processed': len(processable_lines),
                'successful_count': len(results),
                'failed_count': len(errors)
            }
        }

    def validate_payment_configuration(self, payment_method):
        """
        Validate that payment method is properly configured
        """
        if payment_method == 'invoice':
            # Check if commission product exists
            product = self._get_or_create_commission_product('Commission Payment')
            if not product.property_account_income_id and not product.categ_id.property_account_income_categ_id:
                raise ValidationError(_("Commission product income account is not configured"))

        elif payment_method == 'purchase_order':
            # Check purchase configuration
            product = self._get_or_create_commission_product('Commission Service')
            if not product.property_account_expense_id and not product.categ_id.property_account_expense_categ_id:
                raise ValidationError(_("Commission product expense account is not configured"))

        elif payment_method == 'journal_entry':
            # Check journal entry accounts
            expense_account = self._get_commission_expense_account()
            payable_account = self._get_commission_payable_account()

            if not expense_account:
                raise ValidationError(_("Commission expense account is not configured"))
            if not payable_account:
                raise ValidationError(_("Commission payable account is not configured"))

        return True

    def get_payment_summary(self, commission_line_ids):
        """
        Get payment processing summary without actually processing
        """
        commission_lines = self.env['commission.lines'].browse(commission_line_ids)

        summary = {
            'total_lines': len(commission_lines),
            'total_amount': sum(commission_lines.mapped('commission_amount')),
            'processable_lines': 0,
            'already_processed': 0,
            'not_ready': 0,
            'by_payment_method': {},
        }

        for line in commission_lines:
            if line.status in ['approved', 'confirmed'] and not any([line.invoice_id, line.purchase_order_id, line.journal_entry_id]):
                summary['processable_lines'] += 1

                # Group by payment method
                method = line.payment_method or 'auto'
                if method not in summary['by_payment_method']:
                    summary['by_payment_method'][method] = {'count': 0, 'amount': 0}
                summary['by_payment_method'][method]['count'] += 1
                summary['by_payment_method'][method]['amount'] += line.commission_amount

            elif any([line.invoice_id, line.purchase_order_id, line.journal_entry_id]):
                summary['already_processed'] += 1
            else:
                summary['not_ready'] += 1

        return summary