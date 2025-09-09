# KPI Tracking & Performance Management System

## 🔍 Overview

The **KPI Tracking & Performance Management** module is a comprehensive, enterprise-grade solution for Odoo 18 that enables organizations to define, monitor, and evaluate Key Performance Indicators (KPIs) across all departments. Built with advanced formula calculation engine, automated data processing, and intelligent performance analytics.

**Version**: 17.1.3 | **Odoo Compatibility**: 18.0+ | **License**: OPL-1

---

## ✨ Key Features & Capabilities

### � **Advanced KPI Management**
- **Dual Mode Operations**: 
  - **Manual KPIs**: User-submitted values with validation workflows
  - **Automatic KPIs**: Real-time calculations from any Odoo model data
- **Comprehensive Target Types**: 
  - Number values with precision control
  - Percentage calculations with decimal accuracy
  - Currency amounts (₹ Rupees) with formatting
  - Boolean achievements (Yes/No, Pass/Fail)
  - Duration tracking (Hours, Days)
- **Smart Performance Direction**: Configurable higher-is-better or lower-is-better logic
- **Enhanced Formula Engine**: Secure Python evaluation with 15+ built-in functions

### 🏢 **Department & Organization Structure**
- **Multi-Department Support**: Sales, HR, Operations, Marketing, Finance, R&D, IT, Admin, Store, Technician
- **Hierarchical Report Groups**: Logical KPI clustering with department inheritance
- **Flexible User Assignment**: Multi-user KPIs with role-based access
- **Performance Aggregation**: Automatic group-level performance calculation

### 🎯 **Intelligent Performance Tracking**
- **Real-time Achievement Calculation**: Dynamic target vs actual percentage
- **5-Level Color Coding**: 
  - 🟢 **Excellent** (95%+): Green
  - 🔵 **Good** (80-94%): Blue  
  - 🟠 **Average** (70-79%): Orange
  - 🟡 **Needs Improvement** (50-69%): Yellow
  - 🔴 **Underperformance** (<50%): Dark Red
- **Progress Visualization**: Interactive progress bars with tooltips
- **Historical Tracking**: Complete audit trail with submission timestamps
- **Performance Trends**: Time-series analysis and pattern recognition

### 🔔 **Advanced Automation & Notifications**
- **Intelligent CRON Jobs**: 
  - Scheduled automatic KPI updates with error handling
  - Smart batch processing for large datasets
  - Memory-optimized calculations
- **Professional Email System**: 
  - Automated reminders for manual KPI submissions
  - Customizable email templates
  - Bulk notification capabilities
- **Real-time Updates**: Live dashboard refreshing
- **Error Recovery**: Automatic retry mechanisms for failed calculations

### 🔒 **Enterprise Security & Access Control**
- **Three-Tier Security Model**:
  - **KPI Admin**: Full system control (Create, Read, Write, Delete all)
  - **KPI Manager**: Department management (Create, Read, Write department KPIs)
  - **KPI User**: Submission access (Read assigned KPIs, Submit values)
- **Advanced Security Features**:
  - Record-level access rules with user context
  - Formula security validation against code injection
  - Input sanitization and data validation
  - Comprehensive audit logging

### 🎨 **Enhanced User Interface**
- **Modern Dashboard Design**: Clean, intuitive interface with contextual help
- **Enhanced Field Selection**: All model fields available in dropdowns (not just date/datetime)
- **Visual Domain Builder**: No-code filter creation interface
- **Smart Field Migration**: Automatic upgrade handling for field references
- **Responsive Design**: Mobile-friendly interface
- **Contextual Help**: Inline guidance and tooltips

---

## 🛠 Technical Architecture

### **Core Data Models**

| Model | Purpose | Key Features |
|-------|---------|--------------|
| `kpi.report` | Main KPI definition | Formula engine, security validation, auto-calculation |
| `kpi.report.group` | Department organization | Group-level aggregation, user management |
| `kpi.report.submission` | Individual submissions | Audit trail, historical tracking |
| `kpi.report.group.submission` | Group performance history | Department-level analytics |

### **Advanced Formula Calculation Engine**

#### **Supported Built-in Functions**
```python
# Mathematical Functions
len, sum, max, min, abs, round

# Type Conversion
int, float, str, bool

# Data Structures  
list, dict, range, enumerate

# Logical Operations
any, all, sorted, reversed
```

#### **Available Variables**
```python
count_a         # Total records matching time filter
count_b         # Records matching time + domain filters  
records         # Actual record objects for complex calculations
assigned_user   # Current user context
today          # Current date reference
```

