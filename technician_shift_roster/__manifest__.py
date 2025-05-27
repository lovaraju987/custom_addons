{
    'name': "Technician Shift Roster",
    'summary': "Roster management for technicians across stores",
    'description': """
        Manage weekly and daily technician shifts, track attendance, assign slots, and monitor wastage.
    """,
    'images': ["static/description/icon.png"],
    'author': "OneTo7 Safety Nets",
    'website': "https://www.oneto7safetynets.com",
    'category': 'Human Resources',
    'version': '2.0',
    'depends': ['base', 'hr', 'stock'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',  # ← if you created this as a separate file
        'views/technician_roster_views.xml',
        'data/slot_data.xml',
        'data/cron.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}