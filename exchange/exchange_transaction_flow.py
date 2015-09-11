# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Lucas Huber, Copyright: CoĐoo Project
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

from openerp import models, fields, api
from openerp.exceptions import except_orm
from openerp import SUPERUSER_ID
from openerp import workflow
from datetime import datetime, timedelta
import exchange_model
# import re

class ExchangeTransactions(models.Model):
    """
    Main object used for the workflow of transferring values, invoices and messages , from sender_account to receiver_account    It has his own workflow, from draft to done and can be refund.
    The confirm state, used only when there is an external account
    (currency whose wallet isn't managed in odoo), is used so the receiver
    can confirm that the send the money.
    The
    """

    # TBD AttributeError: 'exchange.accounts' object has no attribute 'exchange_rate'
 #   @api.onchange('account_from_id') # if account_from is set, get actual exchange rate
 #   def set_exchange_rate(self):
 #       self.exchange_rate_from = self.account_from_id.exchange_rate



    @api.multi
    def do_test(self):
        """
        write method to get amount after exchange range calculation.
        TBD
        """
        print self, self.exchange_rate_from, self.exchange_rate_to
        return True

    @api.one
    def tr_number_calc(self):
        """
        write method to get new transaction number.
        TBD missing ref now_bup
        :param type: The transaction number to update.
        """
        type2 = self.type_prefix_from + '>' + self.type_prefix_to
        print type2
        return type2 + '-' + datetime.now()

    @api.onchange('type_id') # if account_type is set, create new Transaction NR
    def set_name(self):
        """
        TBD creates a type missmatch error
        :param type: The transaction number to update.
        """
        type2 = self.type_prefix_from + self.type_prefix_to
        print type2
        self.name = type2 + '-' + datetime.now()


    @api.one
    def get_amount_to(self):
        """
        write method to get amount after exchange range calculation.
        TBD
        """
        print self.amount_from, self.exchange_rate_from, self.exchange_rate_to
        print self.amount_from * self.exchange_rate_from * self.exchange_rate_to
        return self.amount_from * self.exchange_rate_from * self.exchange_rate_to


    """
    Following functions are related to workflow
    """
    @api.multi
    def change_state(self, new_state, *args):