#### **Real-world Formula Examples**
```python
# Sales Revenue Calculation
sum(r.amount_total for r in records if r.state == 'sale')

# Lead Conversion Rate
(count_b / count_a) * 100 if count_a > 0 else 0

# Average Deal Size
sum(r.amount_total for r in records) / len(records) if records else 0

# Employee Productivity Score
sum(r.hours_worked for r in records) / 8 * 100

# Quality Score (Lower is Better)
sum(r.defect_count for r in records)

# Complex Conditional Logic
sum(r.amount_total * r.margin_percent / 100 for r in records if r.priority == 'high')
```

---

## 🔐 Security & Compliance

### **Security Groups Configuration**

| Group | Internal Name | Permissions | Use Case |
|-------|---------------|-------------|----------|
| **KPI Admin** | `group_kpi_admin` | Full CRUD access to all KPIs and groups | System administrators, IT team |
| **KPI Manager** | `group_kpi_manager` | Create, edit department KPIs | Department heads, team leaders |
| **KPI User** | `group_kpi_user` | Submit values for assigned KPIs | Employees, individual contributors |

### **Advanced Security Rules**
```xml
<!-- Record-level security example -->
<record id="kpi_report_rule_user" model="ir.rule">
    <field name="name">KPI User Access Rule</field>
    <field name="model_id" ref="model_kpi_report"/>
    <field name="domain_force">[('assigned_user_ids', 'in', user.id)]</field>
    <field name="groups" eval="[(4, ref('group_kpi_user'))]"/>
</record>
```

### **Formula Security Validation**
- **Blocked Keywords**: `import`, `exec`, `eval`, `__`, `open`, `file`, `compile`, `globals`
- **Safe Execution Environment**: Restricted `__builtins__` with only approved functions
- **Input Sanitization**: Automatic cleaning of formula inputs
- **Error Handling**: Graceful degradation with detailed logging

---

## ⚙️ Configuration & Setup

### **Installation Guide**

#### **Prerequisites**
- Odoo 18.0 or later
- Python 3.8+
- Dependencies: `base`, `hr`, `web`, `mail`

#### **Step-by-Step Installation**
1. **Download & Extract**: Place module in Odoo addons directory
2. **Update Apps List**: Restart Odoo server and update apps
3. **Install Module**: Search "KPI Tracking" and install
4. **Configure Security**: Assign users to appropriate groups
5. **Initial Setup**: Create first report group and KPI

### **Security Group Assignment**
```python
# Navigate to Settings > Users & Companies > Users
# Edit each user and add to appropriate groups:

# For System Administrators
Groups: Administration / Access Rights + KPI Admin

# For Department Managers  
Groups: KPI Manager

# For Regular Employees
Groups: KPI User
```

---

## 🚀 Quick Start Guide

### **Creating Your First Manual KPI**

#### **1. Create Report Group**
```
Navigate: KPI Tracking > KPI Groups > Create
Name: "Sales Team Monthly Performance"
Department: Sales
Description: "Track monthly sales targets and achievements"
Assigned Users: [Select sales team members]
```

#### **2. Create Manual KPI**
```
Navigate: KPI Tracking > KPI Reports > Create
KPI Name: "Monthly Sales Revenue"
Report: Sales Team Monthly Performance
KPI Type: Manual
Target Type: Currency
Target Value: 500000 (₹5,00,000)
KPI Direction: Higher is Better
Priority: High
Assigned Users: [Select sales representatives]
```

#### **3. Submit Values**
```
Navigate: KPI Tracking > My KPIs
Click: "Monthly Sales Revenue"
Enter: Manual Input Value (e.g., 450000)
Add: Note (optional)
Click: Manual Refresh
```

### **Creating Your First Automatic KPI**

#### **1. Sales Order Count Example**
```
KPI Name: "Monthly Sales Orders"
KPI Type: Auto
Source Model: Sale Order
Filter Field: Order Date (sale.order)
Filter Type: This Month
Source Domain: [('state', '=', 'sale')] (use domain builder)
Formula: count_a
Target: 100
```

#### **2. Revenue Calculation Example**
```
KPI Name: "Monthly Revenue"
KPI Type: Auto  
Source Model: Sale Order
Filter Field: Order Date (sale.order)
Filter Type: This Month
Source Domain: [('state', 'in', ['sale', 'done'])]
Formula: sum(r.amount_total for r in records)
Target: 1000000
```

#### **3. Lead Conversion Rate Example**
```
KPI Name: "Lead Conversion Rate"
KPI Type: Auto
Source Model: CRM Lead
Filter Field: Create Date (crm.lead)
Filter Type: This Month
Source Domain: [('stage_id.is_won', '=', True)]
Formula: (count_b / count_a) * 100 if count_a > 0 else 0
Target: 25 (%)
```

---

## 📊 Advanced Features

### **Enhanced Filter Field Selection**
- **All Fields Available**: No restriction to date/datetime fields only
- **Smart Field Detection**: Automatic field type recognition
- **Contextual Warnings**: Guidance for non-date fields in time filters
- **Field Migration**: Automatic upgrade handling for field references

