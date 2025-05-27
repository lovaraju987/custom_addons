from odoo import models, fields, api, _
from odoo.exceptions import UserError


class FieldServicePiece(models.Model):
    _name = 'field.service.piece'
    _description = 'Field Service Piece'

    task_id = fields.Many2one('project.task', string='Task', required=True)
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        domain="[('id', 'in', available_product_ids)]"
    )
    height = fields.Float(string='Height (ft)', required=True)
    width = fields.Float(string='Width (ft)', required=True)
    actual_sqft = fields.Float(
        string='Actual Square Feet',
        compute='_compute_actual_sqft',
        store=True
    )
    available_product_ids = fields.Many2many(
        'product.product',
        compute='_compute_available_product_ids',
        store=False,
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Attachments',
        help='Upload photos or videos as proof of measurements.'
    )

    @api.depends('height', 'width')
    def _compute_actual_sqft(self):
        for piece in self:
            piece.actual_sqft = piece.height * piece.width

    @api.depends('task_id')
    def _compute_available_product_ids(self):
        for piece in self:
            if piece.task_id and piece.task_id.sale_line_id:
                sale_order = piece.task_id.sale_line_id.order_id
                piece.available_product_ids = sale_order.order_line.mapped('product_id')
            else:
                piece.available_product_ids = self.env['product.product']

    @api.model
    def create(self, vals):
        if 'attachment_ids' not in vals or not vals.get('attachment_ids'):
            raise UserError(_("Please add at least one attachment as proof before saving."))
        return super(FieldServicePiece, self).create(vals)

    def write(self, vals):
        if 'attachment_ids' in vals and not vals.get('attachment_ids'):
            raise UserError(_("At least one attachment is required."))
        return super(FieldServicePiece, self).write(vals)