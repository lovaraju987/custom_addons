from datetime import timedelta
import logging
import json
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    partner_id = fields.Many2one(
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

    report_date = fields.Datetime(
        string="Report Date",
        compute='_compute_daily_payments'
    )

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

    @api.depends('partner_id')
    def _compute_daily_payments(self):
        # Use today's date for search, but assign now() for report_date so time is included.
        report_day = fields.Date.context_today(self)
        for journal in self:
            # Assign current datetime in the report header
            journal.report_date = fields.Datetime.now()
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
        for journal in self:
            # Parse outstanding_pay_account_balance from kanban_dashboard
            dashboard = json.loads(journal.kanban_dashboard or '{}')
            balance_str = dashboard.get('outstanding_pay_account_balance', '0')
            balance = float(balance_str.replace('₹', '').replace(',', '').strip() or 0.0)

            report_day = fields.Date.context_today(journal)
            payments_today = self.env['account.payment'].search([
                ('journal_id', '=', journal.id),
                ('date', '=', report_day),
                ('state', '=', 'posted')
            ])
            received = sum(pay.amount for pay in payments_today if pay.payment_type == 'inbound')
            sent = sum(pay.amount for pay in payments_today if pay.payment_type == 'outbound')

            journal.current_balance = balance
            journal.total_received_today = received
            journal.total_sent_today = sent

    def print_journal_summary_report(self):
        return self.env.ref('journal_daily_summary_mlr.action_report_journal_daily_summary').report_action(self)