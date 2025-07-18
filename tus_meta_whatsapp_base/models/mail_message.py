import logging
import re
from odoo import _, api, fields, models, modules, tools
from binascii import Error as binascii_error
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import clean_context

_logger = logging.getLogger(__name__)
_image_dataurl = re.compile(r'(data:image/[a-z]+?);base64,([a-z0-9+/\n]{3,}=*)\n*([\'"])(?: data-filename="([^"]*)")?', re.I)
_href_pattern = re.compile(r'<a\s+[^>]*href="([^"]+)"[^>]*>[^<]+</a>')
_pattern = r'<br\s*/?>'


class Message(models.Model):
    """ Messages model: system notification (replacing res.log notifications),
        comments (OpenChatter discussion) and incoming emails. """
    _inherit = 'mail.message'

    message_type = fields.Selection(selection_add=[('wa_msgs', 'WA Msgs')], ondelete={'wa_msgs': lambda recs: recs.write({'wa_msgs': 'odoo'})})
    isWaMsgs = fields.Boolean("WA msgs")
    wa_message_id = fields.Char("Whatsapp Message ID")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    chatter_wa_model = fields.Char('Chatter Wa Message Model', index=True)
    chatter_wa_res_id = fields.Many2oneReference('Chatter Wa Res Id', index=True, model_field='chatter_wa_model')
    chatter_wa_message_id = fields.Integer('Chatter Wa Message Id')
    wa_delivery_status = fields.Char('Whatsapp Delivery Status')
    wa_error_message = fields.Char('Whatsapp Error')
    isWaMsgsRead = fields.Boolean("WA msgs Read")
    wp_status = fields.Selection([
        ('in queue', 'In queue'),
        ('sent', 'Sent'),
        ('delivered', 'delivered'),
        ('received', 'Received'), ('read', 'Read'), ('fail', 'Fail')], store=True)

    @api.model_create_multi
    def create(self, values_list):
        # Multi Companies and Multi Providers Code Here
        provider_id = False
        channel = self.env['discuss.channel']
        tracking_values_list = []
        is_tus_discuss_installed = self.env['ir.module.module'].sudo().search([('state', '=', 'installed'), ('name', '=', 'tus_meta_wa_discuss')])
        for values in values_list:

            if values.get('model') and values.get('res_id'):
                channel = self.env[values.get('model')].browse(values.get('res_id'))
            if values.get('model') == 'discuss.channel' and channel.whatsapp_channel and is_tus_discuss_installed:
                values.update({'message_type': 'wa_msgs', 'isWaMsgs': True})
            if 'email_from' not in values:  # needed to compute reply_to

                author_id, email_from = self.env['mail.thread'].with_context(temporary_id=110.2)._message_compute_author(values.get('author_id'),
                                                                                        email_from=None,
                                                                                        raise_exception=False)
                values['email_from'] = email_from
            if not values.get('message_id'):
                values['message_id'] = self._get_message_id(values)
            if 'reply_to' not in values:
                values['reply_to'] = self._get_reply_to(values)
            if 'record_name' not in values and 'default_record_name' not in self.env.context:
                values['record_name'] = self._get_record_name(values)

            if 'attachment_ids' not in values:
                values['attachment_ids'] = []
            # extract base64 images
            if 'body' in values:
                Attachments = self.env['ir.attachment'].with_context(clean_context(self._context))
                data_to_url = {}

                def base64_to_boundary(match):
                    key = match.group(2)
                    if not data_to_url.get(key):
                        name = match.group(4) if match.group(4) else 'image%s' % len(data_to_url)
                        try:
                            attachment = Attachments.create({
                                'name': name,
                                'datas': match.group(2),
                                'res_model': values.get('model'),
                                'res_id': values.get('res_id'),
                            })
                        except binascii_error:
                            _logger.warning(
                                "Impossible to create an attachment out of badly formated base64 embedded image. Image has been removed.")
                            return match.group(
                                3)  # group(3) is the url ending single/double quote matched by the regexp
                        else:
                            attachment.generate_access_token()
                            values['attachment_ids'].append((4, attachment.id))
                            data_to_url[key] = [
                                '/web/image/%s?access_token=%s' % (attachment.id, attachment.access_token), name]
                    return '%s%s alt="%s"' % (data_to_url[key][0], match.group(3), data_to_url[key][1])

                values['body'] = _image_dataurl.sub(base64_to_boundary, tools.ustr(values['body']))

            # delegate creation of tracking after the create as sudo to avoid access rights issues
            tracking_values_list.append(values.pop('tracking_value_ids', False))

        messages = super(Message, self).create(values_list)

        check_attachment_access = []
        if all(isinstance(command, int) or command[0] in (4, 6) for values in values_list for command in
               values.get('attachment_ids')):
            for values in values_list:
                for command in values.get('attachment_ids'):
                    if isinstance(command, int):
                        check_attachment_access += [command]
                    elif command[0] == 6:
                        check_attachment_access += command[2]
                    else:  # command[0] == 4:
                        check_attachment_access += [command[1]]
        else:
            check_attachment_access = messages.mapped('attachment_ids').ids  # fallback on read if any unknow command
        if check_attachment_access:
            self.env['ir.attachment'].browse(check_attachment_access).check(mode='read')

        for message, values, tracking_values_cmd in zip(messages, values_list, tracking_values_list):
            if tracking_values_cmd:
                vals_lst = [dict(cmd[2], mail_message_id=message.id) for cmd in tracking_values_cmd if
                            len(cmd) == 3 and cmd[0] == 0]
                other_cmd = [cmd for cmd in tracking_values_cmd if len(cmd) != 3 or cmd[0] != 0]
                if vals_lst:
                    self.env['mail.tracking.value'].sudo().create(vals_lst)
                if other_cmd:
                    message.sudo().write({'tracking_value_ids': tracking_values_cmd})

            if message.is_thread_message(values):
                message._invalidate_documents(values.get('model'), values.get('res_id'))

        if 'whatsapp_marketing' not in self.env.context:
            for values in values_list:
                if values.get('message_type') == 'wa_msgs':
                    user = self.env.user
                    if re.search(_pattern, values.get('body', '')):
                        wa_message = re.sub(_pattern, '\n', values.get('body', ''))
                    else:
                        wa_message = _href_pattern.sub(r'\1', values.get('body', ''))
                    vals = {
                        'author_id': user.partner_id.id,
                        'message': wa_message,
                        'type': 'in queue',
                        'attachment_ids': values.get('attachment_ids'),
                        'model': self._context.get('active_model', 'discuss.channel'),
                        'mail_message_id': messages.id,
                    }
                    if 'user_id' in self.env.context and self.env.context.get('user_id'):
                        user = self.env.context.get('user_id')
                    if user.id != self.env.ref('base.public_user').id:
                        if values.get('model') == 'discuss.channel':
                            channel_company_line_id = self.env['channel.provider.line'].search(
                                [('channel_id', '=', message.res_id)])
                            # phone change to mobile
                            if channel_company_line_id.partner_id.mobile:
                                provider_id = channel_company_line_id.provider_id if channel_company_line_id.provider_id else user.provider_id
                                # Multi Companies and Multi Providers Code Here
                                if provider_id:
                                    vals.update({
                                        'provider_id': provider_id.id,
                                        'partner_id': channel_company_line_id.partner_id.id,
                                        'phone': channel_company_line_id.partner_id.mobile,
                                    })

                        else:
                            partner = self.env['res.partner']
                            data = self.env[values.get('model')].sudo().search_read(
                                [('id', '=', int(values.get('res_id')))])
                            if values.get('model') == 'res.partner':
                                partner |= self.env['res.partner'].browse(data[0]['id'])
                            elif self._context.get('partner_id'):
                                partner |= self.env['res.partner'].browse(self._context.get('partner_id', []))
                            elif 'partner_id' in data[0]:
                                if data[0]['partner_id']:
                                    partner |= self.env['res.partner'].browse(data[0]['partner_id'][0])
                                else:
                                    raise AccessError(_("Partner must be Required for whatsapp message!"))
                            else:
                                raise AccessError(_("Partner must be Required for whatsapp message!"))

                            if partner and partner.mobile:
                                # Multi Companies and Multi Providers Code Here
                                user_partner = user.partner_id
                                provider_id = self.env.context.get('provider_id') if self.env.context.get(
                                    'provider_id') else user.provider_id
                                if provider_id:
                                    channel = provider_id.get_channel_whatsapp(partner, provider_id.user_id)
                                author = self.env['res.partner'].search(
                                    [('id', '=', values.get('author_id'))]) if values.get('author_id') and values.get(
                                    'parent_id') else user_partner
                                message_values = {
                                    'body': values.get('body', ''),
                                    'author_id': author.id,
                                    'email_from': author.email or '',
                                    'model': values.get('model'),
                                    'message_type': 'comment',
                                    'isWaMsgs': True,
                                    'subtype_id': self.env['ir.model.data'].sudo()._xmlid_to_res_id('mail.mt_comment'),
                                    'partner_ids': [(4, author.id)],
                                    'res_id': values.get('res_id'),
                                    'reply_to': author.email,
                                    'attachment_ids': values.get('attachment_ids'),
                                    "parent_id": values.get('parent_id')
                                }
                                mail_message = self.env['mail.message'].sudo().create(
                                    message_values)
                                if provider_id:
                                    vals.update({
                                        'provider_id': provider_id.id,
                                        'partner_id': partner.id,
                                        'phone': partner.mobile,
                                    })
                                else:
                                    raise AccessError(_("Please add provider in User!"))

                                for mes in messages:
                                    mes.sudo().write({
                                        'model': "discuss.channel",
                                        'res_id': channel.id,
                                        'chatter_wa_model': values.get("model"),
                                        'chatter_wa_res_id': values.get("res_id"),
                                        'chatter_wa_message_id': mail_message.id,
                                    })

                        if 'company_id' in self.env.context:
                            vals.update({'company_id': self.env.context.get('company_id')})

                        if message.wa_message_id:
                            vals.update({'message_id': values.get('wa_message_id')})

                        if self.env.context.get('whatsapp_application'):
                            self.env['whatsapp.history'].sudo().with_context({'whatsapp_application': True}).create(vals)

                        if message.parent_id and not self.env.context.get(
                                'whatsapp_application') and self.env.context.get(
                            'message') != 'received':
                            self.env['whatsapp.history'].sudo().with_context(
                                {'wa_messsage_id': message, 'message_parent_id': message.parent_id}).create(vals)

                        if not message.parent_id and not self.env.context.get(
                                'whatsapp_application') and self.env.context.get(
                            'message') != 'received' and not self.env.context.get('template_send'):
                            self.env['whatsapp.history'].sudo().with_context({'wa_messsage_id': message}).create(vals)

                        if self.env.context.get('template_send'):
                            if self._context.get('active_model_id'):
                                vals.update({'rec_id': self._context.get('active_model_id')})
                            self.env['whatsapp.history'].sudo().with_context().create(vals)
        return messages

    def _get_message_format_fields(self):
        res = super()._get_message_format_fields()
        res += ['wa_delivery_status', 'wa_error_message', 'wp_status','isWaMsgs']
        return res

