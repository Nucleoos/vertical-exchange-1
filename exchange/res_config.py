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


import logging

from openerp.osv import fields, orm
# import openerp.addons.decimal_precision as dp


class ExchangeConfigSettings(orm.Model):


    # Add Exchange configuration (parameters) to Exchange settings
    _inherit = 'exchange.config.settings'

    _columns = {
        'name': fields.char(
            'Exchange Name',
            required=True,
            size=21,
            help='Name of the Exchange'
        ),
        'code': fields.char(
            'Exchange Code',
            required=False,
            default="GB WXYZ",
            size=7,
            help="Unique Exchange Code (EC)"
                 "First part of the 20 digits Account Code CC BBBB"
                 "CC country code -> DE Germany"
                 "BBBB Exchange code"
        ),
        'res_company_id': fields.many2one(
            'res.company', 'Exchange Organisation',
            help="Organisation or Company that runs the Exchange"
        ),
        'display_balance': fields.boolean('Everyone can see balances?'),
        'journal_id': fields.many2one(
            'account.journal', 'Community Journal', required=True
        ),
        'account_ids': fields.one2many(
            'exchange.config.accounts', 'config_id', 'Accounts templates'
#            domain=lambda self: [('name', '=', self._name)],
#            auto_join=True, string='Lines'
        ),

        # TBD may raise conflicts with exchange rates in accounting system
        'ref_currency_id': fields.many2one(
            'res.currency', 'Reference currency',
            help="Currency which is used to calculate exchange rates for transaction engine /n"
            "ATTENTION Reference currency for Odoo Accounting my differ!",
            domain=[('exchange_currency', '=', True)], required=False
        ),
        'use_account_numbers': fields.boolean(
            'Use of Account Numbering System',
            help="Use of the 20 digits Account Numbering Code 'CC BBBB DDDDDDDD XXXX-KK'"
        ),
    }


class ResPartner(orm.Model):
    """
    Display accounts in partner form and add element for configuration
    specific to the partner
    """
    _inherit = 'res.partner'

    _columns = {
        'exchange_account_ids': fields.one2many(
            'exchange.accounts', 'partner_id', 'Accounts',
            help="Related accounts to this user"
        ),
        'exchange_loan_ids': fields.one2many(
            'exchange.loan.contract', 'partner_id', 'Loans',
            help="Related loans"
        ),
#        'account_balance_ids': fields.one2many(
#            'res.partner.wallet.balance', 'partner_id', 'Balances',
#            readonly=True
#        ),
        'create_date': fields.datetime('Create date'),
        'see_balance': fields.boolean(
            "Can see balance?"
        ),
#  TBD      'see_balance': fields.function(
#            _get_see_balance, type="boolean", string="Can see balance?"
#        ),
    }

class DistributedDB(orm.Model):
    """
    Adds many2one fields to Distributed DB model.
    """
    _inherit = 'distributed.db.list'

    _columns = {
    'config_id': fields.many2one(
        'exchange.config.accounts', 'Config ID',
        help='If ledger are used for an exchange system'),
    }


class ResCurrency(orm.Model):
    """
    Add a boolean in currency to identify currency usable in wallet/exchange
    """
    _inherit = 'res.currency'

    _columns = {
        'exchange_currency': fields.boolean('Exchange currency?', readonly=False)
    }
