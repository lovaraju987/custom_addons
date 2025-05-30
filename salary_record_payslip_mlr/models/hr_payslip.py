from odoo import models, fields, api

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    salary_paid_amount = fields.Float(string="Salary Paid", compute='_compute_salary_paid_amount', store=True)
    salary_payment_ids = fields.One2many('account.payment', 'payslip_id', string="Salary Payments")

    state = fields.Selection(
        selection_add=[
            ('salary_settled_partial', 'Partial Salary Settled'),
            ('salary_settled_full', 'Full Salary Settled'),
        ]
    )

    def _compute_salary_paid_amount(self):
        for payslip in self:
            payslip.salary_paid_amount = sum(payslip.salary_payment_ids.mapped('amount'))

    def _get_net_amount(self):
        self.ensure_one()
        net_line = self.line_ids.filtered(lambda l: l.code == 'NET')
        return net_line.amount if net_line else 0.0

    def _compute_salary_paid_state(self):
        for payslip in self:
            total = payslip.salary_paid_amount
            net = payslip._get_net_amount()
            if total >= net:
                payslip.state = 'salary_settled_full'
            elif total > 0:
                payslip.state = 'salary_settled_partial'

    def action_record_salary_payment(self):
        net_amount = self._get_net_amount()
        paid_amount = self.salary_paid_amount if hasattr(self, 'salary_paid_amount') else 0.0
        return {
            'type': 'ir.actions.act_window',
            'name': 'Record Salary Payment',
            'res_model': 'hr.payslip.salary.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_payslip_id': self.id,
                'default_amount': net_amount - paid_amount,
            },
        }