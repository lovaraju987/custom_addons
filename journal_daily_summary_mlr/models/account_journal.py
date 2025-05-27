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
        store=False
    )

    report_date = fields.Date(
        string="Report Date",
        compute='_compute_daily_entries',
        store=False
    )

    @api.depends('journal_owner_id')
    def _compute_daily_entries(self):
        today = fields.Date.context_today(self)
        report_day = fields.Date.from_string(today) - timedelta(days=1)
        for journal in self:
            journal.report_date = report_day
            journal.entry_lines = self.env['account.move.line'].search([
                ('journal_id', '=', journal.id),
                ('date', '=', report_day)
            ])

    def print_journal_summary_report(self):
        return self.env.ref('journal_daily_summary_mlr.action_report_journal_daily_summary') \
                   .report_action(self, data={'download': True})