# -*- coding: utf-8 -*-
# from odoo import http


# class WhatsappMessageDirectionTracker(http.Controller):
#     @http.route('/whatsapp_message_direction_tracker/whatsapp_message_direction_tracker', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/whatsapp_message_direction_tracker/whatsapp_message_direction_tracker/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('whatsapp_message_direction_tracker.listing', {
#             'root': '/whatsapp_message_direction_tracker/whatsapp_message_direction_tracker',
#             'objects': http.request.env['whatsapp_message_direction_tracker.whatsapp_message_direction_tracker'].search([]),
#         })

#     @http.route('/whatsapp_message_direction_tracker/whatsapp_message_direction_tracker/objects/<model("whatsapp_message_direction_tracker.whatsapp_message_direction_tracker"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('whatsapp_message_direction_tracker.object', {
#             'object': obj
#         })

