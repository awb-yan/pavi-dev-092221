from ..api.aradial_gateway.create_user import AradialAPIGateway
from odoo import api, fields, models, exceptions, _
from psycopg2.extensions import AsIs
import datetime
import logging

_logger = logging.getLogger(__name__)

class AWBAradialConnector(models.Model):

    _name = 'aradial.connector'
    _description = 'AWB Aradial Connector'

    def create_user(
        self, 
        record
    ):

        _logger.info("Create User")

        products = ""

        for line_id in record.recurring_invoice_line_ids:
            if line_id.product_id.display_name.upper() != "DEVICE FEE":
                products += line_id.product_id.display_name.upper()
            facility_type = line_id.product_id.facility_type #TODO: for update to actual field name
            plan_type = line_id.product_id.plan_type #TODO: for update to actual field name
        first_name = record.partner_id.first_name
        last_name = record.partner_id.last_name
        if not first_name:
            first_name = record.partner_id.name
            last_name = ''

        data = {
            'UserID': record.opportunity_id.sms_id_username, #TODO: for update to actual field name
            'Password': record.opportunity_id.sms_id_password, #TODO: for update to actual field name
            'FirstName': first_name,
            'LastName': last_name,
            'Address1': record.partner_id.street,
            'Address2': record.partner_id.street2,
            'City': record.partner_id.city,
            'State': record.partner_id.state_id.name,
            'Country': record.partner_id.country_id.name,
            'Zip': record.partner_id.zip,
            'Offer': products,
            'ServiceType': 'Internet',
            'CustomInfo1': facility_type,
            'CustomInfo2': plan_type,
            'CustomInfo3': record.code
        }

        params = self.env['ir.config_parameter'].sudo()
        aradial_url = params.get_param('aradial_url')
        aradial_username = params.get_param('aradial_username')
        aradial_password = params.get_param('aradial_password')

        _logger.info("Calling API %s" % aradial_url)
        
        user = AradialAPIGateway(
            url=aradial_url,
            username=aradial_username,
            password=aradial_password,
            data=data
        )
        created_user = user.create_user()

        _logger.info("User Creation: %s" % created_user)

        if created_user == "Success":
            return True
        else:
            return False
    