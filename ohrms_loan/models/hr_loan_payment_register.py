from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrLoanPaymentRegister(models.TransientModel):
    _name = "hr.loan.payment.register"
    _description = "Register Loan Payment"

    amount = fields.Float(string="Payment Amount")
    journal_id = fields.Many2one('account.journal', string="Payment Journal", required=True,
                                 help="Select the payment journal")
    payment_date = fields.Date(string="Payment Date", default=fields.Date.today, required=True)

    def action_create_payment(self):
        active_id = self.env.context.get('active_id')
        loan = self.env['hr.loan'].browse(active_id)
        if loan.state != 'approve':
            raise UserError(_("Payment can be registered only for approved loans."))
        # (Implement your payment registration logic here.)
        # For example, mark the first unpaid installment as paid:
        loan_line = loan.loan_lines.filtered(lambda l: not l.paid)[:1]
        if not loan_line:
            raise UserError(_("All installments are already paid."))
        loan_line.write({'paid': True})
        # You could also log a message or update additional fields on the loan
        return {'type': 'ir.actions.act_window_close'}