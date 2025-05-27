{
    "name": "KPI Tracking",
    "version": "11.6.7",
    "summary": "Track and manage department-wise KPIs",
    "description": "in this version updated group achievement calculation logic to take 100 percent only maximum each kpi percent and updated submission history to update correctly",
    "author": "Custom",
    "category": "Custom",
    "depends": ["base", "hr", "board", "web"],
    "data": [
        "security/security.xml",
        "security/kpi_tracking_rules.xml",
        "security/ir.model.access.csv",
        "views/kpi_views.xml",
        "views/kpi_report_group.xml",
        "views/kpi_submission.xml",
        "data/email_template.xml",
        "data/cron.xml"
    ],
    "installable": True,
    "auto_install": False
}
