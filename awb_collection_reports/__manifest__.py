# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Collection Reports",

    'summary': """
        AWB Collection Reports
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Localization',

    'version': '13.0.1.0.3',

    'depends': [
        'account',
        'account_accountant',
        'awb_product_segmentation',
        'awb_payment_allocation',
    ],

    'data': [
        'views/segmentations.xml',
        'views/account_payment_view.xml',
    ],
}
