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
            'Status': '0',
            'CustomInfo1':self.data['CustomInfo1']
        }

        try:
            res = requests.put(
                url=self.url+'/'+self.data['UserID'],
                headers=self.headers,
                data=json.dumps(offer_data),
                auth=HTTPBasicAuth(self.username, self.password)
            )
        except requests.exceptions.MissingSchema as e:
            raise exceptions.ValidationError(e)

        if res.status_code != 204:
            update_offer_state = False
            _logger.error('!!! Error Updating Offer to '+self.data['Offer']+' for Subscriber '+self.data['UserID'])
        else:
            update_offer_state = True

        # Update User's TimeBank
        # if self.data['Timebank'] > 0:
        #     timebank_data = {
        #         'TimeBank': self.data['Timebank']
        #     }

        #     try:
        #         res = requests.post(
        #             url=self.userbalance_url+'/'+self.data['UserID'],
        #             headers=self.headers,
        #             data=json.dumps(timebank_data),
        #             auth=HTTPBasicAuth(self.username, self.password)
        #         )
        #     except requests.exceptions.MissingSchema as e:
        #         raise exceptions.ValidationError(e)

        #     if res.status_code != 201:
        #         update_timebank_state = False
        #         _logger.error('!!! Error Adding to TimeBank for Subscriber '+self.data['UserID'])
        #     else:
        #         update_timebank_state = True

        # return True if update_offer_state and update_timebank_state else False
        return True if update_offer_state else False

