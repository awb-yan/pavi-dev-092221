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
from ..services.subscription_create import SubscriptionCreate
# from ..services.subscription_disconnect import SubsDiscon
# from ..services.subscription_update import SubsUpdate
# from ..services.subscription_renew import SubsRenew
# from ..api.client.sf_updateaccount import Salesforce

import logging

_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    # Outline the fields that will determine the flow
    subscription_status = ''

    @api.model
    def create(self, vals):
       
    #    main_plan = _get_mainplan(vals)
    #    plan_type = main_plan.sf_plan_type
    #    aradial_flag =  ''

    #    data = {
    #       'main_plan': main_plan,
    #       'plan_type': plan_type,
    #       'aradial_flag': aradial_flag,
    #       'subscription': vals, 
    #    }

        # last_subscription = self._checkLastActiveSubscription()

        # SubsCreate = SubscriptionCreate()
        # # Provisioning New Subscription
        # newsubscription = SubsCreate._provision_and_activate(self, vals, last_subscription)
        # # Helper to update Odoo Opportunity
        # Salesforce.update_opportunity(newsubscription)

        # CTP flow for prepaid, 
        # if(last_subscription && newsubscription.opportunity_id is None)
        #     SubsDiscon.disconnect(last_subscription)
        #     # Helper to update Odoo Opportunity
        #     Salesforce.update_opportunity(last_subscription)

        res = super(SaleSubscription, self).create(vals)
        return res
    
    def _create(self, record):
        last_subscription = self._checkLastActiveSubscription(record)

        SubsCreate = SubscriptionCreate()
        # Provisioning New Subscription
        newsubscription = SubsCreate._provision_and_activate(self, record, last_subscription)
        # Helper to update Odoo Opportunity
        Salesforce.update_opportunity(newsubscription)

       
    # @api.model
    # def update(self, vals):
    #     if(subscription_status == 'Disconnected')
        
    #     elif(subscription_status == 'Convert')
        
    #     elif(subscription_status == 'Upgrade')

    #     elif(subscription_status == 'Downgrade')

    def _checkLastActiveSubscription(self, record):
        customer_id = record.customer_number

        activeSubs = self.env['sale.subscription'].search([('customer_number','=', customer_id),('subscription_status', '=', 'new')])
        if activeSubs.length() >= 2:
            return activeSubs[0] 
        else:
            return False