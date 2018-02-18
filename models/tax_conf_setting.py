# -*- coding: utf-8 -*-
from odoo import fields, models,api,_
from odoo.exceptions import ValidationError,RedirectWarning


class TaxConfiguration(models.TransientModel):
    _name = 'tax.config.settings'
    _inherit = 'res.config.settings'

    def execute(self):
        get_param = self.env['ir.config_parameter'].get_param

        textit_url = get_param('textit_url', default='')

        kb_username = get_param('kb_username', default='')
        kb_password = get_param('kb_password', default='')
        api_url = get_param('api_url', default='')

        if textit_url == '':
            action = self.env.ref('base_setup.action_general_configuration')
            raise RedirectWarning(_('One thing is missing.'),
                action.id, _('Configure The Textit SMS Integrator Now'))

        if kb_username == '' or kb_password == '' or api_url == '':
            action = self.env.ref('account.action_account_config')
            raise RedirectWarning(_('KillBill Cradentials are not assigned'),
                action.id, _('Configure The KillBill Now'))

        return super(TaxConfiguration, self).execute()