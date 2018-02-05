# -*- coding: utf-8 -*-

import requests
import logging

_logger = logging.getLogger(__name__)

def send_sms(number,message):
	headers = {
			'Authorization': 'Token 45855a8fdf2280817fd1a0649f57169271c8d621',
		    'Content-Type': 'application/json'
		}
	data = '{"urns": ["tel:+255%s"],"text": "%s"}' %(number,message)
	_logger.info('Sending message : '+message+' on Number : '+number)
	rec = requests.post('https://api.textit.in/api/v2/broadcasts.json', headers=headers, data=data)

