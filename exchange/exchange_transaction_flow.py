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
    Main object used for the workflow of transferring values, invoices and messages , from sender_account to receiver_account    It has his own workflow, from draft to paid and can be refund.

    """


    @api.multi
    def do_test(self):
        """
        write method to get amount after exchange range calculation.
        TBD
        """
        print self, self.exchange_rate_from, self.exchange_rate_to
        return True


    @api.onchange('type_id')  # if account_type is set, create new Transaction NR
    def set_name(self):
        """
        create new Transaction NR
        TBD on new record it generates an error?????
        :param type_id: The type of transaction that determines the prefixes
        """
        if self.type_id is not None:
            type1 = str(self.type_prefix_from.name + '>' + self.type_prefix_to.name)
            d = datetime.now()
            date2 = d.strftime('%Y-%m-%d %H:%M:%S')
            # print self.type_id, date2, self.id
            self.name = type1 + '-' + date2

        # Set is_fee to yes or no depending on the One2many field in transaction.type
        # TBD
            self.is_fee = False

    @api.onchange('account_from_id','account_to_id','amount_from')
        # if account_from to or amount from change calculate new amount to
    def set_amount_to(self):
        #TBD does not work
        amount = self.amount_from * self.exchange_rate_from * self.exchange_rate_to
        print 'amount_to' + amount
        self.amount_to = amount


    @api.one
    def get_amount_to(self):
        """
        write method to get amount after exchange range calculation.
        TBD
        """
        print self.amount_from, self.exchange_rate_from, self.exchange_rate_to
        amount = self.amount_from * self.exchange_rate_from * self.exchange_rate_to
        print amount
        return amount

    """
    Following functions are related to workflow
    """
    @api.multi
    def change_state(self, new_state, *args):
#       Called by workflow, launch needed action depending of the next state
#       for transaction in self.browse(ids):
#          fields = {'state': new_state}
#            if new_state == 'paid':
#               self.prepare_move([transaction.id], 'do_payment')
#            if new_state == 'canceled':
#              self.refund(
#                   [transaction.id],
#                   ['reservation', 'invoice', 'payment', 'do_payment']
#              )
#          self.write([transaction.id], fields)
        return True

    @api.one # STEP 1
    def act_transaction_draft(self):
        # Workflow action 1
        # self.state = 'sent'
        print 'draft'
        return True

    @api.one  # STEP 2a payment
    @api.depends('ext_from','ext_to')
    def act_transaction_sent(self):
        # Workflow action 2a which confirm the transaction and make the payment
        # for currency managed inside Odoo, it goes to confirm or paid state
        # whether there is or not an external db
        print 'sent'
        # Test id user is allowed to do payment
        # self.test_access_role(role)
        # Check is there is an external currency, to determine whether
        # we should stay in sent or go to paid state
        if self.ext_from is True | self.ext_to is True:
            self._payment_extern()

        else:

                # id = self.create(cr, uid, , context=context)
                trans_line = self.env['exchange.transaction.line']
                new = trans_line.create(
                    {'name': 'TEST1',
                    'transfer_type': 'transfer',
                    'transfer_from_id': self.account_from_id,
                    'transfer_to_id': self.account_to_id,
                    'amount_from': self.amount_from,
                    'amount_to': self.amount_to,
                    }
                )
                print new
        return True

    @api.one  # Payment via external db
    @api.depends ()
    def _payment_extern(self):
        # TBD check if external db connection is established
        #perform external transaction
            workflow.trg_validate(
                     self._uid,
                    'exchange.transaction', 
                     self.transaction.id,
                    'trans_draft-sent', self.env.cr
            )

    #    workflow.trg_validate	(uid,
 	#    res_type, res_id,  signal, cr 
    #    )		
    #    return True

    @api.one  # STEP 2b invoiced
    def act_transaction_invoiced(self):
        # Workflow action which sends an invoice to Receiver
        # self.state = 'invoiced'
        print 'step invoiced'
        return True

    @api.one  #  Send Message
    @api.depends('account_from_id','account_to_id')
    def do_content(self):
        # non Workflow action which sends a message to Receiver

     #   trans_line = self.env['exchange.transaction.line']
     #       new = trans_line.create(
     #               {'name': 'Message test',
     #               'transfer_type': 'info',
     #               'transfer_from_id': self.account_from_id,
     #               'transfer_to_id': self.account_to_id,
     #               }
     #       )
     #   print new
        return


    @api.one
    def test_access_role(self, role_to_test):
        # Raise an exception if we try to make
        #  an action denied for the current user
        role = self._get_user_role()
        print 'role_to_test' + role_to_test
        if role != 'selfpayment':
            print role_to_test
     #  else
     #      if role not role_to_test:
     #          raise Exception(
     #               ('Access error!'),
     #               (
     #                   "You need to have the role " + role_to_test +
     #                   " to perform this action!"
     #               ))
        return True

    @api.one
    @api.depends ('sender_id','receiver_id')
    def _get_user_role(self):
        # Control the access rights of the current user
    #   TBD User ID instead Partner ID is needed!
    #   user_obj = self.pool.get('res.users')
    #    res = {}
    #    partner_id = self.pool.get('res.users').browse(
    #        cr, uid, uid, context=context
    #    ).partner_id.id
        # user_id does not result as id
        user_id = lambda self: self.env['exchange.model'].user_partner
        role = 'other'

        #    self.env['res.users'].search(['partner_id', '=', self.sender_id.id])
        # print self.sender_id.id, self.receiver_id.id, user_id, self._uid
        if self.sender_id.id == user_id:
            role = 'is_issuer'
            self.is_issuer = True
        if self.receiver_id.id == user_id:
            role = 'is_receiver'
        if self.receiver_id.id == self._uid & self.sender_id.id == self._uid:
            role = 'selfpayment'
        # print role
        return role

    @api.multi  # OLD
    def prepare_move(self,  action, context=None):
        # Generate the specified transfer
        partner_obj = self.pool.get('res.partner')
        move_obj = self.pool.get('account.move')
        company_obj = self.pool.get('res.company')
        config = self.pool.get('ir.model.data').get_object(
            'base_exchange', 'exchange_settings'
        )

    @api.multi  # OLD
    def get_skip_confirm(self, transaction, context=None):
        # Check is there is an external currency, to determine whether
        # we should go to confirm or paid state
        config_currency_obj = self.pool.get('exchange.config.accounts')

        currency_ids = []
        for currency in transaction.currency_ids:
            currency_ids.append(currency.currency_id.id)
        config_currency_ids = config_currency_obj.search(
            [('currency_id', 'in', currency_ids)]
        )

        skip_confirm = True
        for config_currency in config_currency_obj.browse(
                config_currency_ids
        ):
            if config_currency.external_currency:
                skip_confirm = False
        return skip_confirm

    @api.multi  # OLD
    def refund(self,  fields, context=None):
        # Sends a refund transaction to the Creditor
        move_obj = self.pool.get('account.move')
        date = datetime.now().strftime("%Y-%m-%d")
        for transaction in self.browse( context=context):

            for move_field in fields:
                move = getattr(transaction, move_field + '_id')
                if move:
                    flag = 'cancel_' + move_field
                    reversal_move_id = move_obj.create_reversals(
                        [move.id], date
                    )[0]
                    move_obj.post([reversal_move_id])
                    move_obj.write([reversal_move_id], {
                        'wallet_action': flag,
                        'wallet_transaction_id': transaction.id
                    }, context=context)
                    self.write(
                        [transaction.id],
                        {move_field + '_id': False}, context=context
                    )
                    self.reconcile(
                        [move.id, reversal_move_id], context=context
                    )

# ****************************************************************************
 #   Model Definition Transactions
    _name = 'exchange.transaction'
    _description = 'Exchange Transactions'
    _inherit = ['mail.thread']
    _order = 'emission_date'
 #   Track the status of the transaction to mail.thread

 #   _track = 'state', 'account_wallet.mt_transaction_state': lambda self,
 #           obj, ctx=None: obj.already_published,

    name = fields.Char(
        'Number', size=30, required=True)
        # TBD       default=tr_number_calc('type_id'))
    account_from_id = fields.Many2one(
        'exchange.accounts', 'Account From', required=True, track_visibility='onchange')
    account_to_id = fields.Many2one(
        'exchange.accounts', 'Account To', required=True, track_visibility='onchange')
    type_id = fields.Many2one(
        'exchange.transaction.type', 'Transactions Type', required=True)
    line_ids = fields.One2many(
        'exchange.transaction.line', 'transaction_id',  'Transfer Lines', required=False)
    emission_date = fields.Datetime(
        'Emission Date', required=True, default=datetime.now().strftime("%Y-%m-%d"))
    transaction_date = fields.Datetime(
        'Transaction Date', required=False)
    emission_from = fields.Many2one(
        'res.partner', 'Issued from',
        default=lambda self: self.env['exchange.model'].user_partner)
    amount_from = fields.Float(
        'Amount from Sender', required=True)
    # TBD: should be computed out of exchange rates in res.currency
    amount_to = fields.Float(
        'Amount to Receiver', required=True)


    state = fields.Selection(
            [
                ('draft', 'Draft'),
                ('sent', '⌛Sent'),
                ('invoiced', '⌛Invoiced'),
                ('paid', 'Paid'),
                ('refunded', 'Refunded'),
                ('denied', 'Denied'),
                ('canceled', 'Cancelled'),
            ], 'Status', readonly=False, default='draft', required=True, track_visibility='onchange')

    is_fee = fields.Boolean(
        'Transaction has fees')
    is_invoice = fields.Boolean(
        'Invoice Transaction')

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
        readonly=True, store=True)
    ext_to = fields.Boolean('To external Account',
        related='account_to_id.external_db',
        readonly=True)
    type_prefix_from = fields.Many2one('exchange.account.type',
        'Prefix from', related='type_id.type_prefix_from',
        readonly=True)
    type_prefix_to = fields.Many2one('exchange.account.type',
        'Prefix to', related='type_id.type_prefix_to',
        readonly=True)

    # TBD Computed fields (not stored in DB)
    user_role = fields.Char(
         'User role', store= False,
         compute='_get_user_role', track_visibility='onchange')

# TO CHECK !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#    is_issuer = fields.Boolean(
#         'Is Issuer', store= True,
#         compute='_compute_is_issuer')

#    @api.one
#    @api.depends ('sender_id')
#    def _compute_is_issuer(self):
#        issuer = False
#        user_id = 1
#        #    self.env['res.users'].search(['partner_id', '=', self.sender_id.id])
#        print self.env.cr
#        print self.sender_id.id, user_id, self._uid
#        if user_id == self._uid:
#            issuer = True
#            self.is_issuer = True
#        print issuer
#        return True