### **Visual Domain Builder** 
```
Access: KPI Form > Source Domain field
Features:
- Drag-and-drop filter conditions
- Real-time field suggestions
- Operator auto-completion
- Syntax validation
- Visual AND/OR logic grouping
```

### **Intelligent Error Handling**
```python
# Example error recovery in scheduled_update_kpis
try:
    final_value = eval(rec.formula_field, safe_globals, local_vars)
except Exception as e:
    _logger.error(f"Formula error in KPI {rec.name}: {e}")
    rec.formula_notes = f"Error: {e}"
    final_value = 0.0  # Graceful fallback
```

### **Performance Optimization**
- **Batch Processing**: Efficient handling of multiple KPIs
- **Memory Management**: Optimized record searches
- **Smart Caching**: Reduced database queries
- **Error Logging**: Comprehensive debugging information

---

## 📧 Email & Notification System

### **Automated Email Reminders**
```xml
<!-- CRON Job Configuration -->
<record id="ir_cron_kpi_reminder" model="ir.cron">
    <field name="name">Send KPI Manual Entry Reminders</field>
    <field name="model_id" ref="model_kpi_report"/>
    <field name="state">code</field>
    <field name="code">model.send_manual_kpi_reminders()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="active" eval="True"/>
</record>
```

### **Email Template Features**
- **Professional Design**: Corporate-friendly email format
- **Dynamic Content**: KPI-specific information injection
- **Multi-language Support**: Template translation capability
- **Bulk Operations**: Send to multiple users simultaneously

---

## 🎯 Department-Specific Templates

### **Sales Department KPIs**
```python
# Monthly Revenue
Formula: sum(r.amount_total for r in records)
Domain: [('state', '=', 'sale')]

# Lead Conversion Rate  
Formula: (count_b / count_a) * 100
Domain: [('stage_id.is_won', '=', True)]

# Average Deal Size
Formula: sum(r.amount_total for r in records) / len(records) if records else 0
Domain: [('state', '=', 'sale')]

# Sales Cycle Time
Formula: sum((r.date_closed - r.create_date).days for r in records if r.date_closed) / count_b if count_b else 0
Domain: [('date_closed', '!=', False)]
```

### **HR Department KPIs**
```python
# Employee Retention Rate
Formula: (count_a - count_b) / count_a * 100 if count_a else 0
Domain: [('active', '=', False)]  # count_b = departures

# Training Completion Rate
Formula: count_b / count_a * 100 if count_a else 0
Domain: [('training_completed', '=', True)]

# Recruitment Time (Days)
Formula: sum((r.hire_date - r.application_date).days for r in records if r.hire_date) / count_b if count_b else 0
Domain: [('hire_date', '!=', False)]
```

### **Operations Department KPIs**
```python
# Process Efficiency Rate
Formula: count_b / count_a * 100 if count_a else 0
Domain: [('status', '=', 'completed_on_time')]

# Cost Reduction
Formula: sum(r.cost_saved for r in records)
Domain: [('cost_saved', '>', 0)]

# Quality Score (Defect Rate)
Formula: count_b / count_a * 100 if count_a else 0
Domain: [('has_defects', '=', True)]
```

---

## 📱 User Interface & Experience

### **Dashboard Views**

#### **Enhanced List View**
- **Progress Bars**: Visual achievement representation
- **Color-coded Badges**: Performance level indicators
- **Smart Filtering**: Department, status, achievement level
- **Bulk Actions**: Mass updates and notifications
- **Export Options**: Excel, PDF, CSV formats

#### **Advanced Form View**
- **Tabbed Interface**: Organized information sections
- **Real-time Validation**: Instant formula and domain testing
- **Historical Charts**: Performance trend visualization
- **Submission Timeline**: Chronological submission history
- **Smart Suggestions**: Context-aware field recommendations

#### **Interactive Graph View**
- **Multiple Chart Types**: Line, Bar, Pie, Gauge
- **Time-series Analysis**: Trend identification
- **Comparative Analysis**: Multi-KPI performance
- **Drill-down Capability**: Detailed record exploration

### **Mobile-Responsive Design**
- **Touch-friendly Interface**: Optimized for tablets and phones
- **Simplified Navigation**: Mobile-specific menu structure
- **Offline Capability**: Local data caching
- **Push Notifications**: Mobile alerts for KPI deadlines

---

## 🔄 Automation & CRON Jobs

### **Scheduled KPI Updates**
```python
@api.model
def scheduled_update_kpis(self):
    """Enhanced auto-update with comprehensive error handling"""
    
    # Features:
    # - Batch processing of multiple KPIs
    # - Memory-optimized record searches  
    # - Graceful error handling and recovery
    # - Detailed logging and debugging
    # - Performance monitoring
    # - Automatic retry mechanisms
```

