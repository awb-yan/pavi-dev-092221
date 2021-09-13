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
        
        # plan type flow routing
        if plan_type == 'Postpaid':
            add_to_timebank = self._provision_postpaid(record, last_subscription)
        else:
            add_to_timebank = self._provision_prepaid(record, last_subscription)

        # facility type routing
        if aradial_flag:
            self._activate(record, main_plan, max_retries, add_to_timebank)


        self._start_subscription(record)
        self._generate_atmref(record)
            
       
    # TODO: Yan - update Postpaid provisioning
    def _provision_postpaid(self, record, last_subscription):
        if not last_subscription:
            _logger.info('first')
            # Welcome Provisioning Notification
        else:
            _logger.info('last')
            # Returning Subscriber Notification
            # Check if still active, handle multiple active subs for postpaid
        return 0


    def _provision_prepaid(self, record, last_subscription):
        _logger.info('provision prepaid')
        
        if not last_subscription:
            _logger.info('first subs')
            remaining_seconds = 0
            # Welcome Provisioning Notification
            # self._send_welcome_message(recordset=record, template_name="Subscription Welcome Notification", state="In Progress")
        else:
            # CTP Provisioning Notification
            # Check if still active, query remaining days in aradial
            remaining_seconds = self.env['aradial.connector'].get_remaining_time(last_subscription.opportunity_id.jo_sms_id_username)
        
        return remaining_seconds

   
    def _set_to_draft(self, record):
        _logger.info(' === set_to_draft ===')
        self.record = record

        self.record['stage_id'] = self.env['sale.subscription.stage'].search([("name", "=", "Draft")]).id
        self.record['in_progress'] = False
        self.env.cr.commit()

    def _send_to_aradial(self, record, main_plan, max_retries, additional_time):
        _logger.info('send to aradial')
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
                'CustomInfo1': record.code,                         # subscription_ code
                'CustomInfo2': record.subscriber_location_id.name,  # zone
                'CustomInfo3': record.customer_number,          # customer_id
                'Offer': main_plan.default_code.upper(),
                # 'StartDate': record.date_start.strftime("%m/%d/%Y, %H:%M:%S"),                 # subscription start date
                'Status': 0,                                    # 0 – Active, 1 – Canceled, 2 – Pending, 3 – Suspended
                'FirstName': first_name,
                'LastName': last_name,
                'ServiceType': 'Internet',
                'TimeBank': additional_time, # get the seconds
                'UseTimeBank': 1
            }

            _logger.info(self.data)

            if not self.env['aradial.connector'].create_user(self.data):
                raise Exception
        except:
            if max_retries > 1:
                self._send_to_aradial(record, main_plan, max_retries-1, additional_time)
            else:
                _logger.info('Add to Failed transaction log')
                #throw another exception

    def _start_subscription(self, record):

        _logger.info(' === start subs ===')

        try:
            self.record = record;
            now = datetime.now().strftime("%Y-%m-%d")
            self.record.write({
                'date_start': now,
                'stage_id': self.env['sale.subscription.stage'].search([("name", "=", "In Progress")]).id,
                'in_progress': True
            })
        except:
            _logger.error(f'Error encountered while starting subscription for {self.record.code}..')


    def _generate_atmref(self, record):

        _logger.info(' === _generate_atmref() ===')
        try:
            self.record = record
            # company_id = vals.get('company_id')
            company = self.record.company_id
            # company = self.env['res.company'].search([('id', '=', company_id)])

            code_seq = company.company_code.filtered(
                lambda code: code.is_active == True
            )

            if not code_seq:
                raise UserError("No Active company code, Please check your company code settings")

            self.record.write({
                'atm_ref_sequence': code_seq[0]._get_seq_count()
            })

            # vals['atm_ref_sequence'] = code_seq[0]._get_seq_count()
        except:
            _logger.error('Error encountered while generating atm reference for subscription {self.record.code}..')

    def _activate(self, record, main_plan, max_retries, add_to_timebank):
        _logger.info(' === activate ===')
        self._send_to_aradial(record, main_plan, max_retries, add_to_timebank)