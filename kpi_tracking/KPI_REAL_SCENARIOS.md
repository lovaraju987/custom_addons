# KPI Real-World Scenarios & Configuration Guide

## 📖 Overview

This document provides detailed, step-by-step configuration examples for real-world KPI scenarios. Each example includes all field values, conditions, formulas, and expected outcomes to help you understand how to set up effective KPIs in your organization.

---

## 🎯 Table of Contents

1. [Sales Department KPIs](#sales-department-kpis)
2. [HR Department KPIs](#hr-department-kpis)
3. [Operations Department KPIs](#operations-department-kpis)
4. [Marketing Department KPIs](#marketing-department-kpis)
5. [Finance Department KPIs](#finance-department-kpis)
6. [Customer Service KPIs](#customer-service-kpis)
7. [IT Department KPIs](#it-department-kpis)

---

## 📊 Sales Department KPIs

### 🎯 **Scenario 1: Monthly Sales Revenue Tracking**

**Business Goal**: Track total monthly sales revenue to ensure we meet our ₹10,00,000 target

#### **KPI Configuration**
```yaml
KPI Details:
  Name: "Monthly Sales Revenue"
  Department: Sales
  KPI Type: Auto
  Target Type: Currency (₹)
  Target Value: 1000000
  KPI Direction: Higher is Better
  Priority Weight: Very High (5)

Auto Tracking Configuration:
  Source Model: sale.order
  Filter Field: date_order
  Filter Type: this_month
  Count Field: (leave empty)
  
Source Domain: [('state', 'in', ['sale', 'done'])]
Formula: sum(record.amount_total for record in records)
```

#### **How It Works**
1. **System finds**: All sale orders from this month where state = 'sale' or 'done'
2. **count_a**: Total confirmed orders this month (e.g., 150 orders)
3. **count_b**: Not used (no count field specified)
4. **records**: The actual sale.order records
5. **Formula calculates**: Sum of amount_total from all confirmed orders
6. **Result**: ₹8,50,000 (if that's the total)
7. **Achievement**: (850000 / 1000000) × 100 = 85%

#### **Expected Outcome**
- **Target**: ₹10,00,000
- **Actual**: ₹8,50,000
- **Achievement**: 85%
- **Score**: Good (Green/Blue badge)

---

### 🎯 **Scenario 2: Lead Conversion Rate**

**Business Goal**: Track what percentage of leads convert to sales (target 25%)

#### **KPI Configuration**
```yaml
KPI Details:
  Name: "Monthly Lead Conversion Rate"
  Department: Sales
  KPI Type: Auto
  Target Type: Percentage
  Target Value: 25
  KPI Direction: Higher is Better
  Priority Weight: High (4)

Auto Tracking Configuration:
  Source Model: crm.lead
  Filter Field: create_date (selected from dropdown)
  Filter Type: this_month
  Count Field: is_won (selected from boolean fields dropdown)
  
Source Domain: [('active', '=', True)]
Formula: (count_b / count_a) * 100 if count_a > 0 else 0
```

#### **How It Works**
1. **System finds**: All active leads created this month
2. **count_a**: Total leads created this month (e.g., 120 leads)
3. **count_b**: Leads where is_won = True (e.g., 28 leads)
4. **Formula calculates**: (28 / 120) × 100 = 23.33%
5. **Achievement**: (23.33 / 25) × 100 = 93.33%

#### **Expected Outcome**
- **Target**: 25%
- **Actual**: 23.33%
- **Achievement**: 93.33%
- **Score**: Excellent (Green badge)

---

### 🎯 **Scenario 3: Average Deal Size**

**Business Goal**: Track average deal size to ensure quality deals (target ₹50,000)

#### **KPI Configuration**
```yaml
KPI Details:
  Name: "Average Deal Size"
  Department: Sales
  KPI Type: Auto
  Target Type: Currency (₹)
  Target Value: 50000
  KPI Direction: Higher is Better
  Priority Weight: Medium (3)

Auto Tracking Configuration:
  Source Model: sale.order
  Filter Field: date_order
  Filter Type: this_month
  Count Field: (leave empty)
  
Source Domain: [('state', 'in', ['sale', 'done']), ('amount_total', '>', 0)]
Formula: sum(record.amount_total for record in records) / len(records) if records else 0
```

#### **How It Works**
1. **System finds**: Confirmed orders this month with amount > 0
2. **count_a**: Total confirmed orders (e.g., 85 orders)
3. **records**: Actual sale.order records
4. **Formula calculates**: Total revenue ÷ number of orders
5. **Example**: ₹42,50,000 ÷ 85 = ₹50,000
6. **Achievement**: (50000 / 50000) × 100 = 100%

#### **Expected Outcome**
- **Target**: ₹50,000
- **Actual**: ₹50,000
- **Achievement**: 100%
- **Score**: Excellent (Green badge)

---

### 🎯 **Scenario 4: Sales Team Performance (Manual Entry)**

**Business Goal**: Track individual salesperson performance rating (1-10 scale)

#### **KPI Configuration**
```yaml
KPI Details:
  Name: "Weekly Sales Performance Rating"
  Department: Sales
  KPI Type: Manual
  Target Type: Number
  Target Value: 8
  KPI Direction: Higher is Better
  Priority Weight: High (4)
  Assigned Users: [John Doe, Jane Smith, Mike Wilson]

Manual Entry:
  Users submit their weekly performance rating
  Factors: Client meetings, follow-ups, deal closure, teamwork
```

#### **How It Works**
1. **Each assigned user** submits their weekly rating (1-10)
2. **Manager reviews** and approves/adjusts if needed
3. **System calculates** achievement percentage
4. **Example**: User submits 7.5, Target is 8
5. **Achievement**: (7.5 / 8) × 100 = 93.75%

#### **Expected Outcome**
- **Target**: 8.0
- **Actual**: 7.5
- **Achievement**: 93.75%
- **Score**: Excellent (Green badge)

---

## 👥 HR Department KPIs

### 🎯 **Scenario 5: Employee Retention Rate**

**Business Goal**: Track monthly employee retention (target 95%)

#### **KPI Configuration**
```yaml
KPI Details:
  Name: "Monthly Employee Retention Rate"
  Department: HR
  KPI Type: Auto
  Target Type: Percentage
  Target Value: 95
  KPI Direction: Higher is Better
  Priority Weight: Very High (5)

Auto Tracking Configuration:
  Source Model: hr.employee
  Filter Field: create_date (selected from dropdown)
  Filter Type: this_month
  Count Field: active (selected from boolean fields dropdown)
  
Source Domain: [('employee_type', '=', 'employee')]
Formula: (count_b / count_a) * 100 if count_a > 0 else 100
```

#### **How It Works**
1. **count_a**: All employees who were with company at start of month (e.g., 200)
2. **count_b**: Employees still active at month end (e.g., 192)
3. **Formula**: (192 / 200) × 100 = 96%
4. **Achievement**: (96 / 95) × 100 = 101.05% (capped at 100%)

#### **Expected Outcome**
- **Target**: 95%
- **Actual**: 96%
- **Achievement**: 100%
- **Score**: Excellent (Green badge)

---

### 🎯 **Scenario 6: Training Completion Rate**

**Business Goal**: Ensure 90% of employees complete mandatory training

#### **KPI Configuration**
```yaml
KPI Details:
  Name: "Monthly Training Completion Rate"
  Department: HR
  KPI Type: Auto
  Target Type: Percentage
  Target Value: 90
  KPI Direction: Higher is Better
  Priority Weight: High (4)

Auto Tracking Configuration:
  Source Model: hr.employee
  Filter Field: (not used for this calculation)
  Filter Type: (not applicable)
  Count Field: training_completed (selected from boolean fields dropdown)
  
Source Domain: [('active', '=', True), ('employee_type', '=', 'employee')]
Formula: (count_b / count_a) * 100 if count_a > 0 else 0
```

#### **How It Works**
1. **count_a**: All active employees (e.g., 150)
2. **count_b**: Employees with training_completed = True (e.g., 138)
3. **Formula**: (138 / 150) × 100 = 92%
4. **Achievement**: (92 / 90) × 100 = 102.22% (capped at 100%)

#### **Expected Outcome**
- **Target**: 90%
- **Actual**: 92%
- **Achievement**: 100%
- **Score**: Excellent (Green badge)

---

### 🎯 **Scenario 7: Average Recruitment Time**

**Business Goal**: Reduce time to fill positions to 30 days or less

#### **KPI Configuration**
```yaml
KPI Details:
  Name: "Average Recruitment Time (Days)"
  Department: HR
  KPI Type: Auto
  Target Type: Duration (days)
  Target Value: 30
  KPI Direction: Lower is Better
  Priority Weight: Medium (3)

Auto Tracking Configuration:
  Source Model: hr.job
  Filter Field: create_date
  Filter Type: this_month
  Count Field: (leave empty)
  
Source Domain: [('state', '=', 'recruit'), ('no_of_hired_employee', '>', 0)]
Formula: sum((record.hire_date - record.create_date).days for record in records if record.hire_date) / len([r for r in records if r.hire_date]) if [r for r in records if r.hire_date] else 0
```

#### **How It Works**
1. **System finds**: Job positions filled this month
2. **Formula calculates**: Average days between job posting and hire
3. **Example**: 5 positions filled in 25, 28, 35, 22, 30 days
4. **Average**: (25+28+35+22+30) ÷ 5 = 28 days
5. **Achievement**: (30 / 28) × 100 = 107.14% (capped at 100%)

#### **Expected Outcome**
- **Target**: 30 days
- **Actual**: 28 days
- **Achievement**: 100% (because lower is better and we beat target)
- **Score**: Excellent (Green badge)

---

## 🏭 Operations Department KPIs

### 🎯 **Scenario 8: Production Efficiency Rate**

**Business Goal**: Maintain 85% production efficiency

#### **KPI Configuration**
```yaml
KPI Details:
  Name: "Daily Production Efficiency"
  Department: Operations
  KPI Type: Auto
  Target Type: Percentage
  Target Value: 85
  KPI Direction: Higher is Better
  Priority Weight: Very High (5)

Auto Tracking Configuration:
  Source Model: mrp.production
  Filter Field: date_planned_start
  Filter Type: today
  Count Field: (leave empty)
  
Source Domain: [('state', 'in', ['done', 'progress'])]
Formula: (sum(record.qty_produced for record in records) / sum(record.product_qty for record in records)) * 100 if sum(record.product_qty for record in records) > 0 else 0
```

#### **How It Works**
1. **System finds**: Manufacturing orders started today
2. **Formula calculates**: (Total produced ÷ Total planned) × 100
3. **Example**: Produced 850 units, Planned 1000 units
4. **Efficiency**: (850 ÷ 1000) × 100 = 85%
5. **Achievement**: (85 / 85) × 100 = 100%

#### **Expected Outcome**
- **Target**: 85%
- **Actual**: 85%
- **Achievement**: 100%
- **Score**: Excellent (Green badge)

---

### 🎯 **Scenario 9: Quality Control Pass Rate**

**Business Goal**: Achieve 98% quality pass rate

#### **KPI Configuration**
```yaml
KPI Details:
  Name: "Daily Quality Pass Rate"
  Department: Operations
  KPI Type: Auto
  Target Type: Percentage
  Target Value: 98
  KPI Direction: Higher is Better
  Priority Weight: Very High (5)

Auto Tracking Configuration:
  Source Model: quality.check
  Filter Field: create_date
  Filter Type: today
  Count Field: quality_state_pass
  
Source Domain: [('quality_state', 'in', ['pass', 'fail'])]
Formula: (count_b / count_a) * 100 if count_a > 0 else 0
```

#### **How It Works**
1. **count_a**: Total quality checks performed today (e.g., 500)
2. **count_b**: Quality checks that passed (e.g., 492)
3. **Formula**: (492 ÷ 500) × 100 = 98.4%
4. **Achievement**: (98.4 / 98) × 100 = 100.41% (capped at 100%)

#### **Expected Outcome**
- **Target**: 98%
- **Actual**: 98.4%
- **Achievement**: 100%
- **Score**: Excellent (Green badge)

---

### 🎯 **Scenario 10: Equipment Downtime (Manual)**

**Business Goal**: Minimize equipment downtime (target: max 2 hours/day)

#### **KPI Configuration**
```yaml
KPI Details:
  Name: "Daily Equipment Downtime Hours"
  Department: Operations
  KPI Type: Manual
  Target Type: Duration (hours)
  Target Value: 2
  KPI Direction: Lower is Better
  Priority Weight: High (4)
  Assigned Users: [Production Manager, Maintenance Team Lead]

Manual Entry:
  Users report total downtime hours per day
  Include: Planned maintenance, unexpected breakdowns, setup time
  Exclude: Scheduled breaks, shift changes
```

#### **How It Works**
1. **Assigned users** log downtime incidents daily
2. **System calculates** total downtime hours
3. **Example**: 1.5 hours reported downtime
4. **Achievement**: (2 / 1.5) × 100 = 133.33% (capped at 100% since lower is better)

#### **Expected Outcome**
- **Target**: 2 hours (maximum)
- **Actual**: 1.5 hours
- **Achievement**: 100% (beat the target)
- **Score**: Excellent (Green badge)

---

## 📢 Marketing Department KPIs

### 🎯 **Scenario 11: Campaign ROI**

**Business Goal**: Achieve 300% ROI on marketing campaigns

#### **KPI Configuration**
```yaml
KPI Details:
  Name: "Monthly Campaign ROI"
  Department: Marketing
  KPI Type: Auto
  Target Type: Percentage
  Target Value: 300
  KPI Direction: Higher is Better
  Priority Weight: Very High (5)

Auto Tracking Configuration:
  Source Model: utm.campaign
  Filter Field: create_date
  Filter Type: this_month
  Count Field: (leave empty)
  
Source Domain: [('is_active', '=', True)]
Formula: ((sum(record.revenue_generated for record in records) - sum(record.cost for record in records)) / sum(record.cost for record in records)) * 100 if sum(record.cost for record in records) > 0 else 0
```

#### **How It Works**
1. **System finds**: Active campaigns created this month
2. **Formula**: ((Revenue - Cost) ÷ Cost) × 100
3. **Example**: Revenue ₹5,00,000, Cost ₹1,25,000
4. **ROI**: ((500000 - 125000) ÷ 125000) × 100 = 300%
5. **Achievement**: (300 / 300) × 100 = 100%

#### **Expected Outcome**
- **Target**: 300%
- **Actual**: 300%
- **Achievement**: 100%
- **Score**: Excellent (Green badge)

---

### 🎯 **Scenario 12: Website Traffic Growth**

**Business Goal**: Increase monthly website visitors by 15%

#### **KPI Configuration**
```yaml
KPI Details:
  Name: "Monthly Website Traffic Growth"
  Department: Marketing
  KPI Type: Manual
  Target Type: Percentage
  Target Value: 15
  KPI Direction: Higher is Better
  Priority Weight: Medium (3)
  Assigned Users: [Digital Marketing Manager, SEO Specialist]

Manual Entry:
  Compare current month visitors vs previous month
  Source: Google Analytics data
  Calculate: ((Current - Previous) / Previous) × 100
```

#### **How It Works**
1. **Users extract** data from Google Analytics
2. **Previous month**: 50,000 visitors
3. **Current month**: 58,000 visitors
4. **Growth**: ((58000 - 50000) ÷ 50000) × 100 = 16%
5. **Achievement**: (16 / 15) × 100 = 106.67% (capped at 100%)

#### **Expected Outcome**
- **Target**: 15%
- **Actual**: 16%
- **Achievement**: 100%
- **Score**: Excellent (Green badge)

---

### 🎯 **Scenario 13: Lead Generation Rate**

**Business Goal**: Generate 200 qualified leads per month

#### **KPI Configuration**
```yaml
KPI Details:
  Name: "Monthly Qualified Leads Generated"
  Department: Marketing
  KPI Type: Auto
  Target Type: Number
  Target Value: 200
  KPI Direction: Higher is Better
  Priority Weight: High (4)

Auto Tracking Configuration:
  Source Model: crm.lead
  Filter Field: create_date
  Filter Type: this_month
  Count Field: is_qualified
  
Source Domain: [('source_id.name', 'ilike', 'marketing')]
Formula: count_b
```

#### **How It Works**
1. **count_a**: All leads from marketing sources this month (e.g., 350)
2. **count_b**: Leads marked as qualified (e.g., 185)
3. **Formula**: count_b = 185 qualified leads
4. **Achievement**: (185 / 200) × 100 = 92.5%

#### **Expected Outcome**
- **Target**: 200 leads
- **Actual**: 185 leads
- **Achievement**: 92.5%
- **Score**: Good (Blue badge)

---

## 💰 Finance Department KPIs

### 🎯 **Scenario 14: Cash Flow Management**

**Business Goal**: Maintain positive cash flow (target: ₹5,00,000 minimum)

#### **KPI Configuration**
```yaml
KPI Details:
  Name: "Monthly Cash Flow"
  Department: Finance
  KPI Type: Auto
  Target Type: Currency (₹)
  Target Value: 500000
  KPI Direction: Higher is Better
  Priority Weight: Very High (5)

Auto Tracking Configuration:
  Source Model: account.move
  Filter Field: date
  Filter Type: this_month
  Count Field: (leave empty)
  
Source Domain: [('state', '=', 'posted'), ('move_type', 'in', ['in_invoice', 'out_invoice'])]
Formula: sum(record.amount_total if record.move_type == 'out_invoice' else -record.amount_total for record in records)
```

#### **How It Works**
1. **System finds**: Posted invoices (in and out) this month
2. **Formula**: Sum of outgoing invoices minus incoming invoices
3. **Example**: ₹12,00,000 received - ₹7,00,000 paid = ₹5,00,000
4. **Achievement**: (500000 / 500000) × 100 = 100%

#### **Expected Outcome**
- **Target**: ₹5,00,000
- **Actual**: ₹5,00,000
- **Achievement**: 100%
- **Score**: Excellent (Green badge)

---

### 🎯 **Scenario 15: Accounts Receivable Days**

**Business Goal**: Collect payments within 30 days average

#### **KPI Configuration**
```yaml
KPI Details:
  Name: "Average Collection Days"
  Department: Finance
  KPI Type: Auto
  Target Type: Duration (days)
  Target Value: 30
  KPI Direction: Lower is Better
  Priority Weight: High (4)

Auto Tracking Configuration:
  Source Model: account.move
  Filter Field: invoice_date
  Filter Type: this_month
  Count Field: (leave empty)
  
Source Domain: [('move_type', '=', 'out_invoice'), ('payment_state', '=', 'paid')]
Formula: sum((record.payment_date - record.invoice_date).days for record in records if record.payment_date and record.invoice_date) / len([r for r in records if r.payment_date and r.invoice_date]) if [r for r in records if r.payment_date and r.invoice_date] else 0
```

#### **How It Works**
1. **System finds**: Paid customer invoices from this month
2. **Formula**: Average days between invoice and payment dates
3. **Example**: 25 invoices paid in average 28 days
4. **Achievement**: (30 / 28) × 100 = 107.14% (capped at 100% since lower is better)

#### **Expected Outcome**
- **Target**: 30 days
- **Actual**: 28 days
- **Achievement**: 100%
- **Score**: Excellent (Green badge)

---

### 🎯 **Scenario 16: Budget Variance Control**

**Business Goal**: Keep spending within 5% of budget

#### **KPI Configuration**
```yaml
KPI Details:
  Name: "Monthly Budget Variance"
  Department: Finance
  KPI Type: Manual
  Target Type: Percentage
  Target Value: 5
  KPI Direction: Lower is Better
  Priority Weight: High (4)
  Assigned Users: [CFO, Finance Manager, Budget Controller]

Manual Entry:
  Calculate: |Actual Spending - Budget| / Budget × 100
  Review: Monthly budget vs actual analysis
  Source: Financial reports and budget tracking sheets
```

#### **How It Works**
1. **Users analyze** monthly budget vs actual spending
2. **Budget**: ₹10,00,000, **Actual**: ₹10,30,000
3. **Variance**: |1030000 - 1000000| ÷ 1000000 × 100 = 3%
4. **Achievement**: (5 / 3) × 100 = 166.67% (capped at 100% since lower is better)

#### **Expected Outcome**
- **Target**: 5% (maximum variance)
- **Actual**: 3%
- **Achievement**: 100%
- **Score**: Excellent (Green badge)

---

## 📞 Customer Service KPIs

### 🎯 **Scenario 17: First Call Resolution Rate**

**Business Goal**: Resolve 80% of issues on first contact

#### **KPI Configuration**
```yaml
KPI Details:
  Name: "Daily First Call Resolution Rate"
  Department: Customer Service
  KPI Type: Auto
  Target Type: Percentage
  Target Value: 80
  KPI Direction: Higher is Better
  Priority Weight: Very High (5)

Auto Tracking Configuration:
  Source Model: helpdesk.ticket
  Filter Field: create_date
  Filter Type: today
  Count Field: first_call_resolved
  
Source Domain: [('stage_id.is_close', '=', True)]
Formula: (count_b / count_a) * 100 if count_a > 0 else 0
```

#### **How It Works**
1. **count_a**: All closed tickets created today (e.g., 50)
2. **count_b**: Tickets resolved on first contact (e.g., 42)
3. **Formula**: (42 ÷ 50) × 100 = 84%
4. **Achievement**: (84 / 80) × 100 = 105% (capped at 100%)

#### **Expected Outcome**
- **Target**: 80%
- **Actual**: 84%
- **Achievement**: 100%
- **Score**: Excellent (Green badge)

---

### 🎯 **Scenario 18: Customer Satisfaction Score**

**Business Goal**: Maintain customer satisfaction above 4.5/5

#### **KPI Configuration**
```yaml
KPI Details:
  Name: "Weekly Customer Satisfaction Score"
  Department: Customer Service
  KPI Type: Manual
  Target Type: Number
  Target Value: 4.5
  KPI Direction: Higher is Better
  Priority Weight: Very High (5)
  Assigned Users: [Customer Service Manager, Team Leaders]

Manual Entry:
  Source: Customer feedback surveys, rating systems
  Calculate: Average rating from all customer feedback
  Scale: 1-5 (1=Very Dissatisfied, 5=Very Satisfied)
```

#### **How It Works**
1. **Users collect** customer feedback weekly
2. **Example ratings**: 4.2, 4.8, 4.6, 4.3, 4.7, 4.5, 4.4
3. **Average**: (4.2+4.8+4.6+4.3+4.7+4.5+4.4) ÷ 7 = 4.5
4. **Achievement**: (4.5 / 4.5) × 100 = 100%

#### **Expected Outcome**
- **Target**: 4.5/5
- **Actual**: 4.5/5
- **Achievement**: 100%
- **Score**: Excellent (Green badge)

---

## 💻 IT Department KPIs

### 🎯 **Scenario 19: System Uptime**

**Business Goal**: Maintain 99.5% system uptime

#### **KPI Configuration**
```yaml
KPI Details:
  Name: "Daily System Uptime Percentage"
  Department: IT
  KPI Type: Manual
  Target Type: Percentage
  Target Value: 99.5
  KPI Direction: Higher is Better
  Priority Weight: Very High (5)
  Assigned Users: [IT Manager, System Administrator, Network Admin]

Manual Entry:
  Source: Server monitoring tools, uptime reports
  Calculate: (Total time - Downtime) / Total time × 100
  Period: 24 hours (1440 minutes)
```

#### **How It Works**
1. **Monitor systems** for 24-hour periods
2. **Total time**: 1440 minutes
3. **Downtime**: 5 minutes (server maintenance)
4. **Uptime**: (1440 - 5) ÷ 1440 × 100 = 99.65%
5. **Achievement**: (99.65 / 99.5) × 100 = 100.15% (capped at 100%)

#### **Expected Outcome**
- **Target**: 99.5%
- **Actual**: 99.65%
- **Achievement**: 100%
- **Score**: Excellent (Green badge)

---

### 🎯 **Scenario 20: Average Ticket Resolution Time**

**Business Goal**: Resolve IT tickets within 4 hours average

#### **KPI Configuration**
```yaml
KPI Details:
  Name: "Daily Average Ticket Resolution Time"
  Department: IT
  KPI Type: Auto
  Target Type: Duration (hours)
  Target Value: 4
  KPI Direction: Lower is Better
  Priority Weight: High (4)

Auto Tracking Configuration:
  Source Model: helpdesk.ticket
  Filter Field: create_date
  Filter Type: today
  Count Field: (leave empty)
  
Source Domain: [('stage_id.is_close', '=', True), ('team_id.name', '=', 'IT Support')]
Formula: sum((record.close_date - record.create_date).total_seconds() / 3600 for record in records if record.close_date and record.create_date) / len([r for r in records if r.close_date and r.create_date]) if [r for r in records if r.close_date and r.create_date] else 0
```

#### **How It Works**
1. **System finds**: IT tickets closed today
2. **Formula**: Average hours between creation and closure
3. **Example**: 8 tickets resolved in 2, 3, 5, 4, 3.5, 4.5, 2.5, 3 hours
4. **Average**: (2+3+5+4+3.5+4.5+2.5+3) ÷ 8 = 3.4 hours
5. **Achievement**: (4 / 3.4) × 100 = 117.65% (capped at 100% since lower is better)

#### **Expected Outcome**
- **Target**: 4 hours
- **Actual**: 3.4 hours
- **Achievement**: 100%
- **Score**: Excellent (Green badge)

---

### **Count Field Selection Guide**

#### **What is Count Field?**
The **Count Field** is an optional boolean field that determines what gets counted for `count_b` calculations. 

#### **How to Select Count Field**
1. **Choose Source Model** first (e.g., crm.lead, sale.order)
2. **Count Field dropdown** will show all boolean fields from that model
3. **Select the boolean field** that determines your success criteria
4. **count_b** will count records where this field = True

#### **Common Boolean Fields by Model**
- **crm.lead**: `is_won`, `active`, `is_qualified`
- **sale.order**: `is_confirmed`, `is_delivered`, `is_paid`
- **hr.employee**: `active`, `training_completed`, `performance_review_done`
- **project.task**: `is_closed`, `is_approved`, `is_milestone`
- **helpdesk.ticket**: `is_closed`, `first_call_resolved`, `customer_satisfied`

#### **When to Use Count Field**
- ✅ **Use when**: You need percentage calculations (conversion rates, success rates)
- ✅ **Use when**: You want to count specific conditions (won leads, completed tasks)
- ❌ **Don't use when**: You only need total counts (use `count_a` in formula)
- ❌ **Don't use when**: You're doing sum/average calculations (use `records` in formula)

#### **Count Field Examples**

**Lead Conversion Rate:**
- **Source Model**: crm.lead
- **Count Field**: is_won (boolean)
- **Result**: count_a = total leads, count_b = won leads
- **Formula**: `(count_b / count_a) * 100`

**Order Fulfillment Rate:**
- **Source Model**: sale.order  
- **Count Field**: is_delivered (boolean)
- **Result**: count_a = total orders, count_b = delivered orders
- **Formula**: `(count_b / count_a) * 100`

**No Count Field Needed:**
- **Source Model**: sale.order
- **Count Field**: (leave empty)
- **Result**: count_a = total orders, count_b = 0 (not used)
- **Formula**: `sum(record.amount_total for record in records)`

---

## 🔧 Advanced Configuration Tips

### **Common Field Explanations**

#### **Target Type Selection Guide**
- **Number**: Raw counts, quantities, ratings (e.g., 100 calls, 5 products)
- **Percentage**: Ratios, rates, efficiencies (e.g., 95% uptime, 25% growth)
- **Currency**: Monetary values (e.g., ₹1,00,000 revenue, $5,000 savings)
- **Boolean**: Yes/No achievements (e.g., certification completed, goal met)
- **Duration**: Time measurements (e.g., 2 hours, 30 days, 15 minutes)

#### **KPI Direction Impact**
- **Higher is Better**: Revenue, satisfaction, efficiency, quality scores
- **Lower is Better**: Costs, defects, response times, downtime

#### **Priority Weight Strategy**
- **Very High (5)**: Critical business metrics (revenue, safety, compliance)
- **High (4)**: Important operational metrics (quality, efficiency)
- **Medium (3)**: Supporting metrics (process improvements)
- **Low (2)**: Nice-to-have metrics (secondary indicators)
- **Very Low (1)**: Experimental or tracking-only metrics

### **Formula Best Practices**

#### **Safety Checks Always Include**
```python
# Prevent division by zero
(count_b / count_a) * 100 if count_a > 0 else 0

# Handle empty record sets
sum(record.amount for record in records) if records else 0

# Filter out invalid data
sum(record.amount for record in records if record.amount > 0)
```

#### **Common Formula Patterns**
```python
# Percentage calculation
(count_b / count_a) * 100 if count_a > 0 else 0

# Simple count
count_a

# Sum calculation
sum(record.field_name for record in records)

# Average calculation
sum(record.field_name for record in records) / len(records) if records else 0

# Conditional sum
sum(record.amount for record in records if record.state == 'confirmed')

# Time difference (days)
sum((record.end_date - record.start_date).days for record in records if record.end_date and record.start_date) / len([r for r in records if r.end_date and r.start_date]) if [r for r in records if r.end_date and r.start_date] else 0
```

---

## 📈 Expected Results & Interpretations

### **Achievement Percentage Meanings**
- **100%+**: Target exceeded (Excellent - Green)
- **90-99%**: Close to target (Good - Blue)
- **70-89%**: Moderate performance (Average - Orange)
- **50-69%**: Below expectations (Needs Improvement - Yellow)
- **<50%**: Significant underperformance (Critical - Red)

### **Troubleshooting Common Issues**

#### **Zero Values**
- Check if source model has data for the period
- Verify domain filters aren't too restrictive
- Ensure count field exists and has correct values

#### **Unexpected Results**
- Use "Test Domain" button to verify record counts
- Check date fields and filter types
- Verify formula syntax with simple test cases

#### **Performance Issues**
- Limit date ranges to specific periods
- Use efficient domain filters
- Avoid complex nested calculations

---

## 📞 Support & Next Steps

For additional scenarios or custom KPI configurations:
1. Review your business processes
2. Identify measurable outcomes
3. Map to appropriate Odoo models
4. Test with sample data
5. Deploy gradually with user training

**Contact**: info@oneto7solutions.in for professional KPI consulting and setup services.
