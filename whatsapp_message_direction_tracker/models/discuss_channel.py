from odoo import models, fields

class DiscussChannel(models.Model):
    _inherit = 'discuss.channel'

    last_wa_message_direction = fields.Selection([
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing')
    ], string="Last WhatsApp Message Direction")

    last_wa_message_date = fields.Datetime(string="Last WA Message Date")