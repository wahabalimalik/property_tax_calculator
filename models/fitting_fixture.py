# -*- coding: utf-8 -*-

from odoo import models,fields

class FittingFixture(models.Model):
	_name = 'fitting.fixture'

	name = fields.Char()