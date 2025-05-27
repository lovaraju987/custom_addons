# # -*- coding: utf-8 -*-
# #############################################################################
# from odoo import fields, models, _


# class HrEmployee(models.Model):
#     """Extends the 'hr.employee' model to include loan_count."""
#     _inherit = "hr.employee"

#     loan_count = fields.Integer(
#         string="Loan Count",
#         compute='_compute_loan_info',
#         help="Number of loans associated with the employee"
#     )

#     total_loan_amount = fields.Float(
#         string="Total Loan Amount",
#         compute='_compute_loan_info',
#         help="Sum of all approved loans"
#     )

#     def _compute_loan_info(self):
#         """Compute the number of loans and total amount for the employee."""
#         loan_obj = self.env['hr.loan']
#         for employee in self:
#             loans = loan_obj.search([('employee_id', '=', employee.id)])
#             employee.loan_count = len(loans)
#             employee.total_loan_amount = sum(loans.filtered(
#                 lambda l: l.state == 'approve').mapped('loan_amount'))

#     def action_loan_view(self):
#         """ Opens a view to list all documents related to the current
#          employee."""
#         self.ensure_one()
#         return {
#             'name': _('Loan'),
#             'domain': [('employee_id', '=', self.id)],
#             'res_model': 'hr.loan',
#             'type': 'ir.actions.act_window',
#             'view_id': False,
#             'view_mode': 'tree,form',
#             'help': _('''<p class="oe_view_nocontent_create">
#                            Click to Create for New Loan
#                         </p>'''),
#             'limit': 80,
#             'context': "{'default_employee_id': %s}" % self.id
#         }





# -*- coding: utf-8 -*-
from odoo import fields, models, _

class HrEmployee(models.Model):
    """Extends the 'hr.employee' model to include loan information."""
    _inherit = "hr.employee"

    pending_loan_ids = fields.One2many(
        'hr.loan',
        'employee_id',
        string='Pending Loans',
        domain=[('state', '=', 'approve'), ('balance_amount', '>', 0)],
        help="List of approved loans with remaining balances"
    )
    
    loan_count = fields.Integer(
        string="Loan Count",
        compute='_compute_loan_info',
        help="Number of loans associated with the employee"
    )

    total_loan_amount = fields.Float(
        string="Total Loan Amount",
        compute='_compute_loan_info',
        help="Sum of all approved loans"
    )

    def _compute_loan_info(self):
        """Compute both loan count and total pending balance"""
        for employee in self:
            loans = self.env['hr.loan'].search([
                ('employee_id', '=', employee.id),
                ('state', '=', 'approve'),
                ('balance_amount', '>', 0)
            ])
            employee.loan_count = len(loans)
            employee.total_loan_amount = sum(loans.mapped('balance_amount'))

    def action_loan_view(self):
        """Action to view all loans for this employee."""
        self.ensure_one()
        return {
            'name': _('Loans'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.loan',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id}
        }