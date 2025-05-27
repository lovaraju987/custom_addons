from datetime import timedelta
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

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
    )

    report_date = fields.Date(
        string="Report Date",
        compute='_compute_daily_payments',
    )

    @api.depends('journal_owner_id')
    def _compute_daily_payments(self):
        report_day = fields.Date.context_today(self)
        for journal in self:
            journal.report_date = report_day
            payments = self.env['account.payment'].search([
                ('journal_id', '=', journal.id),
                ('date', '=', report_day),
                ('state', '=', 'posted')
            ])
            _logger.info("Journal [%s]: for date %s, found %d posted payments", 
                         journal.id, report_day, len(payments))
            journal.payment_lines = payments

    def print_journal_summary_report(self):
        # Return a report action
        return self.env.ref('journal_daily_summary_mlr.action_report_journal_daily_summary').report_action(self)