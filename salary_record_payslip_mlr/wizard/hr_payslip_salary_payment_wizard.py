from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrPayslipSalaryPaymentWizard(models.TransientModel):
    _name = 'hr.payslip.salary.payment.wizard'
    _description = 'Salary Payment Wizard'

    payslip_id = fields.Many2one('hr.payslip', required=True, readonly=True)
    amount = fields.Float('Amount', required=True)
    payment_date = fields.Date('Payment Date', required=True, default=fields.Date.today)
    journal_id = fields.Many2one('account.journal', required=True, domain=[('type', 'in', ['bank', 'cash'])])

    def action_confirm_payment(self):
        self.ensure_one()
        payslip = self.payslip_id

        if self.amount <= 0:
            raise UserError(_("Amount must be positive."))

        # Create an account.payment record (or your custom model)
        payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',  # <-- Use 'supplier' instead of 'employee'
            'partner_id': payslip.employee_id.address_id.id,
            'amount': self.amount,
            'date': self.payment_date,
            'journal_id': self.journal_id.id,
            'payment_reference': f'Salary Payment for Payslip {payslip.number or payslip.name}',
        })
        payment.action_post()
        # Update payslip state after payment
        net = payslip._get_net_amount()
        paid = payslip.salary_paid_amount + self.amount
        if paid >= net and net > 0:
            payslip.write({'state': 'salary_settled_full'})
        elif 0 < paid < net:
            payslip.write({'state': 'salary_settled_partial'})
        elif paid == 0:
            payslip.write({'state': 'done'})

        return {'type': 'ir.actions.act_window_close'}