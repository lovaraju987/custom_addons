from odoo import models, fields, api

class TaskOnHoldWizard(models.TransientModel):
    _name = 'task.on.hold.wizard'
    _description = 'Reason for On Hold'

    reason = fields.Text(string="Reason", required=True)

    def action_confirm_on_hold(self):
        """Apply the reason and put the task on hold."""
        active_id = self.env.context.get('active_id')
        if active_id:
            task = self.env['project.task'].browse(active_id)
            task.write({
                'on_hold_reason': self.reason,
            })
            task.action_pause_timer_2()