from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrLoanPaymentRegister(models.TransientModel):
    _name = "hr.loan.payment.register"
    _description = "Register Loan Payment"

    amount = fields.Float(string="Payment Amount", required=True)
    journal_id = fields.Many2one('account.journal', string="Payment Journal", required=True,
                                 help="Select the journal for payment")
    payment_date = fields.Date(string="Payment Date", default=fields.Date.today, required=True)

    @api.model
    def default_get(self, fields_list):
        res = super(HrLoanPaymentRegister, self).default_get(fields_list)
        active_id = self.env.context.get('active_id')
        loan = self.env['hr.loan'].browse(active_id)
        if loan:
            res.update({'amount': loan.remaining_amount})
        return res

    def action_create_payment(self):
        self.ensure_one()
        active_id = self.env.context.get('active_id')
        loan = self.env['hr.loan'].browse(active_id)
        if loan.state not in ['approve', 'partial_paid']:
            raise UserError(_("Payment can be registered only for approved or partially paid loans."))

        if not loan.employee_id or not loan.employee_id.user_id.partner_id:
            raise UserError(_("The loan's employee does not have an associated partner."))

        if self.amount > loan.remaining_amount:
            raise UserError(_("Cannot register a payment more than the remaining amount (%s).") % loan.remaining_amount)

        # Get the partner: prefer user_id.partner_id, fallback to address_id
        partner = loan.employee_id.user_id.partner_id or loan.employee_id.address_id
        if not partner:
            raise UserError(_("The loan's employee does not have an associated partner."))

        payment_vals = {
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': partner.id,
            'amount': self.amount,
            'journal_id': self.journal_id.id,
            'date': self.payment_date,
            'payment_reference': _("Loan Payment for %s") % (loan.name),
        }
        payment = self.env['account.payment'].create(payment_vals)
        payment.action_post()

        new_total = loan.amount_released + self.amount
        new_state = 'full_paid' if new_total >= loan.loan_amount else 'partial_paid'
        loan.write({
            'amount_released': new_total,
            'state': new_state,
        })

        # Mark released lines
        unreleased_lines = loan.loan_lines.filtered(lambda l: not l.released)
        remaining = self.amount
        for line in unreleased_lines:
            if remaining <= 0:
                break
            line.write({'released': True})
            remaining -= line.amount

        return {'type': 'ir.actions.act_window_close'}