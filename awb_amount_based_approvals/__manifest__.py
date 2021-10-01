# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Amount Based Approvals",

    'summary': """
        Amount Based Approvals
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Approvals',

    'version': '13.0.1.2.5',

    'depends': ['approvals', 'requisition_approval'],

    'data': [
        'security/ir.model.access.csv',
        'security/ir.rule.csv',
        'views/approval_rules_view.xml',
        'views/approval_types_view.xml',
        'views/approval_request_view.xml',
        'views/hr_department_view.xml',
    ],
}
