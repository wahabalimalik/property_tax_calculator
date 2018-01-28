# -*- coding: utf-8 -*-

from odoo.addons.connector.event import on_record_create
import logging,time,requests,json
from odoo.http import request
import odoo

_logger = logging.getLogger(__name__)

post_headers = {
	'X-Killbill-ApiKey': 'vunoo',
    'X-Killbill-ApiSecret': 'vunoo',
    'Content-Type': 'application/json',
    'X-Killbill-CreatedBy': 'Swagger',
    }

get_headers = {
    'Accept': 'application/json',
    'X-Killbill-ApiKey': 'vunoo',
    'X-Killbill-ApiSecret': 'vunoo',
    }

@on_record_create(model_names='res.partner')
def res_partner(env, model_name, record_id, vals):

	record = env[model_name].search([('id','=',record_id)])

	data = '''{
		"name":"%s",
		"externalKey":"%s",
		"email":"%s",
		"address1":"%s",
		"address2":"%s",
		"paymentMethodId":"d851aad1-52b8-43d3-ac78-a57f0ce88568",
		"postalCode":"%s",
		"company":"%s",
		"currency": "TZS",
		"city":"%s",
		"state": "%s",
		"country": "%s",
		"phone": "%s",
		"notes": "%s",
		"isNotifiedForInvoices": "True"
	}''' %(
		vals['name'],
		record_id,
		vals['email'],
		vals['street'],
		vals['street2'],
		vals['zip'],
		vals['is_company'],
		vals['city'],
		vals['state_id'],
		vals['country_id'],
		vals['phone'],
		vals['comment']
		)
	
	r = requests.post(
		'http://13.95.148.150:8080/1.0/kb/accounts', 
		headers=post_headers, 
		data=data, 
		auth=('admin', 'password')
	)

	_logger.info('Killbill Post request has respose : %s' %(r.json))

	r = requests.get(
		'http://13.95.148.150:8080/1.0/kb/accounts?externalKey=%s&accountWithBalance=false&accountWithBalanceAndCBA=false&audit=NONE' %(record_id), 
    	headers=get_headers, 
    	auth=('admin', 'password')
    	)

	_logger.info('Killbill Get AccountId : %s' %(r.json()['accountId']))

	record.write({'killbill_id' : r.json()['accountId']})

@on_record_create(model_names='account.invoice')
def event(env, model_name, record_id, vals):

	record = env[model_name].search([('id','=',record_id)])

	params = (
	    ('payInvoice', 'false'),
	    ('autoCommit', 'true'),
	)

	product_line = []

	for x in range(0,len(vals['invoice_line_ids'])):
		if vals['invoice_line_ids'][x]:
			product_line.append({
				"description": ''.join([line.strip() for line in str(vals['invoice_line_ids'][x][2]['name'])]),
				"amount": (
					vals['invoice_line_ids'][x][2]['price_unit'] * 
					vals['invoice_line_ids'][x][2]['quantity']
					) - vals['invoice_line_ids'][x][2]['discount']
			})

	data = '[{"description": "%s","amount": %s,"currency": "TZS","childItems":%s}]' %(
		vals['comment'],
		record.amount_total,
		json.dumps(product_line)
		)

	rec = env['res.partner'].search([("id", "=", vals['partner_id'])])

	r = requests.post(
		'http://13.95.148.150:8080/1.0/kb/invoices/charges/%s?payInvoice=false&autoCommit=true' %(rec.killbill_id), 
		headers=post_headers, 
		params=params, 
		data=data, 
		auth=('admin', 'password'))

	record.write({'kb_invoice_id' : r.json()[0]['invoiceId']})

	params = (
		('withItems', 'false'),
		('withChildrenItems', 'false'),
		('audit', 'NONE'),
		)

	url = 'http://13.95.148.150:8080/1.0/kb/invoices/%s' %(r.json()[0]['invoiceId'])

	r = requests.get(url, headers=get_headers, params=params, auth=('admin', 'password'))
	record.write({'killbill_id' : r.json()['invoiceNumber']})

	_logger.info('Killbill Get request for Invoice has respose : %s' %(r.json))