# -*- coding: utf-8 -*-
# from odoo import http


# class PayslipWhatsappIntegration(http.Controller):
#     @http.route('/payslip_whatsapp_integration/payslip_whatsapp_integration', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payslip_whatsapp_integration/payslip_whatsapp_integration/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('payslip_whatsapp_integration.listing', {
#             'root': '/payslip_whatsapp_integration/payslip_whatsapp_integration',
#             'objects': http.request.env['payslip_whatsapp_integration.payslip_whatsapp_integration'].search([]),
#         })

#     @http.route('/payslip_whatsapp_integration/payslip_whatsapp_integration/objects/<model("payslip_whatsapp_integration.payslip_whatsapp_integration"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payslip_whatsapp_integration.object', {
#             'object': obj
#         })

