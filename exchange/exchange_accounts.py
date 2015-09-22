# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Lucas Huber, Copyright: CoĐoo Project
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
import openerp.addons.decimal_precision as dp

#    List of Accounts for members and the system
#    help='If ledger are used for an exchange system')

class ExchangeAccounts(models.Model):

    @api.onchange('template_id')
    def _get_creditlimit(self):
        print self
        limitout = 9.0
        # template_id.limit_positive_value
        limitout = self.env['exchange.config.accounts'].browse(self._context.get('limit_positive_value'))
        print limitout
        self.limit_positive_value = limitout


    _name = 'exchange.accounts'
    _description = 'Exchange Accounts'
    _order = 'template_id,partner_id,name'

    name = fields.Char('Account Name', size=64,required=True)
    # TBD should be computed field out of 'number_prefix' & 'GeneratedNumber' & 'currency_id'
    number = fields.Char(
        'Account Number', required=True,
        size=16, help='Number of the Account', default='CH-XX-123456')
    desc = fields.Text('Description')
    template_id = fields.Many2one(
        'exchange.config.accounts', 'Account Template',
        track_visibility='onchange', required=True)
    partner_id = fields.Many2one(
        'res.partner', 'Partner', ondelete='cascade',
         help='If account type is not system')
    limit_negative = fields.Boolean('Limit - ?')
    limit_negative_value = fields.Float(
        'Credit Limit -', default=0.0)
    limit_positive = fields.Boolean('Limit + ?')
    limit_positive_value = fields.Float(
        'Account Limit +')

    state = fields.Selection([
        ('open', 'Open'),
        ('blocked', 'Blocked'),
        ('closed', 'Closed'),
    ], 'Account Status', readonly=False,
        required=True, default='open', track_visibility='onchange',
        help="Status of Account"
             "Blocked, for temporary blocking transactions")
    # Related fields (stored in DB)
    type_prefix = fields.Many2one('exchange.account.type',
        'Account Type Prefix', related='template_id.type_prefix',
         readonly=True, store=True)
    external_db = fields.Boolean(
        'External DB', related='template_id.external_db',
         readonly=True, store=True,
         help="Account is performing transactions on an a outside DB/ledger")

    default_account = fields.Boolean(
        'Default account', related='template_id.default_account',
         readonly=True, store=True)
    currency_base = fields.Many2one('res.currency',
        'Currency', related='template_id.currency_id',
         readonly=True)

    exchange_rate = fields.Float(
        'Exchange Rate', related='template_id.exchange_rate',
         readonly=True)
        # TBD Error to many vaules     readonly=True, store=True)
#    user_id = fields.Char('res.users',
#         'User ID', related='partner_id.id',
#        readonly=True)
    with_messaging = fields.Boolean(
        string='Messaging', related='template_id.with_messaging',
        readonly=True)

    # Computed fields
    # Next 2 fields are TBD
    available = fields.Float(
        'Available', store=False,
        compute='_get_available_amount')
    balance = fields.Float(
        'Account Balance', store=False,
        compute='_get_balance')
    reserved = fields.Float('Reserved')

    @api.one
    def do_account_deblock(self):
        self.state = 'open'

    @api.one
    def do_account_block(self):
        self.state = 'blocked'

    @api.one
    def do_account_close(self):
        self.state = 'closed'

    @api.one
    @api.depends('balance','limit_negative_value') # computed field available calculate
    def _get_available_amount(self):

         for record in self:
             record.available = self.balance - self.limit_negative_value

    @api.one # computed field balance calculate
    def _get_balance(self):

        self.balance = 100.0


#    @api.one
#    @api.constrains('account_type', 'partner_id', 'number')
#    def _check_application(self):
#        """
#        Check that the Account are single then other as user accounts
#        """
#        if self.account_type != user
#                self.account_type.id:
#            raise except_orm(_('Data error!'),
#                             _("Only user accounts can have more than one per type"))
#        else
#                self.partner_id.id:
#            raise except_orm(_('Data error!'),
#                             _("Only one user accounts per type"))

class AccountTypesType(models.Model):

    # Lines containing the list of accounts types
    _name = 'exchange.account.type'
    _description = 'Exchange Accounts Types list'

    name = fields.Char(
       'Account Type Key', required=True, size=2, default="XX",
       help="Account key examples"
            "PD Private User Default account"
            "PU Private User sub-account"
            "BD Business User Default account"
            "BC Business User Credit account"
            "SY System account")
    account_name = fields.Char(
       'Account name', size=32, required=True,
       translate=True, default='XY User account',
       help="Name of the Account")
    account_desc = fields.Char(
       'Account Type Description',required=False,
       help='Description')

    _sql_constraints = [
        ('typename_unique', 'unique(name)',
        'We can only have one line per name'),
        ('account_name_unique', 'unique(account_name)',
        'We can only have one line per key'),
    ]


