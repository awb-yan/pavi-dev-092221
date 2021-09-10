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

    def provision_and_activate(self, record, last_subscription):
        max_retries = 3
        self.record = record
        self._set_to_draft(record)
        main_plan = self._get_mainplan(record)
        plan_type = main_plan.sf_plan_type.name
        aradial_flag = main_plan.sf_facility_type.is_aradial_product
        
        # plan type flow routing
        if plan_type == 'Postpaid':
            add_to_timebank = self._provision_postpaid(record, last_subscription)
        else:
            add_to_timebank = self._provision_prepaid(record, last_subscription)

        # facility type routing
        if not aradial_flag:
            return True
        else:
            self._activate(self, record, main_plan, max_retries, add_to_timebank)
       
    # TODO: Yan - update Postpaid provisioning
    def _provision_postpaid(self, record, last_subscription):
        if(last_subscription is None):
            _logger.info('first')
            # Welcome Provisioning Notification
        else:
            _logger.info('last')
            # Returning Subscriber Notification
            # Check if still active, handle multiple active subs for postpaid
        return True


    def _provision_prepaid(self, record, last_subscription):
        if not last_subscription:
            _logger.info('first subs')
            # Welcome Provisioning Notification
        else:
            # CTP Provisioning Notification
            # Check if still active, query remaining days in aradial
            # Kung derived, dapat may laman yung end date ng line item ta dun nalnag mag-minus
            # kung galing Aradial, jusko paano?

            remaining_days = self.env['aradial.connector'].get_remaining(last_subscription.sms_id.username)
        
        return remaining_days

   
    def _set_to_draft(self, record):
        _logger.info(' === set_to_draft ===')
        self.record = record

        self.record['stage_id'] = self.env['sale.subscription.stage'].search([("name", "=", "Draft")]).id
        self.record['in_progress'] = False
        self.env.cr.commit()

    def _get_mainplan(self, record):
        _logger.info(' === get_mainplan ===')

        for line_id in record.recurring_invoice_line_ids:
            # if line_id.product_id.product_tmpl_id.product_segmentation == 'month_service':
            main_plan = line_id.product_id.product_tmpl_id

        return main_plan  

    def _send_to_aradial(self, record, main_plan, max_retries, additional_days):
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
                'FirstName': first_name,
                'LastName': last_name,
                'Address1': record.partner_id.street,
                'Address2': record.partner_id.street2,
                'City': record.partner_id.city,
                'State': record.partner_id.state_id.name,
                'Country': record.partner_id.country_id.name,
                'Zip': record.partner_id.zip,
                'Offer': main_plan.default_code.upper(),
                'ServiceType': 'Internet',
                'CustomInfo1': main_plan.sf_facility_type.name,
                'CustomInfo2': main_plan.sf_plan_type.name,
                'CustomInfo3': record.partner_id.customer_number,
                'CustomInfo4': record.code,
                'TimeBank': additional_days * 86400, # get the seconds
                'UseTimeBank': 1
            }

            if not self.env['aradial.connector'].create_user(self.data):
                raise Exception
        except:
            if max_retries > 1:
                self._send_to_aradial(record, main_plan, max_retries-1, additional_days)
            else:
                _logger.info('Add to Failed transaction log')

    def _start_subscription(self, record):

        _logger.info(' === _activate() ===')

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
        _logger.info(' === activation() ===')
        self._send_to_aradial(record, main_plan, max_retries, add_to_timebank)
        self._start_subscription(record)
        self._generate_atmref(record)
   