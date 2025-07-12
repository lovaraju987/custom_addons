from odoo import models, fields, api
from odoo.exceptions import ValidationError


class KPIDiscussion(models.Model):
    _name = 'kpi.discussion'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'KPI Discussion & Collaboration'
    _order = 'create_date desc'
    _rec_name = 'title'

    title = fields.Char(string='Discussion Title', required=True, tracking=True)
    kpi_id = fields.Many2one('kpi.report', string='Related KPI', required=True, tracking=True)
    discussion_type = fields.Selection([
        ('performance_review', 'Performance Review'),
        ('improvement_plan', 'Improvement Planning'),
        ('target_adjustment', 'Target Adjustment'),
        ('escalation', 'Issue Escalation'),
        ('best_practice', 'Best Practice Sharing'),
        ('feedback', 'Feedback & Suggestions')
    ], string='Discussion Type', required=True, default='performance_review', tracking=True)
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Priority', default='1', tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active Discussion'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ], string='Status', default='draft', tracking=True)
    
    description = fields.Html(string='Description')
    initiator_id = fields.Many2one('res.users', string='Initiated By', 
                                   default=lambda self: self.env.user, readonly=True)
    assigned_to_ids = fields.Many2many('res.users', string='Participants', 
                                       help='Users who should participate in this discussion')
    
    # Discussion metrics
    current_value = fields.Float(string='Current KPI Value', related='kpi_id.value', readonly=True)
    target_value = fields.Float(string='Target Value', related='kpi_id.target_value', readonly=True)
    achievement_percent = fields.Float(string='Achievement %', related='kpi_id.achievement_percent', readonly=True)
    
    # Action items relationship
    action_item_ids = fields.One2many('kpi.action.item', 'discussion_id', string='Action Items')
    action_items_count = fields.Integer(string='Action Items Count', compute='_compute_action_items_count')
    completed_action_items = fields.Integer(string='Completed Actions', compute='_compute_action_items_count')
    
    # Resolution details
    resolution = fields.Html(string='Resolution Details')
    resolved_by_id = fields.Many2one('res.users', string='Resolved By')
    resolved_date = fields.Datetime(string='Resolved Date')
    
    # Related fields for easier filtering
    department = fields.Selection(related='kpi_id.department', store=True, readonly=True)
    kpi_name = fields.Char(related='kpi_id.name', store=True, readonly=True)
    
    @api.depends('action_item_ids', 'action_item_ids.status')
    def _compute_action_items_count(self):
        for record in self:
            record.action_items_count = len(record.action_item_ids)
            record.completed_action_items = len(record.action_item_ids.filtered(lambda x: x.status == 'completed'))
    
    def action_start_discussion(self):
        """Start the discussion and notify participants"""
        self.write({'state': 'active'})
        # Send notification to participants
        if self.assigned_to_ids:
            self.message_post(
                body=f"Discussion '{self.title}' has been started. Please participate and share your insights.",
                partner_ids=self.assigned_to_ids.mapped('partner_id').ids,
                subtype_xmlid='mail.mt_comment'
            )
        return True
    
    def action_resolve_discussion(self):
        """Mark discussion as resolved"""
        self.write({
            'state': 'resolved',
            'resolved_by_id': self.env.user.id,
            'resolved_date': fields.Datetime.now()
        })
        return True
    
    def action_close_discussion(self):
        """Close the discussion"""
        self.write({'state': 'closed'})
        return True
    
    def action_reopen_discussion(self):
        """Reopen a closed discussion"""
        self.write({'state': 'active'})
        return True
    
    def action_view_action_items(self):
        """View action items for this discussion"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kpi.action.item',
            'view_mode': 'tree,form',
            'domain': [('discussion_id', '=', self.id)],
            'context': {'default_discussion_id': self.id},
            'name': f'Action Items - {self.title}',
        }
    
    def action_view_completed_action_items(self):
        """View completed action items for this discussion"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kpi.action.item',
            'view_mode': 'tree,form',
            'domain': [('discussion_id', '=', self.id), ('state', '=', 'completed')],
            'context': {'default_discussion_id': self.id},
            'name': f'Completed Action Items - {self.title}',
        }
    
    @api.model
    def create(self, vals):
        """Override create to notify participants"""
        discussion = super().create(vals)
        if discussion.assigned_to_ids:
            discussion.message_post(
                body=f"You have been added to KPI discussion: '{discussion.title}'",
                partner_ids=discussion.assigned_to_ids.mapped('partner_id').ids,
                subtype_xmlid='mail.mt_comment'
            )
        return discussion


