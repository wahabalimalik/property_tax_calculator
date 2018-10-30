# -*- coding: utf-8 -*-

from odoo import models,fields,api, _
from odoo.exceptions import ValidationError,RedirectWarning
from odoo.addons import decimal_precision as dp

import requests,json
import numpy as np
from shapely.geometry import Point, shape
from functools import partial
import pyproj
from shapely.ops import transform
import logging

_logger = logging.getLogger(__name__)

class BuildingData(models.Model):
	_name = 'building.data'

	#####################################################
	# State of documenting Building information.
	#####################################################
	state = fields.Selection([('draft', 'Draft'), ('staging', 'Staging'), ('verified', 'Verified')], string='Status', readonly=True, copy=False, default='draft')

	#####################################################
	# Below varibles are building Refernce Number as in
	# OSM and use for future reference
	# and type of building e.g (Commercial,Residential)
	#####################################################

	name = fields.Char(string='Building Number', required=True)
	type_id = fields.Char(readonly=True)

	#####################################################
	# Below varibles are address related fields
	##################################################### 

	street_sc = fields.Many2one('standard.cost', string='Street')

	street = fields.Char()
	street2 = fields.Char()
	ward = fields.Char()
	sub_ward = fields.Char()
	zip = fields.Char(change_default=True)
	city = fields.Char()
	state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
	country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

	#####################################################
	# Below varibles are building name , Plot number
	# And Standard cost of Building per square meter
	#####################################################

	property_name = fields.Char()
	plot_number = fields.Char()
	standard_cost = fields.Float(readonly=True, related='street_sc.cost')

	#####################################################
	# Below varibles are building relation with bridge between
	# owners and tenant and there building.
	#####################################################

	owner_id = fields.One2many('building.owner.line','building_data_id')
	tenant_id = fields.One2many('building.tenant.line','building_data_id')

	#####################################################
	# Below varibles are building information
	# which we want to upload to database.
	#####################################################

	tenure = fields.Char()
	walls = fields.Selection([
        ('cement_blocks', 'Cement Blocks'),
        ('glass', 'Glass'),
        ('burnt_bricks', 'Burnt Bricks'),
        ('treated_timber', 'Treated Timber'),
        ('iron_sheet', 'Iron Sheet'),
        ('tree_sticks', 'Tree Sticks/Soil/Soil Bricks'),
        ('other', 'OTHERS'),
        ('none', 'NONE'),
        ], required=True)
	roof = fields.Selection([
        ('roof_slab', 'Roof Slab'),
        ('iron_sheet', 'Iron Sheet'),
        ('cemented_tiles', 'Cemented tiles'),
        ('tiles_sheets', 'Tiles Sheets'),
        ('asbestos', 'Asbestos'),
        ('grass', 'Grass'),
        ('other', 'OTHERS'),
        ('none', 'NONE'),
        ], required=True)
	ceiling = fields.Selection([
        ('cement', 'Cement'),
        ('gipsum', 'Gipsum'),
        ('treated_timber', 'Treated Timber'),
        ('hardboard', 'Hardboard'),
        ('other', 'OTHERS'),
        ('none', 'NONE'),
        ], required=True)
	floor = fields.Selection([
        ('tiles', 'Tiles'),
        ('stones', 'Stones'),
        ('terrazo', 'Terrazo'),
        ('treated_timber', 'Treated Timber'),
        ('cement', 'Cement'),
        ('other', 'OTHERS'),
        ('none', 'NONE'),
        ], required=True)
	windows = fields.Selection([
        ('glass', 'Glass'),
        ('treated_timber', 'Treated Timber'),
        ('treated_timber', 'Treated Timber'),
        ('iron_sheet', 'Iron Sheet'),
        ('marine_board', 'Marine Board'),
        ('other', 'OTHERS'),
        ('none', 'NONE'),
        ], required=True)
	doors = fields.Selection([
        ('treated_timber', 'Treated Timber'),
        ('glass', 'Glass'),
        ('iron_sheet', 'Iron Sheet'),
        ('marine_board', 'Marine Board'),
        ('other', 'OTHERS'),
        ('none', 'NONE'),
        ], required=True)
	state_of_build = fields.Selection([
        ('complete', 'Complete'),
        ('incomplete', 'Inomplete'),
        ], string="State", required=True)
	services = fields.Selection([
        ('electricity_water_telephone', 'Electricity, Water, Telephone'),
        ('electricity_water', 'Electricity and Water'),
        ('telephone_electricity', 'Telephone and electricity'),
        ('electricity_only', 'Electricity Only'),
        ('other', 'OTHERS'),
        ('none', 'NONE'),
        ], required=True)
	condition = fields.Selection([
        ('very_good', 'Very Good'),
        ('good', 'Good'),
        ('average ', 'Average'),
        ('poor', 'Poor')
        ], required=True)
	main_description = fields.Text('Brief description of Main Building')
	room_counts = fields.One2many('building.accommodation.line','building_accommodation_line_id')
	fixture_and_fittng = fields.Many2many('fitting.fixture', required=True)
	out_description = fields.Text('Brief description of Out Building')
	main_building = fields.Char()
	out_building = fields.Char()
	site_work = fields.Text()
	depreciation = fields.Float(required=True)

	building_level = fields.Char()
	building_material = fields.Char()


	#####################################################
	# Nodes fields only for Building Valuations
	#####################################################

	surface_area = fields.Float()
	total_area = fields.Float(digits=dp.get_precision('Area Own by Owner'))
	rate_per_meter_square = fields.Float(compute='_compute_rate')
	replacement_cost = fields.Float(compute='_compute_replacement_cost')
	depreciation_factor = fields.Float(related='depreciation', store=True)
	depreciated_replacement_cost = fields.Float(compute='_compute_depreciated_replacement_cost')
	site_works = fields.Float()
	rateable_value = fields.Char()
	say = fields.Char("Rounded Ratable Value")

	##########################################
	# Invisble fields resposible for view control
	##########################################

	view_data_valuation = fields.Boolean(default=False)

	#####################################################
	# Below function are for building valuation
	# and constrants related to owners for proceeding 
	#####################################################

	@api.multi
	def create_build_data(self):

		##########################################
		# Check form info is complete.
		# All important fields are required
		# except owner
		##########################################
		if not self.owner_id:
			raise ValidationError(_("You must select an owner first!"))

		##########################################
		# Creating polygon
		##########################################

		query = "[timeout:10][out:json];way(%s);(._;>;);out body;" %(self.name)
		
		r = requests.get(
			"http://overpass-api.de/api/interpreter?data=%s" %(query)
			)

		data = json.loads(r.text)
		cordinates = []

		for y in [x['nodes'] for x in data['elements'] if x["type"] == 'way'][0]:
			cordinates.append([(x['lat'], x['lon'] )for x in data['elements'] if x["id"] == y][0])
		
		building_polygon = np.array(cordinates)

		##########################################
		# Calculate area of polygon
		##########################################

		geom = {
			'type': 'Polygon',
			'coordinates': [building_polygon]
			}

		s = shape(geom)

		proj = partial(
			pyproj.transform, pyproj.Proj(init='epsg:4326'),
			pyproj.Proj(init='epsg:3857')
			)

		s_new = transform(proj, s)
		projected_area = transform(proj, s).area

		street_sc_check = False
		for rec in data['elements']:
			if rec['type'] == 'way':
				self.type_id = rec['tags']['building'] if 'building' in rec['tags'] else "Nr"
				self.property_name = rec['tags']['name'] if 'name' in rec['tags'] else "Nr"


				if not self.street_sc:
					osm_street_name = rec['tags']['addr:street'] if 'addr:street' in rec['tags'] else ""
					
					if_standard_costs = self.env['standard.cost'].search([('name','=',osm_street_name)])

					if if_standard_costs:
						self.street_sc = if_standard_costs

					else:
						create_rec = self.env['standard.cost'].create({'name':osm_street_name})

						retrive_rec = self.env['standard.cost'].search([('name','=',osm_street_name)])

						self.street_sc = retrive_rec.id

						street_sc_check = True

				self.building_level = rec['tags']['building:levels'] if 'building:levels' in rec['tags'] else "1"
				self.building_material = rec['tags']['building:material'] if 'building:material' in rec['tags'] else "Nr"
				break

		self.surface_area = projected_area

		self.total_area = float(projected_area) * float(self.building_level)

		if self.type_id and self.type_id == 'commercial' or self.type_id == 'residential' or self.type_id == 'construction':
			for rec in self.owner_id:
				rec.type_id = self.type_id

		if len(self.owner_id) == 1:
			self.owner_id.area_own = self.total_area

		else:
			number_of_owner = len(self.owner_id)
			area_already_specified = sum(x.area_own for x in self.owner_id)
			remaining_area = self.total_area - area_already_specified
			no_f_ownr_alrdy_spcfid_area = 0
			for x in self.owner_id:
				if x.area_own !=0:
					no_f_ownr_alrdy_spcfid_area = no_f_ownr_alrdy_spcfid_area + 1

			if number_of_owner == no_f_ownr_alrdy_spcfid_area and remaining_area > 0:
				raise ValidationError(_("Almost %s square foot area is unspecified.Please allocate it") 
					%(remaining_area))

			if round(area_already_specified,3) > round(self.total_area,3):
				raise ValidationError(_("Area allocated to Owners is greater then Total area of Building"))

			for rec in self.owner_id:
				if rec.area_own == 0:
					rec.area_own = remaining_area / (number_of_owner - no_f_ownr_alrdy_spcfid_area)

				if self.type_id == "commercial" or self.type_id == "residential" or self.type_id == "construction":
					rec.type_id = self.type_id

		self.view_data_valuation = '1'
		if street_sc_check:
			return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': 'standard.cost',
                'target': 'current',
                'context': self._context,
                'res_id': retrive_rec.id,
                'flags': {'initial_mode': 'edit'},
            } 

	@api.one
	@api.depends('walls','roof','ceiling','floor','windows','doors','services','standard_cost')
	def _compute_rate(self):

		##########################################
		# Calculate rate per meter square
		##########################################
		if self.walls and self.roof and self.ceiling and self.floor and self.windows and self.doors and self.services:
			walls = self.walls
			roof = self.roof
			ceiling = self.ceiling
			floor = self.floor
			windows = self.windows
			doors = self.doors
			services = self.services

			walls_type = {
				'cement_blocks' : 100,
				'glass' : 87.5,
				'burnt_bricks' : 75,
				'treated_timber' : 62.5,
				'iron_sheet' : 50,
				'tree_sticks' : 37.5,
				'other' : 25,
				'none' : 12.5,
				}
			roof_type = {
				'roof_slab' : 100,
				'iron_sheet' : 87.5,
				'cemented_tiles' : 75,
				'tiles_sheets' : 62.5,
				'asbestos' : 50,
				'grass' : 37.5,
				'other' : 25,
				'none' : 12.5,
				}
			ceiling_type = {
				'cement' : 100,
				'gipsum' : 87.5,
				'treated_timber' : 75,
				'hardboard' : 62.5,
				'other' : 50,
				'none' : 37.5,
				}
			floor_type = {
				'tiles' : 100,
				'stones' : 87.5,
				'terrazo' : 75,
				'treated_timber' : 62.5,
				'cement' : 50,
				'other' : 37.5,
				'none' : 25,
				}
			windows_type = {
				'glass' : 100,
				'treated_timber' : 87.5,
				'treated_timber' : 75,
				'iron_sheet' : 62.5,
				'marine_board' : 50,
				'other' : 37.5,
				'none' : 25,
				}
			doors_type = {
				'treated_timber' : 100,
				'glass' : 87.5,
				'iron_sheet' : 75,
				'marine_board' : 62.5,
				'other' : 50,
				'none' : 37.5,
				}
			services_type = {
				'electricity_water_telephone' : 100,
				'electricity_water' : 87.5,
				'telephone_electricity' : 75,
				'electricity_only' : 62.5,
				'other' : 50,
				'none' : 37.5,
				}

			walls = walls_type[walls]
			roof = roof_type[roof]
			ceiling = ceiling_type[ceiling]
			floor = floor_type[floor]
			windows = windows_type[windows]
			doors = doors_type[doors]
			services = services_type[services]
			build_condition = (walls+roof+ceiling+floor+windows+doors+services) / 7

			self.rate_per_meter_square = int(self.standard_cost) * build_condition/100

	@api.one
	@api.depends('rate_per_meter_square','total_area')
	def _compute_replacement_cost(self):

		self.replacement_cost = self.rate_per_meter_square * self.total_area

	@api.one
	@api.depends('depreciation_factor','replacement_cost')
	def _compute_depreciated_replacement_cost(self):
		if self.depreciation_factor:
			self.depreciated_replacement_cost = self.replacement_cost - (self.replacement_cost * (self.depreciation_factor / 100))

	@api.onchange('site_works','depreciated_replacement_cost')
	def _compute_depreciated_site_works(self):
		if self.site_works:
			self.rateable_value = self.depreciated_replacement_cost + (self.depreciated_replacement_cost * (self.site_works / 100))

	#####################################################
	# States management
	#####################################################

	@api.multi
	def inits(self):
		#####################################################
		# Checking if the Update Information is clicks
		#####################################################
		if not self.view_data_valuation:
			raise ValidationError(_("Please click Update Information first"))
		# -----------------------------------------------------------
		
		#####################################################
		# double checking if the street is assign or not
		#####################################################
		if not self.street_sc:
			raise ValidationError(_("Please assign Street first"))
		# -----------------------------------------------------------

		#####################################################
		# double checking if the street_sc is exist on standard cost
		# and the cost is in accordance with address
		#####################################################

		standard_costs = self.env['standard.cost'].search([('name','=',self.street_sc.name)])

		if standard_costs and len(standard_costs) ==1:
			self.standard_cost =  standard_costs.cost
		else:
			self.standard_cost = 0
			raise ValidationError(_("This address : %s is not assign at standard cost or assign multiple times.Please fix it first.") %(self.street_sc.name))
		# -----------------------------------------------------------

		if self.view_data_valuation == True:
			if self.owner_id:
				number_of_owner = len(self.owner_id)
				area_already_specified = sum(x.area_own for x in self.owner_id)
				remaining_area = self.total_area - area_already_specified
				no_f_ownr_alrdy_spcfid_area = 0
				for x in self.owner_id:
					if x.area_own !=0:
						no_f_ownr_alrdy_spcfid_area = no_f_ownr_alrdy_spcfid_area + 1

				if remaining_area > 0:
					raise ValidationError(_("Almost %s square foot area is unspecified.Please allocate it") 
						%(remaining_area))

				if round(area_already_specified,3) > round(self.total_area,3):
					raise ValidationError(_("Area allocated to Owners is greater then Total area of Building"))

				for rec in self.owner_id:
					if rec.type_id == False:
						raise ValidationError(_("Please type property type of your owner: %s" %(rec.name.name)))
					
					if self.type_id in ['commercial','residential','construction']:
						if rec.type_id not in self.type_id:
							raise ValidationError(_("Type : %s for owner :%s is not valid." %(rec.type_id,rec.name.name)))
				
			else:
				raise ValidationError(_("Please assign owners of Building First"))

			self.write({'state': 'staging'})
		else:
			raise ValidationError(_("Please Update information before proceed."))

	@api.multi
	def verified(self):
		#####################################################
		# double checking if the street is assign or not
		#####################################################
		if not self.street_sc:
			raise ValidationError(_("Please assign Street first"))
		# -----------------------------------------------------------

		#####################################################
		# double checking if the Site works is assign or not
		#####################################################
		if self.site_works == 0.00:
			raise ValidationError(_("Please assign Site works first"))
		# -----------------------------------------------------------

		#####################################################
		# double checking if the street_sc is exist on standard cost
		# and the cost is in accordance with address
		#####################################################

		standard_costs = self.env['standard.cost'].search([('name','=',self.street_sc.name)])

		if standard_costs and len(standard_costs) ==1:
			self.standard_cost =  standard_costs.cost
		else:
			self.standard_cost = 0
			raise ValidationError(_("This address : %s is not assign at standard cost or assign multiple times.Please fix it first.") %(self.street_sc.name))
		# -----------------------------------------------------------
		
		if self.view_data_valuation == True:
			if self.owner_id:
				number_of_owner = len(self.owner_id)
				area_already_specified = sum(x.area_own for x in self.owner_id)
				remaining_area = self.total_area - area_already_specified
				no_f_ownr_alrdy_spcfid_area = 0
				for x in self.owner_id:
					if x.area_own !=0:
						no_f_ownr_alrdy_spcfid_area = no_f_ownr_alrdy_spcfid_area + 1

				if remaining_area > 0:
					raise ValidationError(_("Almost %s square foot area is unspecified.Please allocate it") 
						%(remaining_area))

				if round(area_already_specified,3) > round(self.total_area,3):
					raise ValidationError(_("Area allocated to Owners is greater then Total area of Building"))

				for rec in self.owner_id:
					if rec.type_id == False:
						raise ValidationError(_("Please type property type of your owner: %s" %(rec.name.name)))
					
					if self.type_id in ['commercial','residential','construction']:
						if rec.type_id not in self.type_id:
							raise ValidationError(_("Type : %s for owner :%s is not valid." %(rec.type_id,rec.name.name)))

				check_double = self.env['owner.building.line'].search([('name','=',self.name)])
				if check_double:
					check_double.unlink()
				for rec in self.owner_id:
					property_val =  rec.area_own * self.rate_per_meter_square
					
					rec.name.building_id.create({
						"name" : self.id,
						"property_name" : self.property_name,
						"area_own" : rec.area_own,
						"property_value" : property_val,
						"property_tax" : property_val * 0.15 / 100 if rec.type_id != 'commercial' else property_val * 0.20 / 100 ,
						"owner_form_id" : rec.name.id

						})
					if self.user_has_groups('textit_sms_service.group_sms_form'):
						number = '+225'+rec.name.mobile[1:]
						message = "Name : %s,TIN : %s,NIC : %s,PID : %s,Address : %s,Area Own : %s,Property Tax : %s TZS" %(
							rec.name.name,
							rec.name.tin,
							rec.name.identification_id,
							self.name,
							self.street_sc.name,
							"%.2f" % round(rec.area_own,2),
							"%.2f" % round(property_val * 0.15 / 100 if rec.type_id != 'commercial' else property_val * 0.20 / 100,2)
							)
						_logger.info('Sending message : '+message+' on Number : '+number)

						self.env['sms.templates'].send_sms(number = number,message=message)

			else:
				raise ValidationError(_("Please assign owners of Building First"))

			# -----------------------------------------------------------

			if self.tenant_id:


				check_double = self.env['tenant.building.line'].search([('name','=',self.name)])
				if check_double:
					check_double.unlink()

				for rec in self.tenant_id:
					if rec.citizen:
						tax = (int(rec.rent)/100) * 10
					else:
						tax = (int(rec.rent)/100) * 15
					
					rec.name.building_rent_id.create({
						"name" : self.id,
						"property_name" : self.property_name,
						"rental_tax" : tax,
						"tenant_form_id" : rec.name.id

						})
					if self.user_has_groups('textit_sms_service.group_sms_form'):
						number = '+225'+rec.name.mobile[1:]
						message = "Name : %s,TIN : %s,NIC : %s,PID : %s,Address : %s,Rental Tax : %s TZS" %(
							rec.name.name,
							rec.name.tin,
							rec.name.identification_id,
							self.name,
							self.street_sc.name,
							"%.2f" % round(tax)
							)
						_logger.info('Sending message : '+message+' on Number : '+number)

						self.env['sms.templates'].send_sms(number = number,message=message)


			# -----------------------------------------------------------
			self.write({'state': 'verified'})
		else:
			raise ValidationError(_("Please Update information before proceed."))

	@api.multi
	def cancel(self):
		self.write({'state': 'draft'})

	@api.multi
	def go_back_to_staging(self):
		self.write({'state': 'staging'})

	#####################################################
	# Adding constrant for uniqe name per record.
	#####################################################

	@api.multi
	def copy(self, default=None):
		self.ensure_one()
		default = dict(default or {}, name=_('%s (copy)') % self.name)
		return super(BuildingData, self).copy(default)

	_sql_constraints = [
        (
        	'uniq_name', 
        	'unique(name)', 
        	"The building already exists with this Number . Reference Number must be unique!"
        ),
    ]