class AccountTemplateConfig(models.Model):

    # Lines containing the general configuration for accounts types

    _name = 'exchange.config.accounts'
    _description = 'Exchange Account Type/Template configuration'
    name = fields.Char(
        'Account Name', required=True, size=40, translate=True,
        help='Name of the Account')

    account_type = fields.Selection([
        ('user', 'User account'),
        ('system', 'System account'),
        ('clearing', 'Clearing account'),
        ('rating', 'Rating account'),
    ], 'Account Type', readonly=False,
        required=True, default='user', track_visibility='onchange',
        help="Type of account /n"
             "User Account, belongs to a user"
             "System Account, belongs to the system or organisation"
             "Clearing Account, belongs to the system or organisation")

    type_prefix = fields.Many2one(
        'exchange.account.type', 'Account Number Prefix/Type', required=False, size=2,
        help="Prefix for Number of the Accounts"
             "in last part of the 21 digits Account Code")

    config_id = fields.Many2one(
        'exchange.config.settings', 'Config ID', required=True)

    accounts_ids = fields.One2many(
        'exchange.accounts', 'template_id', 'Related accounts',
        help='Related accounts for transactions')

    hidden = fields.Boolean(
        'Hidden Account',
        help='Account is hidden to users')

    with_messaging = fields.Boolean(
        'Messaging',
        help='Account allows Messaging')

    default_account = fields.Boolean(
        'Default Account',
        default=False,
        help='This account will be used/attached for new users of the group')

    # TBD Filter on Many2one   about 'product.public.category' = Membership
    membership_type = fields.Many2one(
        'product.product', 'Type of membership', required=False,
        help='For this of membership the accounts will be used')

    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True)

    limit_negative = fields.Boolean('Limit - ?')
    limit_negative_value = fields.Float(
        'ValueLimit -', default=-500.0)

    limit_positive = fields.Boolean('Limit + ?')
    limit_positive_value = fields.Float(
        'Value Limit +', default=500.0)

    account_id = fields.Many2one(
        'account.account', 'Related account', required=False,
        help='Related account for Odoo Accounting purpose')

    external_db = fields.Boolean(
        'External DB',
        help='Check if an outside transaction engine exists')

    external_ledger_id = fields.Many2one(
        'distributed.db.list', 'External Ledger ID')

    initcredit = fields.Float(
        'Initial amount of currency',
        help='Initial amount currency of User gets on this account')
    initcredit_type = fields.Many2one(
        'exchange.transaction.type',
        'Initial credit transaction type')
    # Related fields (not stored in DB)
    # TBD add field name

    exchange_rate = fields.Float(
        'Exchange Rate', related='currency_id.rate',
        readonly=True)

  #       readonly=True, digits=lambda cr:(16, 2))
  #       digits=dp.get_precision('Account')

    _sql_constraints = [
        ('name', 'unique(name)',
        'We can only have one line per name'),
        ('default_account', 'unique(membership_type,default_account)',
        'We can only have one default account per type'),
    ]



#TBD    @api.one
#    @api.constrains('account_type', 'membership_type', 'default_account')
#    def _check_application(self):
#        """
#        Check that the Account are single then other as user accounts
#        """
#        if self.account_type != user
#                self.account_type.id:
#            raise except_orm(_('Data error!'),
#                             _("Only user accounts can have more than one per type"))
#        else
#                self.membership_type.id:
#            raise except_orm(_('Data error!'),
#                             _("Only one user accounts per type"))

    '''
    def update_all_partners(self, cr, uid, context=None):
        # Update balances on all partners
        partner_obj = self.pool.get('res.partner')
        partner_ids = partner_obj.search(cr, uid, [], context=context)
        partner_obj.update_wallet_balance(
            cr, uid, partner_ids, context=context
        )

    def create(self, cr, uid, vals, context=None):
        # Mark the currency as wallet and then
        # update balance on all partners at creation
        self.pool.get('res.currency').write(
            cr, uid, [vals['currency_id']], {'exchange_currency': True},
            context=context
        )
        res = super(AccountTypesConfig, self).create(
            cr, uid, vals, context=context
        )
        self.update_all_partners(cr, uid, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        # Update balance on all partners when modified
        res = super(AccountTypesConfig, self).write(
            cr, uid, ids, vals, context=context
        )
        self.update_all_partners(cr, uid, context=context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        # Remove the wallet flag on the currency
        # and then update balance on all partners
        for currency in self.browse(cr, uid, ids, context=context):
            self.pool.get('res.currency').write(
                cr, uid, [currency.currency_id.id],
                {'exchange_currency': False}, context=context
            )
        res = super(AccountTypesConfig, self).unlink(
            cr, uid, ids, context=context
        )
        self.update_all_partners(cr, uid, context=context)
        return res
    '''

