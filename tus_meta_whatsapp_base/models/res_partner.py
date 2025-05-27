from odoo import _, api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_whatsapp_number = fields.Boolean('Is Whatsapp Number')
    channel_provider_line_ids = fields.One2many('channel.provider.line', 'partner_id', 'Channel Provider Line')
    otp_text = fields.Char(string="OTP Text")
    otp_time = fields.Datetime(string='OTP Time')

    def check_whatsapp_history(self):
        self.ensure_one()
        return {
            "name": _("Whatsapp History"),
            "type": "ir.actions.act_window",
            "res_model": "whatsapp.history",
            "view_mode": "tree",
            "domain": [("partner_id", "=", self.id)],
        }

    # @api.model
    # def im_search(self, name, limit=20, excluded_ids=None):
    #     """ Search partner with a name and return its id, name and im_status.
    #         Note : the user must be logged
    #         :param name : the partner name to search
    #         :param limit : the limit of result to return
    #     """
    #     # This method is supposed to be used only in the context of channel creation or
    #     # extension via an invite. As both of these actions require the 'create' access
    #     # right, we check this specific ACL.
    #     if self.env['discuss.channel'].check_access_rights('create', raise_exception=False):
    #         name = '%' + name + '%'
    #         excluded_partner_ids = [self.env.user.partner_id.id]
    #         self.env.cr.execute("""
    #                         SELECT
    #                             P.id as id,
    #                             P.name as name
    #                         FROM res_partner P
    #                         WHERE P.name ILIKE %s
    #                             AND P.id NOT IN %s
    #                         LIMIT %s
    #                     """, (name, tuple(excluded_partner_ids), limit))
    #         return self.env.cr.dictfetchall()
    #     else:
    #         return {}

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ResPartner, self).create(vals_list)
        for rec in res:
            if rec.mobile:
                rec.mobile = rec.mobile.strip('+').replace(" ", "").replace("-", "")
        return res

    def write(self, vals):
        if 'mobile' in vals:
            if vals.get('mobile'):
                vals.update({'mobile':vals.get('mobile').strip('+').replace(" ", "")})
        res= super(ResPartner, self).write(vals)
        return res

    def sort_whatsapp_channels(self):
        self.ensure_one()
        if self.mobile:
            channels = self.env['discuss.channel'].search([('name', '=', self.mobile)])
            del_channels = self.env['discuss.channel']
            if len(channels) > 1:
                try:
                    main_channel = channels[0]
                    message = self.env['mail.message'].search(
                        [('model', '=', 'discuss.channel'), ('res_id', 'in', channels[1:].ids)])
                    message.update({'res_id': main_channel.id})
                    del_channels += channels[1:]
                except:
                    a = 1
            if del_channels:
                del_channels.unlink()

    def sort_mobile_numbers(self):
        partners = self.search([])
        for par in partners:
            if par.mobile:
                par.mobile = par.mobile.strip('+').replace(" ", "").replace("-", "")
            elif par.phone:
                par.mobile = par.phone.strip('+').replace(" ", "").replace("-", "")

    def unlink_duplicate_channels(self):
        channels = self.env['discuss.channel'].search([('whatsapp_channel', '=', True)])
        channel_name = list(set(channels.mapped('name')))
        del_channels = self.env['discuss.channel']
        for val in channel_name:
            fil_channel = channels.filtered(lambda x: x.name == val)
            if len(fil_channel) > 1:
                try:
                    main_channel = fil_channel[0]
                    message = self.env['mail.message'].search(
                        [('model', '=', 'discuss.channel'), ('res_id', 'in', fil_channel[1:].ids)])
                    message.update({'res_id': main_channel.id})
                    del_channels += fil_channel[1:]
                except:
                    a = 1
        if del_channels:
            del_channels.unlink()


