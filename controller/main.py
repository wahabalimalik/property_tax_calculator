# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

from odoo import fields, http
from odoo.exceptions import AccessError
from odoo.http import request
from odoo import release
import json

import numpy as np

class OsmBuildingData(http.Controller):

    @http.route('/ptc_dashboard/data', type='json', auth='user')
    def osm_id(self, **kw):
        month = {
            1 : 'jan',2 : 'feb',3 : 'mar',4 : 'apl',
            5 : 'may',6 : 'jun',7 : 'jul',8 : 'aug',
            9 : 'sep',10: 'oct',11: 'nov',12: 'dec',
        }

        property_tax = {
            'jan' : 0,'feb' : 0,'mar' : 0,'apl' : 0,
            'may' : 0,'jun' : 0,'jul' : 0,'aug' : 0,
            'sep' : 0,'oct' : 0,'nov' : 0,'dec' : 0,
        }

        rental_tax = {
            'jan' : 0,'feb' : 0,'mar' : 0,'apl' : 0,
            'may' : 0,'jun' : 0,'jul' : 0,'aug' : 0,
            'sep' : 0,'oct' : 0,'nov' : 0,'dec' : 0,
        }

        records = request.env['account.invoice'].search([])

        t_property_tax = 0
        t_rental_tax = 0

        for rec in records:
            if rec.invoice_for == 'property_tax':
                if rec.payments_widget:
                    month_number = int(json.loads(rec.payments_widget)['content'][0]['date'][5:7])
                    amount = int(json.loads(rec.payments_widget)['content'][0]['amount'])

                    property_tax[month[month_number]] = property_tax[month[month_number]] + amount

                    t_property_tax = t_property_tax + amount

            else:
                if rec.payments_widget != 'false':
                    month_number = int(json.loads(rec.payments_widget)['content'][0]['date'][5:7])
                    amount = int(json.loads(rec.payments_widget)['content'][0]['amount'])

                    rental_tax[month[month_number]] = rental_tax[month[month_number]] + amount

                    t_rental_tax = t_rental_tax + amount

        ex_total_pt = 0
        ex_total_rt = 0
        for rec in records:
            if rec.invoice_for == 'property_tax':
                ex_total_pt = ex_total_pt + rec.amount_total

            else:
                ex_total_rt = ex_total_rt + rec.amount_total

        return {
            'building': {
                'buildings_paid': 5,
                'buildings_partially_paid': 4,
                'buildings_not_paid': 3,
            },
            'state': {
                'draft': request.env['building.data'].search_count([('state', '=', 'draft')]),
                'staging': request.env['building.data'].search_count([('state', '=', 'staging')]),
                'verified': request.env['building.data'].search_count([('state', '=', 'verified')]),
            },
            'tax_payment': {
                'property_tax':{
                    'p_jan' : property_tax['jan'],
                    'p_feb' : property_tax['feb'],
                    'p_mar' : property_tax['mar'],
                    'p_apl' : property_tax['apl'],
                    'p_may' : property_tax['may'],
                    'p_jun' : property_tax['jun'],
                    'p_jul' : property_tax['jul'],
                    'p_aug' : property_tax['aug'],
                    'p_sep' : property_tax['sep'],
                    'p_oct' : property_tax['oct'],
                    'p_nov' : property_tax['nov'],
                    'p_dec' : property_tax['dec'],
                },
                'rental_tax': {
                    'r_jan' : rental_tax['jan'],
                    'r_feb' : rental_tax['feb'],
                    'r_mar' : rental_tax['mar'],
                    'r_apl' : rental_tax['apl'],
                    'r_may' : rental_tax['may'],
                    'r_jun' : rental_tax['jun'],
                    'r_jul' : rental_tax['jul'],
                    'r_aug' : rental_tax['aug'],
                    'r_sep' : rental_tax['sep'],
                    'r_oct' : rental_tax['oct'],
                    'r_nov' : rental_tax['nov'],
                    'r_dec' : rental_tax['dec'],
                },
            },
            # 'total_collection': {
            #     'property_tax': t_property_tax,
            #     'rental_tax': t_rental_tax,
            #     'billboard_tax': 500,
            # },
            # 'expected_collection': {
            #     'property_tax': ex_total_pt,
            #     'rental_tax': ex_total_rt,
            #     'billboard_tax': 500,
            # }
        }
