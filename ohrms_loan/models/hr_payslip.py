from odoo import models


class HrPayslip(models.Model):
    """ Extends the 'hr.payslip' model to include
    additional functionality related to employee loans."""
    _inherit = 'hr.payslip'

    def get_inputs(self, contract_ids, date_from, date_to):
        """Compute additional inputs for the employee payslip,
        considering active loans.
        :param contract_ids: Contract ID of the current employee.
        :param date_from: Start date of the payslip.
        :param date_to: End date of the payslip.
        :return: List of dictionaries representing additional inputs for
        the payslip."""

        res = super(HrPayslip, self).get_inputs(contract_ids, date_from, date_to)
        if contract_ids:
            employee_id = self.env['hr.contract'].browse(contract_ids[0].id).employee_id
            loan_lines = self.env['hr.loan.line'].search([
                ('employee_id', '=', employee_id.id),
                ('date', '>=', date_from),
                ('date', '<=', date_to),
                ('released', '=', True),  # Only released lines
                ('paid', '=', False),     # Not yet deducted
                ('loan_id.state', 'in', ['approve', 'partial_paid', 'full_paid'])
            ])
            for loan_line in loan_lines:
                res.append({
                    'code': 'LO',
                    'amount': loan_line.amount,
                    'loan_line_id': loan_line.id,
                    'contract_id': contract_ids[0].id,
                    'name': "Loan",
                })
        return res

    

    def action_payslip_done(self):
        """ Compute the loan amount and remaining amount while confirming
            the payslip"""
        for line in self.input_line_ids:
            if line.loan_line_id:
                line.loan_line_id.paid = True
                line.loan_line_id.loan_id._compute_total_amount()
        return super(HrPayslip, self).action_payslip_done()
