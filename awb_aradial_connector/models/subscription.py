# from ..helpers.password_generator import GeneratePassword
from odoo import api, fields, models, exceptions, _
from openerp.exceptions import Warning
from datetime import datetime

import logging

_logger = logging.getLogger(__name__)

class Subscription(models.Model):
    _inherit = 'sale.subscription'

    state = fields.Char("State", compute='_get_stage_name')
    product_names = fields.Char("Products", compute='_get_subs_product_names')
    product_desc = fields.Char("Products Description", compute='_get_subs_product_names')

    # @api.model
    # def create(self, vals):
    #     vals['stage_id'] = self.env['sale.subscription.stage'].search([("name", "=", "Draft")]).id
    #     vals['in_progress'] = False

    #     res = super(Subscription, self).create(vals)
    #     return res

    @api.depends('stage_id')
    def _get_stage_name(self):
        for rec in self:
            rec.state = rec.stage_id.name

    @api.depends('recurring_invoice_line_ids')
    def _get_subs_product_names(self):
        products = []
        desc = []
        for rec in self:
            for line_item in rec.recurring_invoice_line_ids:
                if line_item.product_id.type == 'service':
                    products.append(line_item.display_name)
                    desc.append(line_item.name)  # description
                    desc.append(str(line_item.quantity))
                    if line_item.date_start:
                        desc.append(line_item.date_start.strftime("%b %d, %Y"))
            rec.product_names = ', '.join(products)
            rec.product_desc = ', '.join(desc)

    def create_aradial_user(
        self,
        record=None
    ):
        
        _logger.info("=== ============ ===")
        _logger.info("=== Subscription ===")
        _logger.info(record)
        _logger.info("=== ============ ===")

        if not record:
            raise exceptions.ValidationError(
                ("Record is required")
            )
        self.record = record
        self.data = self._compose_aradial_payload(record)
        
        # is_valid = self._validate_parameters(
        #     record.subscriber_location_id,
        #     record.atm_ref,
        #     record.stage_id.name
        # )

        # if is_valid:
        #     if record.aradial_product: #TODO: for update to actual field name

        #         self.data = self._compose_aradial_payload(record)

        #         _logger.info("User Details:")
        #         _logger.info("UserID: %s" % self.data['UserID'])
        #         _logger.info("Offer: %s" % self.data['Offer'])
        #         _logger.info("First Name: %s" % self.data['FirstName'])
        #         _logger.info("Last Name: %s" % self.data['LastName'])

        #         for count in range(3):
        #             isUserCreationSuccessful = self.env['aradial.connector'].create_user(self.data)

        #             if isUserCreationSuccessful:
        #                 self.now_date_time = self._successful_user_creation()

        #                 return self.now_date_time
        #             else:
        #                 if count == 2:
        #                     _logger.info("error user creation")
        #                     # add to failure list

        #     else:
        #         self.record.write({
        #             'stage_id': self.env['sale.subscription.stage'].search([("name", "=", "In Progress")]).id,
        #             'in_progress': True
        #         })


    def _validate_parameters(
        self,
        location,
        atm_ref,
        stage
    ):
        _logger.info("Validating Subcription")

        if not location:
            _logger.info("Location is required")
            return False
        if not atm_ref:
            _logger.info("atm_ref is required")
            return False
        if stage != 'Draft':
            _logger.info("Stage should be in Draft")
            return False

        _logger.info("Valid Subscription")
        return True
    
    def _compose_aradial_payload(
        self, 
        record
    ):
        products = ""

        for line_id in record.recurring_invoice_line_ids:
            # if line_id.product_id.product_tmpl_id.product_segmentation == 'month_service':
            aradial_flag = line_id.product_id.product_tmpl_id.sf_facility_type.is_aradial_product
            product = line_id.product_id.display_name.upper()
            facility_type = line_id.product_id.product_tmpl_id.sf_facility_type.name            #TODO: for update to actual field name
            plan_type = line_id.product_id.product_tmpl_id.sf_plan_type.name                    #TODO: for update to actual field name
        first_name = record.partner_id.first_name
        last_name = record.partner_id.last_name
        if not first_name:
            first_name = record.partner_id.name
            last_name = ''

        # data = {
        #     'UserID': record.opportunity_id.sms_id_username, #TODO: for update to actual field name
        #     'Password': record.opportunity_id.sms_id_password, #TODO: for update to actual field name
        #     'FirstName': first_name,
        #     'LastName': last_name,
        #     'Address1': record.partner_id.street,
        #     'Address2': record.partner_id.street2,
        #     'City': record.partner_id.city,
        #     'State': record.partner_id.state_id.name,
        #     'Country': record.partner_id.country_id.name,
        #     'Zip': record.partner_id.zip,
        #     'Offer': products,
        #     'ServiceType': 'Internet',
        #     'CustomInfo1': facility_type,
        #     'CustomInfo2': plan_type,
        #     'CustomInfo3': record.partner_id.customer_number,
        # }

        _logger.info(aradial_flag)
        _logger.info(facility_type)
        _logger.info(plan_type)


        # return data        

    def _successful_user_creation(self):

        # 1. Get current time
        now = datetime.now()
        self.now_date = now.strftime("%Y-%m-%d")
        self.now_date_time = now.strftime("%m/%d/%Y %H:%M%p")

        # 2. Update Subscription Start date
        self.record.write({
            'date_start': self.now_date,
            'stage_id': self.env['sale.subscription.stage'].search([("name", "=", "In Progress")]).id,
            'in_progress': True
        })

        # 3. Call SF API to update start date
        return self.now_date_time


    def _send_welcome_message(self, recordset, template_name, state):
        self.env['awb.sms.send'].send_now(
            recordset=recordset,
            template_name=template_name,
            state=state
        )
        _logger.info("----- SMS Sending Done -----")