### **Performance Monitoring**
```python
# CRON job returns detailed execution statistics
{
    'success_count': 45,      # Successfully updated KPIs
    'error_count': 2,         # Failed KPI updates  
    'errors': [               # Detailed error messages
        'KPI Lead Rate: Domain evaluation failed',
        'KPI Revenue: Model access denied'
    ],
    'execution_time': 12.5,   # Seconds
    'memory_usage': 156       # MB
}
```

---

## 🛡️ Data Migration & Upgrades

### **Automatic Field Migration**
```python
def _try_fix_filter_and_count_fields(self):
    """Automatically migrate field references during upgrades"""
    
    # Features:
    # - Automatic detection of field reference issues
    # - Smart field name matching and correction
    # - Graceful handling of missing fields
    # - Comprehensive logging of migration actions
    # - Zero-downtime migration process
```

### **Backward Compatibility**
- **Legacy Support**: Maintains compatibility with older configurations
- **Gradual Migration**: Step-by-step upgrade process
- **Rollback Capability**: Safe downgrade options
- **Data Preservation**: Complete history retention

---

## 📋 Troubleshooting & Support

### **Common Issues & Solutions**

#### **Formula Calculation Errors**
```python
# Problem: "name 'len' is not defined"
# Solution: Enhanced safe_globals with all required functions

safe_globals = {
    "__builtins__": {
        'len': len, 'sum': sum, 'max': max, 'min': min, 'abs': abs,
        'round': round, 'int': int, 'float': float, 'str': str,
        'bool': bool, 'list': list, 'dict': dict, 'range': range,
        'enumerate': enumerate, 'sorted': sorted, 'reversed': reversed,
        'any': any, 'all': all
    }
}
```

#### **Performance Optimization**
```python
# Problem: Slow KPI calculations
# Solutions:
1. Use specific domain filters to limit record searches
2. Optimize formulas for efficiency
3. Consider database indexing on filter fields
4. Use batch processing for large datasets
5. Monitor CRON job execution times
```

#### **Access Control Issues**
```python
# Problem: Users cannot see assigned KPIs
# Solutions:
1. Verify user group assignments
2. Check record-level security rules
3. Ensure proper KPI user assignments
4. Review department-based access controls
```

### **Debug Mode Features**
```python
# Enhanced debugging for slot_ids formulas
if 'slot_ids' in rec.formula_field and final_value == 0:
    debug_info = []
    for i, record in enumerate(filtered_records[:3]):
        try:
            slot_count = len(getattr(record, 'slot_ids', []))
            debug_info.append(f"Record {i+1}: {slot_count} slots")
        except Exception as e:
            debug_info.append(f"Record {i+1}: Error - {e}")
    
    rec.formula_notes = f"Debug: {'; '.join(debug_info)}. Total: {len(filtered_records)}"
```

---

## 📈 Performance Analytics

### **Built-in Reporting**
- **Executive Dashboard**: High-level performance overview
- **Department Scorecards**: Team-specific performance metrics
- **Trend Analysis**: Historical performance patterns
- **Comparative Reports**: Cross-department analysis
- **Exception Reports**: Underperforming KPIs identification

### **Export & Integration**
- **Excel Export**: Detailed performance data
- **PDF Reports**: Professional formatted reports
- **API Access**: Integration with external systems
- **Data Warehouse**: ETL capabilities for business intelligence

---

## 🔮 Roadmap & Future Enhancements

### **Version 17.2.0 - Advanced Analytics**
- **Predictive Analytics**: ML-based performance forecasting
- **Benchmark Analysis**: Industry standard comparisons
- **What-if Scenarios**: Performance modeling
- **Advanced Visualization**: Interactive charts and dashboards

### **Version 17.3.0 - Collaboration Features**
- **Team Collaboration**: Shared KPI workspaces
- **Comment System**: KPI-specific discussions
- **Approval Workflows**: Multi-level KPI validation
- **Social Features**: Performance sharing and recognition

### **Version 17.4.0 - Integration Expansion**
- **Third-party Integrations**: Salesforce, HubSpot, etc.
- **API Enhancements**: RESTful API for external access
- **Mobile App**: Native mobile application
- **AI Assistant**: Natural language KPI query processing

---

## 📄 Commercial Information

### **Pricing & Licensing**
- **Price**: $29 USD (one-time purchase)
- **License**: OPL-1 (Odoo Proprietary License)
- **Support**: 12 months included
- **Updates**: Free minor version updates

### **Enterprise Features**
- **Advanced Security**: Enterprise-grade access controls
- **Performance Optimization**: High-volume data processing
- **Custom Integrations**: Tailored connector development
- **Professional Services**: Implementation and training

