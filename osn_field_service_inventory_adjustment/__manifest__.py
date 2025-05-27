# -*- coding: utf-8 -*-
{
    'name': "osn_field_service_inventory_adjustment",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
 Manage actual pieces installed during field service tasks and adjust inventory accordingly.  
   
     filted product list in pices  """,

    'author': "OneTo7 Safety Nets",
    'website': "https://www.oneto7safetynets.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.5',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/field_service_task_views.xml',
        'views/field_service_piece_views.xml',
        'data/ir_actions_server.xml',
    ],
    'installable': True,
    'application': True,
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

