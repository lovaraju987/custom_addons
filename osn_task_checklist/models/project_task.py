# models/project_task.py

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    checklist_id = fields.Many2one(
        'task.checklist',
        string="Checklist",
        help="Select the checklist for this task"
    )
    checklist_line_ids = fields.One2many(
        'task.checklist.line',
        'task_id',
        string="Checklist Items",
        help="Checklist items for this task"
    )

        # Computed field to calculate progress
    progress = fields.Float(string="Progress", compute="_compute_progress")

    @api.depends('checklist_line_ids.is_done')
    def _compute_progress(self):
        for task in self:
            total = len(task.checklist_line_ids)
            if total > 0:
                completed = sum(1 for line in task.checklist_line_ids if line.is_done)
                task.progress = (completed / total) * 100
            else:
                task.progress = 0.0

    @api.onchange('checklist_id')
    def _onchange_checklist(self):
        """Populate checklist_line_ids based on the selected checklist."""
        if self.checklist_id:
            self.checklist_line_ids = [(5, 0, 0)]  # Clear existing lines
            self.checklist_line_ids = [
                (0, 0, {
                    'name': item.name,
                    'description': item.description,
                    'is_photo_required': item.is_photo_required,
                    'is_piece_related': item.is_piece_related,
                    'is_mandatory': item.is_mandatory,
                })
                for item in self.checklist_id.checklist_items
            ]
        else:
            self.checklist_line_ids = [(5, 0, 0)]  # Clear if no checklist is selected

    
    def action_open_checklist_item(self):
        # Handle navigation based on `is_piece_related`
        checklist_line = self.env['task.checklist.line'].browse(self._context.get('active_id'))
        if checklist_line.is_piece_related:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Actual Pieces',
                'res_model': 'field.service.piece',
                'view_mode': 'form',
                'target': 'current',
                'context': {
                    'default_task_id': self.id
                },
            }
        return super(ProjectTask, self).action_open_checklist_item()


class TaskChecklistLine(models.Model):
    _name = 'task.checklist.line'
    _description = 'Task Checklist Line'

    task_id = fields.Many2one('project.task', string="Task", ondelete='cascade')
    name = fields.Char(string="Checklist Item", required=True)
    description = fields.Text(string="Item Description",)
    is_photo_required = fields.Boolean(string="Photo?", default=False)
    is_piece_related = fields.Boolean(string="Net Pieces?", default=False)  # New Field
    is_mandatory = fields.Boolean(string="Mandatory?", default=False)  # New Field
    is_done = fields.Boolean(string="Done?", default=False)
    description = fields.Text(string="Description")
    # photo = fields.Binary(string="Attach Photo")
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Attachments',
        help='Upload photos or videos as proof.'
    )



    @api.constrains('is_done', 'is_photo_required', 'attachment_ids')
    def _check_photo_before_done(self):
        for record in self:
            if record.is_photo_required and record.is_done and not record.attachment_ids:
                raise ValidationError(
                    "You cannot mark this item as Done without uploading a photo."
                )

    def action_open_checklist_item(self):
        """Open the checklist item view."""
        if self.is_piece_related:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Actual Pieces',
                'res_model': 'field.service.piece',
                'view_mode': 'form',
                'target': 'current',
                'context': {
                    'default_task_id': self.task_id.id
                },
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Checklist Item',
                'res_model': 'task.checklist.line',
                'view_mode': 'form',
                'view_id': self.env.ref('osn_task_checklist.view_task_checklist_line_form').id,
                'res_id': self.id,
                'target': 'new',
            }

    def action_submit_checklist_item(self):
        """Mark the checklist item as done."""
        self.is_done = True
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel_checklist_item(self):
        """Close the checklist item form without saving."""
        return {'type': 'ir.actions.act_window_close'}