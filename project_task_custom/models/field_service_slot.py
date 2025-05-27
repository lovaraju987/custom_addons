from odoo import models, fields

class FieldServiceSlot(models.Model):
    _name = 'field.service.slot'
    _description = 'Field Service Slot'

    name = fields.Char(string="Slot Name", required=True)
    start_time = fields.Float(string="Start Time (24h)", required=True)
    end_time = fields.Float(string="End Time (24h)", required=True)
    description = fields.Text(string="Description")