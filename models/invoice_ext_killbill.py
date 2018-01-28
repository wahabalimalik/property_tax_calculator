# -*- coding: utf-8 -*-

from odoo import models, fields


class AccInvExt(models.Model):
	_inherit = 'account.invoice'
	
	killbill_id = fields.Char('Control Number')
	kb_invoice_id = fields.Char("Invoice Id")