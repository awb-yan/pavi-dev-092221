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

import logging

_logger = logging.getLogger(__name__)


class SubscriptionCreate(models.Model):
    _inherit = "sale.subscription"

    def provision_and_activation(self, record, main_plan, last_subscription):
        _logger.info('provision and activation')

        max_retries = 3
        self.record = record

        self._set_to_draft(record)
        plan_type = main_plan.sf_plan_type.name
        aradial_flag = main_plan.sf_facility_type.is_aradial_product
        
        # Plan Type Flow routing
        if plan_type == 'Postpaid':
            add_to_timebank = self._provision_postpaid(record, last_subscription)
        else:
            add_to_timebank = self._provision_prepaid(record, last_subscription)

        # Facility Type routing
        if aradial_flag:
            self._send_to_aradial(record, main_plan, max_retries, add_to_timebank, last_subscription)

        self._start_subscription(record, max_retries)

       
    def _set_to_draft(self, record):
        _logger.info(' === set_to_draft ===')
        self.record = record

        self.record['stage_id'] = self.env['sale.subscription.stage'].search([("name", "=", "Draft")]).id
        self.record['in_progress'] = False
        self.env.cr.commit()


    # TODO: update Postpaid provisioning
    def _provision_postpaid(self, record, last_subscription):
        if not last_subscription:
            _logger.info('first')
            # Welcome Provisioning Notification
        else:
            _logger.info('last')
            # Returning Subscriber Notification

        return 0


    def _provision_prepaid(self, record, last_subscription):
        _logger.info('provision prepaid')
        
        if not last_subscription:
            _logger.info('first subs')
            remaining_seconds = 0

            _logger.info(' === Sending SMS Welcome Notification ===')
            # Welcome Provisioning Notification
            self.env["awb.sms.send"]._send_subscription_notif(
                recordset=record,
                template_name="Subscription Welcome Notification",
                state="Draft"
            )
        else:
            # Check if still active, query remaining days in aradial
            remaining_seconds = self.env['aradial.connector'].get_remaining_time(last_subscription.opportunity_id.jo_sms_id_username)

            # _logger.info(' === Sending SMS CTP Notification ===')
            # # CTP Provisioning Notification
            # self.env["awb.sms.send"]._send_subscription_notif(
            #     recordset=record,
            #     template_name="Subscription Payment Notification",
            #     state="Draft"
            # )

        return remaining_seconds

    def _send_to_aradial(self, record, main_plan, max_retries, additional_time, last_subscription):
        _logger.info('send to aradial')
        # New Subscription
        if not last_subscription:
            try:
                # for Residential
                first_name = record.partner_id.first_name
                last_name = record.partner_id.last_name

                # for Corporate
                if not first_name: 
                    first_name = record.partner_id.name
                    last_name = ''

                self.data = {
                    'UserID': record.opportunity_id.jo_sms_id_username,
                    'Password': record.opportunity_id.jo_sms_id_password,
                    'CustomInfo1': record.code,
                    'CustomInfo2': record.subscriber_location_id.name,
                    'CustomInfo3': record.customer_number,
                    'Offer': main_plan.default_code.upper(),
                    'StartDate': record.date_start.strftime("%m/%d/%Y, %H:%M:%S"),
                    'Status': 0,
                    'FirstName': first_name,
                    'LastName': last_name,
                    'ServiceType': 'Internet',
                    'TimeBank': additional_time,
                    'UseTimeBank': 1
                }

                _logger.info(self.data)

                if not self.env['aradial.connector'].create_user(self.data):
                    raise Exception

            except:
                if max_retries > 1:
                    self._send_to_aradial(record, main_plan, max_retries-1, additional_time, last_subscription)
                else:
                    _logger.error(f'Add to Failed transaction log - Subscription code {record.code}')
                    raise Exception(f'Error Creating user in Aradial for {record.code}')

        else:   # CTP - Update User's TimeBank
            # 2 options to handle this:
            #     1. Update the Offer of the User in Aradial (does it add up the remaining timebank?)
            #     2. Get the remaining time and delete the user in Aradial, create new user with the additional_time

            # self.data = {
            #     'Page': 'UserEdit',
            #     'Modify': 1,
            #     'UserID': record.opportunity_id.jo_sms_id_username,
            #     'Password': record.opportunity_id.jo_sms_id_password,
            #     'Offer': main_plan.default_code.upper(),
            #     'TimeBank': additional_time,
            #     'UseTimeBank': 1
            # }

            # _logger.info(self.data)

            # if not self.env['aradial.connector'].update_user(self.data):
            #     raise Exception
            return True


    def _start_subscription(self, record, max_retries):

        _logger.info(' === start subs ===')

        try:
            self.record = record;
            now = datetime.now().strftime("%Y-%m-%d")
            self.record.write({
                'date_start': now,
                'stage_id': self.env['sale.subscription.stage'].search([("name", "=", "In Progress")]).id,
                'in_progress': True
            })

            # Send activation Notification ----
            _logger.info(' === Sending SMS Activation Notification ===')
            self.env["awb.sms.send"]._send_subscription_notif(
                recordset=self.record,
                template_name="Subscription Activation Notification",
                state="In Progress"
            )
        except:
            if max_retries > 1:
                self._start_subscription(record, max_retries-1)
            else:
                _logger.error(f'Error encountered while starting subscription for {self.record.code}..')
                raise Exception(f'Error encountered while starting subscription for {self.record.code}..')


    def generate_atmref(self, record, max_retries):

        _logger.info(' === _generate_atmref() ===')
        try:
            self.record = record
            company = self.record.company_id

            code_seq = company.company_code.filtered(
                lambda code: code.is_active == True
            )

            if not code_seq:
                raise UserError("No Active company code, Please check your company code settings")

            self.record.write({
                'atm_ref_sequence': code_seq[0]._get_seq_count()
            })

        except:
            if max_retries > 1:
                self._generate_atmref(record, max_retries-1)
            else:
                _logger.error(f'Error encountered while generating atm reference for subscription {self.record.code}..')
                raise Exception(f'Error encountered while generating atm reference for subscription {self.record.code}..')

