# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Lucas Huber, Copyright CoĐoo Project
#    based on membership_user by Yannick Buron, Copyright Yannick Buron
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Exchange Membership',
    'version': '0.x',
    'category': 'Association',
    'author': 'Lucas Huber, CoĐoo Project',
    'license': 'AGPL-3',
    'description': """
Exchange Membership
===================

Add Exchange management forms to the association part of Odoo
-------------------------------------------------------------
    * Adding state buttons to Partner
    * Adding the wallet page to Partner
    * Adding the loan page to Partner
    *
""",
    'website': 'https://github.com/codoo/vertical-exchange',
    'depends': ['membership',
                'exchange'
    ],
    'data': [
 #       'security/membership_users_security.xml',
 #       'security/ir.model.access.csv',
        'exchange_membership_view.xml'
    ],
    'installable': True,
}
