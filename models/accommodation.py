# -*- coding: utf-8 -*-

from odoo import models,fields

class Accommodation(models.Model):
	_name = 'accommodation'

	name = fields.Char()