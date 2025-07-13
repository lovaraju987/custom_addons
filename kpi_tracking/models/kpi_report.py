# Your KPI model logic goes here
from odoo import models, fields, api
from lxml import etree
from datetime import timedelta, datetime, time
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from collections import namedtuple
from types import SimpleNamespace
import logging

_logger = logging.getLogger(__name__)

# Constants for model names
KPI_REPORT_SUBMISSION_MODEL = 'kpi.report.submission'
KPI_REPORT_GROUP_MODEL = 'kpi.report.group'
KPI_REPORT_GROUP_SUBMISSION_MODEL = 'kpi.report.group.submission'

class KPIReport(models.Model):
    _name = 'kpi.report'
    _inherit = ['mail.thread']
    _description = 'KPI Report'
    _order = 'department, name'

    # SQL constraints for data integrity
    _sql_constraints = [
        ('target_value_positive', 'CHECK(target_value >= 0)', 'Target value must be positive or zero'),
        ('achievement_percent_range', 'CHECK(achievement_percent >= 0)', 'Achievement percent cannot be negative'),
        ('unique_kpi_name_report', 'UNIQUE(name, report_id)', 'KPI name must be unique within a report group'),
    ]

    count_a = fields.Integer(string="Base Count (count_a)", readonly=True)
    count_b = fields.Integer(string="Filtered Count (count_b)", readonly=True)
    name = fields.Char(string='KPI Name', required=True)
    report_id = fields.Many2one('kpi.report.group', string="Report")
    kpi_type = fields.Selection([('manual', 'Manual'), ('auto', 'Auto')], required=True)
    assigned_user_ids = fields.Many2many('res.users', string="Assigned Users")
    target_type = fields.Selection([
        ('number', 'Number'),
        ('percent', 'Percentage'),
        ('currency', '₹ Rupees'),
        ('boolean', 'Achieved / Not Achieved'),
        ('duration', 'Time (hrs)')
    ], string="Target Type", default='number')

    target_value = fields.Float(string="Target Value")
    target_unit_display = fields.Char(
        compute="_compute_target_unit_display",
        string="Target (with Unit)",
        store=False
    )
    priority_weight = fields.Selection([
            ('1', 'Very Low'),
            ('2', 'Low'),
            ('3', 'Medium'),
            ('4', 'High'),
            ('5', 'Very High')
        ], string="Priority", default='3')
    
    score_label = fields.Char(string="Score Label", compute="_compute_score_label", store=True)
    score_color = fields.Selection([
        ('0', 'Grey'),     # default
        ('1', 'Green'),    # Excellent
        ('2', 'Blue'),     # Good
        ('3', 'Orange'),   # Average
        ('4', 'Yellow'),      # Needs Improvement
        ('5', 'Darkred'),  # Underperformance
    ], string="Score Color", compute="_compute_score_label", store=True)

    @api.depends('achievement_percent')
    def _compute_score_label(self):
        for rec in self:
            percent = rec.achievement_percent or 0.0
            if percent >= 95:
                rec.score_label = "Excellent"
                rec.score_color = '1'
            elif percent >= 80:
                rec.score_label = "Good"
                rec.score_color = '2'
            elif percent >= 70:
                rec.score_label = "Average"
                rec.score_color = '3'
            elif percent >= 50:
                rec.score_label = "Needs Improvement"
                rec.score_color = '4'
            else:
                rec.score_label = "Underperformance"
                rec.score_color = '5'

    @api.depends('target_type', 'target_value')
    def _compute_target_unit_display(self):
        for rec in self:
            if rec.target_type == 'percent':
                rec.target_unit_display = f"{rec.target_value:.2f} %"
            elif rec.target_type == 'currency':
                rec.target_unit_display = f"₹ {rec.target_value:,.2f}"
            elif rec.target_type == 'duration':
                rec.target_unit_display = f"{rec.target_value:.2f} hrs"
            elif rec.target_type == 'boolean':
                rec.target_unit_display = "Achieved" if rec.target_value else "Not Achieved"
            else:
                rec.target_unit_display = f"{rec.target_value}"

    achievement_percent = fields.Float(
        string="Target Achievement (%)",
        compute="_compute_achievement",
        store=True,
        digits=(16, 2)
    )

    kpi_direction = fields.Selection([
                    ('higher_better', 'Higher is Better'),
                    ('lower_better', 'Lower is Better'),
                ], string="KPI Direction", default='higher_better')

    @api.depends('value', 'target_value', 'target_type', 'kpi_direction')
    def _compute_achievement(self):
        for rec in self:
            rec.achievement_percent = rec._calculate_achievement_percent()

    note = fields.Text(string="Note")
    submission_ids = fields.One2many(KPI_REPORT_SUBMISSION_MODEL, 'kpi_id', string="Submission History")
    report_type = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ], string='Report Type')
    department = fields.Selection([
        ('sales', 'Sales'),
        ('technician', 'Technician'),
        ('operations', 'Operations'),
        ('store', 'Store'),
        ('marketing', 'Marketing'),
        ('hr', 'HR'),
        ('finance', 'Finance'),
        ('rnd', 'R&D'),
        ('it', 'IT'),
        ('admin', 'Admin'),
    ])

    @api.onchange('report_id')
    def _onchange_report_id(self):
        if self.report_id and self.report_id.department:
            self.department = self.report_id.department

    manual_value = fields.Float(string="Manual Input Value")
    value = fields.Float(string='Latest Value', readonly=True)
    last_submitted = fields.Date(string='Last Submitted')

    source_model_id = fields.Many2one('ir.model', string='Source Model')
    source_model = fields.Char(related='source_model_id.model', store=True, readonly=True)
    filter_field_id = fields.Many2one(
    'ir.model.fields',
    string='Filter Field',
    domain="[('model_id', '=', source_model_id)]"  # Remove ttype filter
)
    filter_field = fields.Char(related='filter_field_id.name', store=True, readonly=True, string='Filter Field Name')
    filter_type = fields.Selection([
        ('today', 'Today'),
        ('this_week', 'This Week'),
        ('this_month', 'This Month')
    ])
    count_field_id = fields.Many2one(
        'ir.model.fields',
        string='Count Field',
        domain="[('model_id', '=', source_model_id), ('ttype', '=', 'boolean')]",
        help="Boolean field to count for count_b calculation"
    )
    count_field = fields.Char(related='count_field_id.name', store=True, readonly=True, string='Count Field Name')
    formula_field = fields.Text()
    source_domain = fields.Text(string="Source Domain", help="Domain filter for records")
    domain_test_result = fields.Char(readonly=True)
    formula_notes = fields.Text()
    
    # Migration helper field
    needs_filter_field_migration = fields.Boolean(
        string="Needs Filter Field Migration",
        compute="_compute_needs_migration",
        help="Indicates if this KPI needs filter field data migration"
    )
    needs_count_field_migration = fields.Boolean(
        string="Needs Count Field Migration",
        compute="_compute_needs_migration",
        help="Indicates if this KPI needs count field data migration"
    )

    @api.depends('filter_field', 'filter_field_id', 'source_model_id', 'count_field', 'count_field_id')
    def _compute_needs_migration(self):
        """Check if KPI needs filter field or count field migration"""
        for record in self:
            record.needs_filter_field_migration = (
                bool(record.filter_field) and 
                not record.filter_field_id and 
                bool(record.source_model_id)
            )
            record.needs_count_field_migration = (
                bool(record.count_field) and 
                not record.count_field_id and 
                bool(record.source_model_id)
            )

    @api.onchange('source_model_id')
    def _onchange_source_model_id(self):
        """Reset related fields when source model changes"""
        self.domain_test_result = ''
        self.filter_field_id = False
        if self.source_model_id:
            try:
                # Test if model can be accessed
                self.env[self.source_model_id.model].check_access_rights('read')
                self.formula_notes = "Model loaded successfully. Select a date/datetime field for filtering."
            except Exception as e:
                self.formula_notes = f"Error loading model: {e}"
        else:
            self.formula_notes = ""

    @api.onchange('filter_field_id')
    def _onchange_filter_field_id(self):
        """Update formula notes when filter field changes"""
        if self.filter_field_id:
            field_type = self.filter_field_id.ttype
            if field_type == 'date':
                self.formula_notes = f"Selected date field: {self.filter_field_id.name}. Use filter_type to specify time range."
            elif field_type == 'datetime':
                self.formula_notes = f"Selected datetime field: {self.filter_field_id.name}. Use filter_type to specify time range."
            else:
                self.formula_notes = f"Warning: Field {self.filter_field_id.name} is not a date/datetime field."

    @api.onchange('count_field_id')
    def _onchange_count_field_id(self):
        """Update formula notes when count field changes"""
        if self.count_field_id:
            field_type = self.count_field_id.ttype
            if field_type == 'boolean':
                self.formula_notes = f"Selected boolean field: {self.count_field_id.name}. Records where this field is True will be counted as count_b."
            else:
                self.formula_notes = f"Warning: Field {self.count_field_id.name} is not a boolean field. Only boolean fields should be used for count_b calculations."
        else:
            if self.filter_field_id:
                self._onchange_filter_field_id()  # Restore filter field message

    @api.onchange('source_model_id')
    def _onchange_source_model_id(self):
        """Reset related fields when source model changes"""
        self.domain_test_result = ''
        self.filter_field_id = False
        self.count_field_id = False  # Reset count field when model changes
        if self.source_model_id:
            try:
                # Test if model can be accessed
                self.env[self.source_model_id.model].check_access_rights('read')
                self.formula_notes = "Model loaded successfully. Select a date/datetime field for filtering and optionally a boolean field for counting."
            except Exception as e:
                self.formula_notes = f"Error loading model: {e}"
        else:
            self.formula_notes = ""

    def action_test_domain(self):
        self.ensure_one()
        try:
            local_vars = {
                'uid': self.env.uid,
                'user': self.env.user,
                'assigned_user': self.env.user,
                'today': fields.Date.today(),
                'yesterday': fields.Date.today() - timedelta(days=1),
                'datetime': fields.Datetime,
            }
            dummy_record = SimpleNamespace()
            local_vars['record'] = dummy_record

            domain = eval(self.source_domain or '[]', {}, local_vars)

            if not self.source_model:
                self.domain_test_result = "Invalid: Source Model not defined"
                return

            count = self.env[self.source_model].search_count(domain)
            self.domain_test_result = f"Valid domain. {count} records."
        except Exception as e:
            self.domain_test_result = f"Invalid: {str(e)}"

    def action_manual_refresh_kpi(self):
        """Enhanced with permission checks"""
        self.ensure_one()
        
        # Check permissions
        if not self.env.user.has_group('kpi_tracking.group_kpi_admin'):
            if not self.env.user.has_group('kpi_tracking.group_kpi_manager'):
                if self.env.user.id not in self.assigned_user_ids.ids:
                    raise UserError("You can only update KPIs assigned to you.")
        
        today = fields.Date.today()

        if self.kpi_type == 'manual':
            self.sudo().value = self.manual_value

            for user in self.assigned_user_ids:
                # Check for existing submission for today
                existing = self.env[KPI_REPORT_SUBMISSION_MODEL].sudo().search([
                    ('kpi_id', '=', self.id),
                    ('user_id', '=', user.id),
                    ('date', '>=', datetime.combine(today, datetime.min.time())),
                    ('date', '<', datetime.combine(today + relativedelta(days=1), datetime.min.time())),
                ], limit=1)

                vals = {
                    'kpi_id': self.id,
                    'user_id': user.id,
                    'value': self.manual_value,
                    'note': self.note,
                    'date': fields.Datetime.now(),
                }

                if existing:
                    # Update existing submission instead of creating new one
                    existing.sudo().write(vals)
                else:
                    # Create new submission only if none exists for today
                    self.env[KPI_REPORT_SUBMISSION_MODEL].sudo().create(vals)
            
            # Create/update group submission history
            self._create_group_submission_history()

        else:
            self.sudo().scheduled_update_kpis()

    @api.model
    def scheduled_update_kpis(self):
        """Auto update KPI values - with enhanced error handling"""
        today = fields.Date.today()
        
        # Add error tracking
        errors = []
        success_count = 0
        
        for rec in self.search([('kpi_type', '=', 'auto')]):
            try:
                if not rec.source_model_id or not rec.source_model:
                    _logger.warning(f"KPI {rec.name} (ID: {rec.id}) has no source model configured")
                    continue
                    
                model = self.env[rec.source_model]
                assigned_users = rec.assigned_user_ids or self.env.user

                for assigned_user in assigned_users:
                    try:
                        # Enhanced domain validation
                        domain_base = []
                        start_date, end_date = None, None

                        if rec.filter_type == 'today':
                            start_date = datetime.combine(today, time.min)
                            end_date = datetime.combine(today, time.max)
                        elif rec.filter_type == 'this_week':
                            start_date = datetime.combine(today - timedelta(days=today.weekday()), time.min)
                            end_date = datetime.combine(today, time.max)
                        elif rec.filter_type == 'this_month':
                            start_date = datetime.combine(today.replace(day=1), time.min)
                            end_date = datetime.combine(today, time.max)

                        if rec.filter_field and start_date and end_date:
                            domain_base += [
                                (rec.filter_field, '>=', start_date),
                                (rec.filter_field, '<=', end_date)
                            ]

                        # Calculate count_a using only time filter (domain_base)
                        try:
                            records_a = model.search(domain_base)
                            count_a = len(records_a)
                        except Exception as e:
                            _logger.error(f"Error searching records for count_a in KPI {rec.name}: {e}")
                            continue

                        # Calculate count_b and get filtered records for formula
                        count_b = 0
                        filtered_records = model.browse([])  # Default empty recordset
                        domain_with_filter = domain_base[:]
                        
                        if rec.source_domain:
                            try:
                                local_vars = {
                                    'uid': assigned_user.id,
                                    'user': assigned_user,
                                    'assigned_user': assigned_user,
                                    'today': today,
                                    'yesterday': today - timedelta(days=1),
                                    'datetime': fields.Datetime,
                                }
                                additional_domain = eval(rec.source_domain, {}, local_vars)
                                if not isinstance(additional_domain, list):
                                    raise ValueError("Domain must be a list")
                                domain_with_filter += additional_domain
                            except Exception as e:
                                _logger.error(f"Error evaluating domain for KPI {rec.name}: {e}")
                        
                        try:
                            if rec.count_field:
                                # For boolean count_field, filter records by the field
                                all_filtered = model.search(domain_with_filter)
                                count_b = len(all_filtered.filtered(lambda r: getattr(r, rec.count_field, False)))
                                filtered_records = all_filtered  # Use all filtered records for formula
                            else:
                                # For conversion rates, count_b is records matching time + domain filters
                                filtered_records = model.search(domain_with_filter)
                                count_b = len(filtered_records)
                        except Exception as e:
                            _logger.error(f"Error calculating count_b for KPI {rec.name}: {e}")
                            count_b = 0
                            filtered_records = model.browse([])

                        # Safe formula evaluation
                        final_value = 0.0
                        if rec.formula_field:
                            try:
                                # Create safe import function that only allows specific modules
                                def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
                                    """Safe import function that only allows specific modules"""
                                    allowed_modules = {
                                        'json', 're', 'math', 'datetime', 'decimal', 'statistics',
                                        'collections', 'itertools', 'functools', 'operator'
                                    }
                                    if name in allowed_modules:
                                        return __import__(name, globals, locals, fromlist, level)
                                    else:
                                        raise ImportError(f"Module '{name}' is not allowed for security reasons")
                                
                                # Create safe globals with necessary built-ins and controlled __import__
                                safe_globals = {
                                    "__builtins__": {
                                        'len': len,
                                        'sum': sum,
                                        'max': max,
                                        'min': min,
                                        'abs': abs,
                                        'round': round,
                                        'int': int,
                                        'float': float,
                                        'str': str,
                                        'bool': bool,
                                        'list': list,
                                        'dict': dict,
                                        'range': range,
                                        'enumerate': enumerate,
                                        'sorted': sorted,
                                        'reversed': reversed,
                                        'any': any,
                                        'all': all,
                                        '__import__': safe_import,
                                    },
                                }
                                
                                local_vars = {
                                    'count_a': count_a,
                                    'count_b': count_b,
                                    'records': filtered_records,  # Use the properly filtered records
                                    'assigned_user': assigned_user,
                                    'today': today,
                                }
                                final_value = eval(rec.formula_field, safe_globals, local_vars)
                                if not isinstance(final_value, (int, float)):
                                    final_value = float(final_value)
                                
                                # Enhanced debugging for slot formulas
                                if 'slot_ids' in rec.formula_field and final_value == 0:
                                    debug_info = []
                                    for i, record in enumerate(filtered_records[:3]):  # Check first 3 records
                                        try:
                                            slot_count = len(getattr(record, 'slot_ids', []))
                                            debug_info.append(f"Record {i+1}: {slot_count} slots")
                                        except Exception as e:
                                            debug_info.append(f"Record {i+1}: Error accessing slot_ids - {e}")
                                    
                                    rec.formula_notes = f"Formula evaluated for {assigned_user.name}. Debug: {'; '.join(debug_info)}. Total records: {len(filtered_records)}"
                                else:
                                    rec.formula_notes = f"Formula evaluated for {assigned_user.name}"
                                    
                            except Exception as e:
                                _logger.error(f"Error evaluating formula for KPI {rec.name}: {e}")
                                rec.formula_notes = f"Error evaluating for {assigned_user.name}: {e}"
                                final_value = 0.0

                        # Update KPI values safely
                        try:
                            rec.sudo().write({
                                'count_a': count_a,
                                'count_b': count_b,
                                'value': final_value,
                                'last_submitted': today
                            })
                            success_count += 1
                        except Exception as e:
                            _logger.error(f"Error updating KPI {rec.name}: {e}")
                            errors.append(f"KPI {rec.name}: {str(e)}")
                            continue

                        # Create or update submission record safely
                        try:
                            # Check for existing submission for today
                            existing_submission = self.env[KPI_REPORT_SUBMISSION_MODEL].sudo().search([
                                ('kpi_id', '=', rec.id),
                                ('user_id', '=', assigned_user.id),
                                ('date', '>=', datetime.combine(today, datetime.min.time())),
                                ('date', '<', datetime.combine(today + relativedelta(days=1), datetime.min.time())),
                            ], limit=1)
                            
                            submission_vals = {
                                'kpi_id': rec.id,
                                'user_id': assigned_user.id,
                                'value': final_value,
                                'date': fields.Datetime.now(),
                                'note': f'Auto-updated on {today}'
                            }
                            
                            if existing_submission:
                                # Update existing submission instead of creating new one
                                existing_submission.sudo().write(submission_vals)
                            else:
                                # Create new submission only if none exists for today
                                self.env[KPI_REPORT_SUBMISSION_MODEL].sudo().create(submission_vals)
                                
                        except Exception as e:
                            _logger.error(f"Error creating/updating submission for KPI {rec.name}: {e}")
                
                    except Exception as e:
                        _logger.error(f"Error processing user {assigned_user.name} for KPI {rec.name}: {e}")
                        errors.append(f"KPI {rec.name} - User {assigned_user.name}: {str(e)}")
                
                # Create/update group submission history after all users are processed
                try:
                    rec._create_group_submission_history()
                except Exception as e:
                    _logger.error(f"Error creating group submission for KPI {rec.name}: {e}")
                        
            except Exception as e:
                _logger.error(f"Error processing KPI {rec.name}: {e}")
                errors.append(f"KPI {rec.name}: {str(e)}")
        
        # Log summary
        _logger.info(f"KPI auto-update completed: {success_count} successful, {len(errors)} errors")
        if errors:
            _logger.warning(f"KPI update errors: {'; '.join(errors[:5])}{'...' if len(errors) > 5 else ''}")
        
        return {
            'success_count': success_count,
            'error_count': len(errors),
            'errors': errors[:10]  # Limit error list
        }

    @api.constrains('source_domain', 'formula_field', 'source_model')
    def _check_domain_and_formula(self):
        class DummyUser:
            def __init__(self, id):
                self.id = id

        class DummySafeNamespace(SimpleNamespace):
            def __getattr__(self, name):
                return [] if name.endswith('_ids') else 0

        for rec in self:
            if rec.source_domain:
                try:
                    local_vars = {
                        'assigned_user': DummyUser(1),
                        'today': fields.Date.today(),
                        'yesterday': fields.Date.today() - timedelta(days=1),
                        'datetime': fields.Datetime,
                    }
                    eval(rec.source_domain, {}, local_vars)
                except Exception as e:
                    raise ValidationError(f"Invalid domain syntax:\n{e}")

            if rec.formula_field:
                try:
                    # Create safe import function for validation
                    def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
                        """Safe import function that only allows specific modules"""
                        allowed_modules = {
                            'json', 're', 'math', 'datetime', 'decimal', 'statistics',
                            'collections', 'itertools', 'functools', 'operator'
                        }
                        if name in allowed_modules:
                            return __import__(name, globals, locals, fromlist, level)
                        else:
                            raise ImportError(f"Module '{name}' is not allowed for security reasons")
                    
                    dummy_records = [DummySafeNamespace() for _ in range(3)]
                    # Add kanban_dashboard to dummy records for testing
                    for dummy_record in dummy_records:
                        dummy_record.kanban_dashboard = '{"outstanding_pay_account_balance": "₹ 1,000.00"}'
                    
                    safe_globals = {
                        "__builtins__": {
                            'len': len,
                            'sum': sum,
                            'max': max,
                            'min': min,
                            'abs': abs,
                            'round': round,
                            'int': int,
                            'float': float,
                            'str': str,
                            'bool': bool,
                            'list': list,
                            'dict': dict,
                            'range': range,
                            'enumerate': enumerate,
                            'sorted': sorted,
                            'reversed': reversed,
                            'any': any,
                            'all': all,
                            '__import__': safe_import,
                        },
                    }
                    local_vars = {
                        'count_a': 100,
                        'count_b': 20,
                        'count_c': 5,
                        'records': dummy_records,
                        'assigned_user': DummyUser(1),
                        'today': fields.Date.today(),
                        'yesterday': fields.Date.today() - timedelta(days=1),
                        'datetime': fields.Datetime,
                    }
                    eval(rec.formula_field.strip(), safe_globals, local_vars)
                except Exception as e:
                    raise ValidationError(f"Invalid formula:\n{e}")

    @api.constrains('formula_field', 'source_domain')
    def _validate_formula_security(self):
        """Validate formula for security risks"""
        for rec in self:
            rec._validate_formula_keywords()
            rec._validate_domain_keywords()

    def _validate_formula_keywords(self):
        """Check formula for dangerous keywords"""
        if self.formula_field:
            # Remove '__import__' from dangerous keywords since we now provide it safely
            dangerous_keywords = ['exec', 'eval', 'open', 'file', 'compile', 'globals']
            formula_lower = self.formula_field.lower()
            for keyword in dangerous_keywords:
                if keyword in formula_lower:
                    raise ValidationError(f"Formula contains dangerous keyword: {keyword}")

    def _validate_domain_keywords(self):
        """Check domain for dangerous keywords"""
        if self.source_domain:
            # Remove '__import__' from dangerous keywords since we now provide it safely
            dangerous_keywords = ['exec', 'eval', 'open', 'file', 'compile', 'globals']
            domain_lower = self.source_domain.lower()
            for keyword in dangerous_keywords:
                if keyword in domain_lower:
                    raise ValidationError(f"Domain contains dangerous keyword: {keyword}")

    @api.constrains('target_value', 'target_type')
    def _validate_target_value(self):
        """Validate target value based on target type"""
        for rec in self:
            if rec.target_value is not False:  # Allow 0 but not False
                if rec.target_type == 'percent' and rec.target_value > 100:
                    raise ValidationError("Percentage target cannot exceed 100%")
                if rec.target_type == 'boolean' and rec.target_value not in [0, 1]:
                    raise ValidationError("Boolean target must be 0 or 1")
                if rec.target_value < 0:
                    raise ValidationError("Target value cannot be negative")

    @api.model
    def send_manual_kpi_reminders(self):
        manual_kpis = self.search([('kpi_type', '=', 'manual')])
        template = self.env.ref('kpi_tracking.kpi_manual_entry_email_template', raise_if_not_found=False)

        if not template:
            raise UserError("Email template 'kpi_manual_entry_email_template' not found")

        for kpi in manual_kpis:
            for user in kpi.assigned_user_ids:
                template.with_context(kpi_name=kpi.name).send_mail(user.id, force_send=True)

    # Simple boolean field instead of computed field for now
    is_admin = fields.Boolean(string="Can Edit KPI", default=True, store=False)

    # Phase 3: Collaboration & Workflow Excellence - Related Records
    discussion_ids = fields.One2many('kpi.discussion', 'kpi_id', string="Related Discussions")
    action_item_ids = fields.One2many('kpi.action.item', 'kpi_id', string="Related Action Items")
    coaching_session_ids = fields.One2many('kpi.performance.coaching', 'kpi_id', string="Related Coaching Sessions")
    approval_workflow_ids = fields.One2many('kpi.approval.workflow', 'kpi_id', string="Related Approval Workflows")
    
    # Computed counts for smart buttons
    discussion_count = fields.Integer(string="Discussion Count", compute="_compute_collaboration_counts", store=True)
    action_item_count = fields.Integer(string="Action Item Count", compute="_compute_collaboration_counts", store=True)
    coaching_session_count = fields.Integer(string="Coaching Session Count", compute="_compute_collaboration_counts", store=True)
    approval_workflow_count = fields.Integer(string="Approval Workflow Count", compute="_compute_collaboration_counts", store=True)
    
    @api.depends('discussion_ids', 'action_item_ids', 'coaching_session_ids', 'approval_workflow_ids')
    def _compute_collaboration_counts(self):
        """Compute counts for smart buttons"""
        for record in self:
            record.discussion_count = len(record.discussion_ids)
            record.action_item_count = len(record.action_item_ids)
            record.coaching_session_count = len(record.coaching_session_ids)
            record.approval_workflow_count = len(record.approval_workflow_ids)

    def _calculate_achievement_percent(self):
        """Calculate achievement percentage based on target type and direction"""
        if self.target_type in ['number', 'percent', 'currency', 'duration']:
            return self._calculate_numeric_achievement()
        elif self.target_type == 'boolean':
            return 100.0 if self.value else 0.0
        else:
            return 0.0

    def _calculate_numeric_achievement(self):
        """Calculate achievement for numeric target types"""
        if self.kpi_direction == 'higher_better':
            return (self.value / self.target_value * 100) if self.target_value else 0.0
        elif self.kpi_direction == 'lower_better':
            if self.value == 0:
                return 100.0
            else:
                ratio = (self.target_value / self.value * 100) if self.value else 0.0
                return min(ratio, 100.0)
        return 0.0

    @api.model
    def migrate_filter_field_data(self):
        """
        Migrate existing filter_field and count_field string data to Many2one fields.
        This method can be called manually to fix data after module upgrade.
        """
        # Find KPIs with filter_field data but no filter_field_id
        kpis_to_migrate = self.search([
            ('source_model_id', '!=', False),
            '|',
            '&', ('filter_field', '!=', False), ('filter_field_id', '=', False),
            '&', ('count_field', '!=', False), ('count_field_id', '=', False)
        ])
        
        migrated_count = 0
        failed_count = 0
        
        for kpi in kpis_to_migrate:
            try:
                # Migrate filter field
                if kpi.filter_field and not kpi.filter_field_id:
                    filter_field = self.env['ir.model.fields'].search([
                        ('model_id', '=', kpi.source_model_id.id),
                        ('name', '=', kpi.filter_field)
                    ], limit=1)
                    
                    if filter_field:
                        kpi.sudo().write({'filter_field_id': filter_field.id})
                        migrated_count += 1
                        _logger.info(f"Migrated KPI {kpi.name}: filter_field '{kpi.filter_field}' -> filter_field_id {filter_field.id}")
                    else:
                        failed_count += 1
                        _logger.warning(f"Could not find filter field '{kpi.filter_field}' for KPI {kpi.name} (model: {kpi.source_model_id.model})")

                # Migrate count field
                if kpi.count_field and not kpi.count_field_id:
                    count_field = self.env['ir.model.fields'].search([
                        ('model_id', '=', kpi.source_model_id.id),
                        ('name', '=', kpi.count_field),
                        ('ttype', '=', 'boolean')
                    ], limit=1)
                    
                    if count_field:
                        kpi.sudo().write({'count_field_id': count_field.id})
                        migrated_count += 1
                        _logger.info(f"Migrated KPI {kpi.name}: count_field '{kpi.count_field}' -> count_field_id {count_field.id}")
                    else:
                        failed_count += 1
                        _logger.warning(f"Could not find boolean count field '{kpi.count_field}' for KPI {kpi.name} (model: {kpi.source_model_id.model})")
                    
            except Exception as e:
                failed_count += 1
                _logger.error(f"Error migrating KPI {kpi.name}: {str(e)}")
        
        return {
            'migrated': migrated_count,
            'failed': failed_count,
            'message': f"Migration completed: {migrated_count} fields migrated, {failed_count} failed"
        }

    def action_migrate_filter_fields(self):
        """Action to trigger filter field migration"""
        self.ensure_one()
        if not self.env.user.has_group('kpi_tracking.group_kpi_admin'):
            raise UserError("Only KPI Administrators can perform data migration.")
        
        result = self.migrate_filter_field_data()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Migration Completed',
                'message': result['message'],
                'type': 'success' if result['failed'] == 0 else 'warning',
                'sticky': False,
            }
        }

    @api.model
    def default_get(self, fields_list):
        """Override to auto-fix filter field data if needed"""
        result = super().default_get(fields_list)
        return result

    @api.model
    def create(self, vals):
        """Override create to handle field migration if needed"""
        record = super().create(vals)
        record._try_fix_filter_and_count_fields()
        return record

    def write(self, vals):
        """Override write to handle field migration if needed"""
        result = super().write(vals)
        if 'source_model_id' in vals or 'filter_field' in vals or 'count_field' in vals:
            for record in self:
                record._try_fix_filter_and_count_fields()
        return result

    def _try_fix_filter_and_count_fields(self):
        """
        Automatically try to fix filter_field_id and count_field_id if they're empty but have values
        """
        if not self.source_model_id:
            return
            
        updates = {}
        
        # Fix filter field
        if self.filter_field and not self.filter_field_id:
            filter_field = self.env['ir.model.fields'].search([
                ('model_id', '=', self.source_model_id.id),
                ('name', '=', self.filter_field)
            ], limit=1)
            
            if filter_field:
                updates['filter_field_id'] = filter_field.id
                _logger.info(f"Auto-fixed filter_field_id for KPI {self.name}")

        # Fix count field
        if self.count_field and not self.count_field_id:
            count_field = self.env['ir.model.fields'].search([
                ('model_id', '=', self.source_model_id.id),
                ('name', '=', self.count_field),
                ('ttype', '=', 'boolean')
            ], limit=1)
            
            if count_field:
                updates['count_field_id'] = count_field.id
                _logger.info(f"Auto-fixed count_field_id for KPI {self.name}")
        
        # Apply updates if any
        if updates:
            self.sudo().write(updates)

    def _create_group_submission_history(self):
        """Create or update group submission history when KPI is updated"""
        if not self.report_id:
            return
            
        today = fields.Date.today()
        
        # Check if group submission already exists for today
        existing_group_submission = self.env[KPI_REPORT_GROUP_SUBMISSION_MODEL].sudo().search([
            ('report_id', '=', self.report_id.id),
            ('date', '>=', datetime.combine(today, datetime.min.time())),
            ('date', '<', datetime.combine(today + relativedelta(days=1), datetime.min.time())),
        ], limit=1)
        
        # Calculate group achievement percentage
        group_achievement = self.report_id.group_achievement_percent
        group_score_label = self.report_id.score_label
        group_score_color = self.report_id.score_color
        
        group_submission_vals = {
            'report_id': self.report_id.id,
            'value': group_achievement,
            'score_label': group_score_label,
            'score_color': group_score_color,
            'date': fields.Datetime.now(),
            'user_id': self.env.user.id,
            'note': f'Group submission updated on {today} - triggered by KPI: {self.name}'
        }
        
        if existing_group_submission:
            # Update existing group submission
            existing_group_submission.sudo().write(group_submission_vals)
        else:
            # Create new group submission
            self.env[KPI_REPORT_GROUP_SUBMISSION_MODEL].sudo().create(group_submission_vals)

    # Phase 3: Collaboration Action Methods for Smart Buttons
    def action_view_discussions(self):
        """Open related discussions"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Discussions for {self.name}',
            'res_model': 'kpi.discussion',
            'view_mode': 'tree,form',
            'domain': [('kpi_id', '=', self.id)],
            'context': {'default_kpi_id': self.id},
            'target': 'current',
        }
    
    def action_view_action_items(self):
        """Open related action items"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Action Items for {self.name}',
            'res_model': 'kpi.action.item',
            'view_mode': 'tree,form',
            'domain': [('kpi_id', '=', self.id)],
            'context': {'default_kpi_id': self.id},
            'target': 'current',
        }
    
    def action_view_coaching_sessions(self):
        """Open related coaching sessions"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Coaching Sessions for {self.name}',
            'res_model': 'kpi.performance.coaching',
            'view_mode': 'tree,form',
            'domain': [('kpi_id', '=', self.id)],
            'context': {'default_kpi_id': self.id},
            'target': 'current',
        }
    
    def action_view_approval_workflows(self):
        """Open related approval workflows"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Approval Workflows for {self.name}',
            'res_model': 'kpi.approval.workflow',
            'view_mode': 'tree,form',
            'domain': [('kpi_id', '=', self.id)],
            'context': {'default_kpi_id': self.id},
            'target': 'current',
        }
    
    # Quick creation methods for collaboration features
    def action_create_discussion(self):
        """Quick create discussion for this KPI"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'New Discussion for {self.name}',
            'res_model': 'kpi.discussion',
            'view_mode': 'form',
            'context': {
                'default_kpi_id': self.id,
                'default_title': f'Discussion about {self.name}',
                'default_discussion_type': 'performance_review',
                'default_current_value': self.value,
                'default_target_value': self.target_value,
            },
            'target': 'new',
        }
    
    def action_create_action_item(self):
        """Quick create action item for this KPI"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'New Action Item for {self.name}',
            'res_model': 'kpi.action.item',
            'view_mode': 'form',
            'context': {
                'default_kpi_id': self.id,
                'default_title': f'Action item for {self.name}',
                'default_priority': 'medium',
            },
            'target': 'new',
        }
    
    def action_create_coaching_session(self):
        """Quick create coaching session for this KPI"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'New Coaching Session for {self.name}',
            'res_model': 'kpi.performance.coaching',
            'view_mode': 'form',
            'context': {
                'default_kpi_id': self.id,
                'default_title': f'Coaching session for {self.name}',
                'default_session_type': 'performance_improvement',
                'default_current_performance': self.achievement_percent,
            },
            'target': 'new',
        }
    
    def action_create_approval_workflow(self):
        """Quick create approval workflow for this KPI"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'New Approval Workflow for {self.name}',
            'res_model': 'kpi.approval.workflow',
            'view_mode': 'form',
            'context': {
                'default_kpi_id': self.id,
                'default_title': f'Approval workflow for {self.name}',
                'default_workflow_type': 'target_change',
            },
            'target': 'new',
        }
