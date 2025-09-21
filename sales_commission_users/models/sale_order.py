# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
import logging
from odoo import fields, models, api
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    """Inherits Sale order model for adding sales commission."""
    _inherit = 'sale.order'

    commission_ids = fields.One2many('commission.lines',
                                     'sale_order_id',
                                     string='Sales Commission',
                                     help="Commission")

    def action_confirm(self):
        """To add the commission lines in the sale order when its confirmed."""
        res = super(SaleOrder, self).action_confirm()
        try:
            commission = self.env['sales.commission'].search(
                [('sales_person_ids', 'in', self.user_id.id)])
            _logger.info(f"Processing commission for sale order {self.name}, user {self.user_id.name}")

            for com in commission:
                commission_amount = 0.0
                description = ''

                if com.commission_type == 'standard':
                    description = 'Sales Commission - Standard'
                    commission_amount = self.amount_total * com.std_commission_perc / 100

                elif com.commission_type == 'partner_based':
                    if self.partner_id.affiliated:
                        description = 'Sales Commission - Partner based'
                        commission_amount = self.amount_total * com.affiliated_commission_perc / 100
                    else:
                        description = 'Sales Commission - Partner based'
                        commission_amount = self.amount_total * com.non_affiliated_commission_perc / 100

                elif com.commission_type == 'product_based':
                    for rec in com.product_based_ids:
                        order_line = self.order_line.filtered(
                            lambda product: product.product_id == rec.product_id)
                        if order_line:
                            description = 'Sales Commission - Product Based'
                            commission_amount += order_line.price_subtotal * rec.commission / 100

                elif com.commission_type == 'discount_based':
                    for rec in com.discount_based_ids:
                        order_line = self.order_line.filtered(
                            lambda product: product.discount >= rec.discount)
                        if order_line:
                            description = 'Sales Commission - Discount Based'
                            commission_amount += self.amount_total * rec.commission / 100

                if description and commission_amount > 0:
                    _logger.info(f"Creating commission line: {description}, amount: {commission_amount}")
                    self.commission_ids = [(0, 0, {
                        'date': self.date_order,
                        'description': description,
                        'sales_person_id': self.user_id.id,
                        'order_ref': self.name,
                        'partner_id': self.partner_id.id,
                        'commission': com.name,
                        'commission_type': com.commission_type,
                        'commission_amount': commission_amount,
                    })]

        except Exception as e:
            _logger.error(f"Error processing commission for sale order {self.name}: {str(e)}")
            raise UserError(f"Failed to calculate commission: {str(e)}")

        return res
