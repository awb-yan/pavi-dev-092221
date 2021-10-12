# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Subscriber Bill Automation",

    'summary': """
        Subscriber Bill Automation.
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Localization',

    'version': '13.0.1.5.8',

    'depends': ['crm', 'sale_management', 'sale_subscription', 'awb_subscriber_product_information', 'awb_product_segmentation'],

    'data': [
        # 'security/ir.model.access.csv',
        'data/crm_data.xml',
        'data/subscription_atm_ref_sequence.xml',
        'data/res_users_data.xml',
        'views/crm_view.xml',
        'views/sale_view.xml',
        'views/subscription_view.xml',
        'views/res_config_settings.xml',
        'views/partner_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False

}