#       Called by workflow, launch needed action depending of the next state
#       for transaction in self.browse(cr, uid, ids):
#          fields = {'state': new_state}
#            if new_state == 'done':
#               self.prepare_move(cr, uid, [transaction.id], 'confirm')
#            if new_state == 'cancel':
#              self.refund(
#                   cr, uid, [transaction.id],
#                   ['reservation', 'invoice', 'payment', 'confirm']
#              )
#          self.write(cr, uid, [transaction.id], fields)
        return True

    @api.multi
    def confirm(self, cr, uid, ids, *args):
        # Workflow action which confirm the transaction and make the payment
        # for currency managed inside Odoo, it goes to confirm or paid state
        # whether there is or not an external currency
        self.test_access_role(cr, uid, ids, 'is_sender', *args)

        self.write(cr, uid, ids, {'already_published': True})
        for transaction in self.browse(cr, uid, ids):
            self.prepare_move(cr, uid, [transaction.id], 'reservation')
            self.prepare_move(cr, uid, [transaction.id], 'payment')
            skip_confirm = self.get_skip_confirm(cr, uid, transaction)
            if not skip_confirm:
                workflow.trg_validate(
                    uid, 'exchange.transaction', transaction.id,
                    'transaction_draft_confirm', cr
                )
            else:
                workflow.trg_validate(
                    uid, 'exchange.transaction', transaction.id,
                    'transaction_draft_done', cr
                )
        return True

    @api.multi
    def test_access_role(self, cr, uid, ids, role_to_test, *args):
        # Raise an exception if we try to make
        #  an action denied for the current user
        res = self._get_user_role(cr, uid, ids, {}, {})
        for transaction in self.browse(cr, uid, ids):
            role = res[transaction.id]
            if not role[role_to_test]:
                raise Exception(
                    ('Access error!'),
                    (
                        "You need to have the role " + role_to_test +
                        " to perform this action!"
                    ))
        return True

    @api.multi
    def _get_user_role(self, cr, uid, ids, prop, unknow_none, context=None):
        # Control the access rights of the current user
        user_obj = self.pool.get('res.users')
        res = {}
        partner_id = self.pool.get('res.users').browse(
            cr, uid, uid, context=context
        ).partner_id.id
        for transaction in self.browse(cr, uid, ids, context=context):
            res[transaction.id] = {}
            res[transaction.id]['is_sender'] = False
            res[transaction.id]['is_receiver'] = False
            res[transaction.id]['is_moderator'] = False
            if transaction.sender_id.id == partner_id:
                res[transaction.id]['is_sender'] = True
            if transaction.receiver_id.id == partner_id:
                res[transaction.id]['is_receiver'] = True
            if user_obj.has_group(
                    cr, uid, 'exchange.group_exchange_moderator'
            ):
                res[transaction.id]['is_sender'] = True
                res[transaction.id]['is_receiver'] = True
                res[transaction.id]['is_moderator'] = True
        return res

    @api.multi
    def prepare_move(self, cr, uid, ids, action, context=None):
        # Generate the specified transfer
        partner_obj = self.pool.get('res.partner')
        move_obj = self.pool.get('account.move')
        company_obj = self.pool.get('res.company')
        config = self.pool.get('ir.model.data').get_object(
            cr, uid, 'base_community', 'community_settings'
        )

    @api.multi
    def get_skip_confirm(self, cr, uid, transaction, context=None):
        # Check is there is an external currency, to determine whether
        # we should go to confirm or paid state
        config_currency_obj = self.pool.get('exchange.config.accounts')

        currency_ids = []
        for currency in transaction.currency_ids:
            currency_ids.append(currency.currency_id.id)
        config_currency_ids = config_currency_obj.search(
            cr, uid, [('currency_id', 'in', currency_ids)]
        )

        skip_confirm = True
        for config_currency in config_currency_obj.browse(
                cr, uid, config_currency_ids
        ):
            if config_currency.external_currency:
                skip_confirm = False
        return skip_confirm

    @api.multi
    def refund(self, cr, uid, ids, fields, context=None):
        # Reverse all moves linked to the transaction
        move_obj = self.pool.get('account.move')
        date = datetime.now().strftime("%Y-%m-%d")
        for transaction in self.browse(cr, uid, ids, context=context):

            for move_field in fields:
                move = getattr(transaction, move_field + '_id')
                if move:
                    flag = 'cancel_' + move_field
                    reversal_move_id = move_obj.create_reversals(
                        cr, uid, [move.id], date
                    )[0]
                    move_obj.post(cr, uid, [reversal_move_id])
                    move_obj.write(cr, uid, [reversal_move_id], {
                        'wallet_action': flag,
                        'wallet_transaction_id': transaction.id
                    }, context=context)
                    self.write(
                        cr, uid, [transaction.id],
                        {move_field + '_id': False}, context=context
                    )
                    self.reconcile(
                        cr, uid, [move.id, reversal_move_id], context=context
                    )

 #   Model Definition Transactions
    _name = 'exchange.transaction'
    _description = 'Exchange Transactions'
    _inherit = ['mail.thread']
    _order = 'emission_date'
 #   Track the status of the transaction to mail.thread

 #   _track = 'state', 'account_wallet.mt_transaction_state': lambda self,
 #           cr, uid, obj, ctx=None: obj.already_published,

    name = fields.Char(
        'Number', size=30, required=True)
        # TBD       default=tr_number_calc('type_id'))
    account_from_id = fields.Many2one(
        'exchange.accounts', 'Account From', required=True, track_visibility='onchange')
    account_to_id = fields.Many2one(
        'exchange.accounts', 'Account To', required=True, track_visibility='onchange')
    type_id = fields.Many2one(
        'exchange.transaction.type', 'Transactions Type', required=True, track_visibility='onchange')
    line_ids = fields.One2many(
        'exchange.transaction.line', 'transaction_id',  'Transfer Lines', required=False)
    emission_date = fields.Datetime(
        'Emission Date', required=True, default=datetime.now().strftime("%Y-%m-%d"))
    transaction_date = fields.Datetime(
        'Transaction Date', required=False)
    amount_from = fields.Float(
        'Amount from Sender', required=True)
    # TBD: should be computed out of exchange rates in res.currency
    amount_to = fields.Float(
        'Amount to Receiver', required=True, default=get_amount_to)
    # TBD    'Amount to Receiver', required=True, default=get_amount_to())

    state = fields.Selection(
            [
                ('draft', 'Draft'),
                ('sent', 'Sent'),
                ('confirm', 'Confirm'),
                ('done', 'Closed'),
                ('confirm_refund', 'Confirm Refund'),
                ('cancel', 'Cancelled'),
            ], 'Status', readonly=False, default='draft', required=True, track_visibility='onchange')

    is_fee = fields.Boolean('Is a fee transaction')

    fee_ids = fields.Many2one(
        'exchange.transaction', 'Fee or other Transaction', required=False)
    is_loan = fields.Boolean('Is a loan transaction')

    loan_contract_id = fields.Many2one(
        'exchange.loan.contract', 'Related Loan contract', required=False)

    # Related fields (not stored in DB)
    sender_id = fields.Many2one('res.partner',
         'Sending Partner', related='account_from_id.partner_id',
         readonly=True)
    receiver_id = fields.Many2one('res.partner',
         'Receiving Partner', related='account_to_id.partner_id',
         readonly=True)
    currency_from = fields.Many2one('res.currency',
        'Currency from', related='account_from_id.currency_base',
         readonly=True)
    currency_to = fields.Many2one('res.currency',
        'Currency to', related='account_to_id.currency_base',
         readonly=True)
    exchange_rate_from = fields.Float(
        'Exchange rate Sender', required=True, default=1.0)
# TBD   exchange_rate_from = fields.Float('exchange.accounts',
#        'Exchange rate from Sender',  related='account_from_id.exchange_rate',
#         readonly=True)
    exchange_rate_to = fields.Float(
        'Exchange rate Receiver', required=True, default=1.0)

    ext_from = fields.Boolean('From external Account',
        related='account_from_id.external_db',
        readonly=True)
    ext_to = fields.Boolean('To external Account',
        related='account_to_id.external_db',
        readonly=True)
    type_prefix_from = fields.Many2one('exchange.account.type',
         'Prefix from', related='type_id.type_prefix_from',
         readonly=True)
    type_prefix_to = fields.Many2one('exchange.account.type',
         'Prefix to', related='type_id.type_prefix_to',
         readonly=True)
