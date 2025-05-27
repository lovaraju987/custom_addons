# -*- coding: utf-8 -*-
# from odoo import http


# class FieldServiceInventoryAdjustment(http.Controller):
#     @http.route('/field_service_inventory_adjustment/field_service_inventory_adjustment', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/field_service_inventory_adjustment/field_service_inventory_adjustment/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('field_service_inventory_adjustment.listing', {
#             'root': '/field_service_inventory_adjustment/field_service_inventory_adjustment',
#             'objects': http.request.env['field_service_inventory_adjustment.field_service_inventory_adjustment'].search([]),
#         })

#     @http.route('/field_service_inventory_adjustment/field_service_inventory_adjustment/objects/<model("field_service_inventory_adjustment.field_service_inventory_adjustment"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('field_service_inventory_adjustment.object', {
#             'object': obj
#         })

