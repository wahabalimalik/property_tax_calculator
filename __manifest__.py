# -*- coding: utf-8 -*-
{
    'name': "Property Tax Calculator",

    'summary': """
        Calculating Property and Tanent tax of owner""",

    'description': """
Property Tax Calculator
=======================
Calculate:
----------
    i) Area of building in square feet through OSM database.
    ii) Number of owner and tanent with in building.
    iii) Bill board related to that building.
    iv) Info and valuation of building.
    """,

    'author': "Wahab Ali Malik",
    'website': "http://www.glarecom.com",

    'category': 'Tax',
    'version': '0.1',

    'depends': ['base','decimal_precision'],
    'css': ['static/src/css/building_tree.css'],
    
    'data': [
        # 'security/ir.model.access.csv',
        'views/menuitems.xml',
        'views/building_data.xml',
        'views/owner.xml',
        'views/fitting_fixture.xml',
        'views/accommodation.xml',
        'data/building_data.xml',
    ],
    # 'qweb': [
    #     'static/src/xml/dashboard.xml',
    #     ],

}