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

    def physical_discon(self):
        _logger.info(f'Get all subs ending today - 6 months')

        main_plan = None
        sf_update_type = 5
        max_fail_retries = 3
        subscription_to_discon = []

        # 1. get date today - 6 months
        date_to_discon = datetime.now() + relativedelta(months=-6)
        # 2. get subs with end date equals to the result of #1
        subs = self.env['sale.subscription'].search([('subscription_status', '=', 'disconnection'), 
            ('subscription_status_subtype', '=', 'disconnection-temporary'), 
            ('end_datetime', '>=', date_to_discon.strftime("%Y-%m-%d 00:00:00")), 
            ('end_datetime', '<=', date_to_discon.strftime("%Y-%m-%d 11:59:59"))])
        # 3. loop thru the list of subscriptions
        for sub in subs:
        #     3a. get latest subs based on customer id
            customer_id = sub.customer_number
            latest_subs = self.env['sale.subscription'].search([('customer_number', '=', customer_id)], order='id desc', limit = 1)
        #     3b. if the one on the list is latest, issue physical discon
            if sub.id == latest_subs.id:
                subscription_to_discon += sub
        
        if len(subscription_to_discon) > 0:
            for sub in subscription_to_discon:
                self._change_status_subtype(sub,'disconnection-permanent')
        #     3c. update SF
                _logger.info(f'SMS:: Update Account in SF - Update Type {sf_update_type} on Subscription code {sub.code}')
                # try:
                #     self._update_account(main_plan, sub, sf_update_type, max_fail_retries)
                # except:
                #     _logger.error(f'SMS:: !!! Failed to Update Account in SF - Update Type {sf_update_type} on Subscription code {sub.code}')


    def _get_discon_type(self, discon_type, channel):
        types = {
            "sysv": {
                "sf": {"name": "Salesforce", "value": "System, Voluntary"},
                "od": {"name": "Odoo", "value": "disconnection-temporary"},
                "ar": {"name": "Aradial", "value": ""},
                "subs_closed": False,
                "desc": "Subscriber Request",
                "function": "_change_status_subtype"
            },
            "sysi_expiry": {
                "sf": {"name": "Salesforce", "value": "System, Involuntary"},
                "od": {"name": "Odoo", "value": "disconnection-temporary"},
                "ar": {"name": "Aradial", "value": ""},
                "subs_closed": True,
                "desc": "Promo Expiry",
                "function": "_change_status_subtype"
            },
            "sysi_bandwidth": {
                "sf": {"name": "Salesforce", "value": "System, Involuntary"},
                "od": {"name": "Odoo", "value": "disconnection-temporary"},
                "ar": {"name": "Aradial", "value": ""},
                "subs_closed": False,
                "desc": "Bandwidth Usage Exceeded",
                "function": "_change_status_subtype"
            },
            "sysi_nonpayment": {
                "sf": {"name": "Salesforce", "value": "System, Involuntary"},
                "od": {"name": "Odoo", "value": "disconnection-temporary"},
                "ar": {"name": "Aradial", "value": ""},
                "subs_closed": False,
                "desc": "Billing Non-Payment",
                "function": "_change_status_subtype"
            },
            "phyi_nonpayment": {
                "sf": {"name": "Salesforce", "value": "Physical, Involuntary"},
                "od": {"name": "Odoo", "value": "disconnection-permanent"},
                "ar": {"name": "Aradial", "value": ""},
                "subs_closed": False,
                "desc": "Billing Non-Payment",
                "function": "_change_status_subtype"
            },
            "phyv": {
                "sf": {"name": "Salesforce", "value": "Physical, Voluntary"},
                "od": {"name": "Odoo", "value": "disconnection-permanent"},
                "ar": {"name": "Aradial", "value": ""},
                "subs_closed": False,
                "desc": "Subscriber Request",
                "function": "_change_status_subtype"
            },
        }

        discon_type = types.get(discon_type)
        if discon_type:
            value = discon_type.get(channel)
            if value:
                return {
                    "name": value.get("name"),
                    "status": value.get("value"),
                    "subs_closed": discon_type.get("subs_closed"),
                    "description": discon_type.get("desc"),
                    "executable": discon_type.get("function")
                }

        return False

    def _change_status_subtype(self, records, status, is_closed_subs = False, executed=False, ctp=False):
        _logger.info('function: _change_status_subtype')
        for record in records:
            if (
                record.subscription_status != "disconnection"
                or record.subscription_status_subtype != status
            ):
                if is_closed_subs:
                    record.write({
                        "subscription_status": "disconnection",
                        "subscription_status_subtype": status,
                        "stage_id" : self.env['sale.subscription.stage'].search([("name", "=", "Closed")]).id,
                        "in_progress": False
                    })
                else:
                    record.write({
                        "subscription_status": "disconnection",
                        "subscription_status_subtype": status
                    })
                executed = True
                if not ctp:
                    self._send_expirynotification(record)

        return executed

    def _send_expirynotification(self, record):
        try:            
            _logger.info(f'=== Sending Expiry Notification ===')
            _logger.debug(f'=== record {record} ===')
            self.env["awb.sms.send"]._send_subscription_notif(
                recordset=record,
                template_name="Subscription Expiry Notification",
                state="In Progress" 
            )
            _logger.debug('Completed Sending Expiry Notification')
        except:
            _logger.warning('!!! Error sending Expiry Notification')
