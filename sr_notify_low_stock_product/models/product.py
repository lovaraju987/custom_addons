# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import api, fields, models, _
import json


class ProductProduct(models.Model):
    _inherit = "product.product"

    min_qty = fields.Float(string="Min Qty")
    min_qty_visible = fields.Boolean(compute="_compute_min_qty_visible")

    def _compute_min_qty_visible(self):
        for prodcut in self:
            if self.env['ir.config_parameter'].sudo().get_param('sr_notify_low_stock_product.apply_min_qty_on') == 'product':
                prodcut.min_qty_visible = True
            else:
                prodcut.min_qty_visible = False

    def send_min_qty_notification(self):
        apply_min_qty_on = self.env['ir.config_parameter'].sudo().get_param(
            'sr_notify_low_stock_product.apply_min_qty_on')

        company_ids = self.env['res.company'].sudo().search([])
        products = False
        if apply_min_qty_on == 'global':
            min_qty = float(self.env['ir.config_parameter'].sudo().get_param('sr_notify_low_stock_product.min_qty'))
            products = self.search([]).filtered(lambda x: x.qty_available < min_qty)
        if apply_min_qty_on == 'product':
            products = self.search([]).filtered(lambda x: x.qty_available < x.min_qty)
        if apply_min_qty_on == 'category':
            products = self.search([]).filtered(lambda x: x.qty_available < x.categ_id.min_qty)
        if apply_min_qty_on == 'reorder_rule':
            products = self.search([]).filtered(lambda x: x.qty_available < x.reordering_min_qty)

        if products and company_ids:
            for company in company_ids:
                template_id = self.env.ref(
                    'sr_notify_low_stock_product.email_template_min_qty_notification').id
                template = self.env['mail.template'].browse(template_id)
                values = {}
                msg = '<p style="margin: 0px; padding: 0px; font-size: 13px;">Here are your products that have reached the minimum quantity'

                if apply_min_qty_on == 'global':
                    msg += ' (Global)'
                if apply_min_qty_on == 'product':
                    msg += ' (Individual Product)'
                if apply_min_qty_on == 'category':
                    msg += ' (Category)'
                if apply_min_qty_on == 'reorder_rule':
                    msg += ' (Reordering Rule)'

                msg += ':<table style="border: 1px solid black;"><tbody><tr>' \
                    '<th style="width:135px;background-color:#D3D3D3;border: 1px solid black;">Product Variant</th>' \
                    '<th style="width:85px;background-color:#D3D3D3;border: 1px solid black;">Min Qty</th>' \
                    '<th style="width:125px;background-color:#D3D3D3;border: 1px solid black;">On Hand Qty</th>' \
                    '<th style="width:125px;background-color:#D3D3D3;border: 1px solid black;">Forecasted Qty</th>' \
                    '<th style="width:125px;background-color:#D3D3D3;border: 1px solid black;">Company</th></tr>'

                for product in products:
                    warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company.id)])
                    location_ids = warehouse_ids.mapped('lot_stock_id')
                    quant_ids = product.stock_quant_ids.filtered(
                        lambda r: r.location_id.id in location_ids.ids and r.company_id.id == company.id)

                    for quant in quant_ids:  # Iterate through multiple quants
                        # Access the product variant instead of the product
                        forecasted_qty = product.product_variant_id.virtual_available

                        msg += f'<tr><td style="border: 1px solid black;">{product.display_name}</td>' \
                            f'<td style="border: 1px solid black;">'

                        if apply_min_qty_on == 'global':
                            msg += str(float(self.env['ir.config_parameter'].sudo().get_param(
                                'sr_notify_low_stock_product.min_qty')))
                        if apply_min_qty_on == 'product':
                            msg += str(product.min_qty)
                        if apply_min_qty_on == 'category':
                            msg += str(product.categ_id.min_qty)
                        if apply_min_qty_on == 'reorder_rule':
                            msg += str(product.reordering_min_qty)

                        msg += f'</td><td style="border: 1px solid black;">{quant.quantity}</td>' \
                            f'<td style="border: 1px solid black;">{forecasted_qty}</td>' \
                            f'<td style="border: 1px solid black;">{company.name}</td></tr>'

                msg += "</tbody></table>"
                values['subject'] = template.subject
                values['body_html'] = msg

                if self.env['ir.config_parameter'].sudo().get_param('sr_notify_low_stock_product.notify_to') == 'users':
                    user_ids_param = self.env['ir.config_parameter'].sudo().get_param(
                        'sr_notify_low_stock_product.min_qty_user_ids')
                    if user_ids_param:
                        user_ids = self.env['res.users'].browse(json.loads(user_ids_param))
                        emails = set(user.email for user in user_ids if user.email)
                        values['email_to'] = ','.join(emails)

                if self.env['ir.config_parameter'].sudo().get_param('sr_notify_low_stock_product.notify_to') == 'groups':
                    group_ids_param = self.env['ir.config_parameter'].sudo().get_param(
                        'sr_notify_low_stock_product.min_qty_group_ids')
                    if group_ids_param:
                        group_ids = self.env['res.groups'].browse(json.loads(group_ids_param))
                        user_ids = group_ids.mapped('users')
                        emails = set(user.email for user in user_ids if user.email)
                        values['email_to'] = ','.join(emails)

                if self.env['ir.config_parameter'].sudo().get_param('sr_notify_low_stock_product.outgoing_mail_id'):
                    server_id = self.env['ir.mail_server'].browse(int(
                        self.env['ir.config_parameter'].sudo().get_param(
                            'sr_notify_low_stock_product.outgoing_mail_id')))
                    values['mail_server_id'] = server_id.id
                    values['email_from'] = server_id.smtp_user

                email = self.env['mail.mail'].create(values)
                email.send()

class ProductCategory(models.Model):
    _inherit = "product.category"

    min_qty = fields.Float(string="Min Qty")
    min_qty_visible = fields.Boolean(compute="_compute_min_qty_visible")

    def _compute_min_qty_visible(self):
        for prodcut in self:
            if self.env['ir.config_parameter'].sudo().get_param('sr_notify_low_stock_product.apply_min_qty_on') == 'category':
                prodcut.min_qty_visible = True
            else:
                prodcut.min_qty_visible = False