class BuildingOwnerLine(models.Model):
	_name = 'building.owner.line'
	
	#####################################################
	# Below varibles are Owner relation with Building.
	#####################################################

	name = fields.Many2one('res.partner', domain=[('owner', '=', True)], required=True)
	identification_id = fields.Char("Identification No", related='name.identification_id')
	area_own = fields.Float(digits=dp.get_precision('Area Own by Owner'))
	type_id = fields.Selection([
        ('commercial', 'Commercial'),
        ('residential', 'Residential'),
        ('construction', 'Construction')
        ], string= "Area Type")


	building_data_id = fields.Many2one('building.data',  ondelete='cascade')

class BuildingtenantLine(models.Model):
	_name = 'building.tenant.line'
	
	#####################################################
	# Below varibles are tenant relation with Building.
	#####################################################

	name = fields.Many2one('res.partner', domain=[('tenant', '=', True)], required=True)
	owner = fields.Many2one('res.partner', required=True)
	identification_id = fields.Char("Identification No", related='name.identification_id', required=True)
	citizen = fields.Boolean(default=True)
	type_id = fields.Selection([
        ('commercial', 'Commercial'),
        ('residential', 'Residential'),
        # ('construction', 'Construction')
        ], string= "Area Type" , required=True)
	rent = fields.Char(required=True)
	# rent = fields.Float(digits=dp.get_precision('Rent Amount'))

	building_data_id = fields.Many2one('building.data',  ondelete='cascade')

class BuildingAccommodationLine(models.Model):
	_name = 'building.accommodation.line'

	#####################################################
	# Below varibles are Accommodation relation with Building.
	#####################################################

	name = fields.Many2one('accommodation')
	quantity = fields.Integer(default=1)

	building_accommodation_line_id = fields.Many2one('building.data')

class Accommodation(models.Model):
	_name = 'accommodation'

	name = fields.Char()

class FittingFixture(models.Model):
	_name = 'fitting.fixture'

	name = fields.Char()

class StandardCost(models.Model):
	_name = 'standard.cost'

	name = fields.Char("Street")
	cost = fields.Float()