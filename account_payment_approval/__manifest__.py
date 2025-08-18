# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Jumana Haseen (odoo@cybrosys.com)
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
{
    'name': 'Payment Approvals',
    'version': '17.0.2.0.0',
    'category': 'Accounting',
    'summary': """ This modules Enables to use the approval feature in
                    customer and vendor payments.""",
    'description': """This modules enables approval feature in the payment.
     as Approval stage .Approval feature can be applied based on the given 
     amount. """,
    'author': ' Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'depends': ['base', 'account', 'web', 'qr_code_base'],
    'data': [
        'security/account_payment_approval_groups.xml',
        'security/account_payment_approval_security.xml',
        'security/ir.model.access.csv',
        'views/account_payment_views.xml',
        'views/account_payment_approval_menus.xml',
        'report/payment_voucher_report.xml',
        'report/payment_voucher_templates.xml',
        'views/verify_payment_template.xml',
        'data/server_actions.xml',
    ],
    'license': 'LGPL-3',
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
