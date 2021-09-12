from ..api.aradial_gateway.create_user import AradialAPIGatewayCreateUser
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
        data
    ):

        _logger.info("Create User")

        params = self.env['ir.config_parameter'].sudo()
        aradial_url = params.get_param('aradial_url')
        aradial_username = params.get_param('aradial_username')
        aradial_password = params.get_param('aradial_password')

        _logger.info("Calling Create User API %s" % aradial_url)
        
        user = AradialAPIGatewayCreateUser(
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

    def get_remaining_time(
        self, 
        sms_id_username
    ):
        _logger.info("Get Remaining Time")

        params = self.env['ir.config_parameter'].sudo()
        aradial_url = params.get_param('aradial_url')
        aradial_username = params.get_param('aradial_username')
        aradial_password = params.get_param('aradial_password')

        _logger.info("Calling Get User API %s" % aradial_url)
        
        user = AradialAPIGateway(
            url=aradial_url,
            username=aradial_username,
            password=aradial_password
        )
        timebank = user.get_user(sms_id_username)

        # _logger.info("User Creation: %s" % created_user)

        return timebank        
    