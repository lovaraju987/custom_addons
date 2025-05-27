from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrLoanPaymentRegister(models.TransientModel):
    _name = "hr.loan.payment.register"
    _description = "Register Loan Payment"

    amount = fields.Float(string="Payment Amount", required=True)
    journal_id = fields.Many2one('account.journal', string="Payment Journal", required=True,
                                 help="Select the journal for payment")
    payment_date = fields.Date(string="Payment Date", default=fields.Date.today, required=True)

    def action_create_payment(self):
        self.ensure_one()
        active_id = self.env.context.get('active_id')
        loan = self.env['hr.loan'].browse(active_id)
        if loan.state != 'approve':
            raise UserError(_("Payment can be registered only for approved loans."))

        if not loan.employee_id or not loan.employee_id.user_id.partner_id:
            raise UserError(_("The loan's employee does not have an associated partner."))
        
        partner = loan.employee_id.user_id.partner_id

        payment_vals = {
            'payment_type': 'outbound',  # assuming outbound payment for loan repayment
            'partner_type': 'supplier',   # adjust if needed
            'partner_id': partner.id,
            'amount': self.amount,
            'journal_id': self.journal_id.id,
            'date': self.payment_date,      # correct field key for payment date
            'payment_reference': _("Loan Payment for %s") % (loan.name),
        }
        payment = self.env['account.payment'].create(payment_vals)
        payment.action_post()  # post the payment

        new_total = loan.amount_released + self.amount
        new_state = 'full_paid' if new_total >= loan.loan_amount else 'partial_paid'
        loan.write({
            'amount_released': new_total,
            'state': new_state,
        })

        loan_line = loan.loan_lines.filtered(lambda l: not l.paid)[:1]
        if loan_line:
            loan_line.write({'paid': True})
            
        return {'type': 'ir.actions.act_window_close'}