### **Contact Information**
- **Developer**: OneTo7 Solutions
- **Email**: info@oneto7solutions.in
- **Website**: https://www.oneto7solutions.in
- **Support Portal**: Available 24/7 for licensed users

---

## 📚 Additional Resources

### **Documentation**
- **Video Tutorials**: Step-by-step implementation guides
- **Best Practices Guide**: Industry-specific KPI strategies
- **Formula Cookbook**: Ready-to-use calculation examples
- **Integration Manual**: Third-party system connections

### **Training Materials**
- **Administrator Guide**: Complete system configuration
- **User Manual**: End-user operational procedures
- **Developer Guide**: Customization and extension
- **Troubleshooting Guide**: Common issues and solutions

### **Community Support**
- **User Forum**: Community-driven support
- **Knowledge Base**: Searchable solution database
- **Feature Requests**: Community-driven development
- **Bug Reports**: Issue tracking and resolution

---

## ✅ Installation Checklist

### **Pre-Installation**
- [ ] Odoo 18.0+ environment verified
- [ ] User access requirements defined
- [ ] Department structure documented
- [ ] KPI definitions prepared
- [ ] Security groups planned

### **Post-Installation**
- [ ] Security groups configured
- [ ] Users assigned to appropriate groups
- [ ] Email server configured for notifications
- [ ] CRON jobs activated
- [ ] Demo data reviewed and removed if needed
- [ ] First KPI created and tested
- [ ] User training scheduled

### **Production Readiness**
- [ ] Performance testing completed
- [ ] Security audit passed
- [ ] Backup procedures established
- [ ] Monitoring systems configured
- [ ] User documentation distributed
- [ ] Support procedures defined

---

*© 2024 OneTo7 Solutions. All rights reserved. This module is licensed under OPL-1.*

---

## ✨ Key Features

### 📊 **KPI Management**
- **Manual KPIs**: User-entered values with validation and approval workflows
- **Automatic KPIs**: Formula-based calculations from any Odoo model
- **Target Types**: Number, Percentage, Currency (₹), Boolean (Achieved/Not Achieved), Duration (Hours)
- **Performance Direction**: Higher-is-better or Lower-is-better scoring logic

### 🏢 **Department Organization**
- Department-wise KPI organization (Sales, HR, Operations, Marketing, Finance, etc.)
- Report Groups for logical KPI clustering
- User and employee assignments with role-based access

### 🎯 **Performance Tracking**
- Target vs Achievement percentage calculation
- Color-coded performance indicators (Excellent, Good, Average, Needs Improvement, Underperformance)
- Historical submission tracking and audit trails
- Progress bars and visual performance indicators

### 🔔 **Automation & Notifications**
- Scheduled automatic KPI updates via CRON jobs
- Email reminders for manual KPI submissions
- Batch processing for large datasets
- Automated group-level performance aggregation

### 🔒 **Security & Access Control**
- Three-tier security model: Admin, Manager, User
- Record-level access rules
- Formula security validation
- Input sanitization and validation

---

## 🛠 Data Models

| Model | Description |
|-------|-------------|
| `kpi.report` | Main KPI definition with calculation logic |
| `kpi.report.group` | KPI grouping and department organization |
| `kpi.report.submission` | Individual KPI submission history |
| `kpi.report.group.submission` | Group-level performance history |

---

## 🔐 Security Groups

| Group | Permissions | Access Level |
|-------|-------------|--------------|
| **KPI Admin** | Full control of all KPIs, groups, and submissions | Create, Read, Write, Delete |
| **KPI Manager** | Department/group KPIs management | Create, Read, Write |
| **KPI User** | Assigned KPIs only | Read, Submit values |

---

## ⚙️ Configuration

### **Manual KPI Setup**
1. Create a Report Group for your department
2. Define KPI with type 'Manual'
3. Set target type and target value
4. Assign users who will submit values
5. Configure email reminders if needed

### **Automatic KPI Setup**
1. Create KPI with type 'Auto'
2. Select source model (e.g., sale.order, crm.lead)
3. **Select filter field** from dropdown (all fields are now available)
4. Set filter type (today, this week, this month)
5. **Build domain filter** using the visual domain builder (no Python code required)
6. Create formula using available variables:
   - `count_a`: Total records in base domain
   - `count_b`: Records matching filtered domain
   - `records`: Actual record objects
   - `assigned_user`: Current assigned user
   - `today`: Current date

### **Formula Examples**
```python
# Percentage calculation
(count_b / count_a) * 100

# Sum of amounts
sum(record.amount_total for record in records)

# Average calculation
sum(record.amount_total for record in records) / len(records) if records else 0

# Conditional logic
sum(record.amount_total for record in records if record.state == 'sale')
```

---

## 📱 User Interface

