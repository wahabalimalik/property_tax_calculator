# -*- coding: utf-8 -*-

from odoo import models,fields,api, _
from odoo.exceptions import ValidationError

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
	identification_id = fields.Char(string='Identification No',required=True)
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
	# Below varible is relation of owner with tenant.
	#####################################################

	tenants_ids = fields.One2many('owner.tenant.line', 'tnt_ids')

	#####################################################
	# Below varibles are owner information
	# which we want to upload to OSM database.
	#####################################################

	building_id = fields.One2many('owner.building.line','owner_form_id',readonly=True)
	building_rent_id = fields.One2many('tenant.building.line','tenant_form_id',readonly=True)

	vrn = fields.Integer('VRN')
	tin = fields.Char('TIN',required=True)
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
	
	total_building = fields.Float()
	total_tenant_tax = fields.Float(string='Building Tax')
	
	#####################################################
	# Below function is for computing total area own
	# by owner and total property tax
	#####################################################

	@api.one
	@api.depends('building_id')
	def _compute_area_own(self):
		if self.building_id:
			self.total_area_own = sum(x.area_own for x in self.building_id)
			self.total_property_tax = sum(x.property_tax for x in self.building_id)

	#####################################################
	# On creating owner a message should send to his mobile
	#####################################################

	@api.model
	def create(self, vals):
		
		if not vals['mobile']:
			raise ValidationError(_("Please add Mobile number"))

		if self.user_has_groups('textit_sms_service.group_sms_form'):

			message = "Name : %s,TIN : %s,NIC : %s" %(vals["name"],vals["tin"],vals["identification_id"])

			try:
				self.env['sms.templates'].send_sms(number = '+255'+vals["mobile"][1:],message=message)
				return super(ResPartnerOwner, self).create(vals)
			except Exception as e:
				raise e

		return super(ResPartnerOwner, self).create(vals)

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
	# invoice_form_id = fields.Many2one('account.invoice')

class OwnertenantLine(models.Model):
	_name = 'owner.tenant.line'
	_description = "This class is bridge between Owners and tenants"
	
	#####################################################
	# Below varibles are Owner relation with tenants.
	#####################################################

	name = fields.Many2one('res.partner')
	citizen = fields.Boolean()
	rent = fields.Integer()
	type_id = fields.Selection([
        ('commercial', 'Commercial'),
        ('residential', 'Residential'),
        ('construction', 'Construction')
        ], string= "Area Type")
	tax = fields.Float()
	
	tnt_ids = fields.Many2one('res.partner',ondelete='cascade')

class TenantBuildingLine(models.Model):
	_name = 'tenant.building.line'
	_description = "This class is bridge between Tenant and Building"

	name = fields.Many2one('building.data')
	property_name = fields.Char()
	area = fields.Float()
	rental_tax = fields.Float()

	##########################################
	# Connection inverse fields
	##########################################

	tenant_form_id = fields.Many2one('res.partner')