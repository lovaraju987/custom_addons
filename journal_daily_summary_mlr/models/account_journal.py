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
        compute='_compute_daily_payments'
    )

    report_date = fields.Date(
        string="Report Date",
        compute='_compute_daily_payments'
    )

    # New summary fields
    current_balance = fields.Float(
        string="Current Balance",
        compute="_compute_payments_summary"
    )
    total_received_today = fields.Float(
        string="Total Received Today",
        compute="_compute_payments_summary"
    )
    total_sent_today = fields.Float(
        string="Total Sent Today",
        compute="_compute_payments_summary"
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

    @api.depends('payment_lines', 'payment_lines.date', 'payment_lines.state', 'payment_lines.payment_type', 'payment_lines.amount')
    def _compute_payments_summary(self):
        # Use today's date as reference (the report date)
        for journal in self:
            report_day = fields.Date.context_today(journal)
            # Search for all posted payments with date <= today
            payments_all = self.env['account.payment'].search([
                ('journal_id', '=', journal.id),
                ('date', '<=', report_day),
                ('state', '=', 'posted')
            ])
            balance = 0.0
            received = 0.0
            sent = 0.0
            for pay in payments_all:
                if pay.payment_type == 'inbound':
                    balance += pay.amount
                    if pay.date == report_day:
                        received += pay.amount
                elif pay.payment_type == 'outbound':
                    balance -= pay.amount
                    if pay.date == report_day:
                        sent += pay.amount
            journal.current_balance = balance
            journal.total_received_today = received
            journal.total_sent_today = sent

    def print_journal_summary_report(self):
        # Return a report action
        return self.env.ref('journal_daily_summary_mlr.action_report_journal_daily_summary').report_action(self)