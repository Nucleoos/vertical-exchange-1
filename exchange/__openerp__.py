# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Lucas Huber, Copyright CoĐoo Project
#    based on account_wallet by Yannick Buron, Copyright Yannick Buron
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
    'name': 'Exchange / Community Banking',
    'version': '0.x',
    'category': 'Exchange',
    'author': 'Lucas Huber, CoĐoo Project',
    'license': 'AGPL-3',
    'summary': 'Community Exchange',
    'website': 'https://github.com/codoo/vertical-exchange',
    'depends': [
                'account_accountant',
                'account_reversal',
                'base_exchange',
                'distributed_db',
                ],

    'data': [
        'security/exchange_security.xml',
        'security/ir.model.access.csv',
 #       'exchange_old_view.xml',
         'res_config_view.xml',
         'exchange_accounts_view.xml',
         'exchange_transaction_view.xml',
         'exchange_loan_view.xml',
 #       'test_view.xml',
         'exchange_workflow.xml',
         'data/exchange_data.xml',
         'data/account_data.xml',
 #        'data/test_data.xml',
            ],
    """
    'demo': ['data/exchange_demo.xml'],
    'test': [
        'tests/account_wallet_users.yml',
        'tests/account_wallet_rights.yml',
        'tests/account_wallet_moderator.yml',
        'tests/account_wallet_external.yml',
        'tests/account_wallet_limits.yml',
        'tests/account_wallet_balances.yml',
    ],
    """
    'installable': True,
    'application': True,
}