class KPIActionItem(models.Model):
    _name = 'kpi.action.item'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'KPI Action Item'
    _order = 'priority desc, due_date asc'
    _rec_name = 'description'

    discussion_id = fields.Many2one('kpi.discussion', string='Related Discussion', 
                                    required=True, ondelete='cascade')
    kpi_id = fields.Many2one(related='discussion_id.kpi_id', store=True, readonly=True)
    
    description = fields.Text(string='Action Description', required=True)
    detailed_plan = fields.Html(string='Detailed Action Plan')
    
    assigned_to_id = fields.Many2one('res.users', string='Assigned To', required=True, tracking=True)
    created_by_id = fields.Many2one('res.users', string='Created By', 
                                    default=lambda self: self.env.user, readonly=True)
    
    due_date = fields.Date(string='Due Date', required=True, tracking=True)
    start_date = fields.Date(string='Start Date', default=fields.Date.today)
    completed_date = fields.Date(string='Completed Date', readonly=True)
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Critical')
    ], string='Priority', default='1', tracking=True)
    
    status = fields.Selection([
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('blocked', 'Blocked')
    ], string='Status', default='open', tracking=True)
    
    progress_percent = fields.Float(string='Progress %', default=0.0, 
                                    help='Manual progress tracking (0-100%)')
    
    # Results and feedback
    completion_notes = fields.Html(string='Completion Notes')
    impact_description = fields.Text(string='Impact on KPI', 
                                     help='Describe how this action impacted the KPI performance')
    
    # Effort tracking
    estimated_hours = fields.Float(string='Estimated Hours')
    actual_hours = fields.Float(string='Actual Hours')
    
    # Dependencies
    dependent_on_ids = fields.Many2many('kpi.action.item', 'kpi_action_item_dependency_rel',
                                        'action_item_id', 'depends_on_id', 
                                        string='Depends On', 
                                        help='Other action items this depends on')
    blocking_ids = fields.Many2many('kpi.action.item', 'kpi_action_item_dependency_rel',
                                    'depends_on_id', 'action_item_id',
                                    string='Blocking Items',
                                    help='Action items that depend on this one')
    
    @api.constrains('due_date', 'start_date')
    def _check_dates(self):
        for record in self:
            if record.due_date and record.start_date and record.due_date < record.start_date:
                raise ValidationError("Due date cannot be earlier than start date.")
    
    def action_start_progress(self):
        """Mark action item as in progress"""
        self.write({'status': 'in_progress'})
        return True
    
    def action_complete(self):
        """Mark action item as completed"""
        self.write({
            'status': 'completed',
            'completed_date': fields.Date.today(),
            'progress_percent': 100.0
        })
        # Notify discussion participants
        self.discussion_id.message_post(
            body=f"Action item completed: {self.description}",
            subtype_xmlid='mail.mt_comment'
        )
        return True
    
    def action_block(self):
        """Mark action item as blocked"""
        self.write({'status': 'blocked'})
        return True
    
    def action_cancel(self):
        """Cancel the action item"""
        self.write({'status': 'cancelled'})
        return True
    
    def action_reopen(self):
        """Reopen a completed/cancelled action item"""
        self.write({'status': 'open'})
        return True
    
    @api.model
    def create(self, vals):
        """Override create to notify assigned user"""
        action_item = super().create(vals)
        if action_item.assigned_to_id:
            action_item.message_post(
                body=f"New action item assigned to you: {action_item.description}",
                partner_ids=[action_item.assigned_to_id.partner_id.id],
                subtype_xmlid='mail.mt_comment'
            )
        return action_item
    
    def write(self, vals):
        """Override write to notify on assignment changes"""
        result = super().write(vals)
        if 'assigned_to_id' in vals:
            for record in self:
                if record.assigned_to_id:
                    record.message_post(
                        body=f"Action item reassigned to you: {record.description}",
                        partner_ids=[record.assigned_to_id.partner_id.id],
                        subtype_xmlid='mail.mt_comment'
                    )
        return result
