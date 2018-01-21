# -*- coding: utf-8 -*-

from odoo import models,fields,api

class ResPartnerOwner(models.Model):
	_inherit = 'res.partner'

	#####################################################
	# Below varibles are res.partner relation with Building.
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
	citizen = fields.Boolean(default=True)

	#####################################################
	# Below varible is relation of owner with partner.
	#####################################################

	tenants_ids = fields.One2many('owner.tanent.line', 'tnt_ids')

	#####################################################
	# Below varibles are owner information
	# which we want to upload to OSM database.
	#####################################################

	building_id = fields.One2many('owner.building.line','owner_form_id',readonly=True)

	vrn = fields.Integer('VRN')
	tin = fields.Integer('TIN')
	efd = fields.Integer('EFD')
	assess = fields.Boolean()
	branch = fields.Boolean('Branch')
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

	total_area_own = fields.Float(compute='_compute_area_own')
	total_property_tax = fields.Float(string='Property Tax',compute='_compute_area_own')
	
	#####################################################
	# This is unique killbill ID of Owner for charging 
	# tax money from Owner.
	#####################################################

	killbill_id = fields.Char('KillBill ID')

	#####################################################
	# Below function is for computing total area own
	# by owner and total property tax
	####################################################

	@api.one
	@api.depends('building_id')
	def _compute_area_own(self):
		if self.building_id:
			self.total_area_own = sum(x.area_own for x in self.building_id)
			self.total_property_tax = sum(x.property_tax for x in self.building_id)

class OwnerBuildingLine(models.Model):
	_name = 'owner.building.line'
	_description = "This class is bridge between Owners and Building"

	name = fields.Many2one('building.data')
	property_name = fields.Char()
	area_own = fields.Float()
	property_value = fields.Float()
	property_tax = fields.Float()

	##########################################
	# Connection inverse fields
	##########################################

	owner_form_id = fields.Many2one('res.partner')

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