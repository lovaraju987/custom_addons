# -*- coding: utf-8 -*-
# from odoo import http


# class TechnicianShiftRoster(http.Controller):
#     @http.route('/technician_shift_roster/technician_shift_roster', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/technician_shift_roster/technician_shift_roster/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('technician_shift_roster.listing', {
#             'root': '/technician_shift_roster/technician_shift_roster',
#             'objects': http.request.env['technician_shift_roster.technician_shift_roster'].search([]),
#         })

#     @http.route('/technician_shift_roster/technician_shift_roster/objects/<model("technician_shift_roster.technician_shift_roster"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('technician_shift_roster.object', {
#             'object': obj
#         })

