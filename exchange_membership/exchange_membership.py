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

# from lxml import etree
# from lxml.builder import E
from openerp import models, fields, api
from openerp.osv import fields, orm
# from openerp import SUPERUSER_ID
# from openerp.tools.translate import _


class ResPartner(orm.Model):

    """
    Add some field in partner to use for Exchange
    """

    _inherit = 'res.partner'

    _columns = {
    'state' : fields.selection([
        ('application', 'Application'),
        ('open', 'Open'),
        ('blocked', 'Blocked'),
        ('closed', 'Closed'),
        ], 'Membership Status', readonly=False,
        required=True, default='open', track_visibility='onchange',
        help="Status of Account"
             "Blocked, for temporary blocking transactions")
    }

    @api.one
    def do_membership_deblock(self):
        self.state = 'open'

    @api.one
    def do_membership_block(self):
        self.state = 'blocked'
#    def do_membership_block(self, cr, uid, context=None):
#        self.state = 'blocked'

    @api.one
    def do_membership_close(self):
        self.state = 'closed'