### **Dashboard Views**
- **List View**: Quick overview with progress bars and color coding
- **Form View**: Detailed KPI configuration and submission
- **Graph View**: Visual performance trends
- **Pivot View**: Multi-dimensional analysis

### **Key UI Elements**
- Progress bars for achievement visualization
- Color-coded badges for performance levels
- **Visual Domain Builder**: Intuitive interface for creating record filters without Python code
- **Enhanced Filter Field Selection**: All model fields available in dropdown (not just date/datetime)
- Contextual help text for complex fields
- Submission history tracking
- Test buttons for domain and formula validation

---

## 🚀 Installation & Setup

### **Prerequisites**
- Odoo 18.0 or later
- Dependencies: `base`, `hr`, `web`

### **Installation Steps**
1. Copy the module to your Odoo addons directory
2. Update the app list
3. Install the "KPI Tracking" module
4. Configure security groups and assign users
5. Create your first KPI Report Group
6. Define KPIs and start tracking!

---

## 🎨 Domain Builder Feature

The KPI Tracking module now includes a **Visual Domain Builder** that makes it easy to create record filters without writing Python code.

### **How to Use the Domain Builder**

1. **Open a KPI**: Go to KPI Reports → Open any KPI with 'Auto' type
2. **Navigate to Auto Tracking Configuration**: Scroll to the "Auto Tracking Configuration" section
3. **Select Source Model**: Choose the Odoo model you want to filter (e.g., sale.order, hr.employee)
4. **Click on Source Domain**: The domain builder widget will open in a popup dialog
5. **Build Your Filter Visually**:
   - Click "Add node" to add filter conditions
   - Select fields from dropdown menus
   - Choose operators (=, !=, <, >, contains, etc.)
   - Enter values for comparison
   - Use AND/OR logic to combine conditions
6. **Save the Domain**: Click "Save" to apply your domain filter

### **Domain Builder Benefits**

- **No Python Knowledge Required**: Build complex filters using a visual interface
- **Real-time Field Discovery**: All fields from the selected model are available in dropdowns
- **Operator Suggestions**: Appropriate operators are suggested based on field types
- **Syntax Validation**: Built-in validation ensures your domain is correctly formatted
- **Visual Logic**: See AND/OR groupings clearly in the interface

### **Example Domain Filters**

**Sales Orders from Last Month:**
```
[('date_order', '>=', '2024-01-01'), ('date_order', '<=', '2024-01-31')]
```

**Confirmed Sales Orders with Specific Salesperson:**
```
[('state', 'in', ['sale', 'done']), ('user_id.name', '=', 'John Doe')]
```

**HR Employees in Specific Department:**
```
[('department_id.name', 'ilike', 'sales'), ('active', '=', True)]
```

---

## 📧 Email System

The module includes an automated email reminder system:

- **Template**: `kpi_manual_entry_email_template`
- **Frequency**: Daily CRON job for manual KPI reminders
- **Manual Trigger**: Button on Report Groups to send immediate reminders
- **Recipients**: Assigned users with pending manual submissions

---

## 🔄 Automation

### **CRON Jobs**
1. **Auto Refresh KPIs**: Daily update of automatic KPIs
2. **Manual KPI Reminders**: Daily email reminders for pending submissions

### **Batch Processing**
- Efficient processing of large KPI datasets
- Memory-optimized calculations
- Error handling and logging

---

## 🛡️ Security Features

- **Formula Security**: Validation against dangerous code execution
- **Input Sanitization**: Comprehensive data validation
- **Access Control**: Record-level security rules
- **Audit Trail**: Complete submission history tracking

---

## 🎯 Best Practices

### **KPI Design**
- Use clear, measurable KPI names
- Set realistic and achievable targets
- Assign appropriate users to KPIs
- Regularly review and update targets

### **Formula Safety**
- Test formulas thoroughly before deployment
- Use the domain test button to validate filters
- Avoid complex calculations in formulas
- Document formula logic for maintenance

### **Performance Optimization**
- Use specific domains to limit record searches
- Avoid overly complex formulas
- Regular cleanup of old submissions
- Monitor CRON job performance

---

## 📋 Troubleshooting

### **Common Issues**
- **Formula Errors**: Use the Test Domain button to validate syntax
- **Permission Issues**: Check user group assignments
- **Performance Problems**: Review domain filters and optimize queries
- **Email Issues**: Verify email template configuration

### **Support**
For technical support and customization requests, please contact your system administrator or Odoo partner.

---

## 🚀 Future Enhancements Roadmap

### **v1.1 - Visual Insights & Alerts**
- Enhanced color-coded performance indicators
- Real-time dashboard updates
- Performance threshold alerts

### **v1.2 - Deadlines & Compliance**
- KPI submission deadlines
- Compliance tracking and reporting
- Calendar view for KPI schedules

