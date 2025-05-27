
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import models, exceptions, _
from datetime import datetime

class ProjectTask(models.Model):
    _inherit = 'project.task'

    on_hold_reason = fields.Text(string="On Hold Reason", readonly=True)
    customer_satisfied = fields.Selection(
        [('satisfied', 'Satisfied'), ('not_satisfied', 'Not Satisfied')],
        string="Customer Satisfied?",
        default=False
    )

    timer_start_time = fields.Datetime(
        string="Timer Start Time",
        readonly=True,
        help="Tracks when the timer was started."
    )
    timer_total_time = fields.Float(
        string="Total Time (Hours)",
        compute="_compute_total_time",
        store=True,
        help="Total time logged for this task."
    )
    timer_is_running = fields.Boolean(
        string="Is Timer Running",
        default=False,
        readonly=True,
        help="Indicates if the timer is currently running."
    )

    # def write(self, vals):
    #     if self.is_field_service_project and 'stage_id' in vals:
    #         # Check if the current user belongs to the group with ID 155
    #         field_user_group = self.env['res.groups'].browse(155)  # Record ID of your custom group
    #         if field_user_group in self.env.user.groups_id:
    #             raise exceptions.AccessError(_("You do not have permission to update the task stage."))
    #     return super(ProjectTask, self).write(vals)

    def write(self, vals):
        # Check if the stage_id is in the vals dictionary
        if 'stage_id' in vals:
            # Check if the current user belongs to the Field User group
            field_user_group = self.env['res.groups'].browse(162)  # Replace with your custom group ID
            if field_user_group in self.env.user.groups_id:
                # Block direct stage changes from the UI but allow through button clicks
                # We check for a custom flag in the context indicating button-triggered updates
                if not self.env.context.get('from_button', False):
                    raise exceptions.AccessError(_("You do not have permission to update the task stage."))
        
        return super(ProjectTask, self).write(vals)

    @api.depends('timesheet_ids.unit_amount')
    def _compute_total_time(self):
        """Compute total time from timesheets."""
        for task in self:
            task.timer_total_time = sum(task.timesheet_ids.mapped('unit_amount'))

    def _update_task_stage(self, stage_id):
        """Update task stage dynamically based on task's stage name."""
        if stage_id:
            self.write({'stage_id': stage_id})
        else:
            raise ValidationError(f"Stage '{stage_id}' not found!")
        
    def action_start_timer(self):
        """Start the timer and move the task to 'In Progress' stage."""
        if self.timer_is_running:
            raise ValidationError("The timer is already running! Please onhold or stop it first. ")
        self.write({
            'timer_start_time': datetime.now(),
            'timer_is_running': True,
        })
        # Update task stage dynamically to 'In Progress'
        if self.is_field_service_project:
            self._update_task_stage(30)

    def action_pause_timer(self):
        """Pause the timer, log time to timesheet, and move to 'On Hold' stage."""
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'task.on.hold.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_task_id': self.id},
        }
    
    def action_pause_timer_2(self):
        """Pause the timer, log time to timesheet, and move to 'On Hold' stage."""
        if not self.timer_is_running:
            raise ValidationError("The timer is not running!")

        user_id = self.user_ids and self.user_ids[0] or None
        if not user_id:
            raise ValidationError("No user assigned to this task!")

        employee_id = user_id.employee_ids and user_id.employee_ids[0] or None
        if not employee_id or not employee_id.active:
            raise ValidationError("No active employee associated with this task!")

        time_spent = (datetime.now() - self.timer_start_time).total_seconds() / 3600
        on_hold_reason = self.on_hold_reason or "No reason provided"  # Fetch the reason

        self.env['account.analytic.line'].create({
            'name': f"Task {self.name}: Paused. Reason: {on_hold_reason}",
            'task_id': self.id,
            'unit_amount': time_spent,
            'date': datetime.now().date(),
            'project_id': self.project_id.id,
            'employee_id': employee_id.id,
        })
        self.write({
            'timer_start_time': False,
            'timer_is_running': False,
        })
        # Update task stage dynamically to 'On Hold'
        if self.is_field_service_project:
            self._update_task_stage(31)
            

    def action_stop_timer(self):
        """Stop the timer, log time to timesheet, and move to 'Completed' stage."""
        if not self.timer_is_running:
            raise ValidationError("The timer is not running!")
        
        # Check if all mandatory checklist items are completed
        mandatory_items = self.checklist_line_ids.filtered(lambda line: line.is_mandatory)
        incomplete_mandatory_items = mandatory_items.filtered(lambda line: not line.is_done)

        if incomplete_mandatory_items:
            raise ValidationError("Please complete all the mandatory checklist items before stopping the task.")
        

        if not self.customer_satisfied:
            # Open the wizard if the field is not filled
            return {
                'type': 'ir.actions.act_window',
                'name': 'Customer Satisfaction',
                'res_model': 'customer.satisfaction.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'active_id': self.id},
            }

        # # Check progress bar value
        # if self.progress < 60:
        #     raise ValidationError("Please complete the checklist at least 60 percent before stopping the task!")

        user_id = self.user_ids and self.user_ids[0] or None
        if not user_id:
            raise ValidationError("No user assigned to this task!")

        employee_id = user_id.employee_ids and user_id.employee_ids[0] or None
        if not employee_id or not employee_id.active:
            raise ValidationError("No active employee associated with this task!")

        time_spent = (datetime.now() - self.timer_start_time).total_seconds() / 3600
        self.env['account.analytic.line'].create({
            'name': f"Task {self.name}: Stopped",
            'task_id': self.id,
            'unit_amount': time_spent,
            'date': datetime.now().date(),
            'project_id': self.project_id.id,
            'employee_id': employee_id.id,
        })
        self.write({
            'timer_start_time': False,
            'timer_is_running': False,
        })
        # Update task stage dynamically to 'Completed'
        if self.is_field_service_project:
            self._update_task_stage(32)

    def action_resume_timer(self):
        """Resume the timer from the paused state."""
        if self.timer_is_running:
            raise ValidationError("The timer is already running!")

        # Reset the start time as current time
        self.write({
            'timer_start_time': datetime.now(),
            'timer_is_running': True,
        })
        # Update task stage dynamically to 'In Progress' (or any other stage if needed)
        if self.is_field_service_project:
            self._update_task_stage(30)