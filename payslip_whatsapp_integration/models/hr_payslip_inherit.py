from odoo import models, fields

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    partner_id = fields.Many2one(
        'res.partner',
        string="Partner",
        related="employee_id.work_contact_id",  # Use work_contact_id instead
        store=True
    )