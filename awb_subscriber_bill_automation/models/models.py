# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, exceptions, _
from simple_salesforce import Salesforce
from openerp import _
from openerp.exceptions import Warning, ValidationError
from odoo.osv import osv
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class SubscriberBillAutomationModel(models.TransientModel):
    _inherit = 'res.config.settings'

    prepaid_phy_discon = fields.Boolean(string="Prepaid Physical Discon Trigger", default=False)
    postpaid_phy_discon = fields.Boolean(string="Postpaid Physical Discon Trigger", default=False)
    prepaid_discon_days = fields.Integer(default=180)
    postpaid_discon_days = fields.Integer(default=180)

    def get_log(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Salesforce Logs',
            'view_mode': 'tree',
            'res_model': 'sync.history',
            'context': "{'create': False}"
        }

    @api.model
    def set_values(self):
        res = super(SubscriberBillAutomationModel, self).set_values()
        self.env['ir.config_parameter'].set_param('prepaid_physical_discon', self.prepaid_discon_days)
        self.env['ir.config_parameter'].set_param('postpaid_physical_discon', self.postpaid_discon_days)

        return res

    @api.model
    def get_values(self):
        res = super(SubscriberBillAutomationModel, self).get_values()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        prepaid_days = IrConfigParameter.get_param('prepaid_physical_discon')
        postpaid_days = IrConfigParameter.get_param('postpaid_physical_discon')

        res.update(
            prepaid_physical_discon1=prepaid_days,
            postpaid_physical_discon1=postpaid_days
        )

        return res

