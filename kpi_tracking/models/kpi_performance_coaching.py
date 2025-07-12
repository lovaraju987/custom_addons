from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class KPIPerformanceCoaching(models.Model):
    _name = 'kpi.performance.coaching'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'KPI Performance Coaching & Feedback'
    _order = 'create_date desc'
    _rec_name = 'title'

    title = fields.Char(string='Coaching Session Title', required=True, tracking=True)
    kpi_id = fields.Many2one('kpi.report', string='Related KPI', required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, tracking=True)
    manager_id = fields.Many2one('hr.employee', string='Manager/Coach', required=True, tracking=True)
    
    coaching_type = fields.Selection([
        ('improvement_plan', 'Performance Improvement Plan'),
        ('best_practice_sharing', 'Best Practice Sharing'),
        ('mentoring_session', 'Mentoring Session'),
        ('skill_development', 'Skill Development Plan'),
        ('goal_setting', 'Goal Setting Session'),
        ('feedback_session', 'Feedback Session'),
        ('career_development', 'Career Development Discussion')
    ], string='Coaching Type', required=True, default='improvement_plan', tracking=True)
    
    session_date = fields.Datetime(string='Session Date', required=True, tracking=True)
    duration_hours = fields.Float(string='Duration (Hours)', default=1.0)
    
    state = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled')
    ], string='Status', default='scheduled', tracking=True)
    
    # Performance context
    current_performance = fields.Float(string='Current Performance %', 
                                       related='kpi_id.achievement_percent', readonly=True)
    target_performance = fields.Float(string='Target Performance %', default=100.0)
    performance_gap = fields.Float(string='Performance Gap %', 
                                   compute='_compute_performance_gap', store=True)
    
    # Session content
    session_agenda = fields.Html(string='Session Agenda')
    performance_analysis = fields.Html(string='Performance Analysis')
    strengths_identified = fields.Html(string='Strengths Identified')
    improvement_areas = fields.Html(string='Areas for Improvement')
    
    # Feedback exchange
    manager_feedback = fields.Html(string='Manager Feedback')
    employee_response = fields.Html(string='Employee Response')
    employee_concerns = fields.Html(string='Employee Concerns/Questions')
    
    # Development planning
    development_goals = fields.Html(string='Development Goals')
    action_plan = fields.Html(string='Action Plan')
    resources_needed = fields.Html(string='Resources/Support Needed')
    success_metrics = fields.Html(string='Success Metrics')
    
    # Follow-up planning
    next_review_date = fields.Date(string='Next Review Date', tracking=True)
    follow_up_frequency = fields.Selection([
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly')
    ], string='Follow-up Frequency', default='monthly')
    
    # Goal tracking
    goal_ids = fields.One2many('kpi.coaching.goal', 'coaching_id', string='Coaching Goals')
    goals_count = fields.Integer(string='Goals Count', compute='_compute_goals_count')
    completed_goals = fields.Integer(string='Completed Goals', compute='_compute_goals_count')
    
    # Session rating and effectiveness
    employee_satisfaction = fields.Selection([
        ('1', 'Very Dissatisfied'),
        ('2', 'Dissatisfied'),
        ('3', 'Neutral'),
        ('4', 'Satisfied'),
        ('5', 'Very Satisfied')
    ], string='Employee Satisfaction Rating')
    
    coaching_effectiveness = fields.Selection([
        ('1', 'Not Effective'),
        ('2', 'Slightly Effective'),
        ('3', 'Moderately Effective'),
        ('4', 'Very Effective'),
        ('5', 'Extremely Effective')
    ], string='Coaching Effectiveness Rating')
    
    # Progress tracking
    previous_coaching_id = fields.Many2one('kpi.performance.coaching', string='Previous Coaching Session')
    progress_since_last = fields.Html(string='Progress Since Last Session')
    
    # Related fields for filtering
    department = fields.Selection(related='kpi_id.department', store=True, readonly=True)
    kpi_name = fields.Char(related='kpi_id.name', store=True, readonly=True)
    employee_name = fields.Char(related='employee_id.name', store=True, readonly=True)
    manager_name = fields.Char(related='manager_id.name', store=True, readonly=True)
    
    @api.depends('current_performance', 'target_performance')
    def _compute_performance_gap(self):
        for record in self:
            record.performance_gap = record.target_performance - record.current_performance
    
    @api.depends('goal_ids', 'goal_ids.status')
    def _compute_goals_count(self):
        for record in self:
            record.goals_count = len(record.goal_ids)
            record.completed_goals = len(record.goal_ids.filtered(lambda g: g.status == 'achieved'))
    
    def action_start_session(self):
        """Start the coaching session"""
        self.write({'state': 'in_progress'})
        return True
    
    def action_complete_session(self):
        """Complete the coaching session"""
        self.write({'state': 'completed'})
        # Schedule next review if date is set
        if self.next_review_date:
            self._schedule_next_review()
        return True
    
    def action_cancel_session(self):
        """Cancel the coaching session"""
        self.write({'state': 'cancelled'})
        return True
    
    def action_reschedule_session(self):
        """Reschedule the coaching session"""
        self.write({'state': 'rescheduled'})
        return True
    
    def action_create_follow_up(self):
        """Create a follow-up coaching session"""
        next_date = self._calculate_next_session_date()
        
        follow_up = self.copy({
            'title': f"Follow-up: {self.title}",
            'session_date': next_date,
            'state': 'scheduled',
            'previous_coaching_id': self.id,
            'session_agenda': f"Follow-up on previous session: {self.title}",
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kpi.performance.coaching',
            'res_id': follow_up.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def _calculate_next_session_date(self):
        """Calculate next session date based on frequency"""
        base_date = self.session_date or fields.Datetime.now()
        
        if self.follow_up_frequency == 'weekly':
            return base_date + timedelta(weeks=1)
        elif self.follow_up_frequency == 'biweekly':
            return base_date + timedelta(weeks=2)
        elif self.follow_up_frequency == 'monthly':
            return base_date + relativedelta(months=1)
        elif self.follow_up_frequency == 'quarterly':
            return base_date + relativedelta(months=3)
        else:
            return base_date + relativedelta(months=1)
    
    def _schedule_next_review(self):
        """Schedule next review activity"""
        self.activity_schedule(
            'kpi_tracking.mail_activity_kpi_coaching_review',
            date_deadline=self.next_review_date,
            summary=f'KPI Coaching Review: {self.title}',
            user_id=self.manager_id.user_id.id if self.manager_id.user_id else self.env.user.id
        )
    
    @api.model
    def create(self, vals):
        """Override create to notify participants"""
        coaching = super().create(vals)
        # Notify employee and manager
        partners = []
        if coaching.employee_id.user_id:
            partners.append(coaching.employee_id.user_id.partner_id.id)
        if coaching.manager_id.user_id:
            partners.append(coaching.manager_id.user_id.partner_id.id)
        
        if partners:
            coaching.message_post(
                body=f"Coaching session scheduled: {coaching.title}",
                partner_ids=partners,
                subtype_xmlid='mail.mt_comment'
            )
        return coaching
    
    def action_view_goals(self):
        """Open goals related to this coaching session"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kpi.coaching.goal',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('coaching_session_id', '=', self.id)],
            'context': {
                'default_coaching_session_id': self.id,
                'search_default_coaching_session_id': self.id
            },
            'name': f'Goals for {self.title}'
        }
    
    def action_view_completed_goals(self):
        """Open completed goals related to this coaching session"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kpi.coaching.goal',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('coaching_session_id', '=', self.id), ('status', '=', 'achieved')],
            'context': {
                'default_coaching_session_id': self.id,
                'search_default_coaching_session_id': self.id,
                'search_default_achieved': True
            },
            'name': f'Completed Goals for {self.title}'
        }


class KPICoachingGoal(models.Model):
    _name = 'kpi.coaching.goal'
    _description = 'KPI Coaching Goal'
    _order = 'priority desc, target_date asc'
    _rec_name = 'description'

    coaching_id = fields.Many2one('kpi.performance.coaching', string='Coaching Session', 
                                  required=True, ondelete='cascade')
    description = fields.Text(string='Goal Description', required=True)
    detailed_plan = fields.Html(string='Detailed Plan')
    
    goal_type = fields.Selection([
        ('performance', 'Performance Improvement'),
        ('skill', 'Skill Development'),
        ('behavior', 'Behavior Change'),
        ('knowledge', 'Knowledge Acquisition'),
        ('process', 'Process Improvement'),
        ('relationship', 'Relationship Building')
    ], string='Goal Type', required=True)
    
    priority = fields.Selection([
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High'),
        ('4', 'Critical')
    ], string='Priority', default='2')
    
    target_date = fields.Date(string='Target Date', required=True)
    start_date = fields.Date(string='Start Date', default=fields.Date.today)
    
    status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('achieved', 'Achieved'),
        ('partially_achieved', 'Partially Achieved'),
        ('not_achieved', 'Not Achieved'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='not_started')
    
    progress_percent = fields.Float(string='Progress %', default=0.0)
    
    # Success criteria
    success_criteria = fields.Html(string='Success Criteria')
    measurement_method = fields.Text(string='How to Measure Success')
    
    # Results
    achieved_date = fields.Date(string='Achieved Date')
    achievement_notes = fields.Html(string='Achievement Notes')
    lessons_learned = fields.Html(string='Lessons Learned')
    
    # Support and resources
    resources_required = fields.Html(string='Resources Required')
    support_needed = fields.Html(string='Support Needed')
    obstacles = fields.Html(string='Potential Obstacles')
    
    @api.constrains('target_date', 'start_date')
    def _check_dates(self):
        for record in self:
            if record.target_date and record.start_date and record.target_date < record.start_date:
                raise ValidationError("Target date cannot be earlier than start date.")
    
    def action_start_goal(self):
        """Mark goal as in progress"""
        self.write({'status': 'in_progress'})
        return True
    
    def action_achieve_goal(self):
        """Mark goal as achieved"""
        self.write({
            'status': 'achieved',
            'achieved_date': fields.Date.today(),
            'progress_percent': 100.0
        })
        return True
    
    def action_partially_achieve_goal(self):
        """Mark goal as partially achieved"""
        self.write({'status': 'partially_achieved'})
        return True
    
    def action_not_achieve_goal(self):
        """Mark goal as not achieved"""
        self.write({'status': 'not_achieved'})
        return True
    
    def action_cancel_goal(self):
        """Cancel the goal"""
        self.write({'status': 'cancelled'})
        return True


class KPICoachingTemplate(models.Model):
    _name = 'kpi.coaching.template'
    _description = 'KPI Coaching Template'
    _rec_name = 'name'

    name = fields.Char(string='Template Name', required=True)
    coaching_type = fields.Selection([
        ('improvement_plan', 'Performance Improvement Plan'),
        ('best_practice_sharing', 'Best Practice Sharing'),
        ('mentoring_session', 'Mentoring Session'),
        ('skill_development', 'Skill Development Plan'),
        ('goal_setting', 'Goal Setting Session'),
        ('feedback_session', 'Feedback Session'),
        ('career_development', 'Career Development Discussion')
    ], string='Coaching Type', required=True)
    
    department = fields.Selection([
        ('sales', 'Sales'),
        ('operations', 'Operations'),
        ('marketing', 'Marketing'),
        ('finance', 'Finance'),
        ('hr', 'HR'),
        ('store', 'Store'),
        ('admin', 'Administration'),
        ('rnd', 'R&D'),
        ('it', 'IT')
    ], string='Department')
    
    duration_hours = fields.Float(string='Default Duration (Hours)', default=1.0)
    
    # Template content
    agenda_template = fields.Html(string='Agenda Template')
    questions_template = fields.Html(string='Discussion Questions Template')
    goals_template = fields.Html(string='Goals Template')
    action_plan_template = fields.Html(string='Action Plan Template')
    
    # Usage tracking
    usage_count = fields.Integer(string='Times Used', default=0)
    
    def action_use_template(self):
        """Create a new coaching session from this template"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kpi.performance.coaching',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_coaching_type': self.coaching_type,
                'default_duration_hours': self.duration_hours,
                'default_session_agenda': self.agenda_template,
                'default_development_goals': self.goals_template,
                'default_action_plan': self.action_plan_template,
            }
        }
