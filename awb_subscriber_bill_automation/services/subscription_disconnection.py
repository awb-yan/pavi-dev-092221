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

    def prepaid_physical_discon(self):
        _logger.info(f'Get all subs ending today - 6 months')

        # YANYAN
        # search for contacts with expiry_date = today
        sf_update_type = 5
        max_fail_retries = 3
        main_plan = None
        date_to_discon = datetime.now()
        contacts_to_discon = self.env['res.partner'].search([('expiry_date', '>=', date_to_discon.strftime("%Y-%m-%d 00:00:00")), 
            ('expiry_date', '<=', date_to_discon.strftime("%Y-%m-%d 11:59:59"))])
        # search for the subscription using the customer_number
        for contact in contacts_to_discon:
            latest_subs = self.env['sale.subscription'].search([('customer_number', '=', contact.customer_number)], order='id desc', limit=1)
            self._change_status_subtype(latest_subs,'disconnection-permanent', is_closed_subs = True)
            _logger.info('FOR UPDATE IN SF')
            # try:
            #     self._update_account(main_plan, latest_subs, sf_update_type, max_fail_retries)
            # except:
            #     _logger.error(f'SMS:: !!! Failed to Update Account in SF - Update Type {sf_update_type} on Subscription code {latest_subs.code}')



        # permanent discon
        # update SF


        # # 1. get date today - 6 months
        # date_to_discon = datetime.now() + relativedelta(days=-int(prepaid_days))
        # _logger.info(f'Date to Disconnect: {date_to_discon}')
        # # 2. From Contacts, get all prepaid contacts with last_reload_date equal to date_to_discon and disconnection date is empty
        # subscribers = self.env['res.partner'].search([('last_reload_date', '>=', date_to_discon.strftime("%Y-%m-%d 00:00:00")), 
        #     ('last_reload_date', '<=', date_to_discon.strftime("%Y-%m-%d 11:59:59"))])
        # _logger.info(f'Subscribers to Disconnect: {subscribers}')

        # for subscriber in subscribers:
        #     subscription_to_discon.append(subscriber.customer_number)
        # # 3. Update disconnection date and then call SF Update Account
        # subscriptions = self.env['sale.subscription'].search([('customer_id', 'in', subscription_to_discon)])



        # OLD IMPLEM
        # main_plan = None
        # sf_update_type = 5
        # max_fail_retries = 3
        # subscription_to_discon = []
        # 1. get date today - 6 months
        # date_to_discon = datetime.now() + relativedelta(monmths=-6)
        # # 2. get subs with end date equals to the result of #1
        # subs = self.env['sale.subscription'].search([('subscription_status', '=', 'disconnection'), 
        #     ('subscription_status_subtype', '=', 'disconnection-temporary'), 
        #     ('end_datetime', '>=', date_to_discon.strftime("%Y-%m-%d 00:00:00")), 
        #     ('end_datetime', '<=', date_to_discon.strftime("%Y-%m-%d 11:59:59"))])
        # # 3. loop thru the list of subscriptions
        # for sub in subs:
        # #     3a. get latest subs based on customer id
        #     customer_id = sub.customer_number
        #     latest_subs = self.env['sale.subscription'].search([('customer_number', '=', customer_id)], order='id desc', limit = 1)
        # #     3b. if the one on the list is latest, issue physical discon
        #     if sub.id == latest_subs.id:
        #         subscription_to_discon += sub
        
        # if len(subscription_to_discon) > 0:
        #     for sub in subscription_to_discon:
        #         self._change_status_subtype(sub,'disconnection-permanent')
        # #     3c. update SF
        #         _logger.info(f'SMS:: Update Account in SF - Update Type {sf_update_type} on Subscription code {sub.code}')
        #         # try:
        #         #     self._update_account(main_plan, sub, sf_update_type, max_fail_retries)
        #         # except:
        #         #     _logger.error(f'SMS:: !!! Failed to Update Account in SF - Update Type {sf_update_type} on Subscription code {sub.code}')


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
