# -*- coding: utf-8 -*-
from odoo import api, models

class CommissionPayoutReport(models.AbstractModel):
    _name = 'report.enhanced_status.commission_payout_report_template_final'
    _description = 'Commission Payout Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Prepare data for commission report"""
        
        # Get sale orders
        orders = self.env['sale.order'].browse(docids)
        
        # Prepare commission data for each order
        report_data = []
        
        for order in orders:
            # Calculate external commissions (example: based on order lines)
            external_commissions = []
            for line in order.order_line:
                if line.product_uom_qty > 0 and line.price_unit > 0:
                    commission_rate = 5.0  # 5% commission rate
                    commission_amount = (line.price_subtotal * commission_rate) / 100
                    external_commissions.append({
                        'product_name': line.product_id.name,
                        'quantity': line.product_uom_qty,
                        'unit_price': line.price_unit,
                        'subtotal': line.price_subtotal,
                        'rate': commission_rate,
                        'amount': commission_amount,
                        'partner': order.partner_id.name if order.partner_id else 'N/A'
                    })
            
            # Calculate internal commissions (salesperson commission)
            internal_commissions = []
            if order.user_id and order.amount_total > 0:
                commission_rate = 3.0  # 3% internal commission
                commission_amount = (order.amount_total * commission_rate) / 100
                internal_commissions.append({
                    'name': 'Internal Sales Commission',
                    'salesperson': order.user_id.name,
                    'rate': commission_rate,
                    'base_amount': order.amount_total,
                    'amount': commission_amount,
                })
            
            # Legacy commissions (placeholder for historical data)
            legacy_commissions = []
            
            # Calculate totals
            total_external = sum(comm['amount'] for comm in external_commissions)
            total_internal = sum(comm['amount'] for comm in internal_commissions)
            total_legacy = sum(comm.get('amount', 0) for comm in legacy_commissions)
            total_commission = total_external + total_internal + total_legacy
            
            # Add commission data to order
            order_data = {
                'order': order,
                'external_commissions': external_commissions,
                'internal_commissions': internal_commissions,
                'legacy_commissions': legacy_commissions,
                'total_external': total_external,
                'total_internal': total_internal,
                'total_legacy': total_legacy,
                'total_commission': total_commission,
            }
            
            report_data.append(order_data)
        
        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': orders,
            'report_data': report_data,
            'data': data,
        }
