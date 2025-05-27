from odoo import models, fields, api
from datetime import timedelta, date
from odoo.exceptions import ValidationError
import calendar


class TechnicianShiftWeek(models.Model):
    _name = 'technician.shift.week'
    _description = 'Technician Weekly Roster'

    name = fields.Char(string="Week", compute="_compute_name", store=True)
    month = fields.Selection(
        [(str(i), calendar.month_name[i]) for i in range(1, 13)],
        string="Month"
    )
    year = fields.Integer(string="Year")
    week_start = fields.Date(string="Week Start")
    week_end = fields.Date(string="Week End")
    work_location_id = fields.Many2one('hr.work.location', string="Work Location")
    manager_id = fields.Many2one('hr.employee', string="Manager")
    technician_ids = fields.Many2many('hr.employee', string="Technicians")
    shift_ids = fields.One2many('technician.shift', 'week_id', string="Shifts")



    state = fields.Selection([
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed')
    ], string="Roster State", default='draft')

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'




    roster_status = fields.Selection(
    [('expired', 'Expired'), ('active', 'Active'), ('future', 'Future')],
    string='Status',
    compute='_compute_roster_status',
    store=True
    )

    @api.depends('week_start', 'week_end')
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.week_start} - {rec.week_end}" if rec.week_start and rec.week_end else ""

    @api.depends('week_start', 'week_end')
    def _compute_roster_status(self):
        today = date.today()
        for rec in self:
            if rec.week_end and rec.week_end < today:
                rec.roster_status = 'expired'
            elif rec.week_start and rec.week_start > today:
                rec.roster_status = 'future'
            else:
                rec.roster_status = 'active'


    @api.model
    def _update_roster_statuses_cron(self):
        today = fields.Date.today()
        rosters = self.search([])
        for rec in rosters:
            if rec.week_end and rec.week_end < today:
                rec.roster_status = 'expired'
            elif rec.week_start and rec.week_start > today:
                rec.roster_status = 'future'
            else:
                rec.roster_status = 'active'

 
    @api.onchange('week_start')
    def _onchange_week_start(self):
        for rec in self:
            if rec.week_start:
                rec.week_end = rec.week_start + timedelta(days=6)
                rec.month = str(rec.week_start.month)
                rec.year = rec.week_start.year
    
    @api.onchange('work_location_id')
    def _onchange_work_location_id(self):
        if self.work_location_id:
            self.technician_ids = self.work_location_id.default_technician_ids
            self.manager_id = self.work_location_id.default_manager_id





    @api.model
    def create(self, vals):
        if vals.get('week_start'):
            date_start = fields.Date.from_string(vals['week_start'])
            vals['month'] = str(date_start.month)
            vals['year'] = date_start.year
        record = super().create(vals)
        if record.week_start and record.week_end and record.technician_ids:
            record._generate_shifts()
        return record

    def write(self, vals):
        res = super().write(vals)
        if 'week_start' in vals:
            for rec in self:
                if rec.week_start:
                    rec.month = str(rec.week_start.month)
                    rec.year = rec.week_start.year
        if 'technician_ids' in vals or 'week_start' in vals or 'week_end' in vals:
            self._generate_shifts()
        return res
    

    def unlink(self):
        for rec in self:
            if rec.state == 'confirmed':
                raise ValidationError("You cannot delete a confirmed roster.")
        return super().unlink()

    

    @api.constrains('work_location_id', 'week_start', 'week_end')
    def _check_duplicate_roster(self):
        for rec in self:
            if not rec.work_location_id or not rec.week_start or not rec.week_end:
                continue
            overlapping = self.search([
                ('id', '!=', rec.id),
                ('work_location_id', '=', rec.work_location_id.id),
                ('week_start', '<=', rec.week_end),
                ('week_end', '>=', rec.week_start),
            ])
            if overlapping:
                raise ValidationError("A roster already exists for this Work Location in the given week.")

    def _generate_shifts(self):
        for record in self:
            if not record.week_start or not record.week_end or not record.technician_ids:
                continue
            self.env['technician.shift'].search([('week_id', '=', record.id)]).unlink()
            date = record.week_start
            while date <= record.week_end:
                for tech in record.technician_ids:
                    if tech.id:
                        self.env['technician.shift'].create({
                            'week_id': record.id,
                            'date': date,
                            'technician_id': tech.id,
                            # 'status': 'P'
                        })
                date += timedelta(days=1)


class TechnicianShift(models.Model):
    _name = 'technician.shift'
    _description = 'Technician Daily Shift'

    week_id = fields.Many2one('technician.shift.week', string="Week")
    date = fields.Date(string="Date")
    technician_id = fields.Many2one('hr.employee', string="Technician")

    state = fields.Selection([
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed')
    ], string="Roster State", related="week_id.state", store=True)

    # Updated Field
    status = fields.Selection([
        ('P', 'P'),
        ('A', 'A'),
        ('onduty', 'On Duty')  # Newly added
    ], string='Status',)
    slot_ids = fields.Many2many(
        'technician.shift.slot',
        'technician_shift_slot_rel',
        'shift_id', 'slot_id',
        string="Wasted Slots"
    )
    reason = fields.Text(string="Reason")

    working_type = fields.Selection([
    ('working', 'Working Day'),
    ('off', 'Off Day')
    ], string="Work Type", default='working')




class TechnicianShiftSlot(models.Model):
    _name = 'technician.shift.slot'
    _description = 'Shift Slot Option'

    name = fields.Char(string="Slot Name", required=True)