# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class project_task_timer_custom(models.Model):
#     _name = 'project_task_timer_custom.project_task_timer_custom'
#     _description = 'project_task_timer_custom.project_task_timer_custom'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

