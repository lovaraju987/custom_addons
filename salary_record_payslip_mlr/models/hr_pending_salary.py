from odoo import models, fields

class HrPendingSalary(models.Model):
    _name = 'hr.pending.salary'
    _description = 'Pending Salary'

    employee_id = fields.Many2one('hr.employee', required=True, ondelete='cascade')
    amount = fields.Float('Pending Amount', required=True)
    payslip_id = fields.Many2one('hr.payslip', string='Payslip', help='Payslip where this pending salary was generated')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('paid', 'Paid')
    ], default='pending')