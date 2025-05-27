# -*- coding: utf-8 -*-
{
    'name': "osn_task_checklist",

    'summary': "task checklist for project module. along with progress bag and checklist photo attachment",

    'description': """
Long description of module's purpose
    """,

    'author': "OneTo7 Safety Nets",
    'website': "https://www.oneto7safetynets.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'osn_field_service_inventory_adjustment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/project_task_view.xml',
        'views/checklist_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

