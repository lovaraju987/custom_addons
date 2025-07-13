from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


class KPIApprovalWorkflow(models.Model):
    _name = 'kpi.approval.workflow'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'KPI Approval Workflow'
    _order = 'create_date desc'
    _rec_name = 'name'

    name = fields.Char(string='Workflow Name', required=True, tracking=True)
    kpi_id = fields.Many2one('kpi.report', string='Related KPI', required=True, tracking=True)
    workflow_type = fields.Selection([
        ('target_change', 'Target Value Change'),
        ('formula_modification', 'Formula Modification'),
        ('below_threshold', 'Below Threshold Justification'),
        ('exceptional_submission', 'Exceptional Submission'),
        ('kpi_modification', 'KPI Configuration Change'),
        ('department_transfer', 'Department Transfer')
    ], string='Workflow Type', required=True, tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted for Approval'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Priority', default='1', tracking=True)
    
    # Requestor information
    requested_by_id = fields.Many2one('res.users', string='Requested By', 
                                      default=lambda self: self.env.user, readonly=True)
    request_date = fields.Datetime(string='Request Date', default=fields.Datetime.now, readonly=True)
    request_reason = fields.Html(string='Request Reason', required=True)
    
    # Current vs Proposed values
    current_target_value = fields.Float(string='Current Target Value', related='kpi_id.target_value', readonly=True)
    proposed_target_value = fields.Float(string='Proposed Target Value')
    current_formula = fields.Text(string='Current Formula', related='kpi_id.formula_field', readonly=True)
    proposed_formula = fields.Text(string='Proposed Formula')
    
    # Justification for below threshold
    current_achievement = fields.Float(string='Current Achievement %', related='kpi_id.achievement_percent', readonly=True)
    threshold_value = fields.Float(string='Threshold Value', help='Minimum acceptable achievement percentage')
    justification = fields.Html(string='Justification for Below Threshold Performance')
    
    # Approval configuration
    approval_levels = fields.Integer(string='Required Approval Levels', default=1)
    auto_approve_threshold = fields.Float(string='Auto-approve Below %', default=10.0,
                                          help='Automatically approve if change is below this percentage')
    escalation_timeout = fields.Integer(string='Escalation Timeout (hours)', default=48)
    
    # Approval tracking
    approval_line_ids = fields.One2many('kpi.approval.line', 'workflow_id', string='Approval Lines')
    current_approval_level = fields.Integer(string='Current Approval Level', default=0)
    next_approver_id = fields.Many2one('res.users', string='Next Approver', compute='_compute_next_approver')
    
    # Final approval details
    final_approver_id = fields.Many2one('res.users', string='Final Approver')
    approval_date = fields.Datetime(string='Approval Date')
    rejection_reason = fields.Html(string='Rejection Reason')
    
    # Implementation details
    implementation_date = fields.Datetime(string='Implementation Date')
    implemented_by_id = fields.Many2one('res.users', string='Implemented By')
    implementation_notes = fields.Html(string='Implementation Notes')
    
    # Related fields for filtering
    department = fields.Selection(related='kpi_id.department', store=True, readonly=True)
    kpi_name = fields.Char(related='kpi_id.name', store=True, readonly=True)
    
    @api.depends('approval_line_ids', 'approval_line_ids.status', 'current_approval_level')
    def _compute_next_approver(self):
        for record in self:
            next_line = record.approval_line_ids.filtered(
                lambda l: l.approval_level == record.current_approval_level + 1 and l.status == 'pending'
            )
            record.next_approver_id = next_line.approver_id if next_line else False
    
    def action_submit_for_approval(self):
        """Submit the workflow for approval"""
        if not self.approval_line_ids:
            self._create_approval_lines()
        
        self.write({
            'state': 'submitted',
            'current_approval_level': 1
        })
        self._notify_next_approver()
        return True
    
    def action_approve(self):
        """Approve the current level and move to next"""
        current_line = self.approval_line_ids.filtered(
            lambda l: l.approval_level == self.current_approval_level and l.status == 'pending'
        )
        
        if not current_line:
            raise UserError("No pending approval found for current level.")
        
        current_line.write({
            'status': 'approved',
            'approval_date': fields.Datetime.now(),
            'approver_id': self.env.user.id,
            'comments': f'Approved by {self.env.user.name}'
        })
        
        # Check if all levels are approved
        if self.current_approval_level >= self.approval_levels:
            self._finalize_approval()
        else:
            self.current_approval_level += 1
            self._notify_next_approver()
        
        return True
    
    def action_reject(self):
        """Reject the workflow"""
        view_id = self.env.ref('kpi_tracking.view_kpi_approval_rejection_wizard').id
        return {
            'name': 'Rejection Reason',
            'type': 'ir.actions.act_window',
            'res_model': 'kpi.approval.rejection.wizard',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'default_workflow_id': self.id}
        }
    
    def action_cancel(self):
        """Cancel the workflow"""
        self.write({'state': 'cancelled'})
        return True
    
    def action_implement_changes(self):
        """Implement the approved changes"""
        if self.state != 'approved':
            raise UserError("Only approved workflows can be implemented.")
        
        # Implement changes based on workflow type
        if self.workflow_type == 'target_change' and self.proposed_target_value:
            self.kpi_id.write({'target_value': self.proposed_target_value})
        
        elif self.workflow_type == 'formula_modification' and self.proposed_formula:
            self.kpi_id.write({'formula_field': self.proposed_formula})
        
        self.write({
            'implementation_date': fields.Datetime.now(),
            'implemented_by_id': self.env.user.id
        })
        
        # Log the implementation
        self.kpi_id.message_post(
            body=f"Changes implemented from approval workflow: {self.name}",
            subtype_xmlid='mail.mt_comment'
        )
        
        return True
    
    def _create_approval_lines(self):
        """Create approval lines based on configuration"""
        # Get approvers based on KPI hierarchy
        approvers = self._get_approvers()
        
        for level, approver in enumerate(approvers, 1):
            self.env['kpi.approval.line'].create({
                'workflow_id': self.id,
                'approval_level': level,
                'approver_id': approver.id,
                'status': 'pending'
            })
        
        self.approval_levels = len(approvers)
    
    def _get_approvers(self):
        """Get list of approvers based on workflow type and hierarchy"""
        approvers = []
        
        # Get KPI manager first
        kpi_managers = self.env.ref('kpi_tracking.group_kpi_manager').users
        if kpi_managers:
            approvers.append(kpi_managers[0])
        
        # For high priority or significant changes, add admin approval
        if (self.priority in ['2', '3'] or 
            self.workflow_type in ['formula_modification', 'department_transfer'] or
            (self.workflow_type == 'target_change' and 
             abs(self.proposed_target_value - self.current_target_value) / self.current_target_value * 100 > self.auto_approve_threshold)):
            
            kpi_admins = self.env.ref('kpi_tracking.group_kpi_admin').users
            if kpi_admins:
                approvers.append(kpi_admins[0])
        
        return approvers
    
    def _notify_next_approver(self):
        """Notify the next approver"""
        if self.next_approver_id:
            self.message_post(
                body=f"Approval required for {self.workflow_type}: {self.name}",
                partner_ids=[self.next_approver_id.partner_id.id],
                subtype_xmlid='mail.mt_comment'
            )
    
    def _finalize_approval(self):
        """Finalize the approval process"""
        self.write({
            'state': 'approved',
            'final_approver_id': self.env.user.id,
            'approval_date': fields.Datetime.now()
        })
        
        # Notify requestor
        self.message_post(
            body=f"Workflow approved and ready for implementation: {self.name}",
            partner_ids=[self.requested_by_id.partner_id.id],
            subtype_xmlid='mail.mt_comment'
        )
    
    @api.model
    def create(self, vals):
        """Override create to generate name if not provided"""
        if 'name' not in vals or not vals['name']:
            kpi = self.env['kpi.report'].browse(vals.get('kpi_id'))
            workflow_type = vals.get('workflow_type', 'modification')
            vals['name'] = f"{kpi.name} - {dict(self._fields['workflow_type'].selection)[workflow_type]}"
        return super().create(vals)


