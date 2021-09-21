import json
import requests
from odoo import exceptions
from requests.auth import HTTPBasicAuth

import logging

_logger = logging.getLogger(__name__)

class AradialAPIGatewayUpdateUser(object):
    def __init__(
        self,
        url,
        userbalance_url,
        username,
        password,
        data
    ):

        self.url = url
        self.userbalance_url = userbalance_url
        self.username = username
        self.password = password

        self.headers = {
            'Content-Type': 'application/json'
        }

        self.data = data


    def update_user(self):
        _logger.info('function: update_user')

        # Update User's Product
        offer_data = {
            'Offer': self.data['Offer'],
            'Status': 0
        }

        _logger.info(f'Offer: {offer_data}')

        try:
            res = requests.put(
                url=self.url+'/'+self.data.UserID,
                headers=self.headers,
                data=json.dumps(offer_data),
                auth=HTTPBasicAuth(self.username, self.password)
            )
        except requests.exceptions.MissingSchema as e:
            raise exceptions.ValidationError(e)

        _logger.info(f'Update User\'s Offer: {res.json()}')

        # Update User's TimeBank
        timebank_data = {
            'Timebank': self.data['Timebank']
        }

        _logger.info(f'Timebank: {timebank_data}')

        try:
            res = requests.post(
                url=self.userbalance_url+'/'+self.data.UserID,
                headers=self.headers,
                data=json.dumps(timebank_data),
                auth=HTTPBasicAuth(self.username, self.password)
            )
        except requests.exceptions.MissingSchema as e:
            raise exceptions.ValidationError(e)

        _logger.info(f'Update User\'s Timebank: {res.json()}')

        
        state = True if res.status_code == 201 else False
        _logger.info("response [%s]" % res)

        return state

