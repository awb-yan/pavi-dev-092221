import json
import requests
from odoo import exceptions
from requests.auth import HTTPBasicAuth

import logging

_logger = logging.getLogger(__name__)

class AradialAPIGateway(object):
    def __init__(
        self,
        url,
        username,
        password,
        data
    ):

        self.url = url
        self.username = username
        self.password = password

        self.headers = {
            'Content-Type': 'application/json'
        }

        self.data = data


    def create_user(self):

        try:
            res = requests.post(
                url=self.url,
                headers=self.headers,
                data=json.dumps(self.data),
                auth=HTTPBasicAuth(self.username, self.password)
            )
        except requests.exceptions.MissingSchema as e:
            _logger.info(e)
            raise exceptions.ValidationError(e)

        _logger.info(res.json())
        
        state = "Success" if res.status_code == 201 else "Fail"
        _logger.info("response [%s]" % res)



        return state
    
    def get_user(self, sms_id_username):

        try:
            res = requests.get(
                url=self.url + "/" + sms_id_username,
                auth=HTTPBasicAuth(self.username, self.password)
            )
        except requests.exceptions.MissingSchema as e:
            raise exceptions.ValidationError(e)

        _logger.info("==== getUser Response ====")
        _logger.info(res.json())

        if res.status_code == 200:

            response = res.json()
            return response['TimeBank']
        else:
            return 0