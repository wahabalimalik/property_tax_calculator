# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def create(self, vals):
        record = super(Base, self).create(vals)
        self._event('on_record_create').notify(record, fields=vals.keys())
        return record