### **v1.3 - Advanced Analytics**
- Weighted KPI scoring
- Performance rankings and leaderboards
- Trend analysis and predictions

### **v1.4 - Reporting & Export**
- Excel export functionality
- PDF report generation
- Automated report distribution

### **v1.5 - Templates & Automation**
- KPI templates for quick setup
- Auto-generation of recurring KPIs
- Department-based auto-assignment

---

## 📈 Version History

- **v18.1.0**: Odoo 18 compatibility, enhanced security, improved UI
- Enhanced code quality and performance optimizations
- Added comprehensive validation and error handling
- Improved user experience with contextual help

---

## 📄 License

This module is licensed under LGPL-3.

---

## 🏪 Odoo App Store Preparation

This module is prepared for publication on the Odoo App Store with the following commercial settings:

### 💰 **Commercial Information**
- **Price**: $20 USD
- **License**: OPL-1 (Odoo Proprietary License)
- **Category**: Human Resources
- **Author**: OneTo7 Solutions
- **Support**: info@oneto7solutions.in
- **Website**: https://www.oneto7solutions.in

### 📦 **Package Contents**
- ✅ Demo data with sample KPIs and submissions
- ✅ Professional README documentation
- ✅ Commercial license (OPL-1)
- ✅ Security and access control rules
- ✅ Email templates and CRON jobs
- ⚠️ **TODO**: Add static images (banner, icon, screenshots)

### 🖼️ **Required Images** (to be added)
Place these images in `static/description/`:
- `banner.png` (1200x300px) - App Store banner
- `icon.png` (128x128px) - Module icon
- `kpi_dashboard.png` (800x600px) - Dashboard screenshot
- `kpi_form.png` (800x600px) - Form view screenshot
- `kpi_reports.png` (800x600px) - Reports screenshot

### 🔍 **Pre-Publication Checklist**
- [x] Code quality review and refactoring
- [x] Security validation and access controls
- [x] Documentation cleanup and enhancement
- [x] Demo data creation
- [x] Commercial license and pricing
- [x] Manifest file optimization
- [ ] Static images creation
- [ ] Final testing in clean Odoo 18 instance
- [ ] App Store submission and review

---

## 📋 **Step-by-Step User Guide**

### 🚀 **Getting Started - Your First KPI**

#### **Step 1: Install and Setup**
1. Install the KPI Tracking module from Apps
2. Go to **Settings > Users & Companies > Users**
3. Add users to appropriate KPI groups:
   - **KPI Admin**: Full control (IT/Management)
   - **KPI Manager**: Department management (Team Leaders)
   - **KPI User**: Submit KPI values (Employees)

#### **Step 2: Create Your First KPI Group**
1. Navigate to **KPI Tracking > KPI Groups**
2. Click **Create** and fill in:
   - **Name**: "Sales Team Performance"
   - **Department**: Sales
   - **Description**: "Track monthly sales targets and achievements"
   - **Frequency**: Monthly
   - **Start/End Dates**: Set your reporting period
   - **Assigned Users**: Select team members

#### **Step 3: Create a Manual KPI**
1. Go to **KPI Tracking > KPI Reports**
2. Click **Create** and configure:
   - **KPI Name**: "Monthly Sales Revenue"
   - **KPI Group**: Select "Sales Team Performance"
   - **Target Type**: Currency
   - **Target Value**: 100000 (₹1,00,000)
   - **Calculation Type**: Manual
   - **Performance Direction**: Higher is Better
   - **Assigned User**: Select responsible person

#### **Step 4: Submit KPI Values**
1. Users can submit values from:
   - **KPI Reports list**: Click on KPI name
   - **My KPIs**: Shows only assigned KPIs
   - **KPI Submissions**: Historical view
2. Enter **Actual Value** and optional **Notes**
3. Click **Submit** to save

---

## 🔧 **Advanced KPI Configuration**

### **Creating Automatic KPIs**

#### **Sales Order Count Example**
```python
# KPI: Monthly Sales Order Count
Name: "Sales Orders This Month"
Calculation Type: Auto
Source Model: sale.order
Filter Field: date_order (selected from dropdown - all fields available)
Filter Type: this_month
Domain Filter: [('state', '=', 'sale')] (built using visual domain builder)
Formula: count_a
Target: 50
```

#### **Revenue Calculation Example**
```python
# KPI: Monthly Revenue
Name: "Monthly Revenue"
Calculation Type: Auto
Source Model: sale.order
Filter Field: date_order (selected from dropdown - all fields available)
Filter Type: this_month
Domain Filter: [('state', '=', 'sale')] (built using visual domain builder)
Formula: sum(record.amount_total for record in records)
Target: 500000
```

