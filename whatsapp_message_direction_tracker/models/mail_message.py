from odoo import models, api

class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, values_list):
        messages = super(MailMessage, self).create(values_list)

        for msg in messages:
            if (
                msg.message_type == 'wa_msgs'
                and msg.model == 'discuss.channel'
                and msg.res_id
            ):
                channel = self.env['discuss.channel'].browse(msg.res_id)

                if channel:
                    # Check if author is linked to an internal user (not just current user)
                    is_internal_user = bool(msg.author_id and msg.author_id.user_ids)

                    if is_internal_user:
                        # Any internal user replied — outgoing
                        direction = 'outgoing'
                    else:
                        # Customer or unknown partner — incoming
                        direction = 'incoming'

                    # Update channel with latest WA message info
                    channel.sudo().write({
                        'last_wa_message_direction': direction,
                        'last_wa_message_date': msg.create_date,
                    })

        return messages