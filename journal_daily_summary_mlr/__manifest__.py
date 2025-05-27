{
    'name': "journal_daily_summary_mlr",

    'summary': "Daily summary report for journals with WhatsApp-ready owner field",

    'description': """
Generate daily summary reports for each journal, linking journal owner to a contact for WhatsApp automation.
    """,

    'author': "Your Company",
    'website': "https://www.yourcompany.com",

    'category': 'Accounting',
    'version': '1.0',

    'depends': ['base', 'account'],

    'data': [
        'reports/journal_report_template.xml',
        'reports/journal_report.xml',
        'views/account_journal_view.xml'
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}