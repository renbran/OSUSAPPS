# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Vishnu KP (<https://www.cybrosys.com>)
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
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class DiscountBasedSalesCommission(models.Model):
    """Creating a discount based sales commission model."""
    _name = "discount.based.sales.commission"
    _description = " Discount Based Sales Commission"

    sale_commission_id = fields.Many2one("sales.commission",
                                         string='Sales Commission',
                                         help="Sales commission")
    discount = fields.Float(string='Discount %', help="Discount %")
    commission = fields.Float(string='Commission %', help="Commission %")

    @api.constrains('discount', 'commission')
    def _check_percentages(self):
        """Validate discount and commission percentages are within valid range"""
        for record in self:
            if record.discount < 0 or record.discount > 100:
                raise ValidationError("Discount percentage must be between 0 and 100")
            if record.commission < 0 or record.commission > 100:
                raise ValidationError("Commission percentage must be between 0 and 100")
