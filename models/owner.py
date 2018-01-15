# -*- coding: utf-8 -*-

from odoo import models,fields,api

class ResPartnerOwner(models.Model):
	_inherit = 'res.partner'

	#####################################################
	# Below varibles are relation with Building.
	#####################################################

	owner = fields.Boolean(readonly=True)
	tenant = fields.Boolean(readonly=True)

	#####################################################
	# Below varibles are private Info of person.
	#####################################################

	nationality = fields.Many2many('res.country', string='Nationality (Country)')
	identification_id = fields.Char(string='Identification No')
	passport_id = fields.Char('Passport No')
	gender = fields.Selection([
		('male', 'Male'),
		('female', 'Female'),
		('other', 'Other')
	])
	marital = fields.Selection([
		('single', 'Single'),
		('married', 'Married'),
		('widower', 'Widower'),
		('divorced', 'Divorced')
	], string='Marital Status')

	birthday = fields.Date('Date of Birth')

	#####################################################
	# Below varible is relation of owner with partner.
	#####################################################

	tenants_ids = fields.One2many('owner.tanent.line', 'tnt_ids')

	#####################################################
	# Below varibles are owner information
	# which we want to upload to OSM database.
	#####################################################

	bus_id = fields.Many2one('building.data',string="Business ID")

	citizen = fields.Boolean(default=True)
	vrn = fields.Integer('VRN')
	assess = fields.Boolean()
	branch = fields.Boolean('Branch')
	tax = fields.Float(compute='_compute_tax',string='Total Tenant Tax')
	tin = fields.Char('TIN')
	efd = fields.Char('EFD')
	valued = fields.Char('Valued')
	

	#####################################################
	# Fields defining 
	#   i)area own by owner.
	#   ii)Type of building e.g(residential or commercial).
	# 	iii) Replacement cost of building.
	#   iv) Tax on the base of replacement cost.
	#  These fields are storing in res.partner and not 
	#  pushing to OSM.
	#####################################################

	area_own = fields.Float()
	building = fields.Char(compute='_compute_building')
	property_valuation = fields.Float(compute='_compute_valuation',string='Property Valuation')
	property_tax = fields.Float(compute='_compute_tax',string='Property Tax')
	
	#####################################################
	# This is unique killbill ID of Owner for charging 
	# tax money from Owner.
	#####################################################

	killbill_id = fields.Char('KillBill ID')

	#####################################################
	# Below function is for computing building type
	#  e.g(residential or commercial). form reading buil-
	#  -ding information
	####################################################

	@api.one
	@api.depends('bus_id.type_id')
	def _compute_building(self):
		if self.bus_id.type_id:
			self.building = self.bus_id.type_id

	#####################################################
	# Below function is for calculating property tax
	# with respect to building type 
	# e.g(residential or commercial) and property 
	# replacement value.
	####################################################

	@api.one
	@api.depends('property_valuation','building')
	def _compute_tax(self):
		if self.property_valuation and self.building:
			if 'commercial' in self.building:
				self.property_tax = self.property_valuation * 0.20 / 100
			else:
				self.property_tax = self.property_valuation * 0.15 / 100
	#####################################################
	# Below function is for auto caculation of property
	# value it depend on area own by owner
	####################################################

	@api.one
	@api.depends('area_own')
	def _compute_valuation(self):
		if self.area_own:
			self.property_valuation = float(self.area_own) * 50000

class OwnerTanentLine(models.Model):
	_name = 'owner.tanent.line'
	_description = "This class is bridge between Owners and Tanents"
	
	#####################################################
	# Below varibles are Owner relation with Tanents.
	#####################################################

	name = fields.Many2one('res.partner')

	citizen = fields.Boolean()
	rent = fields.Integer()
	# tax = fields.Float(compute='_compute_tax')
	tax = fields.Float()
	
	tnt_ids = fields.Many2one('res.partner',ondelete='cascade')