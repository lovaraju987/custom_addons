# models/checklist.py

from odoo import models, fields, api

class TaskChecklist(models.Model):
    _name = 'task.checklist'
    _description = 'Task Checklist'

    name = fields.Char(string="Checklist Name", required=True)
    description = fields.Text(string="Description")
    checklist_items = fields.One2many(
        'task.checklist.item',
        'checklist_id',
        string="Checklist Items"
    )


class TaskChecklistItem(models.Model):
    _name = 'task.checklist.item'
    _description = 'Task Checklist Item'

    checklist_id = fields.Many2one('task.checklist', string="Checklist", required=True, ondelete='cascade')
    name = fields.Char(string="Item Name", required=True)
    description = fields.Text(string="Item Description",)
    is_photo_required = fields.Boolean(string="Photo?", default=False)
    is_piece_related = fields.Boolean(string="Net Pieces?", default=False)  # New Field
    is_mandatory = fields.Boolean(string="Mandatory?", default=False)  # New Field
    description = fields.Text(string="Description")
    # photo = fields.Binary(string="Attach Photo")
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Attachments',
        help='Upload photos or videos as proof.'
    )


