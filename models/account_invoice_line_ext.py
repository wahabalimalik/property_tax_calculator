# -*- coding: utf-8 -*-

from odoo import models,fields,api,_

import logging

_logger = logging.getLogger(__name__)

class AccountInvoiceExt(models.Model):
	_inherit = 'account.invoice'

	invoice_for = fields.Selection([('property_tax', 'Property Tax'), ('rental_tax', 'Rental Tax')], required=True, string='Invoice For')

class AccountInvoiceLineExt(models.Model):
	_inherit = 'account.invoice.line'

	building_id = fields.Many2one('building.data')

	@api.onchange('building_id')
	def _onchange_building_id(self):
		domain = {}
		if not self.invoice_id:
			return

		part = self.invoice_id.partner_id
		fpos = self.invoice_id.fiscal_position_id
		company = self.invoice_id.company_id
		currency = self.invoice_id.currency_id
		type = self.invoice_id.type

		if not part:
			warning = {
				'title': _('Warning!'),
				'message': _('You must first select a partner!'),
				}
			return {'warning': warning}

		if not self.invoice_id.invoice_for:
			warning = {
				'title': _('Warning!'),
				'message': _('You must first select what is this Invoice For!'),
				}
			return {'warning': warning}

		if not self.building_id:
			if type not in ('in_invoice', 'in_refund'):
				self.price_unit = 0.0
		else:
			if self.invoice_id.invoice_for == 'property_tax':

				if self.invoice_id.partner_id.id not in [rec.name.id for rec in self.building_id.owner_id]:
					self.building_id = False
					warning = {
						'title': _('Denial!'),
						'message': _('Selected Owner did not own this building'),
						}
					return {'warning': warning}
				else:
					self.name = self.building_id.property_name
					self.price_unit =  [rec.property_tax for rec in self.invoice_id.partner_id.building_id if rec.name  == self.building_id][0]

			elif self.invoice_id.invoice_for == 'rental_tax':
				if self.invoice_id.partner_id.id not in [rec.name.id for rec in self.building_id.tenant_id]:
					self.building_id = False
					warning = {
						'title': _('Denial!'),
						'message': _('Selected Tenant did not has this building'),
						}
					return {'warning': warning}
				else:
					self.name = self.building_id.property_name
					self.price_unit =  [rec.rental_tax for rec in self.invoice_id.partner_id.building_rent_id if rec.name  == self.building_id][0]