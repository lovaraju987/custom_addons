from datetime import timedelta
from odoo import models, fields, api

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    journal_owner_id = fields.Many2one(
        'res.partner',
        string='Journal Owner',
        help="Contact responsible for this journal (used for WhatsApp)"
    )

    payment_lines = fields.One2many(
        'account.payment',
        'journal_id',
        string='Payment Lines',
        compute='_compute_daily_payments',
        store=True   # For testing purposes.
    )

    report_date = fields.Date(
        string="Report Date",
        compute='_compute_daily_payments',
        store=True    # For testing purposes; later adjust as needed.
    )

    @api.depends('journal_owner_id')
    def _compute_daily_payments(self):
        # Temporarily using current day for testing
        report_day = fields.Date.context_today(self)
        for journal in self:
            journal.report_date = report_day
            payments = self.env['account.payment'].search([
                ('journal_id', '=', journal.id),
                ('payment_date', '=', report_day)
            ])
            journal.payment_lines = payments

    def print_journal_summary_report(self):
        # Return a report action
        return self.env.ref('journal_daily_summary_mlr.action_report_journal_daily_summary').report_action(self)