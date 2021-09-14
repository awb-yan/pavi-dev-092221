# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime
import requests
import json

import logging

_logger = logging.getLogger(__name__)


class SubscriptionDisconnect(models.Model):
    _inherit = "sale.subscription"

    def disconnect(self, last_subscription):

        params = self.env['ir.config_parameter'].sudo()
        base_url = params.get_param('web.base.url')
        login = params.get_param('odoo_user_login')
        password = params.get_param('odoo_user_password')
        database = params.get_param('odoo_database')

        #OAuth

        AUTH_URL = base_url + '/auth/'
        headers = {'Content-type': 'application/json'}

        data = {
            "jsonrpc": "2.0",
            'params': {
                'login': login,
                'password': password,
                'db': database
            }
        }        

        res = requests.post(
            AUTH_URL,
            data=json.dumps(data),
            headers=headers
        )

        session_id = res.json().get("result").get("session_id")

        # Disconnect Last Active Subscription
        params = {'session_id': session_id}
        data = {
            'params': {
                'channel': 'od',
                'discon_type': 'SYSV',
                'subscriptions': [
                    {'code': last_subscription.code, 'smsid': last_subscription.opportunity_id.jo_sms_id_username}
                    # {'code': 'SUB098', 'smsid': 'CMurillo'}
                ]
            }
        }

        # SYSV
        # SYSI_EXPIRY
        # SYSI_BANDWIDTH
        # SYSI_NONPAYMENT
        # PHYI_NONPAYMENT
        # PHYV


        DISCON_URL = base_url + '/api/subscription/disconnection/'

        res = requests.patch(
            DISCON_URL, 
            data=json.dumps(data), 
            headers=headers,
            params=params
        )

        _logger.info(res.json())
