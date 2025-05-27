from odoo import models, fields, api

class CustomerSatisfactionWizard(models.TransientModel):
    _name = 'customer.satisfaction.wizard'
    _description = 'Customer Satisfaction Wizard'

    customer_satisfied = fields.Selection(
        [('satisfied', 'Satisfied'), ('not_satisfied', 'Not Satisfied')],
        string="Customer Satisfied?",
        required=True
    )

    def action_submit_satisfaction(self):
        # Set the selected value on the task and stop the timer
        task = self.env['project.task'].browse(self.env.context.get('active_id'))
        task.customer_satisfied = self.customer_satisfied
        task.action_stop_timer()  # Call the existing stop timer logic