# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class HrLoan(models.Model):
    _name = "hr.loan"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Loan Request"
    
    # New fields for payment tracking:
    loan_amount = fields.Float(string="Loan Amount", required=True)
    amount_released = fields.Float(string="Amount Released", default=0.0)
    remaining_amount = fields.Float(string="Remaining Amount", compute="_compute_remaining_amount", store=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Waiting Approval'),
        ('approve', 'Approved'),
        ('partial_paid', 'Partial Payment Released'),
        ('full_paid', 'Full Payment Released'),
        ('refuse', 'Refused')
    ], default='draft', tracking=True)
    
    name = fields.Char(string="Loan Name", default="New", readonly=True,
                       help="Name of the loan")
    date = fields.Date(string="Date", default=fields.Date.today(),
                       readonly=True, help="Date of the loan request")
    employee_id = fields.Many2one('hr.employee', string="Employee",
                                  required=True, help="Employee Name",
                                  default=lambda self: self.env.user.employee_id)
    department_id = fields.Many2one('hr.department',
                                    related="employee_id.department_id",
                                    readonly=True,
                                    string="Department",
                                    help="The department to which the "
                                         "employee belongs.")
    installment = fields.Integer(string="No Of Installments", default=1,
                                 help="Number of installments")
    payment_date = fields.Date(string="Payment Start Date", required=True,
                               default=fields.Date.today(),
                               help="Date of the payment")
    loan_lines = fields.One2many('hr.loan.line', 'loan_id',
                                 string="Loan Line",
                                 help="Details of installment lines "
                                      "associated with the loan.",
                                 index=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 help="Company",
                                 default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, help="Currency",
                                  default=lambda self: self.env.user.
                                  company_id.currency_id)
    job_position = fields.Many2one('hr.job',
                                   related="employee_id.job_id",
                                   readonly=True, string="Job Position",
                                   help="Job position of the employee")
    total_amount = fields.Float(string="Total Amount", store=True,
                                readonly=True, compute='_compute_total_amount',
                                help="The total amount of the loan")
    balance_amount = fields.Float(string="Balance Amount", store=True,
                                  compute='_compute_total_amount',
                                  help="""The remaining balance amount of the 
                                  loan after deducting 
                                  the total paid amount.""")
    total_paid_amount = fields.Float(string="Total Paid Amount", store=True,
                                     compute='_compute_total_amount',
                                     help="The total amount that has been "
                                          "paid towards the loan.")

    @api.depends('loan_amount', 'amount_released')
    def _compute_remaining_amount(self):
        for rec in self:
            rec.remaining_amount = rec.loan_amount - rec.amount_released

    def _compute_total_amount(self):
        """ Compute total loan amount,balance amount and total paid amount"""
        total_paid = 0.0
        for loan in self:
            for line in loan.loan_lines:
                if line.paid:
                    total_paid += line.amount
            balance_amount = loan.loan_amount - total_paid
            loan.total_amount = loan.loan_amount
            loan.balance_amount = balance_amount
            loan.total_paid_amount = total_paid

    # @api.model
    # def create(self, values):
    #     """ Check whether any pending loan is for the employee and calculate
    #         the sequence
    #         :param values : Dictionary which contain fields and values"""
    #     loan_count = self.env['hr.loan'].search_count(
    #         [('employee_id', '=', values['employee_id']),
    #          ('state', '=', 'approve'),
    #          ('balance_amount', '!=', 0)
    #          ])
    #     if loan_count:
    #         raise ValidationError(
    #             _("The Employee has already a pending installment"))
    #     else:
    #         values['name'] = self.env['ir.sequence'].get('hr.loan.seq') or ' '
    #         return super(HrLoan, self).create(values)

    @api.model
    def create(self, values):
        """Check total pending balance against maximum allowed"""
        employee_id = values.get('employee_id')
        if employee_id:
            # Get all approved loans for employee
            existing_loans = self.search([
                ('employee_id', '=', employee_id),
                ('state', '=', 'approve')
            ])
            
            # Calculate total pending balance (not total loan amount)
            total_pending_balance = sum(existing_loans.mapped('balance_amount'))
            new_amount = values.get('loan_amount', 0)
            
            # Get the maximum amount from company settings
            max_amount = float(self.env['ir.config_parameter'].sudo().get_param(
                'hr_loan.max_loan_amount', 100000))
            
            if total_pending_balance + new_amount > max_amount:
                raise UserError(
                    _("Total pending balance would exceed maximum allowed (%.2f + %.2f > %.2f)") % 
                    (total_pending_balance, new_amount, max_amount))
        
        values['name'] = self.env['ir.sequence'].get('hr.loan.seq') or ' '
        return super(HrLoan, self).create(values)

    @api.model
    def get_max_loan_amount(self):
        """Helper method to get maximum loan amount, can be overridden"""
        return self.max_loan_amount

    def action_compute_installment(self):
        """This automatically create the installment the employee need to pay to
            company based on payment start date and the no of installments.
            """
        for loan in self:
            loan.loan_lines.unlink()
            date_start = datetime.strptime(str(loan.payment_date), '%Y-%m-%d')
            amount = loan.loan_amount / loan.installment
            for i in range(1, loan.installment + 1):
                self.env['hr.loan.line'].create({
                    'date': date_start,
                    'amount': amount,
                    'employee_id': loan.employee_id.id,
                    'loan_id': loan.id})
                date_start = date_start + relativedelta(months=1)
            loan._compute_total_amount()
        return True

    def action_refuse(self):
        """ Function to reject loan request"""
        return self.write({'state': 'refuse'})

    def action_submit(self):
        """ Function to submit loan request"""
        self.write({'state': 'waiting_approval_1'})

    def action_cancel(self):
        """ Function to cancel loan request"""
        self.write({'state': 'cancel'})

    def action_approve(self):
        """ Function to approve loan request"""
        for data in self:
            if not data.loan_lines:
                raise ValidationError(_("Please Compute installment"))
            else:
                self.write({'state': 'approve'})

    def unlink(self):
        """ Function which restrict the deletion of approved or submitted
                loan request"""
        for loan in self:
            if loan.state not in ('draft', 'cancel'):
                raise UserError(_(
                    'You cannot delete a loan which is not in draft '
                    'or cancelled state'))
        return super(HrLoan, self).unlink()

    def register_payment(self):
        self.ensure_one()
        if self.state not in [ 'approve', 'partial_paid' ] :
            raise UserError(_("Payment can be registered only after the loan is approved or in partial payment stage."))
        return {
            'name': _("Register Loan Payment"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.loan.payment.register',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }


class HrLoanLine(models.Model):
    """ Model for managing details of loan request installments"""
    _name = "hr.loan.line"
    _description = "Installment Line"

    date = fields.Date(string="Payment Date", required=True, help="Date of the payment")
    employee_id = fields.Many2one('hr.employee', string="Employee", help="Employee")
    amount = fields.Float(string="Amount", required=True, help="Amount")
    paid = fields.Boolean(string="Paid", help="Deducted from payslip")
    released = fields.Boolean(string="Released", help="Loan amount released to employee")  # NEW FIELD
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.", help="Reference to the associated loan.")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.", help="Reference to the associated payslip, if any.")
