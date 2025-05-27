# -*- coding: utf-8 -*-
# from odoo import http


# class FieldServiceChecklist(http.Controller):
#     @http.route('/field_service_checklist/field_service_checklist', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/field_service_checklist/field_service_checklist/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('field_service_checklist.listing', {
#             'root': '/field_service_checklist/field_service_checklist',
#             'objects': http.request.env['field_service_checklist.field_service_checklist'].search([]),
#         })

#     @http.route('/field_service_checklist/field_service_checklist/objects/<model("field_service_checklist.field_service_checklist"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('field_service_checklist.object', {
#             'object': obj
#         })

