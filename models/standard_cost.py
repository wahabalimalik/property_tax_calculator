# -*- coding: utf-8 -*-

from odoo import models,fields

class StandardCost(models.Model):
	_name = 'standard.cost'

	name = fields.Char("Street")
	cost = fields.Float()