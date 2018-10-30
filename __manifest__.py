# -*- coding: utf-8 -*-
{
    'name': "Property Tax Calculator",

    'summary': """
        Calculating Property and Tenant tax of owner""",

    'description': """
Property Tax Calculator
=======================
Calculate:
----------
    i) Area of building in square feet through OSM database.
    ii) Number of owner and tenant with in building.
    iii) Bill board related to that building.
    iv) Info and valuation of building.
    """,

    'author': "Wahab Ali Malik",
    'website': "http://www.glarecom.com",

    'category': 'Tax',
    'version': '0.1',
    'application': True,

    'depends': ['decimal_precision','textit_sms_service','odoo_killbill_sync','map_view'],
    # 'css': ['static/src/css/building_tree.css'],
    'qweb': ['static/src/xml/*.xml'],

    
    'data': [
        # 'security/ir.model.access.csv',
        'data/building_data.xml',  
        'views/menuitems.xml',
        'views/dashboard.xml',
        'views/owner.xml',
        'views/building_data.xml',
        'views/tenant.xml',
        'views/fitting_fixture.xml',
        'views/standard_cost.xml',
        'views/accommodation.xml',
        'views/tax_config_setting.xml',
        'views/account_invoice_line_ext.xml',

    ]

}