import json
import requests
from odoo import exceptions,models

import logging


class Salesforce(models.Model):
    _inherit = "sale.subscription"

    def update_opportunity(self, record):

        self.params = {
          'grant_type':  'password',
          'client_id': '3MVG9hrgdTdWwemcOiqfSG11rApV7XpajbLl5bjnUUwkGi6QoIF6o4ax_5gniOjVYEw2Xt6FgNX3CVgnXsP3q',
          'client_secret': '7590BC2BBE40352BE642F5C5599B0DD24A3670E8C785CB05541EC1793266C23C',
          'username': 'theresa.artillero@achievewithoutborders.com',
          'password': 'salesforce1236WeJMvr0mBpAIixPeJThwVDs'
        }

        res = requests.post(
            'https://planetcabletv--devenviro.my.salesforce.com/services/oauth2/token', 
            params=self.params)

        response = res.json()

        token = response['access_token']

        # Update Opportunity Start Date
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + token
        }

        self.data = {
            "SFID":"0064V00001EuVq0QAF",
            "BillCustomerID":"",
            "CurrentBalance":"",
            "LastPaymentAmount":"",
            "BillingAmount":"",
            "LastPaymentDate":"",
            "BillingInvoice":"",
            "BillingATMRef":"",
            "BillDueDate":"",
            "AccountStatus":"",
            "SMS_Activation_Date_Time":"09/09/2021 5:47AM",
            "UpdateType":6
            }

        res = requests.post(
            'https://planetcabletv--devenviro.my.salesforce.com/services/apexrest/Streamtech/SF_ODOO_CustomerID_Update', 
            headers=self.headers,
            data=json.dumps(self.data))



