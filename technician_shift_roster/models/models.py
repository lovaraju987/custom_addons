# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class technician_shift_roster(models.Model):
#     _name = 'technician_shift_roster.technician_shift_roster'
#     _description = 'technician_shift_roster.technician_shift_roster'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100


# in models/models.py or a new file
from odoo import models, fields

class HRWorkLocation(models.Model):
    _inherit = 'hr.work.location'

    default_technician_ids = fields.Many2many('hr.employee', string='Default Technicians')
    default_manager_id = fields.Many2one('hr.employee', string='Default Manager')


