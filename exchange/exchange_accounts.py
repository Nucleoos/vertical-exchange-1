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

from openerp import models, fields
from openerp.exceptions import except_orm

#    List of Accounts for members and the system
#    help='If ledger are used for an exchange system')

class ExchangeAccounts(models.Model):

    _name = 'exchange.accounts'
    _description = 'Exchange Accounts'
    _order = 'sequence,name'

    name = fields.Char('Name', size=64,required=True)
    # TBD should be computed field out of 'number_prefix' & 'GeneratedNumber' & 'currency_id'
    number = fields.Char(
        'Account Number', required=True,
        size=16, help='Number of the Account', default='CH-XX-123456')
    desc = fields.Text('Description')
    template_id = fields.Many2one(
        'exchange.config.accounts', 'Account Template ID', required=True)
#   TBD this related items do force a key error (exchange)!!!
#    account_type = fields.Many2one(string='Account Type',
#        related='exchange.config.accounts.account_type')
#    external_currency = fields.Boolean(string='External currency',
#        related='exchange.config.accounts.external_currency')
#    currency_id = fields.Char(string='Currency',
#        related='exchange.config.accounts.currency_id')

    partner_id = fields.Many2one(
        'res.partner', 'Partner', ondelete='cascade',
         help='If account type is not system')
    limit_negative = fields.Boolean('Limit - ?')
    limit_negative_value = fields.Float(
        'ValueLimit -')
    limit_positive = fields.Boolean('Limit + ?')
    limit_positive_value = fields.Float(
        'Value Limit +')
    available = fields.Float('Available')
    reserved = fields.Float('Reserved')




