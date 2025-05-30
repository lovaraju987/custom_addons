from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrPayslipSalaryPaymentWizard(models.TransientModel):
    _name = 'hr.payslip.salary.payment.wizard'
    _description = 'Salary Payment Wizard'

    payslip_id = fields.Many2one('hr.payslip', required=True, readonly=True)
    amount = fields.Float('Amount', required=True)
    payment_date = fields.Date('Payment Date', required=True, default=fields.Date.today)
    journal_id = fields.Many2one('account.journal', required=True, domain=[('type', 'in', ['bank', 'cash'])])

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        payslip_id = self.env.context.get('default_payslip_id')
        if payslip_id:
            payslip = self.env['hr.payslip'].browse(payslip_id)
            payslip._compute_salary_paid_amount()  # Force recompute
            net = payslip._get_net_amount()
            paid = payslip.salary_paid_amount
            res['amount'] = max(0.0, net - paid)
        return res

    def action_confirm_payment(self):
        self.ensure_one()
        payslip = self.payslip_id

        # Recompute pending amount to avoid race conditions
        payslip._invalidate_cache()
        payslip = payslip.browse(payslip.id)
        net = payslip._get_net_amount()
        paid = payslip.salary_paid_amount
        pending = max(0.0, net - paid)

        if self.amount <= 0:
            raise UserError(_("Amount must be positive."))

        if self.amount > pending:
            raise UserError(_("You cannot pay more than the pending salary amount (%s).") % (pending))

        partner = payslip.employee_id.address_id
        if not partner:
            raise UserError(_("The employee does not have an associated partner."))

        payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': partner.id,
            'amount': self.amount,
            'date': self.payment_date,
            'journal_id': self.journal_id.id,
            'payment_reference': f'Salary Payment for Payslip {payslip.number or payslip.name}',
        })
        payment.action_post()

        paid += self.amount
        if paid >= net and net > 0:
            payslip.write({'state': 'salary_settled_full'})
        elif 0 < paid < net:
            payslip.write({'state': 'salary_settled_partial'})
        elif paid == 0:
            payslip.write({'state': 'done'})

        return {'type': 'ir.actions.act_window_close'}