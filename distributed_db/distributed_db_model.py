# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Lucas Huber
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
import openerp.addons.decimal_precision as dp


class ExchangeConfigSettings(orm.Model):
    """
    Add Exchange configuration (parameters) to community settings
    """

    _inherit = 'exchange.config.settings'

    _columns = {
      'par_res1': fields.integer
        ('Parameter 01 Reserve'
         , help="Reserve Parameter"
         ),
        'par_PUL_to_credit_ratio': fields.integer
        ('PUL to Credit Sum ratio (0-150%)'
         , help="Ratio of the sum of all credits in circulation and the sum "
                "of the Private User Liquidity (PUL) (normally 100%). This "
                "parameter does not affect the ledger directly, but the Credit "
                "limits of the Private User. This will increase the liquidity in "
                "the system."
         ),
        'par_credit_discount': fields.float
        ('Credit Discount (0.0-10%)'
         , help="If this parameter is greater than 0 the business users don’t"
                " have to pay back the full credit sum. It will be reduced to"
                " the percent value of this parameter each month. This will "
                "increase the liquidity in the system."
         ),
        'par_credit_fee': fields.float
        ('Credit creation fee'
         , help="Percentage of KNA credit creation fee for business credit per"
                " month (not discharged from Business User Account)"
         ),
        'par_KIX_chng_delayed_credit': fields.float
        ('KIX change delayed proceeding(0.0-10%)'
         , help="KIX change for normal/delayed proceeding of credit"
         ),
        'par_KIX_chng_default_credit': fields.float(
            'KIX change for defaulted proceeding(0.0-10%)'
         , help="KIX change for defaulted proceeding of credit"
         ),
        'par_res2': fields.float
        ('Parameter 02 Reserve'),
    }

