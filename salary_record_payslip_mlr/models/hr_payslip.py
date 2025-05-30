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
            net = payslip._get_net_amount()
            paid = payslip.salary_paid_amount
            if paid >= net and net > 0:
                payslip.state = 'salary_settled_full'
            elif 0 < paid < net:
                payslip.state = 'salary_settled_partial'
            elif paid == 0:
                payslip.state = 'done'

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

    def get_inputs(self, contract_ids, date_from, date_to):
        res = super().get_inputs(contract_ids, date_from, date_to)
        if contract_ids:
            contract = self.env['hr.contract'].browse(contract_ids[0].id)
            employee = contract.employee_id

            # Find pending salary for this employee
            pending_salary = self.env['hr.pending.salary'].search([
                ('employee_id', '=', employee.id),
                ('state', '=', 'pending')
            ], limit=1)
            if pending_salary:
                res.append({
                    'code': 'PEND_SAL',
                    'amount': pending_salary.amount,
                    'contract_id': contract.id,
                    'name': "Pending Salary Recovery",
                })
        return res

    def action_payslip_done(self):
        res = super().action_payslip_done()
        for payslip in self:
            # Mark pending salary as paid if included in this payslip
            pending_salary = self.env['hr.pending.salary'].search([
                ('employee_id', '=', payslip.employee_id.id),
                ('state', '=', 'pending')
            ])
            for rec in pending_salary:
                rec.write({'state': 'paid', 'payslip_id': payslip.id})
        return res

    # Add this logic after payment registration

    def _create_pending_salary_if_needed(self):
        for payslip in self:
            net = payslip._get_net_amount()
            paid = payslip.salary_paid_amount
            if paid < net:
                # Check if already exists
                existing = self.env['hr.pending.salary'].search([
                    ('employee_id', '=', payslip.employee_id.id),
                    ('state', '=', 'pending')
                ])
                if not existing:
                    self.env['hr.pending.salary'].create({
                        'employee_id': payslip.employee_id.id,
                        'amount': net - paid,
                        'payslip_id': payslip.id,
                        'state': 'pending'
                    })