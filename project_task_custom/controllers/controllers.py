# -*- coding: utf-8 -*-
# from odoo import http


# class ProjectTaskCustom(http.Controller):
#     @http.route('/project_task_custom/project_task_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/project_task_custom/project_task_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('project_task_custom.listing', {
#             'root': '/project_task_custom/project_task_custom',
#             'objects': http.request.env['project_task_custom.project_task_custom'].search([]),
#         })

#     @http.route('/project_task_custom/project_task_custom/objects/<model("project_task_custom.project_task_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('project_task_custom.object', {
#             'object': obj
#         })

