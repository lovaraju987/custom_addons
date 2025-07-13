from odoo import models, fields, api
from statistics import mean
import logging

_logger = logging.getLogger(__name__)


class HrEmployeeKPI(models.Model):
    _inherit = 'hr.employee'

    # KPI-related fields
    assigned_kpi_ids = fields.Many2many(
        'kpi.report', 
        string="Assigned KPIs",
        compute="_compute_assigned_kpis",
        help="KPIs assigned to this employee"
    )
    
    kpi_count = fields.Integer(
        string="Total KPIs",
        compute="_compute_kpi_metrics",
        search="_search_kpi_count",
        help="Total number of KPIs assigned to this employee"
    )
    
    total_kpi_achievement = fields.Float(
        string="Overall KPI Achievement (%)",
        compute="_compute_kpi_metrics",
        search="_search_total_kpi_achievement",
        digits=(16, 2),
        help="Weighted average achievement percentage across all assigned KPIs"
    )
    
    kpi_score_label = fields.Char(
        string="KPI Performance Score",
        compute="_compute_kpi_metrics",
        search="_search_kpi_score_label",
        help="Overall performance label based on KPI achievements"
    )
    
    kpi_score_color = fields.Selection([
        ('0', 'Grey'),     # No KPIs or no data
        ('1', 'Green'),    # Excellent (95%+)
        ('2', 'Blue'),     # Good (80-94%)
        ('3', 'Orange'),   # Average (70-79%)
        ('4', 'Yellow'),   # Needs Improvement (50-69%)
        ('5', 'Darkred'),  # Underperformance (<50%)
    ], string="KPI Score Color", compute="_compute_kpi_metrics")
    
    # Recent KPI submissions
    recent_kpi_submissions = fields.Many2many(
        'kpi.report.submission',
        string="Recent KPI Submissions",
        compute="_compute_recent_submissions",
        help="Recent KPI submissions by this employee"
    )

    @api.depends('user_id')
    def _compute_assigned_kpis(self):
        """Compute KPIs assigned to this employee"""
        for employee in self:
            if employee.user_id:
                # Find KPIs where this employee's user is assigned
                try:
                    assigned_kpis = self.env['kpi.report'].search([
                        ('assigned_user_ids', 'in', employee.user_id.ids)
                    ])
                    employee.assigned_kpi_ids = assigned_kpis
                except Exception:
                    employee.assigned_kpi_ids = self.env['kpi.report']
            else:
                employee.assigned_kpi_ids = self.env['kpi.report']

    @api.depends('assigned_kpi_ids.achievement_percent', 'assigned_kpi_ids.priority_weight')
    def _compute_kpi_metrics(self):
        """Compute KPI metrics for the employee"""
        for employee in self:
            # Check if user has access to KPI data
            if not self.env.user.has_group('kpi_tracking.group_kpi_user') and \
               not self.env.user.has_group('kpi_tracking.group_kpi_manager') and \
               not self.env.user.has_group('kpi_tracking.group_kpi_admin'):
                employee.kpi_count = 0
                employee.total_kpi_achievement = 0.0
                employee.kpi_score_label = ""
                employee.kpi_score_color = '0'
                continue
                
            kpis = employee.assigned_kpi_ids
            employee.kpi_count = len(kpis)
            
            if not kpis:
                employee.total_kpi_achievement = 0.0
                employee.kpi_score_label = "No KPIs Assigned"
                employee.kpi_score_color = '0'
                continue
            
            # Calculate weighted average achievement
            total_weight = 0.0
            weighted_score = 0.0
            
            for kpi in kpis:
                weight = float(kpi.priority_weight or 1.0)
                achievement = min(kpi.achievement_percent or 0.0, 100.0)  # Cap at 100%
                total_weight += weight
                weighted_score += achievement * weight
            
            if total_weight > 0:
                employee.total_kpi_achievement = weighted_score / total_weight
            else:
                employee.total_kpi_achievement = 0.0
            
            # Determine score label and color
            percent = employee.total_kpi_achievement
            if percent >= 95:
                employee.kpi_score_label = "Excellent Performance"
                employee.kpi_score_color = '1'
            elif percent >= 80:
                employee.kpi_score_label = "Good Performance"
                employee.kpi_score_color = '2'
            elif percent >= 70:
                employee.kpi_score_label = "Average Performance"
                employee.kpi_score_color = '3'
            elif percent >= 50:
                employee.kpi_score_label = "Needs Improvement"
                employee.kpi_score_color = '4'
            else:
                employee.kpi_score_label = "Underperformance"
                employee.kpi_score_color = '5'

    @api.depends('user_id')
    def _compute_recent_submissions(self):
        """Compute recent KPI submissions for this employee"""
        for employee in self:
            if employee.user_id:
                try:
                    # Get recent submissions (last 30 days)
                    recent_submissions = self.env['kpi.report.submission'].search([
                        ('user_id', '=', employee.user_id.id),
                        ('date', '>=', fields.Datetime.now() - fields.timedelta(days=30))
                    ], order='date desc', limit=10)
                    employee.recent_kpi_submissions = recent_submissions
                except Exception:
                    employee.recent_kpi_submissions = self.env['kpi.report.submission']
            else:
                employee.recent_kpi_submissions = self.env['kpi.report.submission']

    def action_view_employee_kpis(self):
        """Open assigned KPIs for this employee"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'KPIs for {self.name}',
            'res_model': 'kpi.report',
            'view_mode': 'tree,form',
            'domain': [('assigned_user_ids', 'in', self.user_id.ids)] if self.user_id else [('id', '=', False)],
            'context': {
                'default_assigned_user_ids': [(6, 0, self.user_id.ids)] if self.user_id else [],
                'search_default_assigned_to_employee': 1,
            },
            'target': 'current',
        }

    def action_view_kpi_submissions(self):
        """Open KPI submissions for this employee"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'KPI Submissions for {self.name}',
            'res_model': 'kpi.report.submission',
            'view_mode': 'tree,form',
            'domain': [('user_id', '=', self.user_id.id)] if self.user_id else [('id', '=', False)],
            'context': {
                'default_user_id': self.user_id.id if self.user_id else False,
            },
            'target': 'current',
        }

    def action_create_kpi_discussion(self):
        """Create a new KPI discussion for this employee"""
        self.ensure_one()
        
        # Get the first assigned KPI for context (if any)
        default_kpi = self.assigned_kpi_ids[0] if self.assigned_kpi_ids else False
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'New KPI Discussion for {self.name}',
            'res_model': 'kpi.discussion',
            'view_mode': 'form',
            'context': {
                'default_kpi_id': default_kpi.id if default_kpi else False,
                'default_title': f'Performance discussion with {self.name}',
                'default_discussion_type': 'performance_review',
                'default_participant_ids': [(6, 0, [self.user_id.id] if self.user_id else [])],
            },
            'target': 'new',
        }

    def _search_kpi_count(self, operator, value):
        """Search method for kpi_count field"""
        # Find employees that have KPIs assigned to them
        employees_with_kpis = self.env['hr.employee'].search([
            ('user_id', '!=', False)
        ])
        
        employee_ids = []
        for employee in employees_with_kpis:
            if employee.user_id:
                kpi_count = self.env['kpi.report'].search_count([
                    ('assigned_user_ids', 'in', employee.user_id.ids)
                ])
                
                # Apply the operator
                if operator == '>' and kpi_count > value:
                    employee_ids.append(employee.id)
                elif operator == '=' and kpi_count == value:
                    employee_ids.append(employee.id)
                elif operator == '<' and kpi_count < value:
                    employee_ids.append(employee.id)
                elif operator == '>=' and kpi_count >= value:
                    employee_ids.append(employee.id)
                elif operator == '<=' and kpi_count <= value:
                    employee_ids.append(employee.id)
                elif operator == '!=' and kpi_count != value:
                    employee_ids.append(employee.id)
        
        return [('id', 'in', employee_ids)]

    def _search_total_kpi_achievement(self, operator, value):
        """Search method for total_kpi_achievement field"""
        # Find employees that have KPIs assigned
        employees_with_kpis = self.env['hr.employee'].search([
            ('user_id', '!=', False)
        ])
        
        employee_ids = []
        for employee in employees_with_kpis:
            if employee.user_id:
                # Calculate achievement for this employee
                kpis = self.env['kpi.report'].search([
                    ('assigned_user_ids', 'in', employee.user_id.ids)
                ])
                
                if not kpis:
                    achievement = 0.0
                else:
                    total_weight = sum(float(kpi.priority_weight or 1.0) for kpi in kpis)
                    weighted_score = sum(min(kpi.achievement_percent or 0.0, 100.0) * float(kpi.priority_weight or 1.0) for kpi in kpis)
                    achievement = (weighted_score / total_weight) if total_weight > 0 else 0.0
                
                # Apply the operator
                if operator == '>=' and achievement >= value:
                    employee_ids.append(employee.id)
                elif operator == '<' and achievement < value:
                    employee_ids.append(employee.id)
                elif operator == '=' and achievement == value:
                    employee_ids.append(employee.id)
                elif operator == '>' and achievement > value:
                    employee_ids.append(employee.id)
                elif operator == '<=' and achievement <= value:
                    employee_ids.append(employee.id)
                elif operator == '!=' and achievement != value:
                    employee_ids.append(employee.id)
        
        return [('id', 'in', employee_ids)]

    def _search_kpi_score_label(self, operator, value):
        """Search method for kpi_score_label field"""
        # Find employees that have KPIs assigned
        employees_with_kpis = self.env['hr.employee'].search([
            ('user_id', '!=', False)
        ])
        
        employee_ids = []
        for employee in employees_with_kpis:
            if employee.user_id:
                # Calculate achievement and determine score label
                kpis = self.env['kpi.report'].search([
                    ('assigned_user_ids', 'in', employee.user_id.ids)
                ])
                
                if not kpis:
                    score_label = "No KPIs Assigned"
                else:
                    total_weight = sum(float(kpi.priority_weight or 1.0) for kpi in kpis)
                    weighted_score = sum(min(kpi.achievement_percent or 0.0, 100.0) * float(kpi.priority_weight or 1.0) for kpi in kpis)
                    achievement = (weighted_score / total_weight) if total_weight > 0 else 0.0
                    
                    if achievement >= 95:
                        score_label = "Excellent Performance"
                    elif achievement >= 80:
                        score_label = "Good Performance"
                    elif achievement >= 70:
                        score_label = "Average Performance"
                    elif achievement >= 50:
                        score_label = "Needs Improvement"
                    else:
                        score_label = "Underperformance"
                
                # Apply the operator
                if operator == '=' and score_label == value:
                    employee_ids.append(employee.id)
                elif operator == '!=' and score_label != value:
                    employee_ids.append(employee.id)
                elif operator == 'ilike' and value.lower() in score_label.lower():
                    employee_ids.append(employee.id)
        
        return [('id', 'in', employee_ids)]

    @api.depends('user_id')
    def _compute_recent_submissions(self):
        """Compute recent KPI submissions for this employee"""
        for employee in self:
            if employee.user_id:
                try:
                    # Get recent submissions (last 30 days)
                    recent_submissions = self.env['kpi.report.submission'].search([
                        ('user_id', '=', employee.user_id.id),
                        ('date', '>=', fields.Datetime.now() - fields.timedelta(days=30))
                    ], order='date desc', limit=10)
                    employee.recent_kpi_submissions = recent_submissions
                except Exception:
                    employee.recent_kpi_submissions = self.env['kpi.report.submission']
            else:
                employee.recent_kpi_submissions = self.env['kpi.report.submission']

    def action_view_employee_kpis(self):
        """Open assigned KPIs for this employee"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'KPIs for {self.name}',
            'res_model': 'kpi.report',
            'view_mode': 'tree,form',
            'domain': [('assigned_user_ids', 'in', self.user_id.ids)] if self.user_id else [('id', '=', False)],
            'context': {
                'default_assigned_user_ids': [(6, 0, self.user_id.ids)] if self.user_id else [],
                'search_default_assigned_to_employee': 1,
            },
            'target': 'current',
        }

    def action_view_kpi_submissions(self):
        """Open KPI submissions for this employee"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'KPI Submissions for {self.name}',
            'res_model': 'kpi.report.submission',
            'view_mode': 'tree,form',
            'domain': [('user_id', '=', self.user_id.id)] if self.user_id else [('id', '=', False)],
            'context': {
                'default_user_id': self.user_id.id if self.user_id else False,
            },
            'target': 'current',
        }

    def action_create_kpi_discussion(self):
        """Create a new KPI discussion for this employee"""
        self.ensure_one()
        
        # Get the first assigned KPI for context (if any)
        default_kpi = self.assigned_kpi_ids[0] if self.assigned_kpi_ids else False
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'New KPI Discussion for {self.name}',
            'res_model': 'kpi.discussion',
            'view_mode': 'form',
            'context': {
                'default_kpi_id': default_kpi.id if default_kpi else False,
                'default_title': f'Performance discussion with {self.name}',
                'default_discussion_type': 'performance_review',
                'default_participant_ids': [(6, 0, [self.user_id.id] if self.user_id else [])],
            },
            'target': 'new',
        }
