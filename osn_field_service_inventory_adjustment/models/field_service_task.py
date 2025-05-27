from odoo import models, fields, api, _
from odoo.exceptions import UserError


class FieldServiceTask(models.Model):
    _inherit = 'project.task'

    actual_pieces = fields.One2many(
        'field.service.piece', 'task_id', string='Actual Pieces Installed'
    )
    total_actual_sqft = fields.Float(
        string='Total Actual Square Feet',
        compute='_compute_total_actual_sqft',
        store=True
    )

    @api.depends('actual_pieces')
    def _compute_total_actual_sqft(self):
        for task in self:
            task.total_actual_sqft = sum(piece.actual_sqft for piece in task.actual_pieces)

        # if self.total_actual_sqft > 0:
        #             # Check if all mandatory checklist items are completed
        #     net_piece_items = self.checklist_line_ids.filtered(lambda line: line.is_piece_related)
        #     incomplete_net_piece_items = net_piece_items.filtered(lambda line: not line.is_done)

        #     # Set is_done to True for each item in the filtered records
        #     for item in incomplete_net_piece_items:
        #         item.is_done = True

        for record in self:
            if record.total_actual_sqft > 0:
                            # Check if all mandatory checklist items are completed
                net_piece_items = self.checklist_line_ids.filtered(lambda line: line.is_piece_related)
                incomplete_net_piece_items = net_piece_items.filtered(lambda line: not line.is_done)

                # Set is_done to True for each item in the filtered records
                for item in incomplete_net_piece_items:
                    item.is_done = True
                pass

    def action_close_task(self):
        # Validate that all pieces have at least one attachment
        for task in self:
            for piece in task.actual_pieces:
                if not piece.attachment_ids:
                    raise UserError(_(
                        "Please upload at least one attachment for each piece under task '%s'."
                    ) % task.name)

        # Perform stock adjustments
        for task in self:
            sale_order_line = task.sale_line_id
            if not sale_order_line:
                raise UserError(_("No linked sales order line found."))

            allocated_sqft = sale_order_line.product_uom_qty
            actual_sqft = task.total_actual_sqft

            remaining_sqft = max(allocated_sqft - actual_sqft, 0)

            if remaining_sqft > 0:
                # Create a stock move to restock remaining quantity
                self.env['stock.move'].create({
                    'product_id': sale_order_line.product_id.id,
                    'name': f"Restock from Task {task.name}",
                    'product_uom_qty': remaining_sqft,
                    'product_uom': sale_order_line.product_uom.id,
                    'location_id': task.company_id.stock_location_id.id,
                    'location_dest_id': task.company_id.stock_location_id.id,
                    'state': 'done',  # Directly mark as done
                })

        return super(FieldServiceTask, self).action_close_task()