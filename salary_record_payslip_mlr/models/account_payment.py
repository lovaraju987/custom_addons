from odoo import models, fields

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payslip_id = fields.Many2one('hr.payslip', string="Payslip")