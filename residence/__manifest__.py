# -*- coding: utf-8 -*-
{
    'name': "residence",

    'summary': """
        rumah dinas
    """,

    'author': "bulog",
    'website': "https://www.bulog.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/sequence_data.xml',
        'views/views_operations.xml',
        'views/views_configuration.xml',
        'views/templates.xml',
        'views/menuitem_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
    'application': True,
}
