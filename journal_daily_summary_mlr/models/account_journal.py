from datetime import timedelta
from odoo import models, fields, api

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    journal_owner_id = fields.Many2one(
        'res.partner',
        string='Journal Owner',
        help="Contact responsible for this journal (used for WhatsApp)"
    )

    entry_lines = fields.One2many(
        'account.move.line',
        'journal_id',
        string='Entry Lines',
        compute='_compute_daily_entries',
        store=True   # Changed to store=True for testing
    )

    report_date = fields.Date(
        string="Report Date",
        compute='_compute_daily_entries',
        store=True   # Changed to store=True for testing
    )

    @api.depends('journal_owner_id')
    def _compute_daily_entries(self):
        # Temporarily use current day for testing
        report_day = fields.Date.context_today(self)
        for journal in self:
            journal.report_date = report_day
            move_lines = self.env['account.move.line'].search([
                ('journal_id', '=', journal.id),
                ('date', '=', report_day)
            ])
            journal.entry_lines = move_lines

    def print_journal_summary_report(self):
        # Return a report action
        return self.env.ref('journal_daily_summary_mlr.action_report_journal_daily_summary').report_action(self)