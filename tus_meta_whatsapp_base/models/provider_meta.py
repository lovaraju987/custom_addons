from odoo import models, api, fields, _
from odoo.http import request
import requests
import json
from odoo.exceptions import UserError, ValidationError
import time
import string
import secrets
import urllib.request
import base64
import tempfile
import shutil
import os


class Provider(models.Model):
    _inherit = 'provider'

    provider = fields.Selection(
        selection_add=[('graph_api', "Graph API")], ondelete={'graph_api': 'set default'}, default="graph_api")
    graph_api_url = fields.Char(string="API URL", default="https://graph.facebook.com/v16.0/")
    graph_api_instance_id = fields.Char(string="Instance ID")
    graph_api_business_id = fields.Char(string="WhatsApp Business Account ID")
    graph_api_token = fields.Char(string="Token")
    graph_api_authentication = fields.Selection(
        [('bearer_token', "Bearer Token")], default='bearer_token',
        string='Authentication')
    graph_api_authenticated = fields.Boolean('Authenticated', readonly=True)
    graph_api_app_id = fields.Char(string="App ID")
    user_id = fields.Many2one(string="User", comodel_name='res.users', default=lambda self: self.env.user)

    is_token_generated = fields.Boolean('Is Token Generated')
    call_back_url = fields.Html(string="Call Back URL & Verify Token")

    def GenerateVerifyToken(self):
        seconds = time.time()
        unix_time_to_string = str(seconds).split('.')[0]  # time.time() generates a float example 1596941668.6601112
        alphaNumeric = string.ascii_uppercase + unix_time_to_string
        alphaNumericlower = string.ascii_lowercase + unix_time_to_string
        firstSet = ''.join(secrets.choice(alphaNumeric) for i in range(4))
        secondSet = ''.join(secrets.choice(alphaNumeric) for i in range(4))
        thirdSet = ''.join(secrets.choice(alphaNumericlower) for i in range(4))
        forthSet = ''.join(secrets.choice(alphaNumeric) for i in range(4))
        fifthset = ''.join(secrets.choice(alphaNumericlower) for i in range(4))
        token = firstSet + secondSet + thirdSet + forthSet + fifthset
        return token

    def meta_error_message_display(self, answer):
        if json.loads(answer.text) and 'error' in json.loads(answer.text):
            if 'error_user_msg' in json.loads(answer.text).get('error') and 'error_user_title' in json.loads(
                    answer.text).get('error') and 'error_data' not in json.loads(answer.text).get('error'):
                dict = 'Title  :  ' + json.loads(answer.text).get('error').get(
                    'error_user_title') + '\nMessage  :  ' + json.loads(answer.text).get('error').get(
                    'error_user_msg')
                raise UserError(_(dict))
            elif 'error_user_msg' in json.loads(answer.text).get('error') and 'error_user_title' in json.loads(
                    answer.text).get('error') and 'error_data' in json.loads(answer.text).get('error'):
                dict = 'Title  :  ' + json.loads(answer.text).get('error').get(
                    'error_user_title') + '\nMessage  :  ' + json.loads(answer.text).get('error').get(
                    'error_user_msg') + '\n \n' + json.loads(answer.text).get('error').get('error_data').get(
                    'details')
                raise UserError(_(dict))
            if 'message' in json.loads(answer.text).get('error') and 'error_data' not in json.loads(
                    answer.text).get('error'):
                dict = json.loads(answer.text).get('error').get('message')
                raise UserError(_(dict))
            elif 'message' in json.loads(answer.text).get('error') and 'error_data' in json.loads(
                    answer.text).get('error') and 'details' in json.loads(
                answer.text).get('error').get('error_data'):
                dict = json.loads(answer.text).get('error').get('message') + '\n \n' + json.loads(
                    answer.text).get('error').get('error_data').get('details')
                raise UserError(_(dict))
            else:
                dict = json.loads(answer.text).get('error').get('message')
                raise UserError(_(dict))

    def reload_with_get_status(self):
        if self.graph_api_url and self.graph_api_instance_id and self.graph_api_token:
            url = self.graph_api_url + self.graph_api_instance_id + "?access_token=" + self.graph_api_token

            payload = {
                'full': True,
            }
            headers = {}
            try:
                response = requests.request("GET", url, headers=headers, data=payload)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if response.status_code == 200:
                dict = json.loads(response.text)
                if dict['id'] == self.graph_api_instance_id:
                    self.graph_api_authenticated = True

                    IrConfigParam = request.env['ir.config_parameter'].sudo()
                    base_url = IrConfigParam.get_param('web.base.url', False)

                    data = {
                        "webhookUrl": base_url + "/graph_tus/webhook"
                    }
                    verify_token = self.GenerateVerifyToken()
                    self.call_back_url = ('<p>Now, You can set below details to your facebook configurations.</p><p>Call Back URL: <u><a href="%s">%s</a></u></p><p>Verify Token: <u '
                                          'style="color:#017e84">%s</u></p>') % (
                    data.get('webhookUrl'), data.get('webhookUrl'), verify_token)
                    self.is_token_generated = True
            else:
                self.graph_api_authenticated = False
                self.call_back_url = '<p>Oops, something went wrong, Kindly Double Check the above Credentials. </p>'

    def get_whatsapp_business_details(self):
        if self.graph_api_url and self.graph_api_instance_id and self.graph_api_token:
            url = self.graph_api_url + self.graph_api_instance_id + '/whatsapp_business_profile?fields=about,address,description,email,profile_picture_url,websites,vertical'
            data = {}
            headers = {
                'Authorization': 'Bearer ' + self.graph_api_token
            }
            try:
                response = requests.request("GET", url, headers=headers, data=data)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            try:
                if response.status_code == 200:
                    dict = json.loads(response.text)
                    for data in dict.get('data'):
                        profile_picture_url = data.get('profile_picture_url')
                        self.about = data.get('about', '')
                        self.business_address = data.get('address', '')
                        self.business_description = data.get('description', '')
                        self.business_email = data.get('email', '')
                        self.business_website = data.get('websites', '')
                        self.business_vertical = data.get('vertical', '')
                        if profile_picture_url:
                            business_profile_picture = urllib.request.urlopen(profile_picture_url).read()
                            self.business_profile_picture = base64.b64encode(business_profile_picture)
            except Exception as e:
                raise ValidationError(e)
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    def get_phone_number_by_id(self):
        if self.graph_api_url and self.graph_api_instance_id and self.graph_api_token:
            url = self.graph_api_url + self.graph_api_instance_id
            data = {}
            headers = {
                'Authorization': 'Bearer ' + self.graph_api_token
            }
            try:
                response = requests.request("GET", url, headers=headers, data=data)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            try:
                if response.status_code == 200:
                    data = json.loads(response.text)
                    if data:
                        self.verified_name = data.get('verified_name', '')
                        self.code_verification_status = data.get('code_verification_status', '')
                        self.display_phone_number = data.get('display_phone_number', '')
                        self.quality_rating = data.get('quality_rating', '')
                        self.platform_type = data.get('platform_type', '')
                        self.throughput_level = data.get('throughput').get('level') if data.get('throughput') and data.get('throughput').get('level') else ''
                        self.webhook_configuration = data.get('webhook_configuration').get('application') if data.get('webhook_configuration') and data.get('webhook_configuration').get('application') else ''
            except Exception as e:
                raise ValidationError(e)
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    def update_business_details(self):
        pass

    def get_url(self, provider, media_id, phone_number_id):
        if provider.graph_api_authenticated:
            url = provider.graph_api_url + media_id + "?phone_number_id=" + phone_number_id + "&access_token=" + provider.graph_api_token
            headers = {'Content-type': 'application/json'}
            payload = {}
            try:
                answer = requests.request("GET", url, headers=headers, data=payload)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                self.meta_error_message_display(answer)
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    def graph_api_upload_demo_document(self, attachment):
        if self.graph_api_authenticated:
            url = self.graph_api_url + self.graph_api_app_id + "/uploads"
            data = {
                'file_length': attachment.file_size,
                'file_type': attachment.mimetype,
            }
            headers = {
                'Authorization': 'Bearer ' + self.graph_api_token
            }
            try:
                session_response = requests.post(url, headers=headers, data=data)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if session_response.status_code != 200:
                raise UserError(
                    ("Document upload session open failed"))
            else:
                dicto = json.loads(session_response.text)
                session_response_id = dicto.get('id')
                url = self.graph_api_url + session_response_id
                headers = {
                    'file_offset': '0',
                    'Authorization': 'OAuth ' + self.graph_api_token
                }
                try:
                    answer = requests.post(url, headers=headers, params=data, data=attachment.datas)
                except requests.exceptions.ConnectionError:
                    raise UserError(
                        ("please check your internet connection."))
                if answer.status_code != 200:
                    self.meta_error_message_display(answer)
                return answer

    def graph_api_get_whatsapp_template(self):
        if self.graph_api_authenticated:
            url = self.graph_api_url + self.graph_api_business_id + "/message_templates?limit=6000"
            data = {}
            headers = {
                'Authorization': 'Bearer ' + self.graph_api_token
            }
            try:
                answer = requests.get(url, data=json.dumps(data), headers=headers)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                self.meta_error_message_display(answer)
            else:

                whatsapp_templates = json.loads(answer.text)
                for template in whatsapp_templates['data']:
                    wa_template = self.env['wa.template'].search([('graph_message_template_id', '=', template['id'])])
                    if not wa_template:
                        vals = {
                            'name': template['name'],
                            'provider_id': self.id,
                            'category': template['category'].lower(),
                            'template_status': template['status'],
                            'graph_message_template_id': template['id'],
                            'template_type': 'template',
                            'state': 'added',
                            'language': template['language'],
                            'model_id': self.env.ref('base.model_res_partner').id,
                        }
                        component_list = []
                        for component in template['components']:
                            if component['type'] == 'BODY':
                                vals['body_html'] = component['text']
                            if component['type'] == 'HEADER':
                                if component['format'] == 'TEXT':
                                    component_list.append((0, 0, {
                                        'type': component['type'].lower(),
                                        'formate': component['format'].lower(),
                                        'text': component['text']
                                    }))
                                elif component['format'] in ('IMAGE', 'VIDEO', 'DOCUMENT'):
                                    component_list.append((0, 0, {
                                        'type': component['type'].lower(),
                                        'formate': 'media',
                                        'formate_media_type': 'dynamic',
                                        'media_type': component['format'].lower(),
                                    }))

                            if component['type'] in ['BODY', 'FOOTER']:
                                component_list.append((0, 0, {
                                    'type': component['type'].lower(),
                                    'text': component['text']
                                }))
                            if component['type'] == 'BUTTONS' and component['buttons']:
                                button_list = []
                                for button in component['buttons']:
                                    button_dict = {}
                                    if button['type'] == 'PHONE_NUMBER':
                                        button_dict.update({'button_type': 'phone', 'button_text': button['text'], 'phone_number': button['phone_number']})
                                    if button['type'] == 'URL' and not button.get('example'):
                                        button_dict.update({'button_type': 'url', 'button_text': button['text'], 'url_type': 'static', 'static_website_url': button['url']})
                                    if button['type'] == 'URL' and button.get('example'):
                                        button_dict.update({'button_type': 'url', 'button_text': button['text'], 'url_type': 'dynamic', 'dynamic_website_url': button['url']})
                                    if button['type'] == 'QUICK_REPLY':
                                        button_dict.update(
                                            {'button_type': 'quick_reply', 'button_text': button['text']})
                                    if button['type'] == 'COPY_CODE':
                                        button_dict.update(
                                            {'button_type': 'copy_code', 'button_text': button['text'], 'coupon_text': button['example'][0]})
                                    button_list.append(button_dict)
                                component_list.append((0, 0, {'type': 'buttons', 'wa_button_ids': [(5, 0, 0)] + [(0, 0, button_vals) for button_vals in button_list]}))

                        vals['components_ids'] = component_list

                        self.env['wa.template'].create(vals)

        else:
            raise UserError(
                ("please authenticated your whatsapp."))




    # phone change to mobile
    def graph_api_direct_send_message(self, recipient, message):
        if self.graph_api_authenticated:
            data = {}
            # if quotedMsgId:
            #     data.update({'quotedMsgId':quotedMsgId})
            # phone change to mobile
            data = {
                "messaging_product": "whatsapp",
                "to": recipient.phone or recipient.mobile,
                "type": "text",
                "text": {
                    "body": message,
                }
            }
            url = self.graph_api_url + self.graph_api_instance_id + "/messages?access_token=" + self.graph_api_token
            headers = {
                'Content-Type': 'application/json',
                # 'Authorization': 'Bearer '+self.graph_api_token
            }
            try:
                answer = requests.post(url, data=json.dumps(data), headers=headers)

            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                self.meta_error_message_display(answer)
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    def graph_api_send_message(self, recipient, message, quotedMsgId):
        if self.graph_api_authenticated:
            data = {}
            # if quotedMsgId:
            #     data.update({'quotedMsgId':quotedMsgId})
            # phone change to mobile
            data = {
                "messaging_product": "whatsapp",
                "to": recipient.mobile,
                "type": "text",
                "text": {
                    "body": message,
                }
            }
            url = self.graph_api_url + self.graph_api_instance_id + "/messages?access_token=" + self.graph_api_token
            headers = {
                'Content-Type': 'application/json',
                # 'Authorization': 'Bearer '+self.graph_api_token
            }
            try:
                answer = requests.post(url, data=json.dumps(data), headers=headers)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                self.meta_error_message_display(answer)
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    # phone chnage to mobile
    def graph_api_direct_send_image(self, mobile, attachment_id):
        if self.graph_api_authenticated:
            datas = attachment_id.datas.decode("utf-8")
            data = {
                "phone": mobile,
                "body": "data:" + attachment_id.mimetype + ";base64," + datas,
                "filename": attachment_id.name,
            }
            url = self.graph_api_url + self.graph_api_instance_id + "/sendFile?access_token=" + self.graph_api_token
            headers = {'Content-type': 'application/json'}
            try:
                answer = requests.post(url, data=json.dumps(data), headers=headers)

            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                self.meta_error_message_display(answer)
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    # phone change to mobile
    def graph_api_send_image(self, attachment_id):
        if self.graph_api_authenticated:
            # datas = attachment_id.datas.decode("utf-8")
            file_name = attachment_id.name
            file_path = tempfile.gettempdir() + '/' + file_name
            temp_path = os.path.join(tempfile.gettempdir(), file_path)
            shutil.copy2(attachment_id._full_path(attachment_id.store_fname), temp_path)

            url = self.graph_api_url + self.graph_api_instance_id + "/media"

            payload = {'messaging_product': 'whatsapp'}
            files = [
                ('file', (attachment_id.name, open(file_path, 'rb'), attachment_id.mimetype))
            ]
            headers = {
                'Authorization': 'Bearer ' + self.graph_api_token
            }
            try:
                answer = requests.post(url, headers=headers, data=payload, files=files)

            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                self.meta_error_message_display(answer)
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    def direct_get_image_by_id(self, media_id, recipient, sent_type, attachment_id):
        if self.graph_api_authenticated:
            url = self.graph_api_url + self.graph_api_instance_id + "/messages"
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient.phone or recipient.mobile,
                "type": sent_type,
                sent_type: {
                    "id": media_id
                }
            }
            if sent_type == 'document':
                data[sent_type]['filename'] = attachment_id.name

            payload = json.dumps(data)
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.graph_api_token
            }
            try:
                answer = requests.post(url, headers=headers, data=payload)

            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                self.meta_error_message_display(answer)
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    def get_image_by_id(self, media_id, recipient, sent_type, attachment_id):
        if self.graph_api_authenticated:
            url = self.graph_api_url + self.graph_api_instance_id + "/messages"
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient.mobile,
                "type": sent_type,
                sent_type: {
                    "id": media_id
                }
            }
            if sent_type == 'document':
                data[sent_type]['filename'] = attachment_id.name

            payload = json.dumps(data)
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.graph_api_token
            }
            try:
                answer = requests.post(url, headers=headers, data=payload)

            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                self.meta_error_message_display(answer)
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    # phone change to mobile
    def graph_api_check_phone(self, mobile):
        if self.graph_api_authenticated:
            url = self.graph_api_url + self.graph_api_instance_id + "/checkPhone?access_token=" + self.graph_api_token + "&phone=+" + mobile

            payload = {}
            headers = {}

            try:
                answer = requests.request("GET", url, headers=headers, data=payload)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                self.meta_error_message_display(answer)
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    def send_image(self, attachment_id):
        t = type(self)
        fn = getattr(t, f'{self.provider}_send_image', None)
        res = fn(self, attachment_id)
        return res

    def graph_api_add_template(self, name, language, category, components):
        if self.graph_api_authenticated:
            data = {
                "name": name,
                "language": language,
                "category": category,
                "components": components,
            }
            if category == 'AUTHENTICATION':
                data.pop("language")
                data.update({"languages": [language]})
                url = self.graph_api_url + self.graph_api_business_id + "/upsert_message_templates?access_token=" + self.graph_api_token
            else:
                url = self.graph_api_url + self.graph_api_business_id + "/message_templates?access_token=" + self.graph_api_token

            headers = {'Content-type': 'application/json'}

            try:
                answer = requests.post(url, data=json.dumps(data), headers=headers)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                self.meta_error_message_display(answer)
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    def graph_api_resubmit_template(self, category, template_id, components):
        if self.graph_api_authenticated:
            data = {
                "category": category,
                "components": components,
            }
            if template_id:
                url = self.graph_api_url + template_id
            else:
                raise UserError(("Template UID is missing in the template"))

            headers = {'Content-type': 'application/json',
                       'Authorization': 'Bearer ' + self.graph_api_token}

            try:
                answer = requests.post(url, data=json.dumps(data), headers=headers)

            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                self.meta_error_message_display(answer)
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    def graph_api_direct_send_template(self, template, language, namespace, partner, params):
        if self.graph_api_authenticated:
            url = self.graph_api_url + self.graph_api_instance_id + "/messages"
            payload = json.dumps({
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": partner.phone or partner.mobile,
                "type": "template",
                "template": {
                    "name": template,
                    "language": {
                        "code": language
                    },
                    "components": params
                }
            })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.graph_api_token
            }
            try:
                answer = requests.post(url, headers=headers, data=payload)

            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                self.meta_error_message_display(answer)
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    def graph_api_send_template(self, template, language, namespace, partner, params):
        if self.graph_api_authenticated:
            url = self.graph_api_url + self.graph_api_instance_id + "/messages"
            payload = json.dumps({
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": partner.mobile,
                "type": "template",
                "template": {
                    "name": template,
                    "language": {
                        "code": language
                    },
                    "components": params
                }
            })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.graph_api_token
            }
            try:
                answer = requests.post(url, headers=headers, data=payload)

            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                self.meta_error_message_display(answer)

            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    def graph_api_remove_template(self, name):
        if self.graph_api_authenticated:
            data = {
                "name": name,
                # "language": language,
                # "category": category,
                # "components": components,
            }
            url = self.graph_api_url + self.graph_api_business_id + "/message_templates?name=" + name + "&access_token=" + self.graph_api_token
            headers = {'Content-type': 'application/json'}

            try:
                answer = requests.delete(url, data=json.dumps(data), headers=headers)
                # answer = requests.post(url, headers=headers, data=data)

            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            if answer.status_code != 200:
                self.meta_error_message_display(answer)
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))

    def graph_api_wamsg_mark_as_read(self, message_id):
        """
        When Message Seen/Read in odoo, Double Blue Tick (Read Receipts) in WhatsApp
        """
        if self.graph_api_authenticated:
            url = self.graph_api_url + self.graph_api_instance_id + "/messages"
            data = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id,
            }
            payload = json.dumps(data)
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.graph_api_token
            }
            try:
                answer = requests.post(url, headers=headers, data=payload)
            except requests.exceptions.ConnectionError:
                raise UserError(
                    ("please check your internet connection."))
            # if answer.status_code != 200:
            #     if json.loads(answer.text) and 'error' in json.loads(answer.text) and 'message' in json.loads(
            #             answer.text).get('error'):
            #         dict = json.loads(answer.text).get('error').get('message')
            #         raise UserError(_(dict))
            return answer
        else:
            raise UserError(
                ("please authenticated your whatsapp."))
