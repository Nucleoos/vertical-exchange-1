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

# from openerp import SUPERUSER_ID
# from openerp.tools.translate import _


class ResPartner(models.Model):

    """
    Add some field in partner to use for Exchange
    """

    _inherit = 'res.partner'

    presentation = fields.Text('About me/us')
    show_phone = fields.Boolean('Show phone to others members?')
    exchange_group = fields.Selection([
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
        ],
        readonly=False, track_visibility='onchange',
        help="Role of User in Exchange")
    state = fields.Selection([
        ('application', 'Application'),
        ('open', 'Active'),
        ('blocked', 'Blocked'),
        ('closed', 'Closed'),
        ], 'Membership Status', readonly=False,
        required=True, default='open', track_visibility='onchange',
        help="Status of Account"
             "Blocked, for temporary blocking transactions")
    exchange_user_code = fields.Char(
        'Exchange Code', compute='_compute_code',
        readonly=False, store=True)

    @api.one
    def _member_state(self, ids):
        res = {}
        for id in ids:
            record = self.browse()
            res.update({id:record.membership_state})
        return res

    member_state = fields.Char(
        compute='_member_state',
        store=False)
    membership_type = fields.Many2one('product.product',
        'Membership Type', related='member_lines.membership_id',
         readonly=True, store=True,
         help="Membership Type from Products")


    @api.depends('exchange_group')
    def _compute_code(self):
       # TBD code = str(exchange.config.accounts.code)
        code = 'CH-EXC1'
        partid = '0011'

        type1 = str(code + '-' + partid)
        print partid, type1
        return type1

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

    @api.onchange('res.users.groups_id')
    def _get_user_role(self):
        # Control the access rights of the current user

        if self.pool.get('res.users').has_group(
                'base_exchange.group_exchange_user'):
                self.exchange_group = 'user'
        if self.pool.get('res.users').has_group(
                'base_exchange.group_exchange_moderator'):
                self.exchange_group = 'moderator'
        if self.pool.get('res.users').has_group(
                'base_exchange.group_exchange_admin'):
                self.exchange_group = 'admin'
        return