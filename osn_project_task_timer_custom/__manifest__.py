# -*- coding: utf-8 -*-
{
    'name': "osn_project_task_timer_custom",

    'summary': "start , onhold, resume and stop buttons project tasks implemented. automatically stages changed if it is field service project. time sheets recorded",

    'description': """
Long description of module's purpose

        added error to not stop the task if progress is less than 80 percent. is mandatory field and stop condition added
        added customer satisfied field in task form view as readonly
    """,

    'author': "OneTo7 Safety Nets",
    'website': "https://www.oneto7safetynets.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.5',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'hr_timesheet', 'project_task_custom', 'osn_task_checklist'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/project_task_timer_views.xml',
        'views/customer_satisfaction_wizard_view.xml',
    ],
    'installable': True,
    'application': False,
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