class KPIApprovalLine(models.Model):
    _name = 'kpi.approval.line'
    _description = 'KPI Approval Line'
    _order = 'approval_level asc'

    workflow_id = fields.Many2one('kpi.approval.workflow', string='Workflow', required=True, ondelete='cascade')
    approval_level = fields.Integer(string='Approval Level', required=True)
    approver_id = fields.Many2one('res.users', string='Approver', required=True)
    
    status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='pending')
    
    approval_date = fields.Datetime(string='Approval Date')
    comments = fields.Html(string='Approver Comments')
    
    # Time tracking
    assigned_date = fields.Datetime(string='Assigned Date', default=fields.Datetime.now)
    response_time_hours = fields.Float(string='Response Time (Hours)', compute='_compute_response_time')
    
    @api.depends('assigned_date', 'approval_date')
    def _compute_response_time(self):
        for record in self:
            if record.assigned_date and record.approval_date:
                delta = record.approval_date - record.assigned_date
                record.response_time_hours = delta.total_seconds() / 3600
            else:
                record.response_time_hours = 0.0


class KPIApprovalRejectionWizard(models.TransientModel):
    _name = 'kpi.approval.rejection.wizard'
    _description = 'KPI Approval Rejection Wizard'

    workflow_id = fields.Many2one('kpi.approval.workflow', string='Workflow', required=True)
    rejection_reason = fields.Html(string='Rejection Reason', required=True)
    
    def action_confirm_rejection(self):
        """Confirm the rejection with reason"""
        self.workflow_id.write({
            'state': 'rejected',
            'rejection_reason': self.rejection_reason
        })
        
        # Update current approval line
        current_line = self.workflow_id.approval_line_ids.filtered(
            lambda l: l.approval_level == self.workflow_id.current_approval_level and l.status == 'pending'
        )
        if current_line:
            current_line.write({
                'status': 'rejected',
                'approval_date': fields.Datetime.now(),
                'approver_id': self.env.user.id,
                'comments': self.rejection_reason
            })
        
        # Notify requestor
        self.workflow_id.message_post(
            body=f"Workflow rejected: {self.rejection_reason}",
            partner_ids=[self.workflow_id.requested_by_id.partner_id.id],
            subtype_xmlid='mail.mt_comment'
        )
        
        return {'type': 'ir.actions.act_window_close'}
