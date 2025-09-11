from dataclasses import fields

from odoo import api, models,fields
from odoo.addons.base.models.res_users import is_selection_groups
from odoo.addons.mail.models.discuss.res_users import ResUsers
import requests
from datetime import datetime


class ResUsers(models.Model):
    _inherit = "res.users"

    # Load Limited Whatsapp Channel
    def _init_messaging(self):
        """
        This method is overwritten to load the limited WhatsApp Channels.
        """
        res=super()._init_messaging()
        load_channel_limit = int(
            self.env['ir.config_parameter'].sudo().get_param('tus_meta_wa_discuss.whatsapp_channel'))
        wplimit=load_channel_limit
        fblimit=load_channel_limit
        inslimit=load_channel_limit

        if self._context.get('wplimit', False):
            wplimit = self._context.get('wplimit', False)

        if self._context.get('fblimit', False):
            fblimit = self._context.get('fblimit', False)

        if self._context.get('inslimit', False):
            inslimit = self._context.get('inslimit', False)

        whatsapp_channels = [i for i in res.get('channels') if i.get('channel_type') == 'WpChannels']
        sorted_data = sorted(
                whatsapp_channels,
            key=lambda x: datetime.strptime(x['last_interest_dt'], '%Y-%m-%d %H:%M:%S') if x.get(
                'last_interest_dt') else datetime.min,
            reverse=True
        )
        new_whatsapp_channels = [sorted_data[i].get('id') for i in range(len(sorted_data))][:wplimit]
        new_facebook_channels = [i.get('id') for i in res.get('channels') if i.get('channel_type') == 'FbChannels'][:fblimit]
        new_insta_channels = [i.get('id') for i in res.get('channels') if i.get('channel_type') == 'InstaChannels'][:inslimit]
        new_channels = [i.get('id') for i in res.get('channels') if i.get('channel_type') not in ['WpChannels', 'FbChannels', 'InstaChannels']]
        # channels = [i for i in res.get('channels') if i.get('id') in new_whatsapp_channels + new_channels]
        channels = []
        for channel in res.get('channels'):
            if channel.get('id') in new_whatsapp_channels + new_channels:
                channel['company_id'] = self.env['discuss.channel'].sudo().search([('id','=',channel.get('id')), ('company_id', 'in', self.env.companies.ids)]).company_id.id
                channels.append(channel)
            if channel.get('id') in new_facebook_channels + new_channels:
                channels.append(channel)
            if channel.get('id') in new_insta_channels + new_channels:
                channels.append(channel)
        res.update({'channels':channels})
        return res

    @api.model
    def get_limit_show(self):
        """
        Load parameters for the JS.
        """
        return {'show': int(self.env['ir.config_parameter'].sudo().get_param('tus_meta_wa_discuss.load_whatsapp_channel')),
                'default_show': int(self.env['ir.config_parameter'].sudo().get_param('tus_meta_wa_discuss.whatsapp_channel'))}

