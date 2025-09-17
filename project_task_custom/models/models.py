# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class project_task_custom(models.Model):
#     _name = 'project_task_custom.project_task_custom'
#     _description = 'project_task_custom.project_task_custom'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()

#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import models, exceptions, _



class ProjectTask(models.Model):
    _inherit = 'project.task'


    # @api.model
    # def create(self, vals):
    #     """
    #     Override the create method if you want to set initial data or validations.
    #     """
    #     task = super(ProjectTask, self).create(vals)
    #     task._check_stage_and_add_agent()
    #     return task

    # def write(self, vals):
    #     """
    #     Override the write method to check conditions when the stage changes.
    #     """
    #     result = super(ProjectTask, self).write(vals)
    #     if 'stage_id' in vals or 'tag_ids' in vals:
    #         self._check_stage_and_add_agent()
    #     return result

    # def _check_stage_and_add_agent(self):
    #     # Directly use the stage ID
    #     verified_stage_id = 33  # Replace with your actual stage ID
    #     installation_tag_name = "installation"  # Replace with the correct tag name or reference

    #     for task in self:
    #         print(f"Task: {task.name}")
    #         print(f"Stage ID: {task.stage_id.id}")
    #         print(f"Tags: {task.tag_ids.mapped('name')}")
    #         print(f"Customer: {task.partner_id.name if task.partner_id else 'No Customer'}")
    #         print(f"Assigned User: {task.user_ids.mapped('name') if task.user_ids else 'No Assigned User'}")

    #         if (
    #             task.stage_id.id == verified_stage_id
    #             and installation_tag_name in task.tag_ids.mapped('name')
    #         ):
    #             customer_partner = task.partner_id
    #             assigned_user = task.user_ids and task.user_ids[0]

    #             if customer_partner and assigned_user:
    #                 print(f"Adding {assigned_user.partner_id.name} to {customer_partner.name}'s agents")
    #                 if assigned_user.partner_id not in customer_partner.agents_id:
    #                     customer_partner.agents_id = [(4, assigned_user.partner_id.id)]
    #                 else:
    #                     print(f"{assigned_user.partner_id.name} is already an agent.")
    #             else:
    #                 print("No customer or assigned user found.")
    
    # # Additional fields and methods already exist in your model

    is_field_service_project = fields.Boolean(
        string="Is Field Service Project",
        compute="_compute_is_field_service_project",
        store=True
    )

    def _restrict_task_visibility(self):
        """
        Restrict task visibility for users in the Field User group.
        """
        field_user_group = self.env['res.groups'].browse(162)  # Replace 155 with the correct group ID
        if field_user_group in self.env.user.groups_id:
            for task in self:
                # Check if the user is neither the main responsible nor a collaborator on the task
                if self.env.user.id not in task.user_ids.ids:
                    raise exceptions.AccessError(
                        _("You are not allowed to access tasks not assigned to you.")
                    )

    def read(self, fields=None, load='_classic_read'):
        """
        Override the read method to enforce task visibility restrictions.
        """
        self._restrict_task_visibility()
        return super(ProjectTask, self).read(fields, load)

    def search(self, args, offset=0, limit=None, order=None):
        """
        Override the search method to filter tasks for Field User group members.
        """
        field_user_group = self.env['res.groups'].browse(162)  # Replace 155 with the correct group ID
        if field_user_group in self.env.user.groups_id:
            # Filter tasks for the current user assigned to them (either as main or collaborator)
            args = ['|', ('user_ids', 'in', [self.env.user.id])] + args
        
        # Remove 'count' from the search call
        return super(ProjectTask, self).search(domain=args, offset=offset, limit=limit, order=order)

    @api.depends('project_id')
    @api.onchange('project_id')
    def _compute_is_field_service_project(self):
        for task in self:
            task.is_field_service_project = task.project_id.is_field_service if task.project_id else False
    
    def force_update_is_field_service_project(self):
        """
        Force update `is_field_service_project` for all tasks.
        This ensures the field is recalculated for existing tasks.
        """
        tasks = self.search([])
        for task in tasks:
            task.is_field_service_project = task.project_id.is_field_service

    
    # Computed phone number field
    assignee_phone = fields.Char(
        string="Assignee Phone",
        compute="_compute_assignee_phone",
        store=True,
        help="Phone number of the assigned user"
    )

    @api.depends('user_ids', 'project_id.is_field_service')
    def _compute_assignee_phone(self):
        """
        Compute the phone number of the assignee if the project is a Field Service project.
        """
        for task in self:
            if task.project_id.is_field_service and task.user_ids and task.user_ids:
                # Assuming user_ids contains one primary assignee
                primary_assignee = task.user_ids[0]
                task.assignee_phone = primary_assignee.partner_id.phone
            else:
                task.assignee_phone = False

         # Constraint to allow only one assignee for field service project tasks
    @api.constrains('user_ids')
    def _check_single_assignee_for_field_service(self):
        for task in self:
            if task.is_field_service_project and len(task.user_ids) > 1:
                raise ValidationError("A field service project task can only have one assignee.")

    
    supporting_technicians_ids = fields.Many2many(
        'res.users',
        string="Supporting Technicians",
        help="Select additional technicians supporting the senior technician.",
        domain="[('id', '!=', user_ids)]",
    )

    x_start_date = fields.Date(
        string="Start Date",
        help="The start date for the task."
    )

    @api.onchange('project_id')
    def _onchange_supporting_technicians(self):
        """ Clear supporting technicians if the project is not Field Service. """
        if not self.is_field_service_project:
            self.supporting_technicians_ids = [(5, 0, 0)]  # Clear the Many2many field

    advance_1 = fields.Float(
        string="Advance Amount",
        default=0.0,
        help="Advance amount paid by the customer."
    )

    cancellation_reason = fields.Selection(
        [
            ('technicians_not_available_currently', 'TECHNICAINS NOT AVAILABLE CURRENTLY'),
            ('call_not_lifted_by_customer', 'CALL NOT LIFTED BY CUSTOMER'),
            ('customer_not_interested_now', 'CUSTOMER NOT INTERESTED NOW'),
            ('stock_not_available', 'STOCK NOT AVAILABLE')
        ],
        string="Cancellation Reason",
        help="Reason for task cancellation."
    )

    reschedule_reason = fields.Selection(
        [
            ('technicians_not_available_currently', 'TECHNICAINS NOT AVAILABLE CURRENTLY'),
            ('call_not_lifted_by_customer', 'CALL NOT LIFTED BY CUSTOMER'),
            ('as_per_customer_request', 'AS PER CUSTOMER REQUEST'),
            ('low_stock', 'LOW STOCK')
        ],
        string="Reschedule Reason",
        help="Reason for task rescheduling."
    )

    slot_sdate = fields.Date(
        string="Slot SDate",
        store=True,
        help="The start date of the selected slot"
    )
    slot_edate = fields.Datetime(
        string="Slot EDate",
        store=True,
        help="The end date of the selected slot"
    )

    slot_ids = fields.Many2many(
        'field.service.slot',
        string="Slots",
        help="Select one or more slots for this task."
    )
    estimated_slots = fields.Integer(
        string="Estimated Slots",
        help="Number of slots required for this task.",
        compute="_compute_estimated_slots",
        store=True
    )
    start_time = fields.Float(
        string="Start Time",
        compute="_compute_slot_times",
        store=True,
        help="The start time based on the selected slots."
    )
    end_time = fields.Float(
        string="End Time",
        compute="_compute_slot_times",
        store=True,
        help="The end time based on the selected slots."
    )
    slot_time_range = fields.Char(
        string="Slot Time Range",
        compute="_compute_slot_times",
        store=True,
        help="The computed time range for the selected slots."
    )

    @api.depends('allocated_hours')
    @api.onchange('allocated_hours')
    def _compute_estimated_slots(self):
        for task in self:
            if task.project_id.is_field_service:
                task.estimated_slots = round((task.allocated_hours or 0) / 2)  # Assuming each slot is 2 hours
            else:
                task.estimated_slots = 0
            # if task.slot_ids:
            #     sorted_slots = task.slot_ids.sorted(key=lambda s: s.start_time)
            #     task.start_time = sorted_slots[0].start_time
            #     task.end_time = sorted_slots[-1].end_time
            #     task.slot_time_range = f"{sorted_slots[0].start_time:02.0f}:00 - {sorted_slots[-1].end_time:02.0f}:00"
            # else:
            #     task.start_time = 0.0
            #     task.end_time = 0.0
            #     task.slot_time_range = "No slots selected"

    @api.depends('slot_ids')
    @api.onchange('slot_ids')
    def _compute_slot_times(self):
        for task in self:
            if task.project_id.is_field_service and task.slot_ids:
                sorted_slots = task.slot_ids.sorted(key=lambda s: s.start_time)
                task.start_time = sorted_slots[0].start_time
                task.end_time = sorted_slots[-1].end_time
                task.slot_time_range = f"{sorted_slots[0].start_time:02.0f}:00 - {sorted_slots[-1].end_time:02.0f}:00"
            else:
                task.start_time = 0.0
                task.end_time = 0.0
                task.slot_time_range = "No slots selected"

    
    @api.depends('slot_ids')
    @api.onchange('slot_ids')

    def _compute_allocated_hours(self):
        """
        Compute Allocated Hours based on the number of selected slots.
        Each slot is assumed to be 2 hours.
        """
        for task in self:
            # Calculate allocated hours as the number of slots multiplied by 2
            task.allocated_hours = len(task.slot_ids) * 2

    # @api.onchange('slot_ids')
    # def _onchange_slots(self):
    #     """Automatically update allocated hours based on slot selections."""
    #     self._compute_allocated_hours()
    #     self._compute_slot_times()


class ProjectProject(models.Model):
    _inherit = 'project.project'

    is_field_service = fields.Boolean(
        string="Field Service",
        help="Mark this project as a Field Service project."
    )