#### **Conversion Rate Example**
```python
# KPI: Lead to Sale Conversion Rate
Name: "Lead Conversion Rate"
Calculation Type: Auto
Source Model: crm.lead
Filter Field: create_date (selected from dropdown - all fields available)
Filter Type: this_month
Domain Filter: [('stage_id.is_won', '=', True)] (built using visual domain builder)
Formula: (count_b / count_a) * 100 if count_a > 0 else 0
Target: 25
```

### **Formula Variables Reference**
- **`count_a`**: Total records matching base domain
- **`count_b`**: Records matching filtered domain
- **`records`**: Actual record objects for calculations
- **`assigned_user`**: Current user context
- **`today`**: Current date

---

## 📊 **KPI Monitoring & Analytics**

### **Dashboard Views**

#### **List View Features**
- **Progress Bars**: Visual achievement percentage
- **Color Coding**: 
  - 🟢 Green: >90% achievement
  - 🟡 Yellow: 70-90% achievement
  - 🔴 Red: <70% achievement
- **Quick Actions**: Submit, Edit, View History

#### **Form View Details**
- **Performance Metrics**: Target vs Actual
- **Submission History**: Track all submissions
- **Performance Graph**: Trend analysis
- **Test Buttons**: Validate formulas and domains

#### **Graph View**
- **Line Charts**: Performance trends over time
- **Bar Charts**: Compare multiple KPIs
- **Pivot Tables**: Multi-dimensional analysis

### **Performance Monitoring**

#### **Individual KPI Tracking**
1. **Current Status**: Real-time achievement percentage
2. **Historical Trends**: Performance over time
3. **Submission Frequency**: Track regularity
4. **Performance Alerts**: Email notifications for targets

#### **Department-Level Monitoring**
1. **Group Performance**: Overall department achievement
2. **Team Comparisons**: Inter-departmental analysis
3. **Resource Allocation**: Identify improvement areas
4. **Trend Analysis**: Long-term performance patterns

---

## 📧 **Email Notifications & Reminders**

### **Automated Reminders**
- **Daily CRON Job**: Checks for pending manual KPIs
- **Email Template**: Professional reminder format
- **Recipient Logic**: Only assigned users with pending submissions
- **Customizable**: Modify email content and frequency

### **Manual Reminders**
- **Group Level**: Send reminders to all group members
- **Individual Level**: Target specific users
- **Immediate Send**: Button-triggered notifications
- **Bulk Operations**: Multiple KPIs at once

---

## 🎯 **Best Practices for KPI Success**

### **KPI Design Principles**
1. **SMART Goals**: Specific, Measurable, Achievable, Relevant, Time-bound
2. **Clear Naming**: Use descriptive, unambiguous names
3. **Realistic Targets**: Set achievable yet challenging goals
4. **Regular Review**: Update targets based on performance
5. **User Training**: Ensure all users understand the process

### **Department-Specific Examples**

#### **Sales Department**
- Monthly Revenue Achievement
- Lead Conversion Rate
- Customer Acquisition Cost
- Sales Cycle Time
- Customer Satisfaction Score

#### **HR Department**
- Employee Retention Rate
- Training Completion Rate
- Recruitment Time
- Employee Satisfaction
- Performance Review Completion

#### **Operations Department**
- Process Efficiency Rate
- Cost Reduction Achieved
- Quality Score
- Delivery Time
- Resource Utilization

#### **Marketing Department**
- Campaign ROI
- Lead Generation Rate
- Website Traffic Growth
- Social Media Engagement
- Brand Awareness Score

### **Common Pitfalls to Avoid**
1. **Too Many KPIs**: Focus on 3-5 key metrics per department
2. **Unrealistic Targets**: Set achievable goals
3. **Infrequent Updates**: Regular monitoring is essential
4. **No Action Plans**: Link KPIs to improvement initiatives
5. **Lack of Training**: Ensure users understand the system

---

## 🔍 **Troubleshooting Guide**

### **Common Issues**

#### **Formula Errors**
**Problem**: "Invalid formula syntax"
**Solution**: 
1. Use the **Test Domain** button to validate
2. Check variable names (count_a, count_b, records)
3. Ensure proper Python syntax
4. Test with simple formulas first

#### **Permission Issues**
**Problem**: "Access denied to KPI records"
**Solution**:
1. Check user group assignments
2. Verify record-level security rules
3. Ensure proper role assignments
4. Contact system administrator

#### **Email Not Sending**
**Problem**: "KPI reminders not received"
**Solution**:
1. Check email server configuration
2. Verify email template exists
3. Ensure CRON job is active
4. Check user email addresses

#### **Performance Issues**
**Problem**: "Slow KPI calculations"
**Solution**:
1. Optimize domain filters
2. Reduce formula complexity
3. Use specific date ranges
4. Consider database indexing

### **Getting Help**
- **Documentation**: Comprehensive README included
*© 2024 OneTo7 Solutions. All rights reserved. This module is licensed under OPL-